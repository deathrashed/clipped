import os

html_path = 'showcase/index.html'
if not os.path.exists(html_path):
    print(f"Error: {html_path} not found")
    exit(1)

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Capability Banner
banner = """
  <div class="capability-banner" style="background: var(--surface2, #1a1a1a); padding: 16px; border-radius: 8px; margin-bottom: 24px; display: flex; flex-direction: column; gap: 12px; border: 1px solid var(--border, #333);">
    <div style="font-size: 14px; color: var(--text, #fff);">
      <strong style="color: var(--green, #04d58f);">☁️ Cloud audio clipping is available.</strong><br>
      <span style="color: var(--gold, #f4a900);">Cloud video rendering is coming soon.</span> Use the local Clipped CLI for full FFmpeg/Remotion video generation.
    </div>
    <div style="display: flex; gap: 12px; flex-wrap: wrap;" class="banner-actions">
      <button class="btn btn-primary btn-sm" onclick="document.getElementById('sim-format').value='audio'; window.updateCLI && window.updateCLI();">Generate Audio Clip</button>
      <button class="btn btn-secondary btn-sm" onclick="window.showView && window.showView('toolkit')">Install CLI</button>
      <button class="btn btn-secondary btn-sm" onclick="window.showView && window.showView('showcase')">View Showcase</button>
    </div>
  </div>
"""
if "capability-banner" not in html:
    html = html.replace('<div class="simulator-grid">', banner + '\n  <div class="simulator-grid">')

# 2. Output Format Select
format_select = """
      <!-- Format -->
      <div class="form-group" style="margin-top: 16px;">
        <label for="sim-format">Output Format</label>
        <select id="sim-format" style="width: 100%; padding: 6px; border-radius: 4px; background: #2a2a2a; color: #fff; border: 1px solid #444;">
          <option value="audio">Audio Clip (MP3)</option>
          <option value="video" selected>Video (MP4) - Local CLI Only</option>
        </select>
      </div>
"""
if "id=\"sim-format\"" not in html:
    html = html.replace('<!-- Platform -->', format_select + '\n      <!-- Platform -->')

# 3. Inject JS for Polish (Mobile, Metadata, Toolkit, Run Logic)
js_injection = """
<!-- Productization Polish -->
<style>
  @media (max-width: 768px) {
    .app-shell { grid-template-columns: 1fr !important; }
    .sidebar { display: none; }
    .simulator-grid { grid-template-columns: 1fr !important; }
    .asset-gallery { grid-template-columns: 1fr !important; }
    .template-gallery { grid-template-columns: 1fr 1fr !important; }
    .capability-banner { flex-direction: column !important; }
    .banner-actions { flex-direction: column !important; }
    #job-preview video, #job-preview audio { width: 100% !important; height: auto !important; }
    .terminal-panel { position: sticky; bottom: 0; z-index: 10; max-height: 40vh; }
  }
  .cli-badge { font-size: 10px; color: var(--gold, #f4a900); opacity: 0.8; display: block; margin-top: 4px; }
  .view-state { padding: 40px; text-align: center; }
</style>
<script>
document.addEventListener("DOMContentLoaded", () => {
  // Debug Panel
  const urlParams = new URLSearchParams(window.location.search);
  const isDebug = urlParams.get('debug') === '1';
  document.querySelectorAll('.debug-panel, #debug-panel').forEach(p => {
    p.style.display = isDebug ? 'block' : 'none';
  });

  // Toolkit View
  if (!document.getElementById('view-toolkit')) {
    const toolkitHtml = `
      <section id="view-toolkit" class="view" style="display:none; padding: 20px; max-width: 800px; margin: 0 auto; color: var(--text, #fff);">
        <h2 style="color: var(--green, #04d58f); margin-bottom: 20px;">Clipped Toolkit</h2>
        <p>The Clipped CLI provides full FFmpeg and Remotion video generation locally.</p>

        <div style="background: var(--surface2, #1a1a1a); padding: 16px; border-radius: 8px; margin-bottom: 20px;">
          <h3 style="color: var(--gold, #f4a900); margin-bottom: 12px; font-size: 16px;">Quick Install</h3>
          <pre style="background: #000; padding: 12px; border-radius: 4px; overflow-x: auto; color: #e8e0d6; font-size: 13px;"><code>git clone https://github.com/deathrashed/clipped.git
cd clipped
./install.sh</code></pre>
        </div>

        <div style="background: var(--surface2, #1a1a1a); padding: 16px; border-radius: 8px; margin-bottom: 20px;">
          <h3 style="color: var(--gold, #f4a900); margin-bottom: 12px; font-size: 16px;">Core Commands</h3>
          <pre style="background: #000; padding: 12px; border-radius: 4px; overflow-x: auto; color: #e8e0d6; font-size: 13px;"><code>clipped doctor
clipped templates
clipped audio "track.mp3" 1:30 2:15
clipped video "track.mp3" --template reel --platform instagram</code></pre>
        </div>

        <div style="background: var(--surface2, #1a1a1a); padding: 16px; border-radius: 8px; margin-bottom: 20px;">
          <h3 style="color: var(--gold, #f4a900); margin-bottom: 12px; font-size: 16px;">Requirements & Troubleshooting</h3>
          <ul style="margin-left: 20px; line-height: 1.6;">
            <li>Python 3.10+ required for the CLI.</li>
            <li>Node.js 18+ required for Remotion templates.</li>
            <li>FFmpeg must be installed in your PATH.</li>
          </ul>
        </div>

        <a href="https://github.com/deathrashed/clipped" target="_blank" style="color: #fff; text-decoration: none; padding: 8px 16px; background: #333; border-radius: 4px; display: inline-block;">View on GitHub</a>
      </section>
    `;
    const container = document.querySelector('.main-workspace') || document.querySelector('.container') || document.body;
    container.insertAdjacentHTML('beforeend', toolkitHtml);
  }

  // Label templates "Local CLI Only"
  document.querySelectorAll('.template-card-title').forEach(el => {
    if (!el.querySelector('.cli-badge')) {
      el.insertAdjacentHTML('beforeend', '<span class="cli-badge">Local CLI Only</span>');
    }
  });

  // Empty/Loading states
  ['view-showcase', 'view-library', 'view-smoke-tests'].forEach(id => {
    const el = document.getElementById(id);
    if (el && !el.querySelector('.view-state')) {
      el.insertAdjacentHTML('afterbegin', `
        <div class="view-state loading-state" style="color:var(--muted, #888);">Loading...</div>
        <div class="view-state empty-state" style="display:none; color:var(--muted, #888);">No items found.</div>
        <div class="view-state error-state" style="display:none; color:var(--red, #f56);">Failed to load data.</div>
      `);
      setTimeout(() => {
        const loading = el.querySelector('.loading-state');
        if (loading) loading.style.display = 'none';
        if (el.children.length <= 3) {
          const empty = el.querySelector('.empty-state');
          if (empty) empty.style.display = 'block';
        }
      }, 1000);
    }
  });

  // Metadata Polish
  setInterval(() => {
    if (typeof userClips === 'undefined') return;
    document.querySelectorAll('.showcase-card, .video-card, .audio-card').forEach(card => {
      if (card.dataset.polished) return;
      const titleEl = card.querySelector('.title') || card.querySelector('h3') || card.querySelector('.template-card-title');
      if (!titleEl) return;
      const clip = userClips.find(c => titleEl.textContent.includes(c.title || c.filename));
      if (clip) {
        const metaDiv = document.createElement('div');
        metaDiv.style.cssText = 'display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; font-size: 10px; color: var(--muted, #888);';
        const tags = [clip.engine, clip.aspect, clip.template, clip.platform];
        if (clip.clip_start && clip.clip_end) tags.push(`${clip.clip_start} - ${clip.clip_end}`);
        metaDiv.innerHTML = tags.filter(Boolean).map(t => `<span style="background: var(--surface, #111); padding: 2px 6px; border-radius: 4px; border: 1px solid var(--border, #333);">${t}</span>`).join('');
        card.appendChild(metaDiv);
        card.dataset.polished = 'true';
      }
    });
  }, 1000);

  // Update CLI logic override
  const originalUpdateCLI = window.updateCLI;
  window.updateCLI = function() {
    if (originalUpdateCLI) originalUpdateCLI();
    const format = document.getElementById('sim-format')?.value || 'video';
    const runBtn = document.getElementById('run-btn');
    if (runBtn) {
      if (format === 'video') {
        runBtn.disabled = true;
        runBtn.textContent = "Cloud MP4 rendering is not available yet. Use the Clipped CLI locally.";
      } else {
        runBtn.disabled = false;
        runBtn.textContent = "Generate Audio Clip";
      }
    }
  };
  window.updateCLI();

  // Override Run Button
  const runBtn = document.getElementById('run-btn');
  if (runBtn) {
    const newBtn = runBtn.cloneNode(true);
    runBtn.parentNode.replaceChild(newBtn, runBtn);
    newBtn.addEventListener('click', () => {
      const format = document.getElementById('sim-format')?.value || 'audio';
      if (format === 'video') return;

      const sourceVal = document.getElementById('sim-source').value;
      let url = sourceVal;
      if (sourceVal === 'custom_url') url = document.getElementById('sim-url').value;
      else if (sourceVal === 'local_path') url = document.getElementById('sim-audio-path').value;
      else if (sourceVal === 'juggaknots') url = 'https://www.youtube.com/watch?v=ba7mB8oueCY';
      else if (sourceVal === 'suicideboys') url = 'https://www.youtube.com/watch?v=OtuVJtgSZfA';
      else if (sourceVal === 'stabwounds') url = 'https://www.youtube.com/watch?v=W_iXb-jT70U';

      const payload = {
        url,
        start: document.getElementById('sim-start').value || 0,
        end: document.getElementById('sim-end').value || 30,
        format: 'audio',
        platform: document.getElementById('sim-platform')?.value || 'default'
      };

      const terminalLogs = document.querySelector('.terminal-logs') || document.querySelector('.terminal-body');
      if (terminalLogs) terminalLogs.innerHTML = `<span class="terminal-prompt">> </span><span style="color:var(--green, #04d58f)">Submitting job to cloud...</span>\\n`;

      fetch('/.netlify/functions/clip-request', {
        method: 'POST',
        body: JSON.stringify(payload),
        headers: { 'Content-Type': 'application/json' }
      }).then(res => res.json()).then(data => {
        if (data.error) throw new Error(data.error);
        if (terminalLogs) terminalLogs.innerHTML += `[cloud] Job created: ${data.jobId}\\n[cloud] Processing...\\n`;
        const poll = setInterval(() => {
          fetch(`/.netlify/functions/clip-status?job=${data.jobId}`).then(r=>r.json()).then(sData => {
            if (terminalLogs) terminalLogs.innerHTML += `[cloud] Status: ${sData.status}\\n`;
            if (sData.status === 'done') {
              clearInterval(poll);
              const dlUrl = `/.netlify/functions/clip-download?job=${data.jobId}`;
              if (terminalLogs) terminalLogs.innerHTML += `\\n<span style="color:var(--green, #04d58f)">Success!</span> <a href="${dlUrl}" style="color:var(--gold, #f4a900)" download>Download MP3</a>\\n`;
            } else if (sData.status.startsWith('error')) {
              clearInterval(poll);
              if (terminalLogs) terminalLogs.innerHTML += `\\n<span style="color:var(--red, #f56)">Failed.</span>\\n`;
            }
            if (terminalLogs) terminalLogs.scrollTop = terminalLogs.scrollHeight;
          });
        }, 2000);
      }).catch(err => {
        if (terminalLogs) terminalLogs.innerHTML += `<span style="color:var(--red, #f56)">Error: ${err.message}</span>\\n`;
      });
    });
  }
});
</script>
"""
if "Productization Polish" not in html:
    html = html.replace('</body>', js_injection + '\n</body>')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Applied productization and polish to showcase/index.html")
