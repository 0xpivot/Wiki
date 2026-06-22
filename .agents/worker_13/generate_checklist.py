import os
import re

stats_file = "/home/sanchit/.gemini/antigravity-cli/brain/77399aa3-cb2f-4b0e-8289-c2d532a5d414/file_stats.md"
repo_dir = "/home/sanchit/Notes/VAPT"

# 1. Identify all markdown files in the repository
repo_md_files = []
for root, dirs, files in os.walk(repo_dir):
    # Exclude metadata and configuration directories
    if '.git' in root or '.agents' in root or '.gemini' in root:
        continue
    for file in files:
        if file.endswith('.md') and not file == 'PROJECT.md' and not file == 'README.md':
            rel_path = os.path.relpath(os.path.join(root, file), repo_dir)
            repo_md_files.append(rel_path)

print(f"Found {len(repo_md_files)} markdown files in repo.")

# 10 pilot files to exclude
pilot_files = {
    "Command and Control Operations/I - 94 - Command and Control Foundations and Architectures/16 - Havoc C2 Framework.md",
    "Web Application Security/B - 03 - HTTP Headers/05 - X-Real-IP.md",
    "Web Application Security/B - 03 - HTTP Headers/49 - Pragma.md",
    "Web Application Security/B - 03 - HTTP Headers/07 - X-Rewrite-URL.md",
    "Web Application Security/B - 03 - HTTP Headers/23 - X-Method-Override.md",
    "Web Application Security/B - 03 - HTTP Headers/09 - X-Remote-IP and X-Remote-Addr.md",
    "Web Application Security/B - 03 - HTTP Headers/06 - X-Original-URL.md",
    "Web Application Security/B - 03 - HTTP Headers/04 - X-Forwarded-Proto.md",
    "Web Application Security/B - 03 - HTTP Headers/50 - Expires.md",
    "Web Application Security/B - 03 - HTTP Headers/08 - X-Custom-IP-Authorization.md"
}

# 2. Parse file_stats.md for sizes
file_sizes = {}
with open(stats_file, 'r', encoding='utf-8') as f:
    for line in f:
        # Match format like: | 224 | `path` |
        match = re.match(r'\|\s*(\d+)\s*\|\s*`([^`]+)`', line.strip())
        if match:
            chars = int(match.group(1))
            path = match.group(2)
            file_sizes[path] = chars

# 3. Filter and sort
remaining_repo_md = [f for f in repo_md_files if f not in pilot_files]

# Verify if any are missing from file_stats.md
missing = [f for f in remaining_repo_md if f not in file_sizes]
if missing:
    print(f"Warning: {len(missing)} repo files missing from file_stats.md: {missing}")

# Sort remaining_repo_md based on size in file_sizes.
remaining_repo_md.sort(key=lambda x: file_sizes.get(x, 999999999))

# Write to remaining_files.txt
out_dir = "/home/sanchit/Notes/VAPT/.agents/orchestrator"
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "remaining_files.txt")
with open(out_file, 'w', encoding='utf-8') as f:
    for path in remaining_repo_md:
        f.write(path + '\n')

print(f"Wrote {len(remaining_repo_md)} sorted files to {out_file}")
