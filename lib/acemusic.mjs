// Shared helpers for the ACE Music API examples by useapi.net.
// Node.js 21 or newer, no dependencies (built-in fetch).
// API reference: https://useapi.net/docs/api-acemusic-v1

import { mkdir, writeFile, appendFile } from 'node:fs/promises'
import { join } from 'node:path'

export const API = (process.env.USEAPI_BASE || 'https://api.useapi.net/v1/acemusic').replace(/\/$/, '')
export const TOKEN = process.env.USEAPI_TOKEN

// Credits ACE Music charges per request (as of November 2026): 4 for two songs on ACE Music v1 and v1.1,
// nothing on ACE-Step v1.5 XL, 5 for a vocal + instrumental split and 60 for every stem.
export const PAID_MODELS = ['acemusic-v1', 'acemusic-v1.1']
export const STEMS_CREDITS = { vocals: 5, all: 60 }

export const sleep = ms => new Promise(r => setTimeout(r, ms))
export const log = (...a) => console.log(new Date().toISOString().slice(11, 19), ...a)

// --name value and --flag from the command line
export const args = () => {
    const out = {}
    const argv = process.argv.slice(2)
    for (let i = 0; i < argv.length; i++) {
        if (!argv[i].startsWith('--')) continue
        const key = argv[i].slice(2)
        const next = argv[i + 1]
        out[key] = next === undefined || next.startsWith('--') ? true : (i++, next)
    }
    return out
}

// The ACE Music account to use: --email, else ACEMUSIC_EMAIL, else none (the API picks a healthy account)
export const emailOf = a => (typeof a.email === 'string' && a.email.trim()) || process.env.ACEMUSIC_EMAIL || null

// A songId from --song, or song N of a job record a script saved (--from ../custom-lyrics/output/<job>.json --pick 2)
export const songsFrom = async (a, key = 'song') => {
    if (typeof a[key] === 'string') return a[key].split(',').map(s => s.trim()).filter(Boolean)
    if (typeof a.from !== 'string') return []
    const { readFile } = await import('node:fs/promises')
    const picks = String(a.pick ?? '1').split(',').map(Number)
    const out = []
    for (const file of a.from.split(',')) {
        const job = JSON.parse(await readFile(file.trim(), 'utf8'))
        for (const n of picks) if (job.songs?.[n - 1]?.songId) out.push(job.songs[n - 1].songId)
    }
    return out
}

export const requireToken = () => {
    if (!TOKEN) {
        console.error('Set USEAPI_TOKEN to your useapi.net API token, see https://useapi.net/docs/start-here/setup-useapi')
        process.exit(1)
    }
}

// One API call. JSON in and out, a raw body for uploads. 429 (the account is running its maxJobs) and
// 503 (ACE Music busy, nothing charged) are retried after Retry-After. Other answers are returned as they are.
export const api = async (method, path, { json, query, body, headers = {}, retries = 10 } = {}) => {
    const url = new URL(API + path)
    for (const [k, v] of Object.entries(query ?? {}))
        if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, v)
    for (let attempt = 0; ; attempt++) {
        const res = await fetch(url, {
            method,
            headers: { Authorization: `Bearer ${TOKEN}`, ...(json ? { 'Content-Type': 'application/json' } : {}), ...headers },
            body: json ? JSON.stringify(json) : body,
        })
        const type = res.headers.get('content-type') ?? ''
        const data = type.includes('json') ? await res.json() : res.status === 204 ? null : Buffer.from(await res.arrayBuffer())
        if ((res.status === 429 || res.status === 503) && attempt < retries) {
            const wait = Number(res.headers.get('retry-after')) || 30
            log(`${res.status} ${data?.error ?? ''} — retrying in ${wait} s`)
            await sleep(wait * 1000)
            continue
        }
        return { status: res.status, data, headers: res.headers }
    }
}

export const fail = (what, r) => {
    throw new Error(`${what}: HTTP ${r.status} ${typeof r.data === 'object' && !Buffer.isBuffer(r.data) ? JSON.stringify(r.data) : ''}`)
}

// POST /music in async mode: answers 201 at once with the job (status "processing")
export const createSongs = async body => {
    const r = await api('POST', '/music', { json: { ...body, async: true } })
    if (r.status !== 201 && r.status !== 200) fail('POST /music', r)
    return r.data
}

// POST /music/stems in async mode
export const splitStems = async (songId, mode) => {
    const r = await api('POST', '/music/stems', { json: { songId, mode, async: true } })
    if (r.status !== 201 && r.status !== 200) fail('POST /music/stems', r)
    return r.data
}

// Poll GET /jobs/{jobid} every 10 seconds until the job is completed or failed
export const waitForJob = async (job, { every = 10_000, label = '' } = {}) => {
    let last = ''
    while (job.status === 'processing') {
        await sleep(every)
        const r = await api('GET', `/jobs/${encodeURIComponent(job.jobid)}`)
        if (r.status !== 200) fail(`GET /jobs/${job.jobid}`, r)
        job = r.data
        const now = job.type === 'stems' ? job.status : (job.songs ?? []).map(s => s.status).join(', ')
        if (now !== last) log(`${label} ${job.status} (${now})`)
        last = now
    }
    return job
}

// Credits a finished job used, by the rule ACE Music charges (failed songs that were refunded cost nothing)
export const creditsOf = job => {
    if (job.type === 'stems') return job.status === 'completed' ? STEMS_CREDITS[job.stems?.mode] ?? 0 : 0
    if (job.songs?.length && job.songs.every(s => s.refunded)) return 0
    return PAID_MODELS.includes(job.modelUsed) ? 4 : 0
}

export const slug = s => (s || 'untitled').toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 50) || 'untitled'

export const download = async (url, file) => {
    const res = await fetch(url)
    if (!res.ok) throw new Error(`download ${res.status} ${url.split('?')[0]}`)
    await writeFile(file, Buffer.from(await res.arrayBuffer()))
    return file
}

// Save both songs of a finished job: the mp3 (playUrl when the API returns it, else audioUrl), the cover art,
// a WAV when asked (paid ACE Music plans, not for ACE-Step songs), and the job record as JSON
export const saveSongs = async (job, dir, prefix, { wav = false } = {}) => {
    await mkdir(dir, { recursive: true })
    await writeFile(join(dir, `${prefix}.json`), JSON.stringify(job, null, 2))
    const files = []
    for (const [i, song] of (job.songs ?? []).entries()) {
        if (song.status !== 'succeeded') {
            log(`song ${i + 1}: ${song.status} ${song.error?.message ?? ''}`)
            continue
        }
        const base = join(dir, `${prefix}-${i + 1}-${slug(song.title)}`)
        files.push(await download(song.playUrl || song.audioUrl, `${base}.mp3`))
        if (song.coverUrl) files.push(await download(song.coverUrl, `${base}.jpg`).catch(() => null))
        if (wav) {
            const link = await downloadLink(song.songId, 'wav')
            if (link?.url) files.push(await download(link.url, `${base}.wav`))
        }
        log(`  ${i + 1}. "${song.title}" ${Math.round(song.duration ?? 0)} s → ${base}.mp3`)
    }
    return files.filter(Boolean)
}

// GET /music/download: JSON with a link (mp3, wav) or the file itself (midi, musicxml). ACE Music makes WAV,
// MIDI and MusicXML on the first request, so a 202 is asked again a minute later.
export const downloadLink = async (songId, format, { tries = 5 } = {}) => {
    for (let i = 0; i < tries; i++) {
        const r = await api('GET', '/music/download', { query: { songId, format } })
        if (r.status === 200) return Buffer.isBuffer(r.data) ? { file: r.data, headers: r.headers } : r.data
        if (r.status !== 202) {
            log(`GET /music/download ${format}: HTTP ${r.status} ${r.data?.error ?? ''}`)
            return null
        }
        log(`${format}: ACE Music is still making it, asking again in 60 s`)
        await sleep(60_000)
    }
    return null
}

// GET /music/score: the song's score in ABC notation. ACE Music reads it on the first request (free for ACE Music
// v1 songs, 1 credit for an ACE-Step song, already there for v1.1 songs and uploads). The API waits up to a minute,
// then answers 202: asked again a minute later.
export const readScore = async (songId, { tries = 5 } = {}) => {
    for (let i = 0; i < tries; i++) {
        const r = await api('GET', '/music/score', { query: { songId } })
        if (r.status === 200) return r.data
        if (r.status !== 202) fail('GET /music/score', r)
        log('ACE Music is still reading the score, asking again in 60 s')
        await sleep(60_000)
    }
    return null
}

// ACE Music v1.1 follows a reference by its melody. A song without a score failed with ref_no_melody in our tests
// (credits refunded) and worked once its score was read, so read it first when the song has none.
export const ensureScore = async songId => {
    const r = await api('GET', `/music/${encodeURIComponent(songId)}`)
    if (r.status !== 200) fail(`GET /music/${songId}`, r)
    if (r.data.score) return
    log(`"${r.data.title}" has no score yet: GET /music/score first (ACE Music v1.1 reads the melody from it)`)
    await readScore(songId)
}

// GET /accounts/{email}: the account's live plan and credits (null without an email)
export const creditsLeft = async email => {
    if (!email) return null
    const r = await api('GET', `/accounts/${encodeURIComponent(email)}`)
    return r.status === 200 ? r.data.credits : null
}

// One line per job in output/ledger.jsonl: what ran, on which model, what it cost
export const ledger = async (dir, entry) => {
    await mkdir(dir, { recursive: true })
    await appendFile(join(dir, 'ledger.jsonl'), JSON.stringify({ at: new Date().toISOString(), ...entry }) + '\n')
}

// Submit up to `parallel` requests, wait for them, save the songs. Each item: { body, prefix, wav }
export const runStamp = () => new Date().toISOString().replace(/[-:]/g, '').slice(4, 13).replace('T', '-')

export const runBatch = async (items, dir, { example, parallel = 4 } = {}) => {
    let spent = 0
    const results = []
    const run = runStamp() // file names carry the run's UTC time (MMDD-HHMM), so a new run never overwrites an old one
    items = items.map(i => ({ ...i, prefix: `${i.prefix}-${run}` }))
    for (let start = 0; start < items.length; start += parallel) {
        const chunk = items.slice(start, start + parallel)
        const jobs = []
        for (const item of chunk) {
            log(`#${item.prefix} POST /music (${item.body.model ?? 'acemusic-v1'}${item.body.mode ? `, mode ${item.body.mode}` : ''})`)
            try {
                jobs.push({ item, job: await createSongs(item.body) })
            } catch (e) {
                log(`#${item.prefix} ${e.message}`)
                await ledger(dir, { example, prefix: item.prefix, status: 'refused', error: e.message, credits: 0 })
            }
        }
        for (const { item, job: started } of jobs) {
            const job = await waitForJob(started, { label: `#${item.prefix}` })
            const credits = creditsOf(job)
            spent += credits
            log(`#${item.prefix} ${job.status}: model ${job.model} → ran on ${job.modelUsed}, ${credits} credits${job.error ? `, ${job.error}` : ''}`)
            const files = job.status === 'completed' || job.songs?.some(s => s.status === 'succeeded') ? await saveSongs(job, dir, item.prefix, { wav: item.wav }) : []
            await ledger(dir, {
                example, prefix: item.prefix, status: job.status, model: job.model, modelUsed: job.modelUsed, credits,
                songs: (job.songs ?? []).map(s => ({ title: s.title, duration: s.duration, status: s.status })), error: job.error,
            })
            results.push({ item, job, files })
        }
    }
    return { results, spent }
}
