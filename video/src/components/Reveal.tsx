import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { fitScale, MODEL_SHADOW, STAGE, standOnStage } from "../lib/stage";
import { runFile } from "../lib/timeline";
import type { EventProps } from "./types";

/** Finished model with a glow burst, then set name and number. TODO: 3D spin when 3D renders exist. */
export const Reveal: React.FC<EventProps> = ({ timeline, event }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame, fps, config: { damping: 12 } });
  const text = spring({ frame: frame - 8, fps, config: { damping: 14 } });
  const glow = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });

  const pic = timeline.final_model ?? event.asset?.model ?? null;
  const image = pic?.image ?? timeline.final_image ?? event.asset?.full_image;
  if (!image) return null;
  const scale = pic ? fitScale(pic) * 0.92 : 1;
  const pos = pic ? standOnStage(pic, scale) : { left: 40, top: 300 };
  const width = pic ? pic.width * scale : 1000;
  const height = pic ? pic.height * scale : undefined;

  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: STAGE.centerX - 700,
          top: STAGE.baseline - 1100,
          width: 1400,
          height: 1400,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(255,240,150,0.9) 0%, rgba(255,240,150,0) 65%)",
          opacity: glow,
          transform: `scale(${0.6 + 0.4 * glow})`,
        }}
      />
      <Img
        src={runFile(timeline, image)}
        style={{
          position: "absolute",
          left: pos.left,
          top: pos.top,
          width,
          height,
          transformOrigin: "50% 100%",
          transform: `scale(${0.85 + 0.15 * s})`,
          filter: pic ? MODEL_SHADOW : undefined,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: STAGE.baseline + 60,
          width: "100%",
          textAlign: "center",
          opacity: text,
          transform: `translateY(${(1 - text) * 40}px)`,
        }}
      >
        <div style={{ fontSize: 76, fontWeight: 900 }}>{timeline.set_name}</div>
        {timeline.set_number ? <div style={{ fontSize: 46, marginTop: 10 }}>#{timeline.set_number}</div> : null}
      </div>
    </AbsoluteFill>
  );
};
