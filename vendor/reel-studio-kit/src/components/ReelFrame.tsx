import React from "react";
import { AbsoluteFill, Audio, staticFile } from "remotion";
import type { Brand } from "../brand";
import { BrandProvider, useBrand } from "../brand-context";
import { LayoutProbe } from "./probe";
import { SafeZones } from "./SafeZones";

export type AvatarStyle = "flat" | "illustrated" | "pixel" | "none";

/** Props every reel accepts. `npm run check` and the studio use the last two. */
export type ReelProps = {
  brand?: Brand;
  avatar?: AvatarStyle;
  /** Draw the Instagram UI zones on top (checking only, never the final render). */
  debugSafeZones?: boolean;
  /** Log layout measurements for `npm run check`. */
  probe?: boolean;
  /** Use the animated caption library instead of the plain karaoke captions. One of 23 preset names, e.g. "tiktok", "cinematic-gold" (see src/captioneer/presets). */
  captionPreset?: string;
  /** Or a single style: word-highlight, karaoke, typewriter, bounce, wave, glow, typewriter-erase, pill, flicker, highlighter, blur, rainbow, scale, spotlight. */
  captionStyle?: import("../captioneer/types").CaptionStyle;
};

const Inner: React.FC<{ audio?: string; debugSafeZones?: boolean; probe?: boolean; children: React.ReactNode }> = ({ audio, debugSafeZones, probe, children }) => {
  const b = useBrand();
  return (
    <AbsoluteFill style={{ backgroundColor: b.colors.bg }}>
      {audio ? <Audio src={staticFile(audio)} /> : null}
      {children}
      {debugSafeZones ? <SafeZones /> : null}
      {probe ? <LayoutProbe /> : null}
    </AbsoluteFill>
  );
};

/** Wraps a reel: brand, background, voiceover audio, debug overlay, probe. */
export const ReelFrame: React.FC<{ brand: Brand; audio?: string; debugSafeZones?: boolean; probe?: boolean; children: React.ReactNode }> = ({ brand, children, ...rest }) => (
  <BrandProvider brand={brand}>
    <Inner {...rest}>{children}</Inner>
  </BrandProvider>
);
