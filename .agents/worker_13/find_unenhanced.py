#!/usr/bin/env python3
import os
import sys

# Add repo root to path so we can import verify_enhancement
REPO_ROOT = "/home/sanchit/Notes/VAPT"
sys.path.append(REPO_ROOT)

import verify_enhancement

def main():
    baseline_path = "/home/sanchit/.gemini/antigravity-cli/brain/77399aa3-cb2f-4b0e-8289-c2d532a5d414/file_stats.md"
    baseline = verify_enhancement.parse_baseline(baseline_path)
    
    # Scan all markdown files in REPO_ROOT (ignoring .agents, .git, .obsidian, and the excluded files listed in verify_enhancement.py)
    md_files = verify_enhancement.find_markdown_files(REPO_ROOT)
    
    unenhanced_files = []
    
    for abs_path, rel_path in md_files:
        baseline_size = baseline.get(rel_path)
        passed, reason = verify_enhancement.verify_file(abs_path, rel_path, baseline_size)
        if not passed:
            b_size = baseline_size if baseline_size is not None else 0
            unenhanced_files.append((b_size, rel_path, reason))

    # Sort these unenhanced files in ascending order of their baseline character counts.
    unenhanced_files.sort(key=lambda x: (x[0], x[1]))
    
    # Save the sorted list of unenhanced files to /home/sanchit/Notes/VAPT/unenhanced_files.txt
    output_path = "/home/sanchit/Notes/VAPT/unenhanced_files.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        for b_size, rel_path, reason in unenhanced_files:
            f.write(f"{b_size} | {rel_path}\n")
            
    print(f"Total count of unenhanced files found: {len(unenhanced_files)}")
    print("Top 20 smallest unenhanced files:")
    for b_size, rel_path, reason in unenhanced_files[:20]:
        print(f"{b_size} | {rel_path}")

if __name__ == "__main__":
    main()
