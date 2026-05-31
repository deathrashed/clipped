Problem: Gemini partially wired things, but it didn’t finish the app layer.

What went wrong:

* The gallery is still inline, so the page feels huge and unfocused.
* The waveform area exists, but the audio-loading path is broken/incomplete.
* Platform buttons exist, but the selected platform is not reliably connected to render payload.
* Output format exists, but the generate function appears hardcoded to `format: 'video'`.
* The job panel exists, but it starts hidden and has no strong “running” state unless the request succeeds.
* The original working render pipeline from your previous site was stronger: it submitted `url`, `start`, `end`, `fade`, `format`, `template`, `platform`, then polled `clip-status` and exposed `clip-download`.
* Your sync script is injecting massive static cards directly into `index.html`, which is why the page becomes bloated instead of acting like separate pages/views.


# Gemini Fix Task

Do not redesign the visual style.

Refactor the current `showcase/public/index.html` into a small single-page app with route-like views:

- `#tool`
- `#showcase`
- `#library`
- `#smoke-tests`
- `#toolkit`

Only show one main view at a time. Do not render the full showcase inline under the tool.

## Critical fixes

1. Generate button must call the real Netlify flow:
   - `/.netlify/functions/clip-request`
   - poll `/.netlify/functions/clip-status?job=...`
   - download from `/.netlify/functions/clip-download?job=...`

2. Payload must include:
   - `url`
   - `start`
   - `end`
   - `fade`
   - `format`
   - `template`
   - `platform`

Do not hardcode `format: "video"`.

3. Platform chips must update global state:

```js
appState.platform = button.dataset.platform;
````

1. Format select must update render payload:

```js
format: document.getElementById("out-format").value
```

1. Source must resolve correctly:

   * My Clips: selected library URL
   * URL tab: typed URL
   * Upload: preview only, do not submit unless upload endpoint exists

2. Waveform must load from:

   * selected library audio
   * uploaded local audio
   * direct URL audio when CORS allows

3. Replace fake waveform with canvas waveform after audio loads.

4. Add visible job states:

   * idle
   * submitting
   * queued
   * downloading
   * rendering
   * finalizing
   * complete
   * error

5. Job panel must always show current state, not stay blank.

6. Showcase and library must be generated from `clips.json` dynamically, not injected as thousands of static cards into the page.

## sync_showcase.py change

Stop injecting full video/audio card HTML into `index.html`.

Keep generating only:

* `clips.json`
* `clips-list.js`
* audio dropdown options if needed

Remove or disable:

```py
content = inject(content, "<!-- INSERT_USER_VIDEOS_HERE -->", ...)
content = inject(content, "<!-- INSERT_USER_AUDIOS_HERE -->", ...)
```

The frontend should render galleries from `clips.json`.

## View system

Add CSS:

```css
.view { display:none; }
.view.active { display:block; }
```

Wrap sections:

```html
<section id="view-tool" class="view active">...</section>
<section id="view-showcase" class="view">...</section>
<section id="view-library" class="view">...</section>
<section id="view-smoke-tests" class="view">...</section>
<section id="view-toolkit" class="view">...</section>
```

Nav buttons should call:

```js
showView("tool")
showView("showcase")
showView("library")
showView("smoke-tests")
showView("toolkit")
```

## Render state

Create one global state object:

```js
const appState = {
  clips: [],
  selectedClip: null,
  sourceType: "library",
  sourceUrl: "",
  template: "reel",
  platform: "default",
  format: "video",
  audioBuffer: null,
  selectionStart: 0,
  selectionEnd: 30,
  fade: 0.3,
  jobId: null,
  jobStatus: "idle"
};
```

## Required render function

Use this exact structure:

```js
async function generateClip() {
  const url = getSourceUrl();

  if (!url) {
    showToast("Select a library clip or paste a URL first.", "var(--red)");
    return;
  }

  if (appState.sourceType === "upload") {
    showToast("Local uploads are preview-only until upload backend is added.", "var(--gold)");
    return;
  }

  const payload = {
    url,
    start: Number(appState.selectionStart || 0),
    end: Number(appState.selectionEnd || 30),
    fade: Number(document.getElementById("trim-fade").value || 0.3),
    format: document.getElementById("out-format").value,
    template: document.getElementById("out-format").value === "video" ? appState.template : null,
    platform: appState.platform
  };

  setJobState("submitting", 8);

  const res = await fetch("/.netlify/functions/clip-request", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await res.json();

  if (!res.ok) {
    setJobState("error", 100, data.error || "Request failed");
    return;
  }

  appState.jobId = data.jobId;
  setJobState("queued", 15, `job ${data.jobId.slice(0, 8)}`);
  pollJob(data.jobId, payload.format);
}
```

## Required poll function

```js
async function pollJob(jobId, format) {
  const timer = setInterval(async () => {
    const res = await fetch(`/.netlify/functions/clip-status?job=${jobId}`);
    const { status } = await res.json();

    const lower = String(status || "").toLowerCase();

    if (lower.includes("initializing")) setJobState("initializing", 20, status);
    else if (lower.includes("youtube") || lower.includes("download")) setJobState("downloading", 40, status);
    else if (lower.includes("rendering") || lower.includes("extracting audio clip")) setJobState("rendering", 70, status);
    else if (lower.includes("finalizing")) setJobState("finalizing", 90, status);
    else if (lower === "done") {
      clearInterval(timer);
      setJobState("complete", 100, "complete");
      showOutput(jobId, format);
    } else if (lower.includes("error") || lower.includes("failed")) {
      clearInterval(timer);
      setJobState("error", 100, status);
    } else {
      setJobState("running", 50, status);
    }
  }, 2500);
}
```

## Required output function

```js
function showOutput(jobId, format) {
  const url = `/.netlify/functions/clip-download?job=${jobId}`;
  const output = document.getElementById("job-output");

  output.style.display = "block";

  document.getElementById("download-link").href = url;

  const preview = document.getElementById("job-preview");
  preview.innerHTML = format === "audio"
    ? `<audio controls src="${url}"></audio>`
    : `<video controls playsinline src="${url}"></video>`;
}
```

Add this missing container:

```html
<div id="job-preview" class="output-preview"></div>
```

## Waveform fix

When a library clip is selected:

```js
audio.src = clip.filepath;
appState.sourceUrl = clip.filepath;
loadAudioForWaveform(clip.filepath);
```

Use:

```js
async function loadAudioForWaveform(url) {
  try {
    const res = await fetch(url);
    const buf = await res.arrayBuffer();
    const ctx = new AudioContext();
    appState.audioBuffer = await ctx.decodeAudioData(buf);
    appState.selectionStart = 0;
    appState.selectionEnd = Math.min(30, appState.audioBuffer.duration);
    drawWaveform();
    updateSelectionUI();
  } catch (err) {
    console.warn("Waveform unavailable", err);
    drawFallbackWaveform();
  }
}
```

## Separate pages

The nav must not scroll to huge inline sections. It must switch views.

Example:

```js
function showView(name) {
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.getElementById(`view-${name}`).classList.add("active");

  document.querySelectorAll(".nav-link").forEach(a => a.classList.remove("active"));
  document.querySelector(`[data-view="${name}"]`)?.classList.add("active");
}
```

## Acceptance test

After fixes:

* Selecting a library clip updates metadata and waveform.
* Platform chips visibly select and affect payload.
* Format dropdown affects payload.
* Generate button shows submitting immediately.
* Job lifecycle progress always updates.
* Completed job exposes download + media preview.
* Showcase is on its own view.
* Audio library is on its own view.
* Smoke tests are on their own view.
* Toolkit is on its own view.
* Page no longer contains thousands of injected card HTML.

