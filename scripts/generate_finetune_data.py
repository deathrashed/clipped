
import argparse
import json
import re
from pathlib import Path

DEFAULT_TEMPLATES_DIR = Path("clipped_src/templates")
DEFAULT_OUTPUT = Path("data/training/clipped_training_data.jsonl")


def extract_template_info(file_path: Path) -> dict[str, str]:
    content = Path(file_path).read_text()
    
    # Extract TemplateInfo
    info_match = re.search(r"info\s*=\s*TemplateInfo\((.*?)\)", content, re.DOTALL)
    info_text = info_match.group(1) if info_match else ""
    
    # Extract get_filter_graph implementation
    method_match = re.search(r"def get_filter_graph\(self,.*?\):\n(.*?)(?=\n\s*def|\n\s*class|$)", content, re.DOTALL)
    method_body = method_match.group(1) if method_match else ""
    
    return {
        "instruction": f"Implement the `get_filter_graph` method for the '{file_path.stem}' template in the Clipped media toolkit. Template Info: {info_text.strip()}",
        "output": f"def get_filter_graph(self, assets: MediaAssets, duration: float) -> str:\n{method_body.rstrip()}"
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate template fine-tuning JSONL data.")
    parser.add_argument("--templates-dir", type=Path, default=DEFAULT_TEMPLATES_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    dataset = []
    for f in args.templates_dir.glob("*.py"):
        if f.name in ["__init__.py", "registry.py", "base.py"]:
            continue
        try:
            item = extract_template_info(f)
            dataset.append(item)
        except Exception as e:
            print(f"Error processing {f}: {e}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as out:
        for entry in dataset:
            out.write(json.dumps(entry) + "\n")
    
    print(f"Successfully generated {len(dataset)} examples at {args.output}.")

if __name__ == "__main__":
    main()
