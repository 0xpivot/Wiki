import os
import re

md_files = []
for root, dirs, files in os.walk('.'):
    if '.git' in root or '.obsidian' in root:
        continue
    for file in files:
        if file.endswith('.md'):
            md_files.append(os.path.join(root, file))

files_with_diagrams = []
for md_file in md_files:
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
        blocks = re.findall(r'```(?:text|ascii)?\n(.*?)```', content, re.DOTALL)
        for block in blocks:
            if re.search(r'\+--+\+', block) or re.search(r'-->', block) or re.search(r'<--', block) or re.search(r'┌─+┐', block):
                files_with_diagrams.append(md_file)
                break

with open('diagram_files.txt', 'w') as f:
    for f_name in files_with_diagrams:
        f.write(f_name + '\n')

print(f"Total files with diagrams: {len(files_with_diagrams)}")
