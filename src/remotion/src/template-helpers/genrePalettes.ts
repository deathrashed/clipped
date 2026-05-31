export type GenrePalette = {
  primary: string;
  secondary: string;
  accent: string;
  glow: string;
  bg: string;
  text: string;
  muted: string;
};

const genreMap: Record<string, GenrePalette> = {
  death: {
    primary: "#1a1a3e",
    secondary: "#2d1b69",
    accent: "#00e5ff",
    glow: "#00e5ff66",
    bg: "#05050f",
    text: "#e8e8f0",
    muted: "#8888aa",
  },
  "black metal": {
    primary: "#0a0a0a",
    secondary: "#1a1a1a",
    accent: "#cccccc",
    glow: "#88888844",
    bg: "#000000",
    text: "#cccccc",
    muted: "#666666",
  },
  doom: {
    primary: "#1a0a0a",
    secondary: "#2d1010",
    accent: "#cc3333",
    glow: "#cc333344",
    bg: "#080202",
    text: "#ddcccc",
    muted: "#996666",
  },
  "hip hop": {
    primary: "#1a0f00",
    secondary: "#2d1a00",
    accent: "#ffd75f",
    glow: "#ffd75f66",
    bg: "#080400",
    text: "#fff8e4",
    muted: "#d9c88f",
  },
  rap: {
    primary: "#1a0f00",
    secondary: "#2d1a00",
    accent: "#ffb000",
    glow: "#ffb00066",
    bg: "#080400",
    text: "#fff8e4",
    muted: "#d9c88f",
  },
  edm: {
    primary: "#0a001a",
    secondary: "#1a0033",
    accent: "#ff00ff",
    glow: "#ff00ff55",
    bg: "#040008",
    text: "#f0e8ff",
    muted: "#aa88cc",
  },
  electronic: {
    primary: "#0a001a",
    secondary: "#1a0033",
    accent: "#00e5ff",
    glow: "#00e5ff55",
    bg: "#040008",
    text: "#e8f0ff",
    muted: "#88aacc",
  },
  ambient: {
    primary: "#0a0a14",
    secondary: "#141428",
    accent: "#88ccff",
    glow: "#88ccff33",
    bg: "#040408",
    text: "#dde8f0",
    muted: "#8899aa",
  },
  jazz: {
    primary: "#14100a",
    secondary: "#1e1a12",
    accent: "#f3d36b",
    glow: "#f3d36b44",
    bg: "#080604",
    text: "#f0e8d8",
    muted: "#b0a890",
  },
  rock: {
    primary: "#0f0a0a",
    secondary: "#1e1414",
    accent: "#ff4444",
    glow: "#ff444444",
    bg: "#060202",
    text: "#e8d8d8",
    muted: "#aa8888",
  },
  pop: {
    primary: "#140a14",
    secondary: "#241428",
    accent: "#ff88dd",
    glow: "#ff88dd44",
    bg: "#080408",
    text: "#f0e0e8",
    muted: "#b088aa",
  },
  classical: {
    primary: "#0a0a0a",
    secondary: "#181818",
    accent: "#d4af37",
    glow: "#d4af3744",
    bg: "#040404",
    text: "#e8e0d0",
    muted: "#a09888",
  },
};

export const resolveGenrePalette = (genre: string, fallback?: GenrePalette): GenrePalette => {
  const key = genre?.toLowerCase().trim() || "";
  for (const [k, p] of Object.entries(genreMap)) {
    if (key.includes(k)) return p;
  }
  return fallback ?? {
    primary: "#080808",
    secondary: "#141414",
    accent: "#00e5ff",
    glow: "#00e5ff44",
    bg: "#050505",
    text: "#f0e8e0",
    muted: "#999080",
  };
};
