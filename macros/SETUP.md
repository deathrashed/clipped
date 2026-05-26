# Keyboard Maestro Macros for Clipped

Double-click `clipped.kmmacros` to import the main macro group.
Double-click `clipped-swinsian.kmmacros` to import the focused Swinsian selected-track dynamic reel macro.

---

## Macros

| Hotkey | Name | Action |
|--------|------|--------|
| `⌘⇧[` | **Mark Start** | Marks current Swinsian position as clip start. Shows a notification. |
| `⌘⇧]` | **Mark End + Clip** | Marks current position and immediately clips audio. |
| `⌘⇧V` | **Spinner Video (Last Clip)** | Generates a 1:1 spinner video from the most recent source or clipped audio. |
| `⌘⇧I` | **Instagram Reel (Last Clip)** | Generates a dynamic reel from the most recent source or clipped audio. |
| `⌘⇧U` | **Clip YouTube URL** | Reads a YouTube URL from the clipboard and opens a Terminal clip session. |
| User-assigned | **Utility: Clipped Dynamic Reel** | In the Swinsian group, prompts for start/end and renders the selected track with `reel` + `vertical_full`. |

---

## Prerequisites

1. [Keyboard Maestro](https://www.keyboardmaestro.com/) must be installed and running.
2. The `clipped` shim at `~/Scripts/Riley/clipped/bin/clipped` must be executable:
   ```bash
   chmod +x ~/Scripts/Riley/clipped/bin/clipped
   ```
3. Swinsian must be running for Swinsian-driven macros to work.

---

## Customising Hotkeys

After importing, open Keyboard Maestro Editor, find the "Clipped" macros, then click the trigger to change the hotkey.

---

## Adding More Macros

Prefer exporting a known-good macro from Keyboard Maestro and editing that plist, then validate it:

```bash
plutil -lint macros/*.kmmacros
```
