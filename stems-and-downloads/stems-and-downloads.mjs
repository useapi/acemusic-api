// Stems, downloads (MP3, WAV, MIDI, MusicXML) and the score of a song with the ACE Music API by useapi.net.
// Usage: node stems-and-downloads.mjs --song <songId> [--stems vocals,all|none] [--formats mp3,wav,midi,musicxml] [--score]
//        node stems-and-downloads.mjs --from ../custom-lyrics/output/<job>.json [--pick 1] …
// Stems (5 credits for vocals, 60 for every stem), WAV, MIDI and MusicXML need a paid ACE Music plan (Creator or
// Artist). MP3 and the score work on every plan. ACE-Step songs are MP3 only (no WAV).
// Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#split-a-song-into-stems

import { mkdir, writeFile } from 'node:fs/promises'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import {
    api, args, creditsOf, download, downloadLink, fail, ledger, log, readScore, requireToken, runStamp, slug, songsFrom, splitStems, waitForJob,
} from '../lib/acemusic.mjs'

const HERE = dirname(fileURLToPath(import.meta.url))
const OUT = join(HERE, 'output')
const a = args()
requireToken()
const [songId] = await songsFrom(a)
if (!songId) {
    console.error('Pass the song: --song <songId>, or --from <a job .json the other examples saved> [--pick 2]')
    process.exit(1)
}
const stemModes = String(a.stems ?? 'vocals').split(',').filter(m => m && m !== 'none')
const formats = String(a.formats ?? 'mp3,wav,midi,musicxml').split(',').filter(Boolean)
await mkdir(OUT, { recursive: true })

// GET /music/{songId}: the song with fresh links
const r = await api('GET', `/music/${encodeURIComponent(songId)}`)
if (r.status !== 200) fail('GET /music/{songId}', r)
const song = r.data
const base = join(OUT, `${slug(song.title)}-${runStamp()}`)
log(`"${song.title}" (${song.model}, ${Math.round(song.duration ?? 0)} s)`)

// POST /music/stems for each mode at once (async), then wait for each job and save every track
const jobs = []
for (const mode of stemModes) {
    log(`POST /music/stems mode ${mode}`)
    jobs.push(await splitStems(songId, mode))
}
for (const started of jobs) {
    const job = await waitForJob(started, { label: `stems ${started.stems?.mode}` })
    if (job.status !== 'completed') {
        log(`stems ${job.stems?.mode} ${job.status}: ${job.error ?? ''}`)
        continue
    }
    for (const t of job.stems.tracks) {
        if (!t.url) continue
        await download(t.url, `${base}-stems-${job.stems.mode}-${t.type}.mp3`)
        log(`  ${job.stems.mode}: ${t.type} → ${base}-stems-${job.stems.mode}-${t.type}.mp3`)
    }
    // a song already split in that mode answers at once with its tracks, and no credits are charged again
    const credits = started.status === 'completed' ? 0 : creditsOf(job)
    await ledger(OUT, { example: 'stems-and-downloads', what: `stems ${job.stems.mode}`, status: job.status, credits, tracks: job.stems.tracks.map(t => t.type) })
}

// GET /music/download: mp3 and wav come back as links (wav valid 24 hours), midi and musicxml as the file itself
for (const format of formats) {
    const got = await downloadLink(songId, format)
    if (!got) continue
    const ext = { mp3: 'mp3', wav: 'wav', midi: 'mid', musicxml: 'musicxml' }[format]
    const file = `${base}.${ext}`
    if (got.file) await writeFile(file, got.file)
    else await download(got.playUrl || got.url, file)
    log(`  ${format} → ${file}`)
}

// GET /music/score: ABC notation, every plan (1 credit the first time for an ACE-Step song)
if (a.score) {
    const score = await readScore(songId)
    if (score?.abc) {
        await writeFile(`${base}.abc`, score.abc)
        log(`  score (ABC, ${score.abc.split('\n').length} lines) → ${base}.abc`)
    }
}
