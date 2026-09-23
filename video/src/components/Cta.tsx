import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { EventProps } from "./types";

/** Closing call to action. */
export const Cta: React.FC<EventProps> = ({ event }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame, fps });
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", backgroundColor: "#d01012" }}>
      <div style={{ color: "white", fontSize: 96, fontWeight: 900, transform: `scale(${s})`, textAlign: "center", padding: 60 }}>
        {event.text}
      </div>
    </AbsoluteFill>
  );
};
