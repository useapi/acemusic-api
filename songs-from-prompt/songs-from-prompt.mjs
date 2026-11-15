// Songs from a prompt with the ACE Music API by useapi.net: one request = two songs.
// Usage: node songs-from-prompt.mjs [--prompts prompts.json] [--only 1,3] [--email you@example.com] [--wav]
// Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#make-songs-from-a-prompt

import { readFile } from 'node:fs/promises'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { args, emailOf, requireToken, runBatch, creditsLeft, log } from '../lib/acemusic.mjs'

const HERE = dirname(fileURLToPath(import.meta.url))
const a = args()
const email = emailOf(a)
requireToken()

const prompts = JSON.parse(await readFile(a.prompts ?? join(HERE, 'prompts.json'), 'utf8'))
const only = a.only ? String(a.only).split(',').map(Number) : null

// Every field of an entry goes to POST /music as is (prompt, model, references, images), except "_about" notes
const items = prompts
    .map((p, i) => ({ p, n: i + 1 }))
    .filter(({ n }) => !only || only.includes(n))
    .map(({ p, n }) => ({
        prefix: `${String(n).padStart(2, '0')}-${p.model ?? 'acemusic-v1'}`,
        wav: !!a.wav && (p.model ?? 'acemusic-v1') !== 'ace-step-1.5-xl',
        body: { ...Object.fromEntries(Object.entries(p).filter(([k]) => !k.startsWith('_'))), ...(email ? { email } : {}) },
    }))

const before = await creditsLeft(email)
const { results, spent } = await runBatch(items, join(HERE, 'output'), { example: 'songs-from-prompt' })
log(`done: ${results.filter(r => r.job.status === 'completed').length} of ${items.length} requests completed, about ${spent} credits used${before !== null ? ` (credits before ${before}, now ${await creditsLeft(email)})` : ''}`)
for (const { job } of results)
    for (const s of job.songs ?? []) if (s.status === 'succeeded') console.log(`${s.songId}  "${s.title}"`)
