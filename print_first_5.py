import re
with open('diagram_files.txt', 'r') as f:
    files = [line.strip() for line in f.readlines()[:5]]

for file in files:
    with open(file, 'r', encoding='utf-8') as f2:
        content = f2.read()
        blocks = re.findall(r'```(?:text|ascii)?\n(.*?)```', content, re.DOTALL)
        for b in blocks:
            if re.search(r'\+--+\+', b) or re.search(r'-->', b) or re.search(r'<--', b) or re.search(r'┌─+┐', b):
                print(f"--- Diagram in {file} ---")
                print(b[:500])
                print("...")
