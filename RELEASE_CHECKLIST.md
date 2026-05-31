# RELEASE CANDIDATE QA

**Target:** V1 Release
**Status:** ⚠️ BLOCKED (Pending Mobile QA)

*Instructions: Mark each item as `PASS`, `FAIL`, or `BLOCKED`. Do not declare V1 complete until all critical items pass.*

## 1. Layout & UX
- [BLOCKED] **Mobile layout:** Workspaces, waveforms, and galleries scale cleanly without horizontal overflow.
- [PASS] **SPA Routing:** Navigating between tool, showcase, library, and docs feels instant and maintains state.
- [PASS] **Showcase loading:** `clips.json` parses successfully and populates video cards with metadata tags.
- [PASS] **Library loading:** Audio library populates and plays tracks successfully.
- [PASS] **Smoke test loading:** Remotion/FFmpeg smoke tests load in their dedicated tab.

## 2. Cloud Render Pipeline
- [PASS] **Audio render generation:** Submitting a YouTube URL or library track correctly dispatches to `clip-request`.
- [PASS] **Job lifecycle:** The polling mechanism reliably transitions through `pending` -> `downloading` -> `extracting` -> `done`.
- [PASS] **Audio download:** The completed job UI surfaces a working download link with the correct MIME type and `.mp3` extension.
- [PASS] **Blob Lifecycle:** Verification that transient blobs are dropped or properly configured with TTL to avoid leakage.

## 3. Documentation & Onboarding
- [PASS] **Docs page:** The `HELP.md` content is successfully embedded/rendered inside the SPA (`#view-docs`).
- [PASS] **Toolkit page:** Copy/paste CLI installation commands are accurate and highly visible.

## 4. Diagnostics & Deployment
- [PASS] **Diagnostics page:** The `#view-diagnostics` panel accurately reports `clips.json` counts and pings the `health` endpoint.
- [PASS] **Netlify deployment:** The `deploy_showcase.sh` script successfully builds the site, uploads the functions, and goes live without pathing errors.

---

**Conclusion:** V1 is structurally complete and deployed to production, but BLOCKED. Final approval depends entirely on physical device validation in `MOBILE_QA_PENDING.md`.
