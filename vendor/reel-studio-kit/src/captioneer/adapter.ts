// Glue between this kit and the vendored caption styles.
// The kit's word timings (seconds) -> the library's CaptionData (milliseconds, grouped in phrases).
import type { CaptionData, CaptionSegment } from "./types";

export type KitWord = { word: string; start: number; end: number };

const ENDS_PHRASE = /[.!?:;]$/;

/**
 * Group words into phrases: break after sentence punctuation, or after `maxWords`.
 * Each phrase stays visible `holdMs` after its last word (but never past the next phrase).
 */
export const wordsToCaptionData = (words: KitWord[], opts: { maxWords?: number; holdMs?: number } = {}): CaptionData => {
  const maxWords = opts.maxWords ?? 7;
  const holdMs = opts.holdMs ?? 350;
  const groups: KitWord[][] = [];
  let cur: KitWord[] = [];
  for (const w of words) {
    cur.push(w);
    if (ENDS_PHRASE.test(w.word) || cur.length >= maxWords) {
      groups.push(cur);
      cur = [];
    }
  }
  if (cur.length) groups.push(cur);

  const segments: CaptionSegment[] = groups.map((g, i) => {
    const startMs = Math.round(g[0].start * 1000);
    const lastEnd = Math.round(g[g.length - 1].end * 1000);
    const nextStart = groups[i + 1] ? Math.round(groups[i + 1][0].start * 1000) : Infinity;
    return {
      text: g.map((w) => w.word).join(" "),
      startMs,
      endMs: Math.min(lastEnd + holdMs, nextStart),
      words: g.map((w) => ({ word: w.word, startMs: Math.round(w.start * 1000), endMs: Math.round(w.end * 1000), confidence: 1 })),
    };
  });
  const durationMs = segments.length ? segments[segments.length - 1].endMs : 0;
  return { segments, language: "en", durationMs };
};
