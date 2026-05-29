type LyricsElementProps = {
  lines?: string[];
  mode?: "plain" | "karaoke" | "stacked" | "lower-third";
  activeIndex?: number;
  intensity?: number;
};

export const LyricsElement = ({
  lines,
  mode = "plain",
  activeIndex = 0,
  intensity = 0.5,
}: LyricsElementProps) => {
  if (!lines || lines.length === 0) return null;

  if (mode === "lower-third") {
    const current = lines[Math.min(activeIndex, lines.length - 1)];
    return (
      <div
        style={{
          position: "absolute",
          bottom: "12%",
          left: "5%",
          right: "5%",
          padding: "16px 24px",
          background: "rgba(0,0,0,0.6)",
          borderRadius: 8,
          fontFamily: "'Inter', -apple-system, sans-serif",
          fontSize: 28,
          color: "#fff",
          textAlign: "center",
          opacity: intensity,
        }}
      >
        {current}
      </div>
    );
  }

  if (mode === "stacked") {
    return (
      <div
        style={{
          position: "absolute",
          bottom: "15%",
          left: "5%",
          right: "5%",
          display: "flex",
          flexDirection: "column",
          gap: 8,
          alignItems: "center",
          opacity: intensity,
        }}
      >
        {lines.map((line, i) => (
          <span
            key={i}
            style={{
              fontFamily: "'Inter', -apple-system, sans-serif",
              fontSize: i === activeIndex ? 28 : 20,
              fontWeight: i === activeIndex ? 600 : 400,
              color: i === activeIndex ? "#fff" : "rgba(255,255,255,0.5)",
              transition: "all 0.1s linear",
            }}
          >
            {line}
          </span>
        ))}
      </div>
    );
  }

  return (
    <div
      style={{
        position: "absolute",
        bottom: "12%",
        left: "5%",
        right: "5%",
        textAlign: "center",
        fontFamily: "'Inter', -apple-system, sans-serif",
        fontSize: 28,
        color: "#fff",
        opacity: intensity,
      }}
    >
      {lines.map((line, i) => (
        <div key={i} style={{ marginBottom: i === activeIndex ? 4 : 0 }}>
          {line}
        </div>
      ))}
    </div>
  );
};
