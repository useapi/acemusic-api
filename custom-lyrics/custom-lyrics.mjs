// Your own lyrics, style and title with the ACE Music API by useapi.net, instrumentals, and lyrics written for you.
// Usage: node custom-lyrics.mjs [--prompts prompts.json] [--only 1,3] [--email you@example.com] [--wav]
// Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#sing-your-own-lyrics

import { readFile } from 'node:fs/promises'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { api, args, emailOf, fail, requireToken, runBatch, creditsLeft, log } from '../lib/acemusic.mjs'

const HERE = dirname(fileURLToPath(import.meta.url))
const a = args()
const email = emailOf(a)
requireToken()

// ACE-Step v1.5 XL takes a style of up to 512 characters and lyrics of up to 2,000 (ACE Music v1 / v1.1: 1,000 and 5,000)
const LIMITS = { 'ace-step-1.5-xl': { style: 512, lyrics: 2000 } }
const fit = (text, max) => {
    if (!max || text.length <= max) return text
    const cut = text.slice(0, max)
    return cut.slice(0, Math.max(cut.lastIndexOf('. ') + 1, cut.lastIndexOf(', '))) || cut
}

// writeLyrics → POST /music/lyrics, improveStyle → POST /music/style: ACE Music's writers, no song made yet
const write = async p => {
    const model = p.model ?? 'acemusic-v1'
    const out = {}
    if (p.writeLyrics) {
        log(`POST /music/lyrics "${p.writeLyrics.slice(0, 60)}…"`)
        const r = await api('POST', '/music/lyrics', { json: { prompt: p.writeLyrics, style: p.improveStyle, model, ...(email ? { email } : {}) } })
        if (r.status !== 200) fail('POST /music/lyrics', r)
        out.title = r.data.title
        out.lyrics = r.data.lyrics
        log(`  "${r.data.title}", ${r.data.lyrics.split('\n').length} lines`)
    }
    if (p.improveStyle !== undefined) {
        log(`POST /music/style "${p.improveStyle}"`)
        const r = await api('POST', '/music/style', { json: { style: p.improveStyle, model, ...(email ? { email } : {}) } })
        if (r.status !== 200) fail('POST /music/style', r)
        out.style = r.data.style
        log(`  ${r.data.style.slice(0, 100)}…`)
    }
    if (out.style) out.style = fit(out.style, LIMITS[model]?.style)
    if (out.lyrics) out.lyrics = fit(out.lyrics, LIMITS[model]?.lyrics)
    return out
}

const prompts = JSON.parse(await readFile(a.prompts ?? join(HERE, 'prompts.json'), 'utf8'))
const only = a.only ? String(a.only).split(',').map(Number) : null
const items = []
for (const [i, p] of prompts.entries()) {
    if (only && !only.includes(i + 1)) continue
    const fields = Object.fromEntries(Object.entries(p).filter(([k]) => !k.startsWith('_') && k !== 'writeLyrics' && k !== 'improveStyle'))
    const written = p.writeLyrics || p.improveStyle !== undefined ? await write(p) : {}
    const model = p.model ?? 'acemusic-v1'
    items.push({
        prefix: `${String(i + 1).padStart(2, '0')}-${model}`,
        wav: !!a.wav && model !== 'ace-step-1.5-xl',
        // title, style, lyrics (or instrumental: true), model and the options go to POST /music as they are
        body: { ...written, ...fields, ...(email ? { email } : {}) },
    })
}

const before = await creditsLeft(email)
const { results, spent } = await runBatch(items, join(HERE, 'output'), { example: 'custom-lyrics' })
log(`done: ${results.filter(r => r.job.status === 'completed').length} of ${items.length} requests completed, about ${spent} credits used${before !== null ? ` (credits before ${before}, now ${await creditsLeft(email)})` : ''}`)
for (const { job } of results)
    for (const s of job.songs ?? []) if (s.status === 'succeeded') console.log(`${s.songId}  "${s.title}"`)
