// Captions in any of 14 animated styles / 23 presets (vendored from remotion-captioneer, MIT; see src/captioneer/NOTICE.md).
// Same input as <Karaoke>: the words from public/reels/<id>/captions.words.json.
//   <StyledCaptions words={words} preset="tiktok" />
//   <StyledCaptions words={words} style="bounce" highlightColor={brand.colors.accent} />
// The box sits on the bottom edge of the Instagram safe zone (src/layout.ts), like <Karaoke>.
import React, { useMemo } from "react";
import { AnimatedCaptions } from "../captioneer/components/AnimatedCaptions";
import { applyPreset } from "../captioneer/presets";
import type { CaptionComponentProps, CaptionStyle } from "../captioneer/types";
import { wordsToCaptionData, type KitWord } from "../captioneer/adapter";
import { CAPTION_BOTTOM, HEIGHT, SAFE } from "../layout";

export type StyledCaptionsProps = {
  words: KitWord[];
  /** One of the 23 preset names (see src/captioneer/presets/index.ts), e.g. "tiktok", "cinematic-gold". */
  preset?: string;
  /** Or pick a style directly; overrides the preset's style. */
  style?: CaptionStyle;
  /** Max words per on-screen phrase (3-8). Default 6. */
  maxWords?: number;
  /** Dark outline around the glyphs so the (white) library text reads on light backgrounds too. Default true. */
  outline?: boolean;
  /** Words per line inside a phrase. Default 3. */
  wordsPerLine?: number;
} & Partial<Pick<CaptionComponentProps, "fontFamily" | "fontSize" | "fontColor" | "highlightColor" | "emphasisStyle" | "emphasisColor">>;

export const StyledCaptions: React.FC<StyledCaptionsProps> = ({ words, preset = "tiktok", style, maxWords = 6, wordsPerLine = 3, outline = true, ...over }) => {
  const captions = useMemo(() => wordsToCaptionData(words, { maxWords }), [words, maxWords]);
  const base = applyPreset(preset);
  const props: CaptionComponentProps = {
    ...base,
    ...(style ? { style, animation: undefined } : {}),
    ...Object.fromEntries(Object.entries(over).filter(([, v]) => v !== undefined)),
    captions,
    position: "bottom",
    wordsPerLine,
    useSmartWrap: true,
    maxWidth: 1080 - SAFE.left - SAFE.right,
  };
  // The library centres its text inside its box, so the box is the caption band: 240px tall, its bottom edge on the
  // bottom of the safe zone. Anchored with `top` (from the frame height) so it does not depend on the parent's size.
  const BAND = 240;
  return (
    <div style={{ position: "absolute", left: SAFE.left, width: 1080 - SAFE.left - SAFE.right, top: HEIGHT - CAPTION_BOTTOM - BAND, height: BAND, filter: outline ? "drop-shadow(0 0 3px rgba(10,12,18,.95)) drop-shadow(0 0 3px rgba(10,12,18,.95)) drop-shadow(0 3px 4px rgba(10,12,18,.6))" : undefined }}>
      <AnimatedCaptions {...props} />
    </div>
  );
};
