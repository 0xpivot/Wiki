import os
import json
import re

base_dir = '/home/sanchit/Notes/VAPT/Tools and Real-World Scenarios'
output = {}

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.md'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Find all ```ascii or ```text blocks
            matches = re.finditer(r'```(ascii|text)\n(.*?)\n```', content, re.DOTALL)
            blocks = []
            for m in matches:
                blocks.append({
                    'lang': m.group(1),
                    'content': m.group(2),
                    'full_match': m.group(0)
                })
            
            if blocks:
                output[filepath] = blocks

with open('ascii_blocks.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"Found ascii blocks in {len(output)} files.")
