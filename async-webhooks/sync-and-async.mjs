// Sync and async requests, job polling and replyUrl webhooks with the ACE Music API by useapi.net.
// Usage: node sync-and-async.mjs [--mode sync|async] [--reply-url https://your-server/hook] [--reply-ref my-ref] [--email you@example.com]
//   sync (default): POST /music waits for the songs and answers 200, or 202 with the job if it runs past 100 seconds
//   async: POST /music answers 201 at once, then GET /jobs/{jobid} is polled until the job is completed or failed
//   --reply-url: the API also POSTs the finished job record to that public https URL (see webhook-receiver.mjs)
// Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#sync-async-and-webhooks

import { readFile } from 'node:fs/promises'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { api, args, creditsOf, emailOf, fail, ledger, log, requireToken, saveSongs, waitForJob, runStamp } from '../lib/acemusic.mjs'

const HERE = dirname(fileURLToPath(import.meta.url))
const OUT = join(HERE, 'output')
const a = args()
const email = emailOf(a)
const mode = a.mode === 'async' ? 'async' : 'sync'
requireToken()

const [p] = JSON.parse(await readFile(a.prompts ?? join(HERE, 'prompts.json'), 'utf8'))
const body = {
    ...Object.fromEntries(Object.entries(p).filter(([k]) => !k.startsWith('_'))),
    ...(email ? { email } : {}),
    ...(mode === 'async' ? { async: true } : {}),
    ...(typeof a['reply-url'] === 'string' ? { replyUrl: a['reply-url'], replyRef: typeof a['reply-ref'] === 'string' ? a['reply-ref'] : `example-${runStamp()}` } : {}),
}

const t0 = Date.now()
log(`POST /music (${mode}${body.replyUrl ? ', with replyUrl' : ''})`)
const r = await api('POST', '/music', { json: body })
const secs = () => `${Math.round((Date.now() - t0) / 1000)} s`
let job = r.data
if (r.status === 200) log(`200 after ${secs()}: the songs are ready`)
else if (r.status === 201) log(`201 after ${secs()}: the job is running, jobid ${job.jobid}`)
else if (r.status === 202) log(`202 after ${secs()}: still running after 100 seconds, polling the job`)
else if (r.status === 422) log(`422 after ${secs()}: ACE Music could not make the songs: ${job.error}`)
else fail('POST /music', r)

if (mode === 'async') {
    // GET /jobs: every job running now on your ACE Music accounts
    const running = await api('GET', '/jobs')
    const jobs = running.data?.jobs ?? []
    log(`GET /jobs: ${jobs.length} job(s) running now: ${jobs.map(j => `${j.type} ${j.model ?? j.stemsMode ?? ''}`).join(', ')}`)
}
if (job.status === 'processing') job = await waitForJob(job, { label: 'job' })
log(`${job.status} after ${secs()}: ${job.modelUsed}, ${creditsOf(job)} credits`)

const prefix = `${mode}-${runStamp()}`
if (job.status === 'completed') await saveSongs(job, OUT, prefix)
await ledger(OUT, { example: 'async-webhooks', prefix, mode, status: job.status, httpStatus: r.status, seconds: Math.round((Date.now() - t0) / 1000), modelUsed: job.modelUsed, credits: creditsOf(job), replyUrl: !!body.replyUrl })
if (body.replyUrl) log(`the finished record was also POSTed to your replyUrl (replyRef ${body.replyRef})`)
