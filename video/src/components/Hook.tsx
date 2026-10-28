import { AbsoluteFill, Img, interpolate, useCurrentFrame } from "remotion";
import { fitScale, MODEL_SHADOW, standOnStage } from "../lib/stage";
import { runFile } from "../lib/timeline";
import type { EventProps } from "./types";

/** First 1–2 seconds: a punch-in on the finished model ("this is what we're building"). */
export const Hook: React.FC<EventProps> = ({ timeline, event }) => {
  const frame = useCurrentFrame();
  const pic = timeline.final_model ?? event.asset?.model ?? null;
  const scale = interpolate(frame, [0, 8, 40], [1.12, 1, 1.03], { extrapolateRight: "clamp" });
  const flash = interpolate(frame, [0, 6], [0.8, 0], { extrapolateRight: "clamp" });
  if (!pic) {
    if (!event.asset) return null;
    return (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <Img src={runFile(timeline, event.asset.full_image)} style={{ width: 960, transform: `scale(${scale})` }} />
      </AbsoluteFill>
    );
  }
  const s = fitScale(pic);
  const { left, top } = standOnStage(pic, s);
  return (
    <AbsoluteFill>
      <Img
        src={runFile(timeline, pic.image)}
        style={{
          position: "absolute",
          left,
          top,
          width: pic.width * s,
          height: pic.height * s,
          transformOrigin: "50% 100%",
          transform: `scale(${scale})`,
          filter: MODEL_SHADOW,
        }}
      />
      <AbsoluteFill style={{ backgroundColor: "white", opacity: flash }} />
    </AbsoluteFill>
  );
};
