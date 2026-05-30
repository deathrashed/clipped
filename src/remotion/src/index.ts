import { registerRoot } from "remotion";
import { RemotionRoot } from "./Root";

registerRoot(RemotionRoot);

export type * from "./editor/types";
export {
  selectElement,
  getSelectedElement,
  getSelectedDefinition,
  toggleVisibility,
  moveUp,
  moveDown,
  setTransform,
  setElementProp,
  createEditorState,
  InspectorPanel,
  InspectorControl,
  ElementList,
  TransformControls,
  exportKeyframes,
  importKeyframes,
} from "./editor";

