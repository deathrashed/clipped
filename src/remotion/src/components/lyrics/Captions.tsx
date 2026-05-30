import React, { useEffect, useMemo, useState } from 'react';
import { interpolate, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { SubtitleLine, parseLyrics } from '../../audio/lyrics-utils';
import { fonts } from '../../typography';

export interface CaptionsProps {
  /** Path to a .lrc/.srt/.vtt file (served as Remotion static asset) */
  lyricsSrc?: string | null;
  /** Pre-parsed JSON string from embedded audio metadata */
  lyricsJson?: string | null;
  captionsStyle?: 'off' | 'metadata' | 'lyrics' | 'lower_third' | 'impact';
  metadata?: {
    title: string;
    artist: string;
    album: string;
  };
  originalStart?: number;
}

function useParsedSubtitles(
  lyricsSrc: string | null | undefined,
  lyricsJson: string | null | undefined,
  originalStart: number = 0,
): SubtitleLine[] {
  // 1. If we have inline JSON (from embedded metadata), parse it synchronously
  const inlineLines = useMemo<SubtitleLine[]>(() => {
    if (!lyricsJson) return [];
    try {
      const parsed = JSON.parse(lyricsJson);
      if (Array.isArray(parsed)) {
        return (parsed as SubtitleLine[]).map(line => ({
          ...line,
          start: line.start - originalStart,
          end: line.end - originalStart,
        }));
      }
    } catch (_) {}
    return [];
  }, [lyricsJson, originalStart]);

  // 2. If we have a file reference, fetch it asynchronously
  const [fetchedLines, setFetchedLines] = useState<SubtitleLine[]>([]);

  useEffect(() => {
    if (!lyricsSrc || inlineLines.length > 0) return;
    async function fetchLyrics() {
      try {
        const url = lyricsSrc!.startsWith('http') ? lyricsSrc! : staticFile(lyricsSrc!);
        const res = await fetch(url);
        if (!res.ok) return;
        const text = await res.text();
        const parsed = parseLyrics(text, lyricsSrc!);
        const adjusted = parsed.map(line => ({
          ...line,
          start: line.start - originalStart,
          end: line.end - originalStart,
        }));
        setFetchedLines(adjusted);
      } catch (_) {}
    }
    fetchLyrics();
  }, [lyricsSrc, inlineLines.length, originalStart]);

  return inlineLines.length > 0 ? inlineLines : fetchedLines;
}

export const Captions: React.FC<CaptionsProps> = ({
  lyricsSrc,
  lyricsJson,
  captionsStyle = 'off',
  metadata,
  originalStart = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;
  const subtitles = useParsedSubtitles(lyricsSrc, lyricsJson, originalStart);

  if (captionsStyle === 'off') return null;

  // Metadata-only or no lyrics available → show static metadata
  const noLyrics = subtitles.length === 0;
  if (captionsStyle === 'metadata' || noLyrics) {
    if (!metadata?.title) return null;
    return (
      <div style={{
        position: 'absolute',
        bottom: 80,
        left: 0,
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        textShadow: '0 2px 10px rgba(0,0,0,0.8)',
        fontFamily: fonts.body,
        textAlign: 'center',
        zIndex: 50,
      }}>
        {metadata.title && <h2 style={{ margin: '0 0 10px 0', fontSize: 50, fontWeight: 800 }}>{metadata.title}</h2>}
        {metadata.artist && <h3 style={{ margin: 0, fontSize: 30, fontWeight: 400, opacity: 0.8 }}>{metadata.artist}</h3>}
      </div>
    );
  }

  const activeIndex = subtitles.findIndex(s => currentTime >= s.start && currentTime <= s.end);
  const activeSub = activeIndex >= 0 ? subtitles[activeIndex] : null;

  if (captionsStyle === 'lower_third') {
    return (
      <div style={{
        position: 'absolute',
        bottom: 80,
        left: '10%',
        width: '80%',
        display: 'flex',
        justifyContent: 'center',
        zIndex: 50,
      }}>
        <div style={{
          background: 'rgba(0,0,0,0.62)',
          padding: '18px 36px',
          borderRadius: 18,
          opacity: activeSub ? 1 : 0,
          border: '1px solid rgba(255,255,255,0.08)'
        }}>
          <span style={{
            color: 'white',
            fontFamily: fonts.body,
            fontSize: 38,
            fontWeight: 600,
            textAlign: 'center',
            display: 'block'
          }}>
            {activeSub?.text ?? ''}
          </span>
        </div>
      </div>
    );
  }

  if (captionsStyle === 'impact') {
    if (!activeSub) return null;
    const dur = Math.max(0.01, activeSub.end - activeSub.start);
    const progress = Math.min(1, Math.max(0, (currentTime - activeSub.start) / dur));
    const scale = interpolate(progress, [0, 0.1, 0.9, 1], [0.82, 1, 1, 1.08], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    const opacity = interpolate(progress, [0, 0.1, 0.9, 1], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    return (
      <div style={{
        position: 'absolute', inset: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 50,
        pointerEvents: 'none',
      }}>
        <h1 style={{
          color: 'white',
          fontFamily: fonts.brutal,
          fontSize: 112,
          fontWeight: 900,
          textAlign: 'center',
          textTransform: 'uppercase',
          textShadow: '0 10px 30px rgba(0,0,0,0.6)',
          transform: `scale(${scale})`,
          opacity,
          margin: 0,
          padding: '0 40px'
        }}>
          {activeSub.text}
        </h1>
      </div>
    );
  }

  if (captionsStyle === 'lyrics') {
    const nextSub = activeIndex >= 0 && activeIndex < subtitles.length - 1 ? subtitles[activeIndex + 1] : null;
    return (
      <div style={{
        position: 'absolute',
        bottom: 100,
        left: '8%',
        width: '84%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        zIndex: 50,
        pointerEvents: 'none',
      }}>
        {activeSub && (
          <div style={{
            color: 'white',
            fontFamily: fonts.display,
            fontSize: 46,
            fontWeight: 800,
            textAlign: 'center',
            textShadow: '0 6px 22px rgba(0,0,0,0.85)',
            marginBottom: 18,
          }}>
            {activeSub.text}
          </div>
        )}
        {nextSub && (
          <div style={{
            color: 'rgba(255,255,255,0.48)',
            fontFamily: fonts.body,
            fontSize: 32,
            fontWeight: 600,
            textAlign: 'center',
            textShadow: '0 4px 10px rgba(0,0,0,0.5)',
          }}>
            {nextSub.text}
          </div>
        )}
      </div>
    );
  }

  return null;
};
