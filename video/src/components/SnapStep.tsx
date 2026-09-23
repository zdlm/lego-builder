import { AbsoluteFill, Audio, Img, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { assetFile, runFile } from "../lib/timeline";
import type { EventProps } from "./types";

/**
 * One beat: the new parts drop from above onto the previous step, bounce, and lock in with a flash,
 * a small screen shake and a click sound. Falls back to a pop-in of the full step image when there
 * is no cutout.
 */
export const SnapStep: React.FC<EventProps> = ({ timeline, event }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const a = event.asset;
  if (!a) return null;

  const drop = spring({ frame, fps, config: { damping: 11, stiffness: 180, mass: 0.6 } });
  const landed = frame >= 4;
  const shake = landed ? interpolate(frame, [4, 6, 8, 10], [0, 8, -5, 0], { extrapolateRight: "clamp" }) : 0;
  const flash = interpolate(frame, [4, 6, 12], [0, 0.6, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ transform: `translateY(${shake}px)`, justifyContent: "center", alignItems: "center" }}>
      {a.cutout && a.cutout_bbox ? (
        <div style={{ position: "relative" }}>
          <Img src={runFile(timeline, a.base_image)} style={{ width: 960 }} />
          <Img
            src={runFile(timeline, a.cutout)}
            style={{ position: "absolute", left: 0, top: 0, transform: `translateY(${(1 - drop) * -600}px)` }}
          />
          {/* TODO: scale cutout position from step-image pixels to the displayed 960px width */}
        </div>
      ) : (
        <Img src={runFile(timeline, a.full_image)} style={{ width: 960, transform: `scale(${0.9 + 0.1 * drop})` }} />
      )}
      <AbsoluteFill style={{ backgroundColor: "white", opacity: flash }} />
      {event.sfx ? <Audio src={assetFile(event.sfx)} /> : null}
    </AbsoluteFill>
  );
};
