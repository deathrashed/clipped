# Netlify Isolation & Live Producer Transition Plan

## Objective
1. **Architectural Isolation**: Move all Netlify-specific code (frontend, backend functions, config) into the `showcase/` directory to keep the core `clipped` CLI repository clean and modular.
2. **Live Producer Transition**: Fix the "Network Error" and remove hardcoded simulations so the live Netlify site acts as a real clip producer for public users.
3. **URL Update**: Change all references from `riley-clipped-showcase.netlify.app` to `clipped-showcase.netlify.app`.

## Phase 1: Architectural Reorganization
To prevent Netlify configuration from polluting the local CLI tool, we will isolate it entirely within the `showcase/` directory:
- Create a new folder structure: Move the current contents of `showcase/` into a new `showcase/public/` folder.
- Move `netlify.toml` into `showcase/netlify.toml`.
- Move the `netlify/` folder (containing `functions/` and `bin/`) into `showcase/netlify/`.
- Update `scripts/deploy_showcase.sh` and `scripts/build_showcase.sh` to target this new directory structure and use the new URL `https://clipped-showcase.netlify.app`.
- *Note: After this phase, you will need to update your Netlify Site Settings to set the "Base directory" to `showcase` and change the site name to `clipped-showcase`.*

## Phase 2: Frontend Refactoring (`showcase/public/index.html`)
- **Remove Hardcoded Simulation**: Delete the duplicated "Simulator Javascript" block that automatically plays the Juggaknots video after 6.7 seconds regardless of input.
- **Rename UI Elements**: Change buttons and text from "Run Render Simulation" to "Render Clip" to reflect the transition to a real producer.
- **URL Mapping**: Change the URL handling so that if a demo track (like Juggaknots) is selected, it maps to its absolute URL hosted on the live showcase site (e.g., `https://clipped-showcase.netlify.app/tests/audio-templates/...`) so the backend can download it.
- **Error Handling**: Update the API request logic to better handle and display errors, showing the actual backend error message instead of a generic "Network Error".

## Phase 3: Backend Fixes (`showcase/netlify/functions/`)
The current "Visual Simulator" fails because it sends keywords like `juggaknots` instead of real URLs to the backend, which rejects them with a 400 error.
- **`clip-request.js`**: Update validation to accept the hosted URL format for the demo tracks, not just YouTube URLs.
- **`clip-job-background.js`**: Add logic to handle standard HTTP/HTTPS file URLs (using `curl` or Node.js `fetch` to download the MP3) instead of relying exclusively on `yt-dlp` for everything.
- **Binary Limits**: Ensure the 50MB Netlify zipped Lambda limit isn't broken by the bundled `ffmpeg`/`yt-dlp` binaries. If they cause deployment failures, implement a fallback to download lightweight static builds on cold start.

## Verification
- Run a local test or trigger a Netlify deploy to ensure the new folder structure builds correctly.
- Verify that anyone visiting `https://clipped-showcase.netlify.app` can render a custom video using both YouTube URLs and built-in demo tracks without hitting the 400 Network Error, and that the UI displays the actual generated clip instead of the hardcoded simulation.