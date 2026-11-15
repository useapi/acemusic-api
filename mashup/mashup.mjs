// Mash up 2 or 3 songs into one with the ACE Music API by useapi.net (ACE Music v1.1 Preview, 4 credits).
// Usage: node mashup.mjs --songs <songId>,<songId>[,<songId>] [--prompts prompts.json] [--model acemusic-v1]
//        node mashup.mjs --from <job1.json>,<job2.json> [--pick 1]
// Every song must be on the same ACE Music account. A mashup always runs on acemusic-v1.1: the job reports the
// model you asked for (model) and the one that ran (modelUsed).
// Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#mash-up-two-or-three-songs

import { readFile } from 'node:fs/promises'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { args, ensureScore, requireToken, runBatch, songsFrom, log } from '../lib/acemusic.mjs'

const HERE = dirname(fileURLToPath(import.meta.url))
const a = args()
requireToken()
const songs = await songsFrom(a, 'songs')
if (songs.length < 2 || songs.length > 3) {
    console.error('Pass 2 or 3 songs: --songs <songId>,<songId>, or --from <job1.json>,<job2.json> [--pick 1]')
    process.exit(1)
}

// ACE Music v1.1 follows each song's melody: make sure every song has its score
for (const s of songs) await ensureScore(s)

const prompts = JSON.parse(await readFile(a.prompts ?? join(HERE, 'prompts.json'), 'utf8'))
const items = prompts.map((p, i) => ({
    prefix: `${String(i + 1).padStart(2, '0')}-mashup`,
    body: { mode: 'mashup', model: a.model ?? 'acemusic-v1.1', references: songs, ...Object.fromEntries(Object.entries(p).filter(([k]) => !k.startsWith('_'))) },
}))

const { results, spent } = await runBatch(items, join(HERE, 'output'), { example: 'mashup' })
log(`done: ${results.filter(r => r.job.status === 'completed').length} of ${items.length} mashups completed, about ${spent} credits used`)
for (const { job } of results)
    for (const s of job.songs ?? []) if (s.status === 'succeeded') console.log(`${s.songId}  "${s.title}"`)
