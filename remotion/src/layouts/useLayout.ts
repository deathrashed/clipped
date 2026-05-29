import { useVideoConfig } from "remotion";
import type { ZoneName } from "./zones";
import { getZone } from "./zones";
import { classifyAspect, getSafeInsets } from "./safe-zones";

/** Returns resolved pixel values for the named layout zone. */
export const useLayout = (name: ZoneName) => {
  const { width, height } = useVideoConfig();
  const aspect = classifyAspect(width, height);
  const zone = getZone(name, aspect);
  const safe = getSafeInsets(width, height);

  return {
    /** Artwork center in pixels. */
    artwork: {
      cx: zone.artwork.cx * width,
      cy: zone.artwork.cy * height,
      /** Square artwork side length. */
      size: zone.artwork.size * Math.min(width, height),
    },
    /** Typography anchor in pixels. */
    typography: {
      left:  zone.typography.left  * width,
      top:   zone.typography.top   * height,
      width: zone.typography.width * width,
      align: zone.typography.align,
    },
    /** Visualizer strip in pixels. */
    visualizer: {
      cx:     zone.visualizer.cx     * width,
      bottom: zone.visualizer.bottom * height,
      width:  zone.visualizer.width  * width,
    },
    /** Logo zone in pixels. */
    logo: {
      cx:    zone.logo.cx    * width,
      top:   zone.logo.top   * height,
      width: zone.logo.width * width,
    },
    safe,
    width,
    height,
    aspect,
  };
};
