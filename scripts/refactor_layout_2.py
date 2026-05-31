import re

def main():
    with open("showcase/index.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    old_template_select_pattern = r'<div class="form-group">\s*<label for="sim-template">Video Template</label>\s*<select id="sim-template">.*?</select>\s*</div>'
          
    new_template_picker = """      <div class="form-group">
        <label>Video Template</label>
        <div class="template-picker-grid" id="sim-template-grid">
          <div class="template-card active" data-value="pulse_reel">
            <div class="template-icon">🌊</div>
            <div class="template-name">Pulse Reel</div>
          </div>
          <div class="template-card" data-value="gallery_square">
            <div class="template-icon">🖼️</div>
            <div class="template-name">Gallery Square</div>
          </div>
          <div class="template-card" data-value="record_square">
            <div class="template-icon">💿</div>
            <div class="template-name">Record Square</div>
          </div>
          <div class="template-card" data-value="fluid_scene">
            <div class="template-icon">💧</div>
            <div class="template-name">Fluid Scene</div>
          </div>
          <div class="template-card" data-value="metal_vhs">
            <div class="template-icon">📼</div>
            <div class="template-name">Metal VHS</div>
          </div>
          <div class="template-card" data-value="premium_card">
            <div class="template-icon">✨</div>
            <div class="template-name">Premium Card</div>
          </div>
          <div class="template-card" data-value="reel">
            <div class="template-icon">📱</div>
            <div class="template-name">Classic Reel</div>
          </div>
          <div class="template-card" data-value="vertical_wave">
            <div class="template-icon">〰️</div>
            <div class="template-name">Vertical Wave</div>
          </div>
        </div>
        <input type="hidden" id="sim-template" value="pulse_reel">
      </div>
      
      <script>
        // Setup Visual Template Picker
        document.addEventListener('DOMContentLoaded', () => {
          const cards = document.querySelectorAll('.template-card');
          const hiddenInput = document.getElementById('sim-template');
          
          if(cards.length > 0) {
            cards.forEach(card => {
              card.addEventListener('click', () => {
                cards.forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                hiddenInput.value = card.getAttribute('data-value');
              });
            });
          }
        });
      </script>"""
          
    html, count = re.subn(old_template_select_pattern, new_template_picker, html, flags=re.DOTALL)
    if count > 0:
        print("Visual Picker applied successfully.")
    else:
        print("WARNING: template select pattern not found!")

    with open("showcase/index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
if __name__ == "__main__":
    main()
