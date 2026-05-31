import re

def main():
    with open("showcase/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. ADD CSS FOR SIDEBAR & TEMPLATE GALLERY
    sidebar_css = """
    /* ==== APP LAYOUT (SIDEBAR + MAIN) ==== */
    .app-layout {
      display: flex;
      gap: 30px;
      max-width: 1500px;
      margin: 0 auto;
    }

    .app-sidebar {
      width: 260px;
      flex-shrink: 0;
      position: sticky;
      top: 20px;
      height: max-content;
      padding: 10px 0;
    }

    .app-sidebar .btn-container {
      flex-direction: column;
      gap: 8px;
    }

    .app-sidebar .btn-link {
      width: 100%;
      justify-content: flex-start;
      padding: 10px 14px;
    }

    .app-main {
      flex: 1;
      min-width: 0;
    }

    /* ==== VISUAL TEMPLATE GALLERY ==== */
    .template-picker-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
      gap: 12px;
      margin-bottom: 12px;
    }

    .template-card {
      background: #1a1a24;
      border: 1.5px solid #2a2a3a;
      border-radius: 8px;
      padding: 10px;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
    }

    .template-card:hover {
      border-color: #953ebf;
      background: #231b2e;
    }

    .template-card.active {
      border-color: #04d58f;
      background: rgba(4, 213, 143, 0.1);
    }

    .template-icon {
      width: 40px;
      height: 40px;
      background: #2a2a3a;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
    }

    .template-card.active .template-icon {
      background: rgba(4, 213, 143, 0.2);
    }

    .template-name {
      font-size: 11px;
      color: #e0e0e0;
      font-weight: 600;
    }

    @media (max-width: 900px) {
      .app-layout {
        flex-direction: column;
        gap: 15px;
      }
      .app-sidebar {
        width: 100%;
        position: static;
      }
      .app-sidebar .btn-container {
        flex-direction: row;
      }
    }
    """
    
    html = html.replace('/* ==== MOBILE OPTIMISATIONS ==== */', sidebar_css + '\n  /* ==== MOBILE OPTIMISATIONS ==== */')

    # 2. RESTRUCTURE HTML TO WRAP SIDEBAR
    
    # We want to extract `.header` and `.btn-container` and put them in `.app-sidebar`
    # and wrap everything else in `.app-main`.
    
    # Let's find the main <div class="container"> start and end
    # Actually, the user has:
    # <body>
    #   <div class="container">
    #     <div class="header">...</div>
    #     <div class="btn-container">...</div>
    #     <!-- SECTION 1 ... -->
    
    # We can replace body content using regex
    
    # Find header block
    header_match = re.search(r'(<div class="header">.*?</div>\n)', html, re.DOTALL)
    if not header_match: print("Header not found")
    header_html = header_match.group(1) if header_match else ""
    
    # Find btn-container block
    btn_match = re.search(r'(<div class="btn-container">.*?</div>\n)', html, re.DOTALL)
    btn_html = btn_match.group(1) if btn_match else ""
    
    # Remove header and btn-container from original container
    html = html.replace(header_html, '')
    html = html.replace(btn_html, '')
    
    # Inject the app-layout wrapper
    wrapper_open = f"""<div class="app-layout">
  <div class="app-sidebar">
    {header_html}
    {btn_html}
  </div>
  <div class="app-main">
"""
    wrapper_close = "\n  </div>\n</div>\n"
    
    html = html.replace('<div class="container">', wrapper_open + '    <div class="container">')
    html = html.replace('</body>', wrapper_close + '</body>')


    # 3. CONVERT DROPDOWN TEMPLATE PICKER TO VISUAL PICKER
    
    old_template_select = """          <div class="form-group">
            <label>Template</label>
            <select id="sim-template">
              <option value="pulse_reel">pulse_reel (Remotion)</option>
              <option value="gallery_square">gallery_square (Remotion)</option>
              <option value="record_square">record_square (Remotion)</option>
              <option value="fluid_scene">fluid_scene (Remotion)</option>
              <option value="metal_vhs">metal_vhs (Remotion)</option>
              <option value="premium_card">premium_card (Remotion)</option>
              <option value="reel">reel (FFmpeg)</option>
              <option value="vertical_wave">vertical_wave (FFmpeg)</option>
            </select>
          </div>"""
          
    new_template_picker = """          <div class="form-group">
            <label>Template</label>
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
              
              cards.forEach(card => {
                card.addEventListener('click', () => {
                  cards.forEach(c => c.classList.remove('active'));
                  card.classList.add('active');
                  hiddenInput.value = card.getAttribute('data-value');
                  
                  // Also trigger the change event if needed
                  hiddenInput.dispatchEvent(new Event('change'));
                });
              });
            });
          </script>"""
          
    if old_template_select in html:
        html = html.replace(old_template_select, new_template_picker)
    else:
        print("WARNING: template select not found for replacement!")

    with open("showcase/index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print("Layout and Visual Picker applied successfully.")

if __name__ == "__main__":
    main()
