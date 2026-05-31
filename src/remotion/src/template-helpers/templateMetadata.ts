import type { ClippedRenderProps } from "../types";

export type FormattedMetadata = {
  title: string;
  artist: string;
  album: string;
  year: string;
  genre: string;
  label: string;
  compact: string;
  compactShort: string;
  fullLine: string;
  labelValue: Array<{ label: string; value: string }>;
};

const clean = (val: string | number | null | undefined, fallback = ""): string => {
  const s = String(val ?? "").trim();
  return s.length > 0 ? s : fallback;
};

const fmt = (vals: string[]): string => vals.filter(Boolean).join(" · ");

export const formatMetadata = (props: ClippedRenderProps): FormattedMetadata => {
  const m = props.metadata;
  const title = clean(m.title, clean(m.sourceFilename, "Untitled"));
  const artist = clean(m.artist, "Unknown Artist");
  const album = clean(m.album);
  const year = clean(m.year);
  const genre = clean(m.genre);
  const label = "";

  return {
    title,
    artist,
    album,
    year,
    genre,
    label,
    compact: fmt([album, year, genre]),
    compactShort: fmt([year, genre]),
    fullLine: fmt([artist, album, year, genre]),
    labelValue: [
      { label: "Track", value: title },
      { label: "Artist", value: artist },
      ...(album ? [{ label: "Album", value: album }] : []),
      ...(year ? [{ label: "Year", value: year }] : []),
      ...(genre ? [{ label: "Genre", value: genre }] : []),
    ],
  };
};
