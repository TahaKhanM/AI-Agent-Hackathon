// Precedent video pipeline — Playwright capture helper (screenshots + screen-recording).
// [Prompts/08]  SOURCE is committed here; node_modules + browsers + all output live in the
// gitignored precedent-video-drop/ tree. Run with:
//   NODE_PATH=precedent-video-drop/pipeline-node/node_modules \
//   PLAYWRIGHT_BROWSERS_PATH=precedent-video-drop/pipeline-node/.pw-browsers \
//   node Prep/video/pipeline/capture.mjs <mode> ...
//
// Modes:
//   screenshot <src> <out.png> [w] [h] [scale]      full-viewport screenshot of a file/URL
//   record-url <url> <outdir> <ms> [w] [h]          open a URL, hold ms, save the webm to outdir
//
// The driving harnesses (V2 time-lapse, V3 console takes) import { recordSession } below.
// Playwright lives in the gitignored install; resolve it via PW_BASE (default: the pipeline-node dir).
import { createRequire } from 'node:module'
import path from 'node:path'
import fs from 'node:fs'
import { fileURLToPath } from 'node:url'

const _here = path.dirname(fileURLToPath(import.meta.url))
const PW_BASE = process.env.PW_BASE
  || path.resolve(_here, '../../../precedent-video-drop/pipeline-node')
const require = createRequire(path.join(PW_BASE, 'package.json'))
const { chromium } = require('playwright')

const VIEW = { width: 1920, height: 1080 }

function toURL(src) {
  if (/^https?:\/\//.test(src)) return src
  return 'file://' + path.resolve(src)
}

export async function screenshot(src, out, w = VIEW.width, h = VIEW.height, scale = 1) {
  const browser = await chromium.launch()
  const ctx = await browser.newContext({ viewport: { width: +w, height: +h }, deviceScaleFactor: +scale })
  const page = await ctx.newPage()
  await page.goto(toURL(src), { waitUntil: 'networkidle' })
  await page.waitForTimeout(250) // let fonts/render settle
  fs.mkdirSync(path.dirname(out), { recursive: true })
  await page.screenshot({ path: out })
  await browser.close()
  return out
}

// Record a driven session. `drive(page)` does the interactions; the webm is written under outdir
// and renamed to outName. Returns the final webm path.
export async function recordSession(startURL, outdir, outName, drive, w = VIEW.width, h = VIEW.height) {
  fs.mkdirSync(outdir, { recursive: true })
  const browser = await chromium.launch()
  const ctx = await browser.newContext({
    viewport: { width: +w, height: +h },
    deviceScaleFactor: 1,
    recordVideo: { dir: outdir, size: { width: +w, height: +h } },
  })
  const page = await ctx.newPage()
  if (startURL) await page.goto(toURL(startURL), { waitUntil: 'domcontentloaded' })
  await drive(page)
  const video = page.video()
  await ctx.close() // finalizes the webm
  await browser.close()
  const tmp = await video.path()
  const finalPath = path.join(outdir, outName)
  fs.renameSync(tmp, finalPath)
  return finalPath
}

// ---- CLI ----
const [, , mode, ...rest] = process.argv
if (mode === 'screenshot') {
  const [src, out, w, h, scale] = rest
  screenshot(src, out, w, h, scale).then(p => { console.log('screenshot ->', p) })
    .catch(e => { console.error(e); process.exit(1) })
} else if (mode === 'record-url') {
  const [url, outdir, ms, w, h] = rest
  recordSession(url, outdir, 'rec.webm', async (page) => { await page.waitForTimeout(+ms || 2000) }, w, h)
    .then(p => { console.log('recorded ->', p) })
    .catch(e => { console.error(e); process.exit(1) })
} else if (mode) {
  console.error('unknown mode:', mode); process.exit(2)
}
