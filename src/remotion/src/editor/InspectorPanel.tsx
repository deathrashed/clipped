import type { EditorState } from "./types";
import type { InspectorSection } from "../elements/types";
import { InspectorControl } from "./InspectorControl";
import { getSelectedDefinition, getSelectedElement, setElementProp } from "./state";
import { resolveInspectorValue, applyInspectorDefaults, transformSection, appearanceSection } from "../elements/inspector";

type InspectorPanelProps = {
  state: EditorState;
  onStateChange: (state: EditorState) => void;
  showTransformSection?: boolean;
};

export const InspectorPanel = ({ state, onStateChange, showTransformSection = true }: InspectorPanelProps) => {
  const def = getSelectedDefinition(state);
  const selectedEl = getSelectedElement(state);

  if (!def || !selectedEl) {
    return (
      <div style={emptyStyle}>
        <span style={{ color: "#666" }}>No element selected</span>
      </div>
    );
  }

  const instance = selectedEl.instance;
  const fullProps = applyInspectorDefaults(instance.props || {}, def.inspector);
  if (instance.transform) {
    fullProps.transform = { ...instance.transform };
  }
  if (instance.appearance) {
    fullProps.appearance = { ...instance.appearance };
  }

  const sections: InspectorSection[] = showTransformSection
    ? def.inspector
    : def.inspector.filter((s) => s.title !== "Transform");

  return (
    <div style={panelStyle}>
      <div style={headerStyle}>{def.label}</div>
      {sections.map((section) => {
        const sectionKey = `${def.id}-${section.title}`;
        const expanded = state.expandedSections[sectionKey] !== false;

        return (
          <div key={sectionKey} style={{ marginBottom: 12 }}>
            <div
              style={sectionHeaderStyle}
              onClick={() => {
                onStateChange({
                  ...state,
                  expandedSections: {
                    ...state.expandedSections,
                    [sectionKey]: !expanded,
                  },
                });
              }}
            >
              <span>{expanded ? "▾" : "▸"}</span>
              <span style={{ fontWeight: 600, fontSize: 13, color: "#eee" }}>
                {section.title}
              </span>
            </div>
            {expanded && (
              <div style={{ paddingLeft: 8 }}>
                {section.controls.map((control) => {
                  const value = resolveInspectorValue(control.key, fullProps);
                  return (
                    <div key={control.key} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                      <div style={{ flex: 1 }}>
                        <InspectorControl
                          control={control}
                          value={value}
                          onChange={(newValue) => {
                            onStateChange(setElementProp(state, selectedEl.id, control.key, newValue));
                          }}
                        />
                      </div>
                      {control.keyframeable && (
                        <button
                          disabled
                          style={keyframeBtnStyle}
                          title="Keyframe editor coming in Phase 6"
                        >
                          ◆
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

const panelStyle: React.CSSProperties = {
  background: "#1a1a1a",
  borderRadius: 8,
  padding: 12,
  fontSize: 13,
  color: "#ccc",
  fontFamily: "system-ui, sans-serif",
};

const emptyStyle: React.CSSProperties = {
  ...panelStyle,
  textAlign: "center",
  padding: 24,
};

const headerStyle: React.CSSProperties = {
  fontSize: 14,
  fontWeight: 700,
  color: "#fff",
  marginBottom: 12,
  paddingBottom: 8,
  borderBottom: "1px solid #333",
};

const sectionHeaderStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 6,
  cursor: "pointer",
  padding: "4px 0",
  userSelect: "none",
};

const keyframeBtnStyle: React.CSSProperties = {
  background: "none",
  border: "1px solid #555",
  color: "#555",
  borderRadius: 4,
  cursor: "not-allowed",
  fontSize: 10,
  padding: "2px 6px",
  opacity: 0.4,
};
