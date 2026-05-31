import re

def main():
    with open("showcase/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # The simulation JS
    simulation_js = """
<script>
// SIMULATOR JAVASCRIPT
document.addEventListener('DOMContentLoaded', () => {
    const runBtn = document.getElementById('run-btn');
    const logs = document.getElementById('terminal-logs');
    const progressBar = document.getElementById('progress-bar');
    const progressContainer = document.getElementById('progress-container');
    const previewWrapper = document.getElementById('preview-wrapper');
    const previewVideo = document.getElementById('preview-video');
    const previewTitle = document.getElementById('preview-title');

    function addLog(msg) {
        const time = new Date().toLocaleTimeString();
        logs.innerHTML += `\\n<span style="color:#a39c93">[${time}]</span> ${msg}`;
        logs.scrollTop = logs.scrollHeight;
    }

    runBtn.addEventListener('click', async () => {
        runBtn.disabled = true;
        runBtn.innerText = "Running...";
        progressContainer.style.display = 'block';
        progressBar.style.width = '10%';
        previewWrapper.style.display = 'none';
        previewVideo.src = '';
        
        let sourceVal = document.getElementById('sim-source').value;
        const start = document.getElementById('sim-start').value;
        const end = document.getElementById('sim-end').value;
        const template = document.getElementById('sim-template').value;
        
        let url = sourceVal;
        if (sourceVal === 'custom_url') {
            url = document.getElementById('sim-url').value;
        }

        // 1. Kick off request
        addLog(`Initiating render for source: ${url}`);
        addLog(`Time range: ${start} - ${end}`);
        addLog(`Template: ${template}`);
        
        try {
            const reqRes = await fetch('/.netlify/functions/clip-request', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, start, end, template, format: template ? 'video' : 'audio' })
            });
            
            if (!reqRes.ok) throw new Error("Failed to start job");
            
            const { jobId } = await reqRes.json();
            addLog(`Job ID assigned: ${jobId}`);
            progressBar.style.width = '30%';

            // 2. Poll for status
            let interval = setInterval(async () => {
                const statusRes = await fetch(`/.netlify/functions/clip-status?job=${jobId}`);
                if (!statusRes.ok) return;
                const { status } = await statusRes.json();
                
                addLog(`Status Update: ${status}`);
                
                if (status.includes('Extracting')) progressBar.style.width = '50%';
                if (status.includes('Rendering')) progressBar.style.width = '75%';
                if (status.includes('Finalizing')) progressBar.style.width = '90%';
                
                if (status === 'done' || status.includes('error')) {
                    clearInterval(interval);
                    runBtn.disabled = false;
                    runBtn.innerText = "Run Render Simulation";
                    progressBar.style.width = '100%';
                    
                    if (status === 'done') {
                        addLog(`Job completed successfully! Fetching generated media...`);
                        
                        // 3. Download the result
                        previewWrapper.style.display = 'flex';
                        previewTitle.innerText = `Generated: ${template || 'Audio Clip'}`;
                        
                        // Set preview source to the download endpoint
                        previewVideo.src = `/.netlify/functions/clip-download?job=${jobId}`;
                        previewVideo.play();
                    } else {
                        addLog(`\\n<span style="color:#ff3333">Error: ${status}</span>`);
                    }
                }
            }, 2000);

        } catch(err) {
            addLog(`\\n<span style="color:#ff3333">Network Error: ${err.message}</span>`);
            runBtn.disabled = false;
            runBtn.innerText = "Run Render Simulation";
            progressBar.style.width = '100%';
            progressBar.style.background = '#ff3333';
        }
    });
});
</script>
"""

    if 'SIMULATOR JAVASCRIPT' not in html:
        html = html.replace('</body>', simulation_js + '\n</body>')

    with open("showcase/index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
if __name__ == "__main__":
    main()
