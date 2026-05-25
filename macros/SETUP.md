# Keyboard Maestro Macros for Clipped

Double-click `clipped.kmmacros` to import all macros at once.

---

## Macros

| Hotkey | Name | Action |
|--------|------|--------|
| `⌘⇧[` | **Mark Start** | Marks current Swinsian position as clip start. Shows a notification. |
| `⌘⇧]` | **Mark End + Clip** | Marks current position and immediately clips audio. |
| `⌘⇧V` | **Spinner Video (Last Clip)** | Generates a 1:1 spinner video from the most recent `_audio/` file. |
| `⌘⇧I` | **Instagram Reel (Last Clip)** | Generates a 9:16 vertical spinner reel from the most recent `_audio/` file. |
| `⌘⇧U` | **Clip YouTube URL** | Reads a YouTube URL from the clipboard and opens a Terminal clip session. |

---

## Prerequisites

1. [Keyboard Maestro](https://www.keyboardmaestro.com/) must be installed and running.
2. The `clipped` shim at `~/Scripts/Riley/clipped/bin/clipped` must be executable:
   ```bash
   chmod +x ~/Scripts/Riley/clipped/bin/clipped
   ```
3. Swinsian must be running for `⌘⇧[` and `⌘⇧]` to work.

---

## Customising Hotkeys

After importing, open Keyboard Maestro Editor → find the "Clipped" macros → click the trigger to change the hotkey.

---

## Adding More Macros

Copy one of the existing `<dict>` blocks in `clipped.kmmacros`, change:
- `<key>Name</key>` — display name
- `<key>UID</key>` — must be a unique string
- `<key>KeyCode</key>` — see [KM key codes](https://wiki.keyboardmaestro.com/action/Execute_a_Shell_Script)
- `<key>Script</key>` — the shell script to run
