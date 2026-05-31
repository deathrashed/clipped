#!/usr/bin/env python3
"""Generate per-template props JSON for frame sheet rendering."""
import json, sys

template_path = sys.argv[1]
comp_id = sys.argv[2]
template_id = sys.argv[3]
width = int(sys.argv[4])
height = int(sys.argv[5])

with open(template_path) as f:
    p = json.load(f)

p["compositionId"] = comp_id
p["templateId"] = template_id
p["width"] = width
p["height"] = height

print(json.dumps(p))
