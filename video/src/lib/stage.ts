// Shared layout for showing models: one fixed "stage" so the model never jumps between steps.
import type { Picture, Timeline } from "./timeline";

export const STAGE = { centerX: 540, baseline: 1420, maxWidth: 940, maxHeight: 1080 };

/** One scale for every model in the video, so the model grows step by step instead of jumping. */
export const modelScale = (t: Timeline): number => {
    const pics: Picture[] = t.events.flatMap((e) =>
        e.asset ? [e.asset.model, e.asset.prev_model].filter((p): p is Picture => p !== null) : [],
    );
    if (pics.length === 0) return 1;
    const w = Math.max(...pics.map((p) => p.width));
    const h = Math.max(...pics.map((p) => p.height));
    return Math.min(STAGE.maxWidth / w, STAGE.maxHeight / h, 2.5);
};

/** Scale that fits a single picture on the stage (hook / reveal). */
export const fitScale = (p: Picture): number =>
    Math.min(STAGE.maxWidth / p.width, STAGE.maxHeight / p.height, 2.5);

/** Top-left of a picture standing on the stage baseline, horizontally centred. */
export const standOnStage = (p: Picture, scale: number): { left: number; top: number } => ({
    left: STAGE.centerX - (p.width * scale) / 2,
    top: STAGE.baseline - p.height * scale,
});

export const MODEL_SHADOW = "drop-shadow(0 18px 22px rgba(0, 40, 80, 0.22))";
