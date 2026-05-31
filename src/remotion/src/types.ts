export type RemotionTemplateId =
  | "pulse_reel" | "gallery_square" | "record_square" | "fluid_scene" | "metal_vhs" | "premium_card"
  | "vinyl_sleeve_pro" | "artist_focus_pro" | "metadata_card_pro" | "waveform_stage_pro" | "metal_vhs_pro"
  | "glass_card_pro" | "neon_pulse_pro" | "concert_poster_pro" | "cinematic_pro" | "spinner_pro"
  | "collector_card" | "band_intro" | "audio_orb";

export type RemotionCompositionId =
  | "pulse-reel" | "gallery-square" | "record-square" | "fluid-scene" | "metal-vhs" | "premium-card"
  | "vinyl-sleeve-pro" | "artist-focus-pro" | "metadata-card-pro" | "waveform-stage-pro" | "metal-vhs-pro"
  | "glass-card-pro" | "neon-pulse-pro" | "concert-poster-pro" | "cinematic-pro" | "spinner-pro"
  | "collector-card" | "band-intro" | "audio-orb";

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
