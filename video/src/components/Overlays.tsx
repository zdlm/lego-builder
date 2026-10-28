import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { Timeline } from "../lib/timeline";

/** Step counter and progress bar shown during the snap section; fades in with the first click. */
export const Overlays: React.FC<{ timeline: Timeline }> = ({ timeline }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const snaps = timeline.events.filter((e) => e.kind === "snap");
  const landed = [...snaps].reverse().find((e) => (e.impact_s ?? e.start_s) <= t);
  const lastSnap = snaps[snaps.length - 1];
  const firstSnap = snaps[0];
  if (!landed || !lastSnap || !firstSnap || t > lastSnap.start_s + lastSnap.duration_s) return null;
  const firstImpact = firstSnap.impact_s ?? firstSnap.start_s;
  const opacity = interpolate(t, [firstImpact, firstImpact + 0.3], [0, 1], { extrapolateRight: "clamp" });
  const progress = (landed.step_number ?? 0) / Math.max(1, timeline.total_steps);
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", padding: "0 80px 140px", opacity }}>
      <div
        style={{
          fontSize: 54,
          fontWeight: 800,
          letterSpacing: 1,
          marginBottom: 22,
          padding: "10px 34px",
          borderRadius: 40,
          background: "rgba(255, 255, 255, 0.85)",
          color: "#1b2a3a",
          fontVariantNumeric: "tabular-nums",
        }}
      >
        STEP {landed.step_number} / {timeline.total_steps}
      </div>
      <div style={{ width: "100%", height: 18, background: "rgba(0, 40, 80, 0.15)", borderRadius: 9 }}>
        <div style={{ width: `${progress * 100}%`, height: "100%", background: "#ffcf00", borderRadius: 9 }} />
      </div>
    </AbsoluteFill>
  );
};
