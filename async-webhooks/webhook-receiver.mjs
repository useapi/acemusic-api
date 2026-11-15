// A minimal replyUrl receiver for the ACE Music API by useapi.net: prints each job record it gets and saves it to
// output/webhooks.jsonl. The API POSTs the finished job record (the same JSON as GET /jobs/{jobid}) once per job.
// Usage: node webhook-receiver.mjs [--port 8080]
// The replyUrl must be a public https URL: put this behind a tunnel or a reverse proxy, then pass that URL as
// --reply-url to sync-and-async.mjs (or replyUrl to POST /music).

import { createServer } from 'node:http'
import { mkdir, appendFile } from 'node:fs/promises'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const port = Number(process.argv[process.argv.indexOf('--port') + 1]) || 8080
await mkdir(join(HERE, 'output'), { recursive: true })

createServer((req, res) => {
    if (req.method !== 'POST') return res.writeHead(405).end()
    let raw = ''
    req.on('data', c => (raw += c))
    req.on('end', async () => {
        res.writeHead(200, { 'Content-Type': 'application/json' }).end('{"ok":true}')
        try {
            const job = JSON.parse(raw)
            console.log(`${new Date().toISOString()} ${job.type} job ${job.status} (replyRef ${job.replyRef ?? '-'})`)
            for (const s of job.songs ?? []) console.log(`  "${s.title}" ${s.status} ${s.audioUrl ?? ''}`)
            for (const t of job.stems?.tracks ?? []) console.log(`  ${t.type} ${t.url ? 'ready' : '-'}`)
            if (job.error) console.log(`  error ${job.code}: ${job.error}`)
            await appendFile(join(HERE, 'output', 'webhooks.jsonl'), raw.replace(/\n/g, ' ') + '\n')
        } catch (e) {
            console.log('not JSON:', raw.slice(0, 200))
        }
    })
}).listen(port, () => console.log(`listening on http://localhost:${port} — expose it as https and pass that URL as replyUrl`))
