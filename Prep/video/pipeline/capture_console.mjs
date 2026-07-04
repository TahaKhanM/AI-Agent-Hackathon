// V3 console capture harness — records the Precedent console (Chromium 1920x1080) while the
// harness drives the REAL loop over HTTP on a scripted timeline. [Prompts/08]
// Seed 4207, frozen build → byte-identical retakes. One webm per shot; a take-manifest JSON
// records the exact drive timeline so any shot re-captures identically.
//
// Reset discipline (learned): the RUNNING server must be reset IN-PROCESS via POST /api/demo/reset
// (STATE.reset reconnects STATE.conn). NEVER call scripts/demo_reset.py against a running server —
// it rebuilds the DB file out from under the live STATE.conn and every retrieval then fails closed.
//
// Usage:
//   PW_BASE=... PLAYWRIGHT_BROWSERS_PATH=... PRECEDENT_CONSOLE_URL=http://127.0.0.1:8200 \
//   node Prep/video/pipeline/capture_console.mjs <shot3|shot4|shot6> <take-int> <outdir>
import { recordSession } from './capture.mjs'
import fs from 'node:fs'
import path from 'node:path'

const CONSOLE = process.env.PRECEDENT_CONSOLE_URL || 'http://127.0.0.1:8200'
const [, , shot, takeArg, outdirArg] = process.argv
const take = takeArg || '1'
const outdir = outdirArg || 'precedent-video-drop/raw'
const W = 1920, H = 1080

const sleep = ms => new Promise(r => setTimeout(r, ms))
const timeline = []   // recorded drive timeline for the take-manifest
async function POST(pathname, note) {
  const t = Date.now()
  const res = await fetch(CONSOLE + pathname, { method: 'POST',
    headers: { 'Content-Type': 'application/json' }, body: '{}' })
  const body = await res.text()
  timeline.push({ at_ms: t, post: pathname, note, status: res.status, body: body.slice(0, 200) })
  return body
}
async function postJSON(pathname, obj, note) {
  const t = Date.now()
  const res = await fetch(CONSOLE + pathname, { method: 'POST',
    headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(obj) })
  const body = await res.text()
  timeline.push({ at_ms: t, post: pathname, note, status: res.status, body: body.slice(0, 200) })
  return body
}

// Move the cursor smoothly to an element and (optionally) click it. Playwright's click already
// scrolls into view; the pre-move + dwell gives the "human decides" beat on camera.
async function cursorTo(page, selector, { dwell = 1000, click = false } = {}) {
  const el = page.locator(selector).first()
  await el.scrollIntoViewIfNeeded().catch(() => {})
  const box = await el.boundingBox()
  if (box) await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 24 })
  await sleep(dwell)
  if (click) await el.click().catch(async () => { await page.evaluate(s => document.querySelector(s)?.click(), selector) })
}

// Rebind the console Approve button to the REAL held-approval resume (/api/drive/{n}/approve),
// so the visible hero click performs the honest T1 approval (approved by ops-lead), not the
// cosmetic console approve. A recording affordance only — product code is untouched.
async function rebindApproveToDrive(page) {
  await page.evaluate(() => {
    window.approve = async (id) => {
      const n = String(id).replace('INC-', '')
      await fetch('/api/drive/' + n + '/approve', { method: 'POST' })
      if (window.refresh) await window.refresh()
    }
  })
}

const INC1_APPROVE = '.inc:has-text("INC-1") button:has-text("Approve")'
const INC1_PROMOTE = '.inc:has-text("INC-1") button:has-text("Promote")'
const INC3_TRIAGE  = '.inc:has-text("INC-3") button:has-text("Triage")'
const PUB_CLASS = 'publisher|PUB-4012|schedule_item'
const SCHED_CLASS = 'scheduler|SCH-DUP-002|schedule_item'

async function driveShot3(page) {
  // Console home + gentle pan. ~10s.
  await POST('/api/demo/reset', 'clean in-process state')
  await sleep(1200)
  await page.reload({ waitUntil: 'networkidle' })
  await sleep(2500)                                   // hold on the home
  await page.mouse.move(700, 300, { steps: 20 })
  await page.evaluate(() => window.scrollTo({ top: 220, behavior: 'smooth' }))
  await sleep(2500)
  await cursorTo(page, '#incidents', { dwell: 1500 }) // hover the incident feed
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }))
  await sleep(2500)
}

// Move the cursor slowly over the Trace panel lines for `ms`, modelling a human reading the
// retrieved plan + rollback before deciding. Keeps the ~40s review dwell from being dead footage
// and makes the elapsed bar climb honestly to ~58s (the human decision time the 58s already counts).
async function reviewPlan(page, ms) {
  const t0 = Date.now()
  const ys = [140, 175, 205, 250, 300, 205, 175]
  let i = 0
  while (Date.now() - t0 < ms) {
    await page.mouse.move(1200 + (i % 2 ? 180 : -60), ys[i % ys.length], { steps: 18 })
    await sleep(2400)
    i++
  }
}

async function driveShot4(page) {
  // Incident 1: messy ticket → hold at gate → human reviews plan+rollback → hero Approve →
  // execute/verify → Promote. Paced so the elapsed bar lands near ~58s (the cross-surface number,
  // which already includes human review time); the manifest speeds it ~1.5x to the 40s slot.
  await POST('/api/demo/reset', 'clean in-process state')
  await postJSON('/api/revoke', { class_key: PUB_CLASS, principal: 'ops-lead' }, 'ladder hygiene: publisher → L1 so the gate shows')
  await sleep(1000)
  await page.reload({ waitUntil: 'networkidle' })
  await rebindApproveToDrive(page)
  await sleep(2500)                                   // show clean home + baseline bar
  await postJSON('/api/drive/1?hold=true', {}, 'real loop → gate (triage/risk/approval_requested)')
  await sleep(4000)                                   // trace fills to the gate (poll ~1.5s)
  await reviewPlan(page, 38000)                       // human reads the plan + rollback (~38s)
  await cursorTo(page, INC1_APPROVE, { dwell: 3000, click: true })   // hero click #1 (→ drive approve)
  await sleep(5000)                                   // execute → verify → memory_stored (elapsed ~55s)
  await rebindApproveToDrive(page)                    // (idempotent; reload-safe)
  await cursorTo(page, INC1_PROMOTE, { dwell: 2500, click: true })   // hero click #2 → Standing Approval
  await sleep(4000)                                   // badge flips; Revoke appears
}

async function driveShot6(page) {
  // Recovery (rollback + demote) then the refusal card. ~30s. Flake the PUBLISHER class — its fix is
  // a PUBLIC runbook (always permitted), so the fast-path reaches execution reliably; the
  // SCHED-restricted scheduler fix can fail-closed right after a reset before the ACL sync is fresh.
  await POST('/api/demo/reset', 'clean in-process state')
  await postJSON('/api/revoke', { class_key: PUB_CLASS, principal: 'ops-lead' }, 'ladder hygiene: publisher → L1')
  await sleep(1000)
  await page.reload({ waitUntil: 'networkidle' })
  await sleep(2000)
  // Recovery: promote the publisher class to STANDING, then flake it → rollback → demote.
  await postJSON('/api/promote', { class_key: PUB_CLASS, principal: 'ops-lead' }, 'pre-approve the fix class')
  await sleep(2500)                                   // badge → Standing Approval
  await postJSON('/api/drive/1/flake', {}, 'standing fast-path flakes → auto-rollback → class demoted')
  await sleep(5000)                                   // trace: executed → rolled_back → class_demoted
  // Refusal: triage the rights incident → restricted (count + owner only).
  await cursorTo(page, INC3_TRIAGE, { dwell: 2000, click: true })
  await sleep(5000)                                   // refusal card holds
}

const DRIVERS = { shot3: driveShot3, shot4: driveShot4, shot6: driveShot6 }

async function main() {
  const drive = DRIVERS[shot]
  if (!drive) { console.error('unknown shot:', shot, '(shot3|shot4|shot6)'); process.exit(2) }
  const outName = `${shot}-take${take}.webm`
  const webm = await recordSession(CONSOLE + '/', outdir, outName, async (page) => {
    await page.waitForLoadState('networkidle').catch(() => {})
    await drive(page)
  }, W, H)
  // write the take-manifest (drive timeline) next to the webm
  const manifest = { shot, take, console: CONSOLE, seed: 4207, recorded_webm: path.basename(webm), timeline }
  fs.writeFileSync(path.join(outdir, `${shot}-take${take}.timeline.json`), JSON.stringify(manifest, null, 2))
  console.log('captured', webm, '\n timeline:', JSON.stringify(timeline.map(t => t.post + ' ' + t.status)))
}
main().catch(e => { console.error(e); process.exit(1) })
