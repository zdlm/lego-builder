import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import type { Timeline } from "../lib/timeline";

/** Step counter and progress bar shown during the snap section. */
export const Overlays: React.FC<{ timeline: Timeline }> = ({ timeline }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const current = [...timeline.events].reverse().find((e) => e.kind === "snap" && e.start_s <= t);
  const lastSnap = [...timeline.events].reverse().find((e) => e.kind === "snap");
  if (!current || !lastSnap || t > lastSnap.start_s + lastSnap.duration_s) return null;
  const progress = (current.step_number ?? 0) / Math.max(1, timeline.total_steps);
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", padding: 60 }}>
      <div style={{ fontSize: 56, fontWeight: 800, marginBottom: 20 }}>
        Step {current.step_number}/{timeline.total_steps}
      </div>
      <div style={{ height: 16, background: "#0002", borderRadius: 8 }}>
        <div style={{ width: `${progress * 100}%`, height: "100%", background: "#ffcf00", borderRadius: 8 }} />
      </div>
    </AbsoluteFill>
  );
};
