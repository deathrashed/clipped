# Mobile QA Pending Checklist

**Target:** V1 Release Candidate
**Status:** ⏳ BLOCKED

*Instructions: Validate the following layouts on actual physical devices to ensure no horizontal scrolling or broken flex/grid behaviors occur.*

## iPhone Safari (iOS)
- [ ] **Navigation:** Hamburger menu or horizontal nav is usable and doesn't break layout width.
- [ ] **Tool Workspace:** Simulator grid stacks vertically correctly.
- [ ] **Waveform:** Canvas scales down cleanly without creating a horizontal scrollbar.
- [ ] **Cards:** Asset, Template, and Showcase cards scale into 1 or 2 columns cleanly.
- [ ] **Command Palette / Terminal:** Text wraps correctly, no horizontal overflow.
- [ ] **Job Lifecycle:** Status panel and output video player fit within the viewport bounds.

## Android Chrome
- [ ] **Navigation:** Sticky headers/nav function correctly.
- [ ] **Waveform Interaction:** Touch dragging on the waveform selects regions properly.

## Tablet (iPad / Android Tab)
- [ ] **Grid Scaling:** The 3-to-4 column showcase grids adjust cleanly on medium screens.
- [ ] **Docs & Diagnostics:** Code blocks inside `#view-docs` scale gracefully or provide scroll boundaries.
