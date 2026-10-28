import { AbsoluteFill, Audio, Sequence, useVideoConfig } from "remotion";
import { Cta } from "../components/Cta";
import { Hook } from "../components/Hook";
import { Overlays } from "../components/Overlays";
import { Reveal } from "../components/Reveal";
import { SnapStep } from "../components/SnapStep";
import { assetFile, type Timeline, type TimelineEvent } from "../lib/timeline";

const renderEvent = (t: Timeline, e: TimelineEvent) => {
  switch (e.kind) {
    case "hook":
      return <Hook timeline={t} event={e} />;
    case "snap":
      return <SnapStep timeline={t} event={e} />;
    case "reveal":
      return <Reveal timeline={t} event={e} />;
    case "cta":
      return <Cta timeline={t} event={e} />;
  }
};

/** Top-level video: plays each timeline event as a Sequence over the music track. */
export const BuildReel: React.FC<Timeline> = (t) => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ background: "radial-gradient(circle at 50% 45%, #ffffff 0%, #e3f3ff 55%, #bfe2fa 100%)" }}>
      {t.music ? <Audio src={assetFile(t.music)} trimBefore={Math.round(t.music_start_s * fps)} /> : null}
      {t.events.map((e, i) => (
        <Sequence
          key={i}
          from={Math.round(e.start_s * fps)}
          durationInFrames={Math.max(1, Math.round(e.duration_s * fps))}
        >
          {renderEvent(t, e)}
        </Sequence>
      ))}
      <Overlays timeline={t} />
    </AbsoluteFill>
  );
};
