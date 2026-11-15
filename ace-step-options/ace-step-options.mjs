// ACE-Step v1.5 XL with tempo, key, time signature, length, styles to avoid and thinking, by the ACE Music API (useapi.net).
// ACE-Step songs use no credits on any ACE Music plan, the Free plan included.
// Usage: node ace-step-options.mjs [--prompts prompts.json] [--only 1,3] [--email you@example.com]
// Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#control-tempo-key-and-time-signature-with-ace-step

import { readFile } from 'node:fs/promises'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { args, emailOf, requireToken, runBatch, log } from '../lib/acemusic.mjs'

const HERE = dirname(fileURLToPath(import.meta.url))
const a = args()
const email = emailOf(a)
requireToken()

// bpm 30-200, timeSignature 2/4 3/4 4/4 6/8, key "C major" … "B minor", duration 10-240 s, negative up to 200
// characters, thinking 0-100: these options work in mode generate on ace-step-1.5-xl only
const prompts = JSON.parse(await readFile(a.prompts ?? join(HERE, 'prompts.json'), 'utf8'))
const only = a.only ? String(a.only).split(',').map(Number) : null
const items = prompts
    .map((p, i) => ({ p, n: i + 1 }))
    .filter(({ n }) => !only || only.includes(n))
    .map(({ p, n }) => ({
        prefix: `${String(n).padStart(2, '0')}-${(p.title ?? 'song').toLowerCase().replace(/[^a-z0-9]+/g, '-')}`,
        body: {
            model: 'ace-step-1.5-xl',
            ...Object.fromEntries(Object.entries(p).filter(([k]) => !k.startsWith('_'))),
            ...(email ? { email } : {}),
        },
    }))

const { results } = await runBatch(items, join(HERE, 'output'), { example: 'ace-step-options' })
for (const { item, job } of results) {
    const { bpm, timeSignature, key, duration } = item.body
    log(`${item.body.title}: asked ${bpm} bpm, ${timeSignature}, ${key}, ${duration} s → ${(job.songs ?? []).map(s => `${Math.round(s.duration ?? 0)} s`).join(' / ')}`)
}
