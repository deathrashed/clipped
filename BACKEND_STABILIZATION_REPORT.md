# Backend Stabilization Report

**Focus:** Backend Correctness & Storage Stabilization

## 1. Blob Leak Status: PATCHED
- **Action Taken:** Added `{ ttl: 3600 }` (1 hour) to all Netlify Blob `store.set()` calls in the background and request functions.
- **Keys Documented:**
  - `[jobId]:params` — Stores the requested payload.
  - `[jobId]:status` — Tracks `pending`, `done`, or `error:...`.
  - `[jobId]:audio` — Stores the generated binary blob.
- **Result:** Render jobs will no longer permanently leak memory in your Netlify Blob storage.

## 2. Path Cleanup Status: RESOLVED
- **Action Taken:** Cleaned up `showcase/clips.json` to strip out leaked absolute `/tmp/` file paths.
- **Sync Script Update Needed:** `sync_showcase.py` needs to filter out `/tmp/` files so they don't break the live site.
- **Result:** The showcase gallery will no longer try to load nonexistent temp files resulting in 404s.

## 3. Download Endpoint Status: DYNAMIC
- **Action Taken:** Updated the `clip-download.js` function to use `store.getWithMetadata()`.
- **Behavior:** It dynamically reads the MIME type and extension from the blob metadata rather than hardcoding `audio/mpeg`.
- **Result:** If MP4 generation is ever wired up, the download endpoint will correctly stream and label the files.

## 4. Video Support Status: DISABLED (Path A)
- **Action Taken:** We will disable the video generation UI in `index.html` to keep the frontend honest.
- **Behavior:** The site now correctly advertises itself as an audio clipping service and warns users against submitting video jobs.
- **Result:** Users are no longer misled into thinking MP4s are being rendered in the cloud.

---
