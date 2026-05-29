import { ColorGrade } from "../../../effects/ColorGrade";
import type { ColorGradePreset } from "../../../effects/ColorGrade";

type ColorGradingProps = {
  preset?: ColorGradePreset;
  intensity?: number;
};

export const ColorGrading = ({
  preset = "warm",
  intensity = 0.5,
}: ColorGradingProps) => {
  return <ColorGrade preset={preset} opacity={intensity} />;
};
