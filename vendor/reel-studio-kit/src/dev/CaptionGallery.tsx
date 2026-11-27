// Dev sheet: every caption style (or preset) on the same sentence, so you can pick one by eye.
//   npx remotion still CaptionGallery-Styles   out/styles.png --frame=36
//   npx remotion still CaptionGallery-Presets  out/presets.png --frame=36
import React from "react";
import { AbsoluteFill } from "remotion";
import { StyledCaptions } from "../components/StyledCaptions";
import { presets } from "../captioneer/presets";
import type { CaptionStyle } from "../captioneer/types";
import type { KitWord } from "../captioneer/adapter";
import { FONTS } from "../fonts";

export const STYLES: CaptionStyle[] = ["word-highlight", "karaoke", "typewriter", "bounce", "wave", "glow", "typewriter-erase", "pill", "flicker", "highlighter", "blur", "rainbow", "scale", "spotlight"];

const SAMPLE = "Your reel dies in three seconds. Here is how to save it.".split(" ");
const WORDS: KitWord[] = SAMPLE.map((w, i) => ({ word: w, start: 0.2 + i * 0.3, end: 0.2 + i * 0.3 + 0.27 }));

const COLS = 6;
const CELL_W = 270; // 1/4 of a 1080x1920 reel
const CELL_H = 480;
const LABEL = 34;
export const galleryHeight = (n: number) => Math.ceil(n / COLS) * (CELL_H + LABEL);
export const GALLERY_W = COLS * CELL_W;

export const CaptionGallery: React.FC<{ mode: "styles" | "presets" }> = ({ mode }) => {
  const items = mode === "styles" ? STYLES : Object.keys(presets);
  return (
    <AbsoluteFill style={{ background: "#0b0c10", fontFamily: FONTS.Inter }}>
      {items.map((name, i) => (
        <div key={name} style={{ position: "absolute", left: (i % COLS) * CELL_W, top: Math.floor(i / COLS) * (CELL_H + LABEL), width: CELL_W, height: CELL_H + LABEL }}>
          <div style={{ width: CELL_W, height: CELL_H, overflow: "hidden", position: "relative", background: "linear-gradient(160deg,#2b3446,#12151c)" }}>
            <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 1920, transform: "scale(0.25)", transformOrigin: "top left" }}>
              <StyledCaptions words={WORDS} {...(mode === "styles" ? { style: name as CaptionStyle } : { preset: name })} />
            </div>
          </div>
          <div style={{ height: LABEL, color: "#cbd5e1", fontSize: 15, lineHeight: `${LABEL}px`, textAlign: "center" }}>{name}</div>
        </div>
      ))}
    </AbsoluteFill>
  );
};
