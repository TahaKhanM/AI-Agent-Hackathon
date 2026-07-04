// Render a caption as a full-frame 1920x1080 TRANSPARENT PNG (brand lower-third), for ffmpeg
// `overlay` compositing — this build of ffmpeg has no libass/drawtext, so captions are burned as
// PNG overlays (crisper + on-brand anyway). [Prompts/08]
//   node render_caption.mjs <out.png> "<caption text>"
import { createRequire } from 'node:module'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
const _here = path.dirname(fileURLToPath(import.meta.url))
const PW_BASE = process.env.PW_BASE || path.resolve(_here, '../../../precedent-video-drop/pipeline-node')
const require = createRequire(path.join(PW_BASE, 'package.json'))
const { chromium } = require('playwright')

const [, , out, text] = process.argv
const safe = (text || '').replace(/</g, '&lt;').replace(/>/g, '&gt;')

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{width:1920px;height:1080px;background:transparent;overflow:hidden}
  .wrap{position:absolute;left:0;right:0;bottom:64px;display:flex;justify-content:center}
  .cap{max-width:1640px;background:rgba(9,12,18,.82);border:1px solid rgba(110,143,214,.42);
    border-radius:14px;padding:22px 40px;color:#F1F1E2;font-family:"Helvetica Neue",Arial,sans-serif;
    font-size:40px;line-height:1.34;text-align:center;font-weight:500;
    text-shadow:0 2px 8px rgba(0,0,0,.6);box-shadow:0 8px 40px rgba(0,0,0,.5)}
  .cap .accent{color:#9fb6e8}
</style></head><body>
  <div class="wrap"><div class="cap">${safe}</div></div>
</body></html>`

const browser = await chromium.launch()
const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 })
const page = await ctx.newPage()
await page.setContent(html, { waitUntil: 'networkidle' })
await page.waitForTimeout(120)
await page.screenshot({ path: out, omitBackground: true })   // transparent PNG
await browser.close()
console.log('caption ->', out)
