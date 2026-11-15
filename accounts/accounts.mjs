// Your ACE Music accounts in the ACE Music API by useapi.net: list them, read the live credits, add one, set maxJobs.
// Usage: node accounts.mjs                                   list the accounts (plan, maxJobs, health)
//        node accounts.mjs --credits --email you@example.com  live plan, credits left, models and their limits
//        ACEMUSIC_PASSWORD=… node accounts.mjs --add --email you@example.com [--max-jobs 4]
//        node accounts.mjs --max-jobs 2 --email you@example.com
// The password is the one you sign in with at acemusic.ai. It is read from ACEMUSIC_PASSWORD, never from the command line.
// Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#several-ace-music-accounts

import { api, args, emailOf, fail, log, requireToken } from '../lib/acemusic.mjs'

const a = args()
const email = emailOf(a)
requireToken()
const maxJobs = a['max-jobs'] !== undefined ? Number(a['max-jobs']) : undefined
const needEmail = () => {
    if (!email) {
        console.error('Pass --email (or set ACEMUSIC_EMAIL)')
        process.exit(1)
    }
}

if (a.add) {
    // POST /accounts {email, password, maxJobs?}: signs in to ACE Music, checks the account, then stores it
    needEmail()
    if (!process.env.ACEMUSIC_PASSWORD) {
        console.error('Set ACEMUSIC_PASSWORD to the account\'s acemusic.ai password')
        process.exit(1)
    }
    const r = await api('POST', '/accounts', { json: { email, password: process.env.ACEMUSIC_PASSWORD, ...(maxJobs ? { maxJobs } : {}) } })
    if (r.status !== 200) fail('POST /accounts', r)
    log(`added: ${r.data.plan_name ?? r.data.plan} plan, ${r.data.credits} credits, maxJobs ${r.data.maxJobs}`)
} else if (maxJobs) {
    // POST /accounts {email, maxJobs}: changes only maxJobs (1 to 4), nothing is sent to ACE Music
    needEmail()
    const r = await api('POST', '/accounts', { json: { email, maxJobs } })
    if (r.status !== 200) fail('POST /accounts', r)
    log(`maxJobs is now ${r.data.maxJobs}`)
} else if (a.credits) {
    // GET /accounts/{email}: read live from ACE Music
    needEmail()
    const r = await api('GET', `/accounts/${encodeURIComponent(email)}`)
    if (r.status !== 200) fail('GET /accounts/{email}', r)
    const d = r.data
    console.log(`${d.plan_name} (${d.cycle ?? 'free'}): ${d.credits} credits left, maxJobs ${d.maxJobs}, ${d.health}`)
    console.log(`costs: a request ${d.costs?.song} credits, stems ${d.costs?.stems?.['0']} (vocals) / ${d.costs?.stems?.['2']} (all)`)
    for (const m of d.models ?? []) console.log(`  ${m.id}: ${m.name}${m.free ? ', no credits' : ''}, style up to ${m.limits?.style}, lyrics up to ${m.limits?.lyrics}`)
} else {
    // GET /accounts: every account you added, as stored
    const r = await api('GET', '/accounts')
    if (r.status !== 200) fail('GET /accounts', r)
    for (const acc of Object.values(r.data)) console.log(`${acc.email}: ${acc.plan}, maxJobs ${acc.maxJobs}, ${acc.health}${acc.error ? `, error: ${acc.error}` : ''}`)
}
