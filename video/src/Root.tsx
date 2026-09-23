import { Composition } from "remotion";
import { BuildReel } from "./compositions/BuildReel";
import { sampleTimeline, type Timeline } from "./lib/timeline";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="BuildReel"
    component={BuildReel}
    defaultProps={sampleTimeline}
    fps={30}
    width={1080}
    height={1920}
    durationInFrames={30 * 30}
    calculateMetadata={({ props }: { props: Timeline }) => ({
      fps: props.fps,
      width: props.width,
      height: props.height,
      durationInFrames: Math.round(props.length_s * props.fps),
    })}
  />
);
