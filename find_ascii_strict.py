import os
import re

def find_ascii_diagrams(directory):
    md_files = []
    for root, dirs, files in os.walk(directory):
        if '.git' in root or '.obsidian' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    
    diagram_files = {}
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            blocks = re.findall(r'```(?:text|ascii)?\n(.*?)```', content, re.DOTALL)
            for block in blocks:
                # Look for characteristic diagram patterns: boxes or arrows
                if re.search(r'\+--+\+', block) or re.search(r'-->', block) or re.search(r'<--', block) or re.search(r'┌─+┐', block):
                    if md_file not in diagram_files:
                        diagram_files[md_file] = []
                    diagram_files[md_file].append(block)
    
    total = 0
    for k, v in diagram_files.items():
        print(f"File: {k} has {len(v)} strict diagrams")
        total += len(v)
    print(f"Total strict diagrams: {total}")

find_ascii_diagrams('.')
