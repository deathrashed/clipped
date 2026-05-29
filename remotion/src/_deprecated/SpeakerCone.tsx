import { useCurrentFrame } from "remotion";
import type { AudioAnalysis } from "../audio/audio-utils";

/**
 * SpeakerCone — vibrating physical speaker graphic.
 * Concentric speaker layers scale up on heavy bass hits.
 */
export const SpeakerCone = ({
  audio,
  accentColor,
  size = 400,
}: {
  audio: AudioAnalysis;
  accentColor?: string;
  size?: number;
}) => {
  const frame = useCurrentFrame();
  const bass = audio.bass;
  const pulse = 1 + bass * 0.18;

  return (
    <div
      style={{
        width: size,
        height: size,
        position: "relative",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {/* Outer frame/rim */}
      <div
        style={{
          width: size,
          height: size,
          borderRadius: "50%",
          background: "radial-gradient(circle, #2a2a2a 0%, #151515 80%, #0a0a0a 100%)",
          boxShadow: "0 20px 50px rgba(0,0,0,0.6)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {/* Vibrating cone */}
        <div
          style={{
            width: size * 0.85,
            height: size * 0.85,
            borderRadius: "50%",
            background: "radial-gradient(circle, #1a1a1a 0%, #111 70%, #050505 100%)",
            transform: `scale(${pulse})`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: accentColor ? `0 0 ${20 + bass * 40}px ${accentColor}22` : undefined,
            transition: "transform 0.05s ease-out",
          }}
        >
          {/* Inner dust cap */}
          <div
            style={{
              position: "absolute",
              width: size * 0.35,
              height: size * 0.35,
              borderRadius: "50%",
              background: "radial-gradient(circle, #333 0%, #1a1a1a 80%, #000 100%)",
              boxShadow: "inset 0 4px 10px rgba(255,255,255,0.1), 0 10px 20px rgba(0,0,0,0.5)",
              transform: `scale(${1 + bass * 0.05})`,
            }}
          />
        </div>
      </div>
    </div>
  );
};
