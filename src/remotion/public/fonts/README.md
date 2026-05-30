# Clipped Local Fonts

All font files are checked in to `public/fonts/` for fully deterministic offline rendering.
Each font directory maps to a family name used in `src/typography/fonts.ts`.

## Inventory

```
remotion/public/fonts/
  Anton/
    Anton-Regular.woff2 (400)
  Barlow/
    Barlow-Regular.woff2 (400)
    Barlow-SemiBold.woff2 (600)
    Barlow-Bold.woff2 (700)
  BebasNeue/
    BebasNeue-Regular.woff2 (400)
    BebasNeue-Bold.woff2 (700)
  Exo2/
    Exo2-Regular.woff2 (400)
    Exo2-Medium.woff2 (500)
    Exo2-Bold.woff2 (700)
  Impact/
    Impact.woff2 (400)
  Inter/
    Inter-Thin.woff2 (100)
    Inter-ExtraLight.woff2 (200)
    Inter-Light.woff2 (300)
    Inter-Regular.woff2 (400)
    Inter-Medium.woff2 (500)
    Inter-SemiBold.woff2 (600)
    Inter-Bold.woff2 (700)
    Inter-ExtraBold.woff2 (800)
    Inter-Black.woff2 (900)
  Molot/
    Molot.woff2 (400)
  Montserrat/
    Montserrat-Regular.woff2 (400)
    Montserrat-Medium.woff2 (500)
    Montserrat-SemiBold.woff2 (600)
    Montserrat-Bold.woff2 (700)
  Oswald/
    Oswald-ExtraLight.woff2 (200)
    Oswald-Light.woff2 (300)
    Oswald-Regular.woff2 (400)
    Oswald-Medium.woff2 (500)
    Oswald-SemiBold.woff2 (600)
    Oswald-Bold.woff2 (700)
    Oswald-Heavy.woff2 (800)
  PeaceSans/
    PeaceSans.woff2 (400)
  Poppins/
    Poppins-Regular.woff2 (400)
    Poppins-Medium.woff2 (500)
    Poppins-SemiBold.woff2 (600)
    Poppins-Bold.woff2 (700)
  Roboto/
    Roboto-Regular.woff2 (400)
    Roboto-Medium.woff2 (500)
    Roboto-Bold.woff2 (700)
  Russo/
    RussoOne-Regular.woff2 (400)
  SF/
    SF-Compact-Text-Black.woff2 (900)
    SF-Pro-Text-Semibold.woff2 (600)
  SpaceMono/
    SpaceMono-Regular.woff2 (400)
    SpaceMono-Italic.woff2 (400)
    SpaceMono-Bold.woff2 (700)
    SpaceMono-BoldItalic.woff2 (700)
```

## Adding Fonts

1. Download WOFF2 files into a new or existing family directory under `public/fonts/`
2. Register the font in `src/typography/fonts.ts` using `loadFont({ family, filePath, weight })`
3. Add entries to `scripts/check-fonts.mjs`
4. Run `npm run check:fonts` to verify

If files are missing, the loader logs a network warning and falls back to the system font stack.
