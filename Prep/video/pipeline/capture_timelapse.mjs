// V2 manual-loop time-lapse — Playwright grinds a human-speed pass through the dated legacy-admin
// mockup (read ticket → hunt KB, open wrong articles → admin form → raise approval → wait). No humans
// filmed, fully retakeable. ffmpeg then does 8x + the clock overlay (see build_timelapse.sh). [Prompts/08]
import { recordSession } from './capture.mjs'
const sleep = ms => new Promise(r => setTimeout(r, ms))
const [, , outdirArg] = process.argv
const outdir = outdirArg || 'precedent-video-drop/raw'
const MOCK = 'Prep/video/pipeline/cards/legacy_admin.html'

async function grind(page) {
  await sleep(2500)                                   // read the messy ticket (Incident tab)
  await page.mouse.move(700, 500, { steps: 20 })
  await page.evaluate(() => document.getElementById('main').scrollTo({ top: 200, behavior: 'smooth' }))
  await sleep(2000)
  // hunt the knowledge base
  await page.click('#tab-kb'); await sleep(1200)
  await page.click('#kbq')
  await page.type('#kbq', 'epg publish 9pm slot blank err 4102', { delay: 90 })
  await sleep(1200)
  await page.click('.result:nth-child(1)'); await sleep(2200)     // KB-2231 — wrong (schema ref)
  await page.click('.result:nth-child(2)'); await sleep(2200)     // KB-4477 — wrong (Sky Q device)
  await page.mouse.move(600, 640, { steps: 16 })
  await page.click('.result:nth-child(3)'); await sleep(2200)     // KB-0001 — the fix, buried
  // apply the change in the clunky admin console
  await page.click('#tab-admin'); await sleep(1400)
  await page.click('#ecode')
  await page.type('#ecode', 'PUB-4012', { delay: 130 })
  await sleep(1600)
  await page.mouse.move(400, 720, { steps: 14 })
  await page.click('#submitbtn'); await sleep(1200)                // → raise approval
  // wait in the approval queue
  await sleep(4200)
}

const outName = 'asset_manual_loop_raw.webm'
recordSession(MOCK, outdir, outName, grind, 1920, 1080)
  .then(p => console.log('recorded', p))
  .catch(e => { console.error(e); process.exit(1) })
