import type { ElementInstance } from "../elements/types";

export type EditorElementState = {
  id: string;
  instance: ElementInstance;
  visible: boolean;
  locked: boolean;
};

export type EditorState = {
  elements: EditorElementState[];
  selectedId: string | null;
  expandedSections: Record<string, boolean>;
};

export type Keyframe = {
  frame: number;
  value: number;
  easing?: "linear" | "ease" | "easeIn" | "easeOut" | "spring";
};

export type KeyframeData = {
  elementId: string;
  controlKey: string;
  keyframes: Keyframe[];
};

export type KeyframeSet = {
  keyframes: KeyframeData[];
};
