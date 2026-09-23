import { AbsoluteFill, Img, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { runFile } from "../lib/timeline";
import type { EventProps } from "./types";

/** Finished model reveal with set name and number. TODO: 3D spin when 3D renders exist. */
export const Reveal: React.FC<EventProps> = ({ timeline, event }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame, fps, config: { damping: 14 } });
  if (!event.asset) return null;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", gap: 40 }}>
      <Img src={runFile(timeline, event.asset.full_image)} style={{ width: 1000, transform: `scale(${0.8 + 0.2 * s})` }} />
      <div style={{ fontSize: 72, fontWeight: 800, opacity: s }}>{timeline.set_name}</div>
      {timeline.set_number ? <div style={{ fontSize: 44, opacity: s }}>#{timeline.set_number}</div> : null}
    </AbsoluteFill>
  );
};
