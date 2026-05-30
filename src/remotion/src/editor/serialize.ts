import type { EditorState, KeyframeSet, KeyframeData, Keyframe } from "./types";
import { keyParts } from "./state";
import registry from "../elements/registry";

function getRoot(
  instance: Record<string, unknown>,
  key: string
): Record<string, unknown> {
  const rootKey = key.split(".")[0];
  if (rootKey === "transform") return (instance.transform ?? {}) as Record<string, unknown>;
  if (rootKey === "appearance") return (instance.appearance ?? {}) as Record<string, unknown>;
  return (instance.props ?? {}) as Record<string, unknown>;
}

function setRoot(
  instance: Record<string, unknown>,
  key: string,
  root: Record<string, unknown>
): void {
  const rootKey = key.split(".")[0];
  if (rootKey === "transform") instance.transform = root as typeof instance.transform;
  else if (rootKey === "appearance") instance.appearance = root as typeof instance.appearance;
  else instance.props = root as typeof instance.props;
}

function walkToKeyframes(
  obj: Record<string, unknown>,
  key: string
): Keyframe[] | null {
  const relParts = keyParts(key).slice(1);
  let current: unknown = obj;
  for (const part of relParts) {
    if (current && typeof current === "object" && part in (current as Record<string, unknown>)) {
      current = (current as Record<string, unknown>)[part];
    } else {
      return null;
    }
  }
  if (current && typeof current === "object") {
    const kf = (current as Record<string, unknown>).keyframes;
    if (Array.isArray(kf)) return kf as Keyframe[];
  }
  return null;
}

export function exportKeyframes(state: EditorState): KeyframeSet {
  const keyframes: KeyframeData[] = [];

  for (const el of state.elements) {
    const def = registry.find((d) => d.id === el.id);
    if (!def) continue;

    for (const section of def.inspector) {
      for (const control of section.controls) {
        if (!control.keyframeable) continue;
        const root = getRoot(el.instance as Record<string, unknown>, control.key);
        const instanceKeyframes = walkToKeyframes(root, control.key);
        if (instanceKeyframes && instanceKeyframes.length > 0) {
          keyframes.push({
            elementId: el.id,
            controlKey: control.key,
            keyframes: instanceKeyframes,
          });
        }
      }
    }
  }

  return { keyframes };
}

export function importKeyframes(state: EditorState, set: KeyframeSet): EditorState {
  if (!set?.keyframes?.length) return state;

  let newState = state;

  for (const kf of set.keyframes) {
    newState = {
      ...newState,
      elements: newState.elements.map((el) => {
        if (el.id !== kf.elementId) return el;
        const newInstance = { ...el.instance } as Record<string, unknown>;
        const root = getRoot(newInstance, kf.controlKey);

        const relParts = keyParts(kf.controlKey).slice(1);
        let current: Record<string, unknown> = root;
        for (let i = 0; i < relParts.length - 1; i++) {
          const part = relParts[i];
          current[part] =
            current[part] && typeof current[part] === "object" && !Array.isArray(current[part])
              ? { ...(current[part] as Record<string, unknown>) }
              : {};
          current = current[part] as Record<string, unknown>;
        }

        const lastPart = relParts[relParts.length - 1];
        const existing = current[lastPart];
        if (existing && typeof existing === "object" && !Array.isArray(existing)) {
          current[lastPart] = {
            ...(existing as Record<string, unknown>),
            keyframes: kf.keyframes,
          };
        } else {
          current[lastPart] = existing !== undefined
            ? { value: existing, keyframes: kf.keyframes }
            : { keyframes: kf.keyframes };
        }

        setRoot(newInstance, kf.controlKey, root);
        return { ...el, instance: newInstance as typeof el.instance };
      }),
    };
  }

  return newState;
}
