#!/usr/bin/env python3
import os
import sys
import re

# Baseline stats file path
DEFAULT_BASELINE_PATH = "/home/sanchit/.gemini/antigravity-cli/brain/77399aa3-cb2f-4b0e-8289-c2d532a5d414/file_stats.md"
DEFAULT_REPO_ROOT = "/home/sanchit/Notes/VAPT"

def parse_baseline(file_stats_path):
    baseline = {}
    if not os.path.exists(file_stats_path):
        print(f"Warning: Baseline stats file not found at {file_stats_path}")
        return baseline
        
    with open(file_stats_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    for line in content.split('\n'):
        if line.strip().startswith('|'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4:
                char_str = parts[1]
                file_rel_path = parts[2].strip('`').strip()
                if char_str.isdigit():
                    baseline[file_rel_path] = int(char_str)
    return baseline

def find_markdown_files(repo_root):
    ignored_folders = {'.agents', '.obsidian', '.git'}
    ignored_files = {
        'VAPT-Plan2-PortSwigger.md',
        'VAPT-Plan3-Expanded.md',
        'VAPT-Vault-Plan.md',
        'PROJECT.md'
    }
    md_files = []
    
    for root, dirs, files in os.walk(repo_root):
        # Exclude metadata folders in-place
        dirs[:] = [d for d in dirs if d not in ignored_folders]
        for file in files:
            if file.endswith('.md') and file not in ignored_files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, repo_root)
                md_files.append((abs_path, rel_path))
    return md_files

def get_section_content(content, header_regex):
    lines = content.split('\n')
    header_idx = -1
    header_level = 0
    pattern = re.compile(r'^(#+)\s+(.*)$')
    rx = re.compile(header_regex, re.IGNORECASE)
    
    for idx, line in enumerate(lines):
        m = pattern.match(line.strip())
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            if rx.search(title):
                header_level = level
                header_idx = idx
                break
                
    if header_idx == -1:
        return None
        
    section_lines = []
    for line in lines[header_idx + 1:]:
        m = pattern.match(line.strip())
        if m:
            next_level = len(m.group(1))
            if next_level <= header_level:
                break
        section_lines.append(line)
        
    return '\n'.join(section_lines)


def check_placeholders(content):
    patterns = [
        (r'\bTODO\b', "TODO"),
        (r'\bTBD\b', "TBD"),
        (r'lorem\s+ipsum', "Lorem Ipsum"),
        (r'\[insert[^\]]*\]', "[insert ...]"),
        (r'<insert[^>]*>', "<insert ...>"),
        (r'\[enter[^\]]*\]', "[enter ...]"),
        (r'<enter[^>]*>', "<enter ...>"),
        (r'\[placeholder[^\]]*\]', "[placeholder]"),
        (r'<placeholder[^>]*>', "<placeholder>"),
        (r'\bplaceholder\b', "placeholder"),
        (r'\bfill\s+here\b', "fill here"),
        (r'\bwrite\s+here\b', "write here"),
    ]
    for p, label in patterns:
        match = re.search(p, content, re.IGNORECASE)
        if match:
            return True, f"{label} (matched '{match.group(0)}')"
    return False, None

def verify_file(abs_path, rel_path, baseline_size):
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"Error reading file: {str(e)}"
        
    current_size = len(content)
    
    # 1. Check required sections presence and that they are not empty
    use_cases_content = get_section_content(content, r'(?:practical\s+)?use\s+cases')
    commands_content = get_section_content(content, r'(?:commands|command\s+list)')
    sample_output_content = get_section_content(content, r'sample\s+output')
    
    missing_sections = []
    if use_cases_content is None:
        missing_sections.append("Use Cases")
    elif len(re.sub(r'[^a-zA-Z0-9]', '', use_cases_content)) < 5:
        missing_sections.append("Use Cases (empty)")
        
    if commands_content is None:
        missing_sections.append("Commands")
    elif len(re.sub(r'[^a-zA-Z0-9]', '', commands_content)) < 5:
        missing_sections.append("Commands (empty)")
        
    if sample_output_content is None:
        missing_sections.append("Sample Output")
    elif len(re.sub(r'[^a-zA-Z0-9]', '', sample_output_content)) < 5:
        missing_sections.append("Sample Output (empty)")
        
    if missing_sections:
        return False, f"Missing required sections: {', '.join(missing_sections)}"
        
    # 2. Check size increase compared to baseline
    if baseline_size is not None:
        if current_size <= baseline_size:
            return False, f"Size not increased (current: {current_size}, baseline: {baseline_size})"
    else:
        # If not in baseline, count as size increased (it is a new file)
        pass
        
    # 3. Check for placeholders/template filler text
    has_placeholder, placeholder_detail = check_placeholders(content)
    if has_placeholder:
        return False, f"Contains template placeholder: {placeholder_detail}"
        
    return True, f"Success (size: {current_size}, baseline: {baseline_size if baseline_size is not None else 'N/A'})"

def main():
    repo_root = DEFAULT_REPO_ROOT
    baseline_path = DEFAULT_BASELINE_PATH
    
    if len(sys.argv) > 1:
        repo_root = sys.argv[1]
    if len(sys.argv) > 2:
        baseline_path = sys.argv[2]
        
    print(f"=== Starting VAPT Notes Enhancement Verification ===")
    print(f"Repository Root: {repo_root}")
    print(f"Baseline Path  : {baseline_path}\n")
    
    baseline = parse_baseline(baseline_path)
    md_files = find_markdown_files(repo_root)
    
    total_files = len(md_files)
    passed_count = 0
    failed_details = []
    
    print(f"Scanning {total_files} markdown files...\n")
    
    for abs_path, rel_path in sorted(md_files):
        baseline_size = baseline.get(rel_path)
        passed, reason = verify_file(abs_path, rel_path, baseline_size)
        if passed:
            passed_count += 1
        else:
            failed_details.append((rel_path, reason))
            
    print("=== Detailed Failure Log (First 50 failures shown) ===")
    for rel_path, reason in failed_details[:50]:
        print(f"FAIL: {rel_path} -> {reason}")
    if len(failed_details) > 50:
        print(f"... and {len(failed_details) - 50} more failures.")
        
    print("\n=== SUMMARY REPORT ===")
    print(f"Total markdown files found : {total_files}")
    print(f"Enhanced files (Passed)    : {passed_count}")
    print(f"Unenhanced files (Failed)  : {len(failed_details)}")
    
    pass_percentage = (passed_count / total_files * 100) if total_files > 0 else 0.0
    print(f"Percentage Enhanced        : {pass_percentage:.2f}%")
    print(f"Status                     : {'PASS' if passed_count == total_files else 'FAIL'}")
    
    # Exit with code 0 if all enhanced, or if we just ran successfully.
    # To indicate the overall repo status, we return 0 on success (all enhanced) or 1 if any unenhanced.
    # Since this is a verification script, returning non-zero on verification failures is standard.
    # However, let's return 0 when the script executes successfully but verification fails, or return 1.
    # Let's exit with 0 if all pass, 1 if any fail.
    sys.exit(0 if passed_count == total_files else 1)

if __name__ == '__main__':
    main()
