import "./index.css";
import { Composition } from "remotion";
import { ProductPromoV2, config } from "./Composition";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ProductPromoV2"
        component={ProductPromoV2}
        durationInFrames={4500}
        fps={config.fps}
        width={config.width}
        height={config.height}
        defaultProps={{}}
      />
    </>
  );
};
