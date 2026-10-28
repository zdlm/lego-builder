import { AbsoluteFill, Audio, Easing, Img, interpolate, Sequence, useCurrentFrame, useVideoConfig } from "remotion";
import { cameraScale, MODEL_SHADOW, standOnStage } from "../lib/stage";
import { assetFile, runFile, type Picture, type Timeline } from "../lib/timeline";
import type { EventProps } from "./types";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const Model: React.FC<{ timeline: Timeline; pic: Picture; scale: number; squash?: number }> = ({
  timeline,
  pic,
  scale,
  squash = 1,
}) => {
  const { left, top } = standOnStage(pic, scale);
  return (
    <Img
      src={runFile(timeline, pic.image)}
      style={{
        position: "absolute",
        left,
        top,
        width: pic.width * scale,
        height: pic.height * scale,
        transformOrigin: "50% 100%",
        transform: `scale(${2 - squash}, ${squash})`,
        filter: MODEL_SHADOW,
      }}
    />
  );
};

/**
 * One step: the new parts fall onto the previous model and, exactly on the beat (`impact_s`),
 * the picture cuts to the new model with a squash, a ring burst, a small shake and a click.
 */
export const SnapStep: React.FC<EventProps> = ({ timeline, event }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const a = event.asset;
  if (!a) return null;

  const impact = Math.max(0, Math.round(((event.impact_s ?? event.start_s) - event.start_s) * fps));
  const landed = frame >= impact;
  const k = frame - impact;
  // Start the click early by its leading silence so the audible "click" is on the beat.
  const sfxFrom = impact - Math.round(event.sfx_lead_s * fps);
  // The same click every step: vary the level a little so it doesn't sound mechanical.
  const sfxVolume = 0.8 + 0.1 * ((event.step_number ?? 0) % 3);
  const sfx = event.sfx ? (
    <Sequence from={Math.max(0, sfxFrom)}>
      <Audio src={assetFile(event.sfx)} trimBefore={Math.max(0, -sfxFrom)} volume={sfxVolume} />
    </Sequence>
  ) : null;

  if (!a.model) {
    const pop = landed ? interpolate(k, [0, 3, 8], [0.9, 1.03, 1], clamp) : 0;
    return (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        {landed ? <Img src={runFile(timeline, a.full_image)} style={{ width: 960, transform: `scale(${pop})` }} /> : null}
        {sfx}
      </AbsoluteFill>
    );
  }

  const length = Math.max(1, Math.round(event.duration_s * fps));
  const camera = interpolate(frame, [0, length], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const scale = cameraScale(timeline, event, camera);
  const { left, top } = standOnStage(a.model, scale);
  const target = {
    x: left + a.landing_x * a.model.width * scale,
    y: top + a.landing_y * a.model.height * scale,
  };

  const squash = landed ? interpolate(k, [0, 2, 5, 9], [0.93, 1.03, 0.99, 1], clamp) : 1;
  const shake = landed ? interpolate(k, [0, 2, 4, 6], [0, 7, -4, 0], clamp) : 0;
  const ring = interpolate(k, [0, 10], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const flash = interpolate(k, [0, 1, 6], [0, 0.25, 0], clamp);
  const fall = interpolate(frame, [0, Math.max(impact, 1)], [0, 1], { ...clamp, easing: Easing.in(Easing.quad) });

  return (
    <AbsoluteFill style={{ transform: `translateY(${shake}px)` }}>
      {landed ? (
        <Model timeline={timeline} pic={a.model} scale={scale} squash={squash} />
      ) : a.prev_model ? (
        <Model timeline={timeline} pic={a.prev_model} scale={scale} />
      ) : null}

      {!landed
        ? a.parts.map((p, i) => {
          const spread = (i - (a.parts.length - 1) / 2) * 140;
          const startX = target.x + spread * 1.6;
          const startY = target.y - 700 - i * 40;
          const x = startX + (target.x + spread * 0.3 - startX) * fall;
          const y = startY + (target.y - startY) * fall;
          const spin = (1 - fall) * (i % 2 === 0 ? -25 : 25);
          return (
            <Img
              key={p.image}
              src={runFile(timeline, p.image)}
              style={{
                position: "absolute",
                left: x - (p.width * scale) / 2,
                top: y - (p.height * scale) / 2,
                width: p.width * scale,
                height: p.height * scale,
                opacity: Math.min(1, fall * 4),
                transform: `rotate(${spin}deg)`,
                filter: MODEL_SHADOW,
              }}
            />
          );
        })
        : null}

      {landed && ring < 1 ? (
        <div
          style={{
            position: "absolute",
            left: target.x - 160 * ring,
            top: target.y - 160 * ring,
            width: 320 * ring,
            height: 320 * ring,
            borderRadius: "50%",
            border: `${Math.max(1, 14 * (1 - ring))}px solid rgba(255, 255, 255, ${1 - ring})`,
          }}
        />
      ) : null}
      <AbsoluteFill style={{ backgroundColor: "white", opacity: flash }} />
      {sfx}
    </AbsoluteFill>
  );
};
