import type { EditorState } from "./types";
import { toggleVisibility, moveUp, moveDown, selectElement } from "./state";
import registry from "../elements/registry";

type ElementListProps = {
  state: EditorState;
  onStateChange: (state: EditorState) => void;
};

export const ElementList = ({ state, onStateChange }: ElementListProps) => {
  return (
    <div style={listStyle}>
      <div style={headerStyle}>Elements</div>
      {state.elements.length === 0 && (
        <div style={{ color: "#666", padding: 12, fontSize: 12, textAlign: "center" }}>
          No elements
        </div>
      )}
      {state.elements.map((el, idx) => {
        const def = registry.find((d) => d.id === el.id);
        const label = def?.label ?? el.id;
        const isSelected = el.id === state.selectedId;
        const isFirst = idx === 0;
        const isLast = idx === state.elements.length - 1;

        return (
          <div
            key={el.id}
            style={{
              ...rowStyle,
              background: isSelected ? "#2a2a3a" : "transparent",
            }}
          >
            <button
              style={iconBtnStyle}
              onClick={() => onStateChange(toggleVisibility(state, el.id))}
              title={el.visible ? "Hide" : "Show"}
            >
              {el.visible ? "👁" : "—"}
            </button>

            <div
              style={labelRowStyle}
              onClick={() => onStateChange(selectElement(state, el.id))}
            >
              <span style={{ fontSize: 13, color: isSelected ? "#fff" : "#ccc" }}>
                {label}
              </span>
              {el.locked && <span style={{ fontSize: 10, color: "#666", marginLeft: 4 }}>🔒</span>}
            </div>

            <div style={{ display: "flex", gap: 2 }}>
              <button
                style={{ ...iconBtnStyle, opacity: isFirst ? 0.3 : 1 }}
                disabled={isFirst}
                onClick={() => onStateChange(moveUp(state, el.id))}
                title="Move up"
              >
                ▲
              </button>
              <button
                style={{ ...iconBtnStyle, opacity: isLast ? 0.3 : 1 }}
                disabled={isLast}
                onClick={() => onStateChange(moveDown(state, el.id))}
                title="Move down"
              >
                ▼
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
};

const listStyle: React.CSSProperties = {
  background: "#1a1a1a",
  borderRadius: 8,
  overflow: "hidden",
  fontFamily: "system-ui, sans-serif",
};

const headerStyle: React.CSSProperties = {
  fontSize: 14,
  fontWeight: 700,
  color: "#fff",
  padding: "8px 12px",
  borderBottom: "1px solid #333",
};

const rowStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 6,
  padding: "6px 12px",
  cursor: "pointer",
  borderBottom: "1px solid #222",
};

const labelRowStyle: React.CSSProperties = {
  flex: 1,
  display: "flex",
  alignItems: "center",
};

const iconBtnStyle: React.CSSProperties = {
  background: "none",
  border: "none",
  color: "#888",
  cursor: "pointer",
  fontSize: 11,
  padding: "2px 4px",
};
