export type RemotionTemplateId = "pulse_reel" | "gallery_square" | "record_square" | "fluid_scene" | "metal_vhs" | "premium_card";
export type RemotionCompositionId = "pulse-reel" | "gallery-square" | "record-square" | "fluid-scene" | "metal-vhs" | "premium-card";

export type MotionLevel = "low" | "medium" | "high";
export type WaveformMode =
  | "none"
  | "bars"
  | "mirror"
  | "radial"
  | "ring"
  | "ribbon"
  | "flower"
  | "oscilloscope"
  | "particles";
export type PaletteName = "auto" | "cyan" | "red" | "gold" | "mono";
export type VisualStyle = "classic" | "brutal" | "neon" | "zine" | "cinematic" | "doom" | "frost" | "vhs" | "hiphop";

export type ClippedRenderProps = {
  version: number;
  templateId: RemotionTemplateId;
  compositionId: RemotionCompositionId;
  platformName: string;
  width: number;
  height: number;
  fps: number;
  durationSeconds: number;
  durationFrames: number;
  assets: {
    audioSrc: string | null;
    coverSrc: string | null;
    logoSrc: string | null;
    artistImageSrc: string | null;
    backgroundSrc: string | null;
    lyrics: string | null;
    lyricsJson: string | null;
    extraImageSrcs: string[];
    mediaSrcs: string[];
  };
  metadata: {
    artist: string;
    title: string;
    album: string;
    trackNumber: number;
    year: string;
    genre: string;
    sourceFilename: string;
  };
  audio: {
    fadeIn: number | null;
    fadeOut: number | null;
    volume: number;
    originalStart: number;
    preparedDuration: number;
  };
  options: {
    style: VisualStyle | string;
    motion: MotionLevel | string;
    waveform: WaveformMode | string;
    palette: PaletteName | string;
    scene_pack: string;
    effects: string;
    captions: string;
    mediaMode: string;
    cleanLogo: boolean;
    logoBg: string;
    logoFuzz: number;
    seed: string;
  };
  encoding: {
    codec: string;
    crf: number;
    audioCodec: string;
    audioBitrate: string;
    pixelFormat: string;
  };
};
