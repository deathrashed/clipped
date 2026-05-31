import re

def main():
    with open("showcase/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Wrap the template tests in the Library tab
    tests_start_pattern = r'(<div class="main-heading" id="template-tests">)'
    
    library_tab_start = """
      </div> <!-- End Main Tab -->
      <div class="tab-content" id="tab-library">
"""
    html, n = re.subn(tests_start_pattern, library_tab_start + r'\1', html, count=1)
    print(f"Injected Library tab split: {n}")
    
    # Close the library tab before the builder or about
    builder_start_pattern = r'(<div class="main-heading" id="builder">)'
    html, n = re.subn(builder_start_pattern, "</div> <!-- End Library Tab -->\n" + r'\1', html, count=1)
    if n == 0:
        # Try about section
        about_start_pattern = r'(<div class="main-heading" id="about">)'
        html, n = re.subn(about_start_pattern, "</div> <!-- End Library Tab -->\n" + r'\1', html, count=1)
    print(f"Closed Library tab: {n}")

    # Fix audio collapsible ending
    # Right now, audio details doesn't close! We need to close it before library tab starts.
    # We can inject it right before `</div> <!-- End Main Tab -->`
    library_start_pattern = r'(</div> <!-- End Main Tab -->)'
    html, n = re.subn(library_start_pattern, r'</details>\n\1', html, count=1)
    print(f"Closed audio collapsible: {n}")

    with open("showcase/index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
if __name__ == "__main__":
    main()
