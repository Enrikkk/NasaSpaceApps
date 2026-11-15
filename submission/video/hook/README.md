# Opening hook (0.0–9.6 s) of the Agrockham promo video

This is a motion-graphics animation, 9.6 s long, at 1920×1080 and 30 fps, with no audio. It follows version A of the hook, "Fruit, field, ground, data".

| File | What |
|---|---|
| `index.html` | The animation. Open `index.html?t=4.0` to see the exact frame at any time. It is deterministic: fixed seeds, no timers, no `Math.random`, no `Date`. |
| `render_frames.mjs` | Drives headless Chromium through the DevTools protocol. It calls `renderAt(t)` for each frame and saves one PNG per frame. It needs no npm packages. |
| `render.sh` | Renders the frames, then encodes and checks `hook.mp4` |
| `hook.mp4` | Output: 288 frames, 9.6 s, H.264 yuv420p, CRF 18, no audio track |
| `sound_cues.txt` | Voiceover and sound-effect timings, for whoever adds the audio |

## Run

```bash
./render.sh
```

It takes about 4–5 minutes. It writes `frames/f0000.png … f0287.png` (git-ignored) and `hook.mp4`, then prints the ffprobe check (`duration=9.600000`, `nb_frames=288`). If your browser is not `chromium`, set `CHROME=/path/to/chrome`.

To render a few frames only:

```bash
node render_frames.mjs /tmp/qc 30 9.6 0.5,4.0,8.5
```

## Shots

| Time | Shot | Corner label |
|---|---|---|
| 0.0–1.6 | A tomato splits under a harsh sun, with heat haze, lens flare and a slow push-in | ILLUSTRATIVE |
| 1.6–3.2 | Camera at water level over a flooded lettuce field: rain, splash rings, a floating tomato, camera shake | ILLUSTRATIVE |
| 3.2–4.8 | Top-down view of cracked earth crusted with salt and a wilted lettuce, faded colours, slow push-in | ILLUSTRATIVE |
| 4.8–7.6 | The field freezes and three rain columns rise: ERA5 · NASA POWER · IMERG, with a bracket labelled ~40% | ILLUSTRATIVE DATA |
| 7.6–9.6 | Fast rise to a schematic aerial view of the Campo de Cartagena and the Mar Menor, with one parcel highlighted. Caption: Ley 3/2020 | PLACEHOLDER MAP |

Each line has a subtitle at the bottom and a matching headline in capitals at the top left. The first frame is shot 1, never black, and there is no logo or title card.

**Rain column heights.** The column heights follow the ratio of the three sources' 2024 annual rain on the demo parcel. The figures are in `research/predictive-model-research.md`: ERA5 is about 70% of IMERG, and IMERG is about 40% above ERA5. No mm values appear on screen. The only number shown is "~40%".

**The map is not a real map.** It is a hand-drawn diagram: the coast, lagoon, parcels, towns and roads are approximate shapes, not survey data. Before the final cut, replace it with a screen recording of the real Agrockham globe, framed the same way, so the cut into the demo matches.

## Assets, licences and tools

- **Visuals:** all of them are drawn in code in `index.html` (SVG/CSS, made by the team). There are no stock images, no photos, no NASA or agency logos, and no third-party icons.
- **Fonts:** Inter (SIL Open Font License 1.1), with DejaVu Sans as a fallback (Bitstream Vera / DejaVu licence, free). Both are system fonts and neither is embedded in the repo.
- **Tools:**
  - Chromium headless (BSD-style licence)
  - Node.js 22+ (MIT)
  - FFmpeg with libx264 (LGPL/GPL)
- **Data names shown:** ERA5 (Copernicus/ECMWF), NASA POWER and GPM IMERG (NASA). They are already cited in `submission/data-citations.md`, and appear here as plain text only.
- **SI/AI disclosure:** the code for this animation was written with Claude (Anthropic) under the team's direction. The concept and the script came from the team's creative brief. This must be listed in `submission/ai-use.md`.
- **Audio:** none yet. See `sound_cues.txt`. Any sound added later must be original or openly licensed (CC0, or CC-BY with attribution) and listed in `submission/`.
