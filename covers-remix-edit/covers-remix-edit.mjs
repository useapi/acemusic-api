// Cover, remix or edit a song with the ACE Music API by useapi.net.
// Usage: node covers-remix-edit.mjs --song <songId> [--only 1,3] [--prompts prompts.json]
//        node covers-remix-edit.mjs --from ../custom-lyrics/output/<job>.json [--pick 1]
// The song can be any songId: one the API made, one from your Library (GET /music), or your own upload (POST /files).
// The request runs on the ACE Music account that holds the song.
// Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#covers-remixes-and-edits

import { readFile } from 'node:fs/promises'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { args, ensureScore, requireToken, runBatch, songsFrom, log } from '../lib/acemusic.mjs'

const HERE = dirname(fileURLToPath(import.meta.url))
const a = args()
requireToken()
const [song] = await songsFrom(a)
if (!song) {
    console.error('Pass the song to work on: --song <songId>, or --from <a job .json the other examples saved> [--pick 2]')
    process.exit(1)
}

// mode cover: acemusic-v1.1, or ACE-Step on ace-step-1.5-xl (key, coverStrength, remixStrength)
// mode remix and edit: ace-step-1.5-xl only. edit needs start and end (seconds) and the new lyrics of that part
const prompts = JSON.parse(await readFile(a.prompts ?? join(HERE, 'prompts.json'), 'utf8'))
const only = a.only ? String(a.only).split(',').map(Number) : null
const items = prompts
    .map((p, i) => ({ p, n: i + 1 }))
    .filter(({ n }) => !only || only.includes(n))
    .map(({ p, n }) => ({
        prefix: `${String(n).padStart(2, '0')}-${p.mode}-${p.model ?? 'acemusic-v1'}`,
        body: { references: [song], ...Object.fromEntries(Object.entries(p).filter(([k]) => !k.startsWith('_'))) },
    }))

// A cover on ACE Music v1 or v1.1 runs on v1.1, which follows the song's melody. The API reads an ACE Music v1 song's
// score by itself (free); an ACE-Step song's score must be read first (1 credit), so make sure the song has its score
if (items.some(i => i.body.mode === 'cover' && i.body.model !== 'ace-step-1.5-xl')) await ensureScore(song)

const { results, spent } = await runBatch(items, join(HERE, 'output'), { example: 'covers-remix-edit' })
log(`done: ${results.filter(r => r.job.status === 'completed').length} of ${items.length} requests completed, about ${spent} credits used`)
for (const { job } of results)
    for (const s of job.songs ?? []) if (s.status === 'succeeded') console.log(`${s.songId}  "${s.title}" (${s.kind})`)
