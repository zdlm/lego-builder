# Glossary

| Term | Meaning |
|---|---|
| Step | One numbered build panel in the instruction booklet. Identified by the number printed on the page, not by list position. |
| Run | One execution of the pipeline on one PDF + music. Lives in `data/runs/<run_id>/`. |
| Stage | One numbered pipeline module (`s01_extract` … `s06_timeline`). Reads and writes files in the run directory. |
| Contract | A JSON file shape defined in `models.py` and passed between stages or to Remotion. |
| Timeline | `06_timeline.json`: the ordered list of events the video renders. The only handoff to `video/`. |
| Event | One entry in the timeline: `hook`, `snap`, `reveal` or `cta`. |
| Snap | The moment new parts lock into place, landing exactly on a beat, with click SFX, shake and flash. |
| Hook | The first 1–2 seconds: the most striking image, shown to stop the scroll. |
| Reveal | The finale: the finished model plus set name and number. |
| CTA | Call-to-action card at the very end. |
| Milestone | A step where the model visibly takes shape (new colour block, sub-assembly joined, moving part added). Scored higher. |
| Visual change | 0–1 estimate of how much a step changes the picture. |
| Satisfaction score | Combined score used by `s03_select` to choose steps (visual change, milestone, pacing). |
| Role | Why a selected step is in the video: `hook`, `build`, `climax` or `reveal`. |
| Diff mask | OpenCV mask of the region that is new in a step compared with the previous one. |
| Aligned image | A step image warped onto the previous step's coordinate frame (ORB + homography) so the diff is clean. |
| Cutout | RGBA crop of the newly added parts, used for the 2D drop-in animation. |
| Beat / downbeat | Beats detected by librosa; downbeats are the first beat of each bar (currently approximated as every 4th beat). |
| Length | Target video length in seconds: 15, 30 or 60. |
