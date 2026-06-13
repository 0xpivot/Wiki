import sys
import textwrap

def wrap_markdown(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    in_code_block = False
    in_frontmatter = False
    for i, line in enumerate(lines):
        if i == 0 and line == '---':
            in_frontmatter = True
            new_lines.append(line)
            continue
        if in_frontmatter and line == '---':
            in_frontmatter = False
            new_lines.append(line)
            continue
            
        if in_frontmatter:
            new_lines.append(line)
            continue

        if line.startswith('```'):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue

        if in_code_block:
            new_lines.append(line)
            continue
            
        if line.startswith('#'):
            new_lines.append(line)
            continue
            
        if line.strip() == '':
            new_lines.append(line)
            continue
            
        if line.startswith('**Expert Answer:**'):
            new_lines.append(line)
            continue
            
        # wrap
        wrapped = textwrap.fill(line, width=76)
        for w_line in wrapped.split('\n'):
            new_lines.append(w_line)
            
    with open(file_path, 'w') as f:
        f.write('\n'.join(new_lines))

for f in sys.argv[1:]:
    wrap_markdown(f)
