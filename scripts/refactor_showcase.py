import re

def main():
    with open("showcase/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Wider container & Desktop layout prep
    html = html.replace('max-width: 1100px;', 'max-width: 1350px;')
    html = html.replace('max-width: 750px;', 'max-width: 1200px;')

    # 2. Ghostty terminal panel
    old_term_css = """    .terminal-panel {
      background: #1e1e1e;
      border: 1.5px solid #7f8c8d;
      border-radius: 8px;
      padding: 12px;
      display: flex;
      flex-direction: column;
      height: 380px;
      box-sizing: border-box;
      transition: border-color 0.2s;
    }

    .terminal-panel:hover {
      border-color: #1d99f3;
    }

    .terminal-header {
      display: flex;
      margin-bottom: 10px;
      border-bottom: 1px solid #414141;
      padding-bottom: 6px;
      align-items: center;
      justify-content: center;
    }

    .terminal-title {
      font-size: 12px;
      font-family: monospace;
      color: #eff0f1;
      font-weight: 600;
    }

    .terminal-logs {
      flex: 1;
      font-family: monospace;
      font-size: 12px;
      color: #e0e0e0;
      overflow-y: auto;
      white-space: pre-wrap;
      line-height: 1.4;
    }

    .terminal-prompt {
      color: #1d99f3;
      font-weight: bold;
    }"""
    
    new_term_css = """    .terminal-panel {
      background: #0d0f18; /* Ghostty minimalist dark */
      border: 1px solid #2a2a3a;
      border-radius: 8px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      height: 380px;
      box-sizing: border-box;
      box-shadow: inset 0px 0px 20px rgba(0,0,0,0.5);
      transition: border-color 0.2s;
    }

    .terminal-panel:hover {
      border-color: #4a4a5a;
    }

    .terminal-header {
      display: flex;
      margin-bottom: 10px;
      padding-bottom: 6px;
      align-items: center;
      justify-content: space-between;
    }

    .terminal-title {
      display: none;
    }

    .terminal-logs {
      flex: 1;
      font-family: "JetBrains Mono", "SF Mono", monospace;
      font-size: 13px;
      color: #babbce;
      overflow-y: auto;
      white-space: pre-wrap;
      line-height: 1.5;
    }

    .terminal-prompt {
      color: #953ebf;
      font-weight: 500;
    }"""
    
    if old_term_css in html:
        html = html.replace(old_term_css, new_term_css)
    else:
        print("WARNING: terminal CSS not found")

    # 3. Clean start/end values
    html = html.replace('value="2.41"', '')
    html = html.replace('value="3.06"', '')
    
    # 4. Replace terminal prompts
    html = html.replace('user@clipped ~$ ', '~ $ ')
    html = html.replace('riley@macbook', '~')
    html = html.replace('<span class="terminal-prompt">> </span>', '<span class="terminal-prompt">~ $ </span>')

    # 5. Fix Global CLI Installation paths
    html = html.replace('/Users/rd/Scripts/Riley/clipped/_video/${template}_${filename.replace(/\\.[^/.]+$/, "")}.mp4', './_video/${template}_${filename.replace(/\\.[^/.]+$/, "")}.mp4')
    
    with open("showcase/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Base UI fixes applied.")

if __name__ == "__main__":
    main()
