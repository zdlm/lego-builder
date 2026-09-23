# LEGO Builder — Hackathon Project Plan

Last updated: 2026-09-23

## 1. Goal

Automatically turn LEGO building instructions into **beat-synced short videos** made for social media (TikTok / Instagram Reels / YouTube Shorts / Xiaohongshu / Douyin), to use for marketing.

What viewers should feel: bricks snap into place one after another in time with the music, *click, click, click*, and then the finished model is revealed. It should be satisfying and a little addictive, so people want to buy the set, build it and share the video.

This is not a tutorial. It is a **showcase video** meant to make people want the set. Showing every step accurately doesn't matter. Rhythm and satisfaction come first.

## 2. What the finished video looks like

- Vertical 9:16, 1080×1920, in three lengths: 15s, 30s and 60s
- The first 1–2 seconds are the hook: a flash of the finished model, or the most striking step
- The middle uses selected build steps synced to the beat. On each beat a part snaps into place, with a click sound, a slight screen shake and a flash
- The pace starts slow and builds, ending in a rapid burst of snaps right before the finale (the satisfaction peak)
- The ending reveals the complete model with a spin or zoom, then shows the set name, set number and a call to action ("Ready to build it?")

## 3. Pipeline

```
Instruction PDF
  → ① Split pages and segment steps
  → ② AI understands each step (what was added, how big the visual change is)
  → ③ Pick the snap moments
  → ④ Generate build animation assets for each step
  → ⑤ Detect beats in the music and align steps to them
  → ⑥ Compose the video programmatically, with SFX and captions
  → Vertical MP4s (multiple lengths)
```

### ① Page splitting and step segmentation
- Render the PDF to high-resolution images with PyMuPDF
- A page often holds several steps. Use Claude's vision capability to detect each step's bounding box and step number, then crop each step into its own image
- Filter out cover pages, parts lists and ad pages

### ② Step understanding
Produce structured JSON for each step, for example:
```json
{ "step": 42, "new_parts": ["1x4 red plate ×2"], "visual_change": 0.8,
  "is_milestone": true, "note": "Roof closes; the overall shape appears for the first time" }
```
- Also diff each pair of consecutive step images with OpenCV to get a mask of the newly added region, which the animation step uses

### ③ Picking snap moments (core algorithm)
Give each step a "satisfaction score" that combines:
- How big the visual change is (diff area)
- Whether it's a milestone: the shape comes together, a large block of color appears, a mechanism or moving part is attached, or sub-assemblies join
- Pacing: fewer steps at the start, denser in the middle, accelerating toward the end

Select N steps based on video length and the number of beats in the music. Claude can do the final ranking and explain each pick, which makes manual tweaks easy.

### ④ Build animation (two tiers)
- **2D (MVP, required):** Use the instruction image as the base. Cut out the new parts using the diff mask and animate them dropping in from above, bouncing and flashing as they lock into place. This is simple to build, looks consistent, and keeps the official illustration style of the instructions.
- **3D (bonus):** If 3D model data is available (LDraw, a BrickLink Studio .io file, or LEGO internal CAD data), render real parts dropping and snapping together with Blender and an LDraw import add-on. This gives the best result.
- **AI video generation (experimental, not the main track):** Image-to-video tools such as Veo, Kling or Runway tend to get brick geometry wrong. Only consider them for atmospheric shots at the end.

### ⑤ Beat sync
- Pick a royalty-free, high-energy track (or AI-generated music)
- Detect beats and downbeats with librosa
- Align each selected step to a beat. In the climax, use one part per beat or per half-beat
- Layer a click sound effect on every snap. Rotate between 3–5 variants at random so it doesn't sound mechanical

### ⑥ Video composition
- Recommended: **Remotion** (write videos in React with frame-accurate timeline control; well suited to beat sync and motion graphics; can batch-export multiple versions)
- Alternatives: MoviePy or FFmpeg
- Overlays: a step counter ("Step 42/120"), a progress bar, a running part count, brand captions and the CTA

## 4. Tech stack

| Stage | Choice |
|---|---|
| PDF processing | Python + PyMuPDF |
| Visual understanding / step selection | Claude API (vision) |
| Image diffing | OpenCV |
| Beat detection | librosa |
| 3D rendering (bonus) | Blender + LDraw import add-on |
| Video composition | Remotion (Node/React) |
| Frontend (optional) | Next.js: upload PDF → choose length and music → preview/download |

## 5. Feature priorities

| Priority | Feature |
|---|---|
| Must | PDF → segmented step images |
| Must | Claude analysis, satisfaction scoring and step selection |
| Must | 2D part drop-in animation |
| Must | Beat alignment and click SFX |
| Must | One finished 30-second vertical video |
| Should | Automatic 15s / 60s exports |
| Should | Opening hook and ending reveal templates |
| Should | Simple web UI for manually adjusting the selected steps |
| Nice | Realistic 3D build rendering |
| Nice | Several visual style templates (minimal, retro, neon night) |
| Nice | Auto-generated social captions and hashtags |

## 6. Hackathon schedule (assuming 48 hours)

| Time | Goal |
|---|---|
| 0–4h | Pick one demo instruction set; set up the project skeleton; get PDF splitting and step segmentation working |
| 4–12h | Claude step understanding, diff masks, satisfaction scoring and step selection |
| 12–24h | Remotion template: part drop-in animation, beat alignment, SFX |
| 24–32h | First 30-second cut; team reviews it and tunes the pacing |
| 32–40h | Opening hook, ending reveal, multiple lengths; 3D or web UI if time allows |
| 40–48h | Polish, prepare the demo, record a backup video |

## 7. Suggested roles (3–4 people)

- A: PDF parsing, step segmentation, diffing
- B: Claude prompts and the step selection algorithm
- C: Remotion animation, beat sync, SFX
- D (optional): 3D rendering, web UI, demo and copywriting

## 8. Risks and mitigations

- **Inaccurate step segmentation:** Demo with 1–2 instruction sets that have clean layouts, and fix bounding boxes by hand if needed
- **Noisy diff masks** (camera angle and scale can change between pages): Align images first with feature matching. If that doesn't work, fall back to a simpler animation where the whole new step image pops in
- **Music licensing:** Use a royalty-free library or AI-generated music
- **Brand and asset usage:** Before publishing, confirm that using the instruction illustrations and trademarks follows brand guidelines
- **Live demo failure:** Pre-render the finished video as a backup

## 9. Demo Day script

1. Open with the finished 15-second video to grab the judges
2. Show how many pages and steps the original instruction PDF has
3. Upload it live and show the snap steps the AI picked, with its reasons
4. Generate with one click and play the result
5. Pitch the business value: every new set launch gets social media assets automatically, with no editing cost

## 10. Open questions

- Which LEGO set to demo with (ideally a mid-size set with a clear "it comes together" moment, such as a sports car or a building)
- Whether 3D model data is available for that set
- The actual hackathon length and team size
- Which platforms come first (this decides video length and caption style)
