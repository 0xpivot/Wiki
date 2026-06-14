import os
import sys

directory = '/home/sanchit/Notes/VAPT/Cloud and Container Security'
output_file = 'blocks_to_process.txt'

with open(output_file, 'w') as out:
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r') as f:
                        lines = f.readlines()
                except Exception as e:
                    continue
                
                in_block = False
                block_lines = []
                start_line = 0
                
                for i, line in enumerate(lines):
                    if line.strip().startswith('```text') or line.strip().startswith('```ascii'):
                        in_block = True
                        start_line = i + 1
                        block_lines = [line]
                    elif in_block and line.strip() == '```':
                        block_lines.append(line)
                        in_block = False
                        # check if it looks like a diagram
                        content = "".join(block_lines)
                        if '+' in content and '-' in content or '|' in content or '->' in content:
                            out.write(f"FILE: {path}\nSTART_LINE: {start_line}\nEND_LINE: {i+1}\n")
                            out.write(content)
                            out.write("\n---\n")
                    elif in_block:
                        block_lines.append(line)

print("Extraction complete.")
