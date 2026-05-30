import type { InspectorControl as InspectorControlType } from "../elements/types";

type InspectorControlProps = {
  control: InspectorControlType;
  value: unknown;
  onChange: (value: unknown) => void;
};

function parseNumber(raw: string, fallback: number): number {
  const parsed = parseFloat(raw);
  return Number.isNaN(parsed) ? fallback : parsed;
}

export const InspectorControl = ({ control, value, onChange }: InspectorControlProps) => {
  const val = value ?? control.defaultValue;

  switch (control.type) {
    case "number":
      return (
        <label style={labelStyle}>
          <span style={labelTextStyle}>{control.label}</span>
          <input
            type="number"
            value={val as number}
            onChange={(e) => onChange(parseNumber(e.target.value, control.defaultValue))}
            min={control.min}
            max={control.max}
            step={control.step}
            style={inputStyle}
          />
        </label>
      );
    case "slider":
      return (
        <label style={labelStyle}>
          <span style={labelTextStyle}>{control.label}</span>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <input
              type="range"
              value={val as number}
              onChange={(e) => onChange(parseNumber(e.target.value, control.defaultValue))}
              min={control.min}
              max={control.max}
              step={control.step ?? 0.01}
              style={{ flex: 1 }}
            />
            <span style={readoutStyle}>{Number(val).toFixed(2)}</span>
          </div>
        </label>
      );
    case "color":
      return (
        <label style={labelStyle}>
          <span style={labelTextStyle}>{control.label}</span>
          <input
            type="color"
            value={val as string}
            onChange={(e) => onChange(e.target.value)}
          />
        </label>
      );
    case "boolean":
      return (
        <label style={{ ...labelStyle, flexDirection: "row", gap: 8 }}>
          <input
            type="checkbox"
            checked={val as boolean}
            onChange={(e) => onChange(e.target.checked)}
          />
          <span style={labelTextStyle}>{control.label}</span>
        </label>
      );
    case "select":
      return (
        <label style={labelStyle}>
          <span style={labelTextStyle}>{control.label}</span>
          <select
            value={val as string}
            onChange={(e) => onChange(e.target.value)}
            style={selectStyle}
          >
            {control.options.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        </label>
      );
    default:
      return null;
  }
};

const labelStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 4,
  fontSize: 12,
  color: "#ccc",
  marginBottom: 8,
};

const labelTextStyle: React.CSSProperties = {
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
};

const selectStyle: React.CSSProperties = {
  ...inputStyle,
  minWidth: 120,
};

const readoutStyle: React.CSSProperties = {
  fontSize: 11,
  color: "#888",
  minWidth: 40,
  textAlign: "right",
};
