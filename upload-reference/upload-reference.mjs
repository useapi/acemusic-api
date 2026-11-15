// Upload your own audio and an image with the ACE Music API by useapi.net (POST /files), then make songs guided by them.
// Usage: node upload-reference.mjs --audio my-song.mp3 [--image picture.jpg] [--title "My demo"] [--only 1,2] [--email you@example.com]
// Audio: MP3, WAV, FLAC, OGG, M4A or AAC, up to 100 MB and 8 minutes. ACE Music transcribes it into a Library song
// (lyrics, style, tempo, melody), usable as a reference: in a prompt, or to cover, remix, edit or mash up.
// Image: JPEG, PNG or WebP, up to 10 MB, for a prompt's images.
// Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#guide-songs-with-your-own-audio-and-images

import { readFile, mkdir, appendFile } from 'node:fs/promises'
import { join, dirname, extname, basename } from 'node:path'
import { fileURLToPath } from 'node:url'
import { api, args, emailOf, fail, requireToken, runBatch, log, sleep } from '../lib/acemusic.mjs'

const HERE = dirname(fileURLToPath(import.meta.url))
const a = args()
const email = emailOf(a)
requireToken()
if (typeof a.audio !== 'string' && typeof a.image !== 'string') {
    console.error('Pass --audio <file> and/or --image <file>')
    process.exit(1)
}

const TYPES = {
    '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.flac': 'audio/flac', '.ogg': 'audio/ogg', '.m4a': 'audio/mp4', '.aac': 'audio/aac',
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp',
}

// POST /files: the file as the raw request body with its Content-Type (fetch sends Content-Length)
const upload = async (file, title) => {
    const type = TYPES[extname(file).toLowerCase()]
    if (!type) throw new Error(`unsupported file type: ${file}`)
    log(`POST /files ${basename(file)} (${type})`)
    const r = await api('POST', '/files', { query: { email, title }, body: await readFile(file), headers: { 'Content-Type': type } })
    if (r.status !== 200 && r.status !== 202) fail('POST /files', r)
    let item = r.data
    // audio still being transcribed after 90 s answers 202: read the song until it is done
    while (item.songId && item.status !== 'succeeded' && item.status !== 'failed') {
        await sleep(10_000)
        const g = await api('GET', `/music/${encodeURIComponent(item.songId)}`)
        if (g.status !== 200) fail('GET /music/{songId}', g)
        item = g.data
    }
    if (item.status === 'failed') throw new Error(`ACE Music could not read ${file}: ${item.error?.message ?? ''}`)
    // keep the ids: a songId works with covers-remix-edit and mashup (--song), a mediaId in a prompt's images
    await mkdir(join(HERE, 'output'), { recursive: true })
    await appendFile(join(HERE, 'output', 'uploads.jsonl'), JSON.stringify({ at: new Date().toISOString(), file: basename(file), songId: item.songId, mediaId: item.mediaId, title: item.title, seconds: item.duration, bpm: item.upload?.bpm }) + '\n')
    return item
}

const audio = typeof a.audio === 'string' ? await upload(a.audio, typeof a.title === 'string' ? a.title : undefined) : null
if (audio) log(`  songId ${audio.songId}\n  heard: ${audio.upload?.bpm ?? '?'} bpm, ${audio.duration} s, "${(audio.style ?? '').slice(0, 120)}…"`)
const image = typeof a.image === 'string' ? await upload(a.image) : null
if (image) log(`  mediaId ${image.mediaId}`)

const prompts = JSON.parse(await readFile(a.prompts ?? join(HERE, 'prompts.json'), 'utf8'))
const only = a.only ? String(a.only).split(',').map(Number) : null
const items = []
for (const [i, p] of prompts.entries()) {
    if (only && !only.includes(i + 1)) continue
    if ((p.useAudio && !audio) || (p.useImage && !image)) {
        log(`#${i + 1} skipped: it needs ${p.useAudio ? '--audio' : '--image'}`)
        continue
    }
    const fields = Object.fromEntries(Object.entries(p).filter(([k]) => !k.startsWith('_') && k !== 'useAudio' && k !== 'useImage'))
    items.push({
        prefix: `${String(i + 1).padStart(2, '0')}-${p.useAudio ? 'audio' : 'image'}-${p.model ?? 'acemusic-v1'}`,
        // the request runs on the account that holds the upload, so no email is needed here
        body: { ...fields, ...(p.useAudio ? { references: [audio.songId] } : {}), ...(p.useImage ? { images: [image.mediaId] } : {}) },
    })
}

const { results, spent } = await runBatch(items, join(HERE, 'output'), { example: 'upload-reference' })
log(`done: ${results.filter(r => r.job.status === 'completed').length} of ${items.length} requests completed, about ${spent} credits used`)
for (const { job } of results)
    for (const s of job.songs ?? []) if (s.status === 'succeeded') console.log(`${s.songId}  "${s.title}"`)
