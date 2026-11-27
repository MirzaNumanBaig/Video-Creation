import React from "react";
import { Composition, Folder } from "remotion";
import { FPS, HEIGHT, WIDTH } from "./layout";
import { PlaceholderSheet } from "./dev/PlaceholderSheet";
import { REELS } from "./reels/registry";
import { CaptionGallery, GALLERY_W, STYLES, galleryHeight } from "./dev/CaptionGallery";
import { presets } from "./captioneer/presets";

export const Root: React.FC = () => (
  <>
    {REELS.map((r) => (
      <React.Fragment key={r.id}>
        <Composition id={r.id} component={r.Component} width={WIDTH} height={HEIGHT} fps={FPS} durationInFrames={r.durationInFrames} defaultProps={{}} />
        {r.variants?.length ? (
          <Folder name={`${r.id}-variants`}>
            {r.variants.map((v) => (
              <Composition
                key={v.suffix}
                id={`${r.id}-${v.suffix}`}
                component={r.Component}
                width={WIDTH}
                height={HEIGHT}
                fps={FPS}
                durationInFrames={r.durationInFrames}
                defaultProps={v.props}
              />
            ))}
          </Folder>
        ) : null}
      </React.Fragment>
    ))}
    <Folder name="Dev">
      <Composition id="PlaceholderSheet-Illustrated" component={PlaceholderSheet} width={2000} height={1600} fps={1} durationInFrames={1} defaultProps={{ look: "illustrated" as const }} />
      <Composition id="PlaceholderSheet-Pixel" component={PlaceholderSheet} width={2000} height={1600} fps={1} durationInFrames={1} defaultProps={{ look: "pixel" as const }} />
      <Composition id="CaptionGallery-Styles" component={CaptionGallery} width={GALLERY_W} height={galleryHeight(STYLES.length)} fps={30} durationInFrames={120} defaultProps={{ mode: "styles" as const }} />
      <Composition id="CaptionGallery-Presets" component={CaptionGallery} width={GALLERY_W} height={galleryHeight(Object.keys(presets).length)} fps={30} durationInFrames={120} defaultProps={{ mode: "presets" as const }} />
    </Folder>
  </>
);
