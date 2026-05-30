# Phase 3 — Art Direction + QA Fixtures Report

## Fixtures Created

| File | Composition | Metadata | Assets | Purpose |
|------|-----------|----------|-------|---------|
| `qa-metal.json` | metal-vhs | Disincarnate — "Entranced" (Death Metal, 1993) | Real cover/logo/artist | Black-metal VHS aesthetic |
| `qa-hiphop.json` | pulse-reel | Onyx — "Slam Harder" (Hardcore Hip-Hop, 2024) | Real assets | Vertical reel, high motion |
| `qa-vinyl.json` | record-square | Hiroshi Suzuki — "Romance" (Jazz-Funk, 1976) | Cover only, no logo/artist | Record spinner fallback test |
| `qa-vhs.json` | fluid-scene | Crystal Castles — "Untrust Us" (Electroclash, 2010) | No assets (all null) | Full fallback visual test |
| `qa-clean.json` | premium-card | Nala Sinephro — "Continuum 7" (Ambient Jazz, 2024) | Cover + logo, no artist | Editorial clean card test |

## Templates Updated

### Fallback Artwork Replacement (`♫` → `FallbackArtwork`)
- **GallerySquare** — Replaced inline ♫ div with `<FallbackArtwork>` component
- **MetalVHS** — Replaced inline ♫ div with `<FallbackArtwork>` component
- **PulseReel** — Replaced inline ♫ div with `<FallbackArtwork>` component
- **PremiumCard** — Replaced inline ♫ div with `<FallbackArtwork>` component

### New Components
- `src/artwork/FallbackArtwork.tsx` — Intentional gradient-backed artwork with radial bloom, diagonal sweep, and seed-driven hue
- `src/artwork/FallbackLogo.tsx` — Initials-based monogram fallback (Oswald font)
- `src/artwork/FallbackArtistImage.tsx` — Gradient panel with accent blooms and initial

### TextTrackIn Integration
- **PremiumCard** — Title/artist metadata now uses `<TextTrackIn>` with editorial letter-spacing collapse (0.18em → -0.02em) instead of plain opacity fade

### Default Props Updated
- `default-props.json` metadata changed from "Remotion Preview" / "Clipped" → "Nala Sinephro" / "Continuum 7"

### Deprecated Markers
- `_deprecated/Waveform.tsx` — Added `@deprecated` header
- `_deprecated/SpeakerCone.tsx` — Added `@deprecated` header
- `_deprecated/Spectrum.tsx` — Added `@deprecated` header

### Tooling
- `scripts/check-fonts.mjs` — Checks 10 expected font files; exits with code 1 on `--strict`
- `package.json` — Added `check:fonts` script

## QA Renders

All 10 renders completed successfully.

| Render | File Size |
|--------|-----------|
| GallerySquare × Hip-Hop | 1.9 MB |
| GallerySquare × Metal | 993 KB |
| GallerySquare × Editorial | 1.4 MB |
| RecordSquare × Vinyl | 1.0 MB |
| RecordSquare × Metal | 627 KB |
| PulseReel × Hip-Hop | 1.3 MB |
| MetalVHS × Metal | 1.0 MB |
| MetalVHS × No Assets | 1.1 MB |
| PremiumCard × Clean | 916 KB |
| PremiumCard × Vinyl (No Logo) | 1.2 MB |

## Verification

- Typecheck: ✅ (tsc --noEmit passes)
- Compositions: ✅ All 6 registered
- Font check: ⚠️ 0/10 local fonts found (system fallback only)
- Deprecated headers: ✅ Added to 3 files
- TextTrackIn integration: ✅ PremiumCard metadata track-in

## Known Issues

1. **Font files missing** — All 10 expected woff2 files absent from `public/fonts/`. Falls back to system stacks. Font download is deliberate; check-fonts.mjs validates this.
2. **qa-vhs.json has all null assets** — Intentionally tests full fallback path. The FallbackArtwork component renders seed-driven gradients with no album art at all.
