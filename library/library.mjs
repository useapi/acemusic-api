// Your ACE Music Library with the ACE Music API by useapi.net: list songs, read one with fresh links, delete one.
// Usage: node library.mjs [--limit 20] [--all] [--email you@example.com]   list the Library, newest first
//        node library.mjs --song <songId>                                  one song with fresh links
//        node library.mjs --delete <songId>                                move a song to ACE Music's trash
// The Library holds every song of the account: made through the API or on acemusic.ai, and your uploads.
// Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#your-library

import { api, args, emailOf, fail, log, requireToken } from '../lib/acemusic.mjs'

const a = args()
const email = emailOf(a)
requireToken()

if (typeof a.song === 'string') {
    // GET /music/{songId}: the song with fresh links (playUrl for players, its stems when it was split)
    const r = await api('GET', `/music/${encodeURIComponent(a.song)}`)
    if (r.status !== 200) fail('GET /music/{songId}', r)
    const s = r.data
    console.log(`"${s.title}" ${s.status}, ${s.model ?? 'upload'}, ${Math.round(s.duration ?? 0)} s, ${s.kind}${s.score ? ', has a score' : ''}`)
    console.log(`  style: ${s.style}`)
    console.log(`  audioUrl: ${s.audioUrl}`)
    if (s.playUrl) console.log(`  playUrl: until ${s.playUrlExpires}`)
    for (const [mode, st] of Object.entries(s.stems ?? {})) console.log(`  stems ${mode}: ${(st.tracks ?? []).map(t => t.type).join(', ')}`)
} else if (typeof a.delete === 'string') {
    // DELETE /music/{songId}: 204, the song goes to the account's trash on acemusic.ai
    const r = await api('DELETE', `/music/${encodeURIComponent(a.delete)}`)
    if (r.status !== 204) fail('DELETE /music/{songId}', r)
    log('deleted (moved to the ACE Music trash, restorable on acemusic.ai only)')
} else {
    // GET /music: one page of the Library, and `next` for the following page (null on the last one)
    let after = null
    let n = 0
    do {
        const r = await api('GET', '/music', { query: { email, limit: a.limit ?? 20, after } })
        if (r.status !== 200) fail('GET /music', r)
        for (const s of r.data.songs) console.log(`${++n}. "${s.title}" ${s.model ?? 'upload'} ${Math.round(s.duration ?? 0)} s ${s.kind}  ${s.songId}`)
        after = r.data.next
    } while (a.all && after)
    if (after) log('more songs: --all lists every page')
}
