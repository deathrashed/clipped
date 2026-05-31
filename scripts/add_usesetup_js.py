import re

def main():
    with open("showcase/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    use_setup_js = """
<script>
// USE SETUP JAVASCRIPT
function useSetup(source, start, end, template) {
    // Switch to Main tab if not already active
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    document.querySelector('.tab-btn[data-target="tab-main"]').classList.add('active');
    document.getElementById('tab-main').classList.add('active');
    
    // Smooth scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Populate inputs
    const sourceEl = document.getElementById('sim-source');
    // Try to find matching value, or default to it
    let optionFound = false;
    for(let i=0; i<sourceEl.options.length; i++) {
        if(sourceEl.options[i].value.includes(source) || source.includes(sourceEl.options[i].value)) {
            sourceEl.value = sourceEl.options[i].value;
            optionFound = true;
            break;
        }
    }
    
    if (start) document.getElementById('sim-start').value = start;
    if (end) document.getElementById('sim-end').value = end;
    if (template) document.getElementById('sim-template').value = template;
    
    const logs = document.getElementById('terminal-logs');
    if(logs) {
        logs.innerHTML += `\\n<span style="color:#04d58f">[System]</span> Setup loaded. Ready to run simulation.`;
        logs.scrollTop = logs.scrollHeight;
    }
}
</script>
"""

    if 'USE SETUP JAVASCRIPT' not in html:
        html = html.replace('</body>', use_setup_js + '\n</body>')

    with open("showcase/index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
if __name__ == "__main__":
    main()
