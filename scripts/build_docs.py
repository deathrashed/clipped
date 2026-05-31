#!/usr/bin/env python3
import os
import subprocess

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HELP_MD = os.path.join(REPO_DIR, "docs", "HELP.md")
DOCS_OUT = os.path.join(REPO_DIR, "showcase", "docs.html")

def build_docs():
    print("==> Compiling HELP.md to HTML...")
    try:
        # Use npx marked to safely convert Markdown to HTML (zero-config, downloads temporarily if missing)
        result = subprocess.run(
            ["npx", "--yes", "marked", "-i", HELP_MD],
            capture_output=True, text=True, check=True
        )
        html_content = result.stdout
    except Exception as e:
        print(f"Warning: npx marked failed ({e}). Falling back to plain text.")
        with open(HELP_MD, 'r', encoding='utf-8') as f:
            html_content = f"<pre style='white-space: pre-wrap;'>{f.read()}</pre>"

    print(f"==> Writing to {DOCS_OUT}...")
    with open(DOCS_OUT, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("==> Docs build complete.")

if __name__ == "__main__":
    build_docs()
