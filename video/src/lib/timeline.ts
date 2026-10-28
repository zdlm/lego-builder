// Mirror of pipeline/src/lego_builder/models.py (Timeline and friends).
// Keep in sync: if you change one, change the other and bump SCHEMA_VERSION.
import { staticFile } from "remotion";

export const SCHEMA_VERSION = "0.5.0";

export type BBox = { x: number; y: number; w: number; h: number };

/** RGBA image with a transparent background, relative to the run dir. */
export type Picture = { image: string; width: number; height: number };

export type StepAsset = {
  step_number: number;
  full_image: string; // full panel, fallback when no model cut-out
  model: Picture | null; // model after this step
  prev_model: Picture | null; // model before this step
  parts: Picture[]; // new parts cut from the callout
  landing_x: number; // where the parts land, as a fraction of model width
  landing_y: number; // ... and of model height
};

export type TimelineEvent = {
  kind: "hook" | "snap" | "reveal" | "cta";
  start_s: number;
  duration_s: number;
  step_number: number | null;
  asset: StepAsset | null;
  impact_s: number | null; // snap only: when the parts land (on a beat), video time
  sfx: string | null; // repo-relative, e.g. assets/sfx/click1.wav
  sfx_lead_s: number; // silence at the start of sfx; start it this much before impact_s
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
  music_start_s: number; // where in the track playback starts
  total_steps: number;
  final_image: string | null; // finished-model image for the reveal, relative to the run dir
  final_model: Picture | null; // finished model with a transparent background
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
  music_start_s: 0,
  total_steps: 0,
  final_image: null,
  final_model: null,
  events: [{ kind: "cta", start_s: 0, duration_s: 15, step_number: null, asset: null, impact_s: null, sfx: null, sfx_lead_s: 0, text: "Load a run: make preview RUN=<run_id>" }],
};
