import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { MODEL_SHADOW } from "../lib/stage";
import { runFile } from "../lib/timeline";
import type { EventProps } from "./types";

/** Closing card: the finished model, the call to action, and the set name and number. */
export const Cta: React.FC<EventProps> = ({ timeline, event }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 12 } });
  const text = spring({ frame: frame - 4, fps, config: { damping: 14 } });
  const bg = interpolate(frame, [0, 6], [0, 1], { extrapolateRight: "clamp" });
  const pic = timeline.final_model;
  const width = pic ? Math.min(620, pic.width * 1.4) : 0;
  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        gap: 50,
        background: `rgba(208, 16, 18, ${bg})`,
        color: "white",
        textAlign: "center",
      }}
    >
      {pic ? (
        <Img
          src={runFile(timeline, pic.image)}
          style={{ width, transform: `scale(${0.7 + 0.3 * pop})`, filter: MODEL_SHADOW }}
        />
      ) : null}
      <div style={{ fontSize: 104, fontWeight: 900, lineHeight: 1.05, padding: "0 70px", transform: `scale(${text})` }}>
        {event.text}
      </div>
      <div
        style={{
          fontSize: 44,
          fontWeight: 700,
          padding: "14px 40px",
          borderRadius: 50,
          background: "#ffcf00",
          color: "#1b1b1b",
          opacity: text,
        }}
      >
        {timeline.set_name}
        {timeline.set_number ? ` · ${timeline.set_number}` : ""}
      </div>
    </AbsoluteFill>
  );
};
