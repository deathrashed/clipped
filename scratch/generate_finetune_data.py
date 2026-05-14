
import json
import os
import re
from pathlib import Path

TEMPLATES_DIR = "clipped_src/templates"

def extract_template_info(file_path):
    content = Path(file_path).read_text()
    
    # Extract TemplateInfo
    info_match = re.search(r"info\s*=\s*TemplateInfo\((.*?)\)", content, re.DOTALL)
    info_text = info_match.group(1) if info_match else ""
    
    # Extract get_filter_graph implementation
    method_match = re.search(r"def get_filter_graph\(self,.*?\):\n(.*?)(?=\n\s*def|\n\s*class|$)", content, re.DOTALL)
    method_body = method_match.group(1) if method_match else ""
    
    return {
        "instruction": f"Implement the `get_filter_graph` method for the '{Path(file_path).stem}' template in the Clipped media toolkit. Template Info: {info_text.strip()}",
        "output": f"def get_filter_graph(self, params: RenderParams) -> str:\n{method_body.rstrip()}"
    }

def main():
    dataset = []
    for f in Path(TEMPLATES_DIR).glob("*.py"):
        if f.name in ["__init__.py", "registry.py", "base.py"]:
            continue
        try:
            item = extract_template_info(f)
            dataset.append(item)
        except Exception as e:
            print(f"Error processing {f}: {e}")

    with open("clipped_training_data.jsonl", "w") as out:
        for entry in dataset:
            out.write(json.dumps(entry) + "\n")
    
    print(f"Successfully generated {len(dataset)} examples for fine-tuning.")

if __name__ == "__main__":
    main()
