// Captures index.html frame by frame with headless Chromium (DevTools protocol, no npm packages).
// Usage: node render_frames.mjs [outDir=frames] [fps=30] [duration=9.6] [onlyTimes=comma list of seconds]
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.resolve(process.argv[2] || path.join(here, 'frames'));
const fps = Number(process.argv[3] || 30);
const dur = Number(process.argv[4] || 9.6);
const only = process.argv[5] ? process.argv[5].split(',').map(Number) : null;
const CHROME = process.env.CHROME || 'chromium';
const port = 9300 + Math.floor(Math.random() * 500);
const sleep = ms => new Promise(r => setTimeout(r, ms));

const userDir = fs.mkdtempSync(path.join(os.tmpdir(), 'hook-chrome-'));
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${port}`, '--no-first-run',
  '--no-default-browser-check', '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=1920,1080',
  '--disable-gpu', '--font-render-hinting=none', `--user-data-dir=${userDir}`, 'about:blank'], { stdio: 'ignore' });

async function getJSON(url) {
  for (let i = 0; i < 150; i++) { try { return await (await fetch(url)).json(); } catch { await sleep(100); } }
  throw new Error('Chromium DevTools did not start');
}

try {
  const page = (await getJSON(`http://127.0.0.1:${port}/json/list`)).find(x => x.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let id = 0; const pending = new Map();
  ws.onmessage = e => { const m = JSON.parse(e.data); const p = m.id && pending.get(m.id);
    if (p) { pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); } };
  const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
  const evaluate = async expr => { const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text); return r.result.value; };

  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'file://' + path.join(here, 'index.html') + '?t=0' });
  for (let i = 0; !(await evaluate('window.__ready === true').catch(() => false)); i++) { if (i > 200) throw new Error('page not ready'); await sleep(50); }

  fs.mkdirSync(outDir, { recursive: true });
  const times = only || Array.from({ length: Math.round(dur * fps) }, (_, i) => i / fps);
  for (let i = 0; i < times.length; i++) {
    const t = times[i];
    await evaluate(`renderAt(${t}); new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r(true))))`);
    const shot = await send('Page.captureScreenshot', { format: 'png', clip: { x: 0, y: 0, width: 1920, height: 1080, scale: 1 } });
    const name = only ? `t${t.toFixed(2)}.png` : `f${String(i).padStart(4, '0')}.png`;
    fs.writeFileSync(path.join(outDir, name), Buffer.from(shot.data, 'base64'));
    if (!only && i % 30 === 0) process.stdout.write(`frame ${i}/${times.length}\n`);
  }
  ws.close();
} finally {
  chrome.kill('SIGTERM');
  await sleep(300);
  fs.rmSync(userDir, { recursive: true, force: true });
}
