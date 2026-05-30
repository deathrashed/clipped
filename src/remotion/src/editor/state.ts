import type { EditorState, EditorElementState } from "./types";
import type { ElementDefinition } from "../elements/types";
import registry from "../elements/registry";

export type TransformField =
  | "transform.position.x"
  | "transform.position.y"
  | "transform.rotation.z"
  | "transform.scale";

export function keyParts(key: string): string[] {
  const root = key.split(".")[0];
  if (root === "transform" || root === "appearance") {
    return key.split(".");
  }
  return ["props", ...key.split(".")];
}

function deepCopyPath(
  obj: Record<string, unknown>,
  parts: string[]
): Record<string, unknown> {
  let target = { ...obj };
  let result = target;
  for (let i = 0; i < parts.length - 1; i++) {
    const part = parts[i];
    const existing = target[part];
    target[part] =
      existing && typeof existing === "object" && !Array.isArray(existing)
        ? { ...(existing as Record<string, unknown>) }
        : {};
    target = target[part] as Record<string, unknown>;
  }
  return result;
}

export function selectElement(state: EditorState, id: string | null): EditorState {
  return { ...state, selectedId: id };
}

export function getSelectedElement(state: EditorState): EditorElementState | null {
  if (!state.selectedId) return null;
  return state.elements.find((el) => el.id === state.selectedId) ?? null;
}

export function getSelectedDefinition(state: EditorState): ElementDefinition | null {
  if (!state.selectedId) return null;
  return registry.find((d) => d.id === state.selectedId) ?? null;
}

export function toggleVisibility(state: EditorState, id: string): EditorState {
  return {
    ...state,
    elements: state.elements.map((el) =>
      el.id === id ? { ...el, visible: !el.visible } : el
    ),
  };
}

export function moveUp(state: EditorState, id: string): EditorState {
  const idx = state.elements.findIndex((el) => el.id === id);
  if (idx <= 0) return state;
  const elements = [...state.elements];
  [elements[idx - 1], elements[idx]] = [elements[idx], elements[idx - 1]];
  return { ...state, elements };
}

export function moveDown(state: EditorState, id: string): EditorState {
  const idx = state.elements.findIndex((el) => el.id === id);
  if (idx === -1 || idx >= state.elements.length - 1) return state;
  const elements = [...state.elements];
  [elements[idx], elements[idx + 1]] = [elements[idx + 1], elements[idx]];
  return { ...state, elements };
}

function setNestedProp(
  state: EditorState,
  id: string,
  key: string,
  value: unknown
): EditorState {
  const parts = keyParts(key);
  const lastPart = parts[parts.length - 1];

  return {
    ...state,
    elements: state.elements.map((el) => {
      if (el.id !== id) return el;
      const newInstance = deepCopyPath(
        el.instance as Record<string, unknown>,
        parts
      );
      let current: Record<string, unknown> = newInstance;
      for (let i = 0; i < parts.length - 1; i++) {
        current = current[parts[i]] as Record<string, unknown>;
      }
      current[lastPart] = value;
      return { ...el, instance: newInstance as typeof el.instance };
    }),
  };
}

export function setTransform(
  state: EditorState,
  id: string,
  field: TransformField,
  value: number
): EditorState {
  return setNestedProp(state, id, field, value);
}

export function setElementProp(
  state: EditorState,
  id: string,
  key: string,
  value: unknown
): EditorState {
  return setNestedProp(state, id, key, value);
}

export function createEditorState(elements: EditorElementState[]): EditorState {
  return {
    elements,
    selectedId: null,
    expandedSections: {},
  };
}
