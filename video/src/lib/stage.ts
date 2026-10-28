// Shared layout for showing models: one fixed "stage" so the model never jumps between steps.
import type { Picture, Timeline, TimelineEvent } from "./timeline";

export const STAGE = { centerX: 540, baseline: 1420, maxWidth: 940, maxHeight: 1080 };
export const FONT = '"Helvetica Neue", Helvetica, Arial, sans-serif';

// Instruction drawings are rasterised at ~200 dpi; zooming further gets visibly soft.
const MAX_ZOOM = 2.6;

/** Scale that fits a single picture on the stage. */
export const fitScale = (p: Picture): number =>
    Math.min(STAGE.maxWidth / p.width, STAGE.maxHeight / p.height, MAX_ZOOM);

/** Per snap: the largest scale at which every model so far fits, so the camera only pulls back. */
const cameraTargets = (t: Timeline): Map<TimelineEvent, number> => {
    const out = new Map<TimelineEvent, number>();
    let s = MAX_ZOOM;
    for (const e of t.events) {
        if (e.kind !== "snap" || !e.asset) continue;
        for (const p of [e.asset.prev_model, e.asset.model]) {
            if (p) s = Math.min(s, fitScale(p) * 0.85);
        }
        out.set(e, s);
    }
    return out;
};

/** Camera scale during a snap: eases from the previous snap's framing to this one (progress 0–1). */
export const cameraScale = (t: Timeline, event: TimelineEvent, progress: number): number => {
    const targets = cameraTargets(t);
    const snaps = [...targets.keys()];
    const i = snaps.indexOf(event);
    const to = targets.get(event) ?? MAX_ZOOM;
    const prev = i > 0 ? snaps[i - 1] : undefined;
    const from = prev ? (targets.get(prev) ?? to) : to;
    return from + (to - from) * progress;
};

/** Top-left of a picture standing on the stage baseline, horizontally centred. */
export const standOnStage = (p: Picture, scale: number): { left: number; top: number } => ({
    left: STAGE.centerX - (p.width * scale) / 2,
    top: STAGE.baseline - p.height * scale,
});

export const MODEL_SHADOW = "drop-shadow(0 18px 22px rgba(0, 40, 80, 0.22))";
