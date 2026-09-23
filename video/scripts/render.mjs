// Render a run: RUN_ID=<id> LEN=30 npm run render  → out/<id>_<LEN>s.mp4
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";

const runId = process.env.RUN_ID;
const len = process.env.LEN ?? "30";
if (!runId) throw new Error("Set RUN_ID");
execFileSync("node", ["scripts/link-run.mjs"], { stdio: "inherit" });
const props = `public/runs/${runId}/06_timeline.json`;
if (!existsSync(props)) throw new Error(`${props} not found — run the pipeline first`);
execFileSync(
  "npx",
  ["remotion", "render", "src/index.ts", "BuildReel", `out/${runId}_${len}s.mp4`, `--props=${props}`],
  { stdio: "inherit" },
);
