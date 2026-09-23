// Mirror of pipeline/src/lego_builder/models.py (Timeline and friends).
// Keep in sync: if you change one, change the other and bump SCHEMA_VERSION.
import { staticFile } from "remotion";

export const SCHEMA_VERSION = "0.2.0";

export type BBox = { x: number; y: number; w: number; h: number };

export type StepAsset = {
  step_number: number;
  base_image: string; // relative to the run dir
  base_width: number; // native pixel size of base_image, for scaling cutout_bbox
  base_height: number;
  full_image: string;
  cutout: string | null;
  cutout_bbox: BBox | null; // in base_image's pixel coordinate frame
};

export type TimelineEvent = {
  kind: "hook" | "snap" | "reveal" | "cta";
  start_s: number;
  duration_s: number;
  step_number: number | null;
  asset: StepAsset | null;
  sfx: string | null; // repo-relative, e.g. assets/sfx/click1.wav
  text: string | null;
};

export type Timeline = {
  schema_version: string;
  run_id: string;
  set_name: string;
  set_number: string | null;
  fps: number;
  width: number;
  height: number;
  length_s: 15 | 30 | 60;
  music: string; // repo-relative, must live under assets/
  total_steps: number;
  events: TimelineEvent[];
};

/** URL for a file inside the run directory. */
export const runFile = (t: Timeline, rel: string): string => staticFile(`runs/${t.run_id}/${rel}`);

/** URL for a repo-relative asset path (music / sfx). */
export const assetFile = (repoRelative: string): string => staticFile(repoRelative);

/** Placeholder used by Remotion Studio when no run is loaded. */
export const sampleTimeline: Timeline = {
  schema_version: SCHEMA_VERSION,
  run_id: "sample",
  set_name: "Sample Set",
  set_number: "00000",
  fps: 30,
  width: 1080,
  height: 1920,
  length_s: 15,
  music: "",
  total_steps: 0,
  events: [{ kind: "cta", start_s: 0, duration_s: 15, step_number: null, asset: null, sfx: null, text: "Load a run: make preview RUN=<run_id>" }],
};
