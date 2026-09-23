import { AbsoluteFill, Img, interpolate, useCurrentFrame } from "remotion";
import { runFile } from "../lib/timeline";
import type { EventProps } from "./types";

/** First 1–2 seconds: flash the most striking step with a punch-in zoom. */
export const Hook: React.FC<EventProps> = ({ timeline, event }) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, 10, 45], [1.3, 1, 1.05], { extrapolateRight: "clamp" });
  if (!event.asset) return null;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", backgroundColor: "#111" }}>
      <Img src={runFile(timeline, event.asset.full_image)} style={{ width: 1000, transform: `scale(${scale})` }} />
    </AbsoluteFill>
  );
};
