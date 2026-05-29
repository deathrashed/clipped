# Clipped Local Fonts

To enable fully deterministic offline rendering, copy the following font files (in WOFF2 or TTF format) into their respective directories.

## Expected Directory Hierarchy

```
remotion/public/fonts/
  Inter/
    Inter-Regular.woff2 (Weight: 400)
    Inter-Medium.woff2 (Weight: 500)
    Inter-SemiBold.woff2 (Weight: 600)
    Inter-Bold.woff2 (Weight: 700)
  Oswald/
    Oswald-Regular.woff2 (Weight: 400)
    Oswald-Medium.woff2 (Weight: 500)
    Oswald-Bold.woff2 (Weight: 700)
  BebasNeue/
    BebasNeue-Regular.woff2 (Weight: 400)
  SpaceMono/
    SpaceMono-Regular.woff2 (Weight: 400)
    SpaceMono-Bold.woff2 (Weight: 700)
```

If these files are missing, the visualizer will gracefully fall back to default system sans-serif/monospace font stacks.
