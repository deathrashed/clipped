import type { EditorState } from "./types";
import { getSelectedElement, setTransform, type TransformField } from "./state";

type TransformControlsProps = {
  state: EditorState;
  onStateChange: (state: EditorState) => void;
};

const fields: { key: TransformField; label: string }[] = [
  { key: "transform.position.x", label: "Position X" },
  { key: "transform.position.y", label: "Position Y" },
  { key: "transform.rotation.z", label: "Rotation Z" },
  { key: "transform.scale", label: "Scale" },
];

export const TransformControls = ({ state, onStateChange }: TransformControlsProps) => {
  const selectedEl = getSelectedElement(state);
  if (!selectedEl) return null;

  const t = selectedEl.instance.transform;

  const getValue = (key: string): number => {
    if (key === "transform.scale") return t?.scale ?? 1;
    if (key === "transform.rotation.z") return t?.rotation?.z ?? 0;
    if (key === "transform.position.x") return t?.position?.x ?? 0;
    if (key === "transform.position.y") return t?.position?.y ?? 0;
    return 0;
  };

  const getBounds = (key: string): { min?: number; max?: number; step?: number } => {
    if (key === "transform.scale") return { min: 0.01, max: 10, step: 0.01 };
    if (key === "transform.rotation.z") return { min: -360, max: 360, step: 1 };
    return { min: -9999, max: 9999, step: 1 };
  };

  return (
    <div style={panelStyle}>
      <div style={headerStyle}>Transform</div>
      {fields.map(({ key, label }) => {
        const bounds = getBounds(key);
        return (
          <label key={key} style={labelStyle}>
            <span style={labelTextStyle}>{label}</span>
            <input
              type="number"
              value={getValue(key)}
              onChange={(e) =>
                onStateChange(setTransform(state, selectedEl.id, key, parseFloat(e.target.value)))
              }
              min={bounds.min}
              max={bounds.max}
              step={bounds.step}
              style={inputStyle}
            />
          </label>
        );
      })}
    </div>
  );
};

const panelStyle: React.CSSProperties = {
  background: "#1a1a1a",
  borderRadius: 8,
  padding: 12,
  fontFamily: "system-ui, sans-serif",
};

const headerStyle: React.CSSProperties = {
  fontSize: 14,
  fontWeight: 700,
  color: "#fff",
  marginBottom: 8,
  paddingBottom: 8,
  borderBottom: "1px solid #333",
};

const labelStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: 8,
  marginBottom: 6,
};

const labelTextStyle: React.CSSProperties = {
  fontSize: 12,
  color: "#ccc",
  fontWeight: 500,
  textTransform: "uppercase",
  letterSpacing: "0.5px",
};

const inputStyle: React.CSSProperties = {
  background: "#2a2a2a",
  color: "#fff",
  border: "1px solid #444",
  borderRadius: 4,
  padding: "4px 8px",
  fontSize: 13,
  width: 80,
  textAlign: "right",
};
