import os
import shutil
import subprocess
import sys

output_file = "/home/sanchit/Notes/VAPT/.agents/worker_5/cli_check_output.txt"
lines = []

def log(msg):
    print(msg)
    lines.append(msg + "\n")

log("=== CLI and LLM Executable Scan ===")

# 1. Check commands in PATH
commands = ['antigravity', 'antigravity-cli', 'gemini', 'gemini-cli', 'agent', 'agent-cli']
found_commands = {}

log("\n--- Checking System PATH for Target CLIs ---")
for cmd in commands:
    path = shutil.which(cmd)
    if path:
        log(f"FOUND in PATH: {cmd} -> {path}")
        found_commands[cmd] = path
    else:
        log(f"NOT FOUND in PATH: {cmd}")

# Also try running 'which' or 'type' just in case
for cmd in commands:
    if cmd not in found_commands:
        try:
            res = subprocess.run(['which', cmd], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                path = res.stdout.strip()
                log(f"FOUND via which: {cmd} -> {path}")
                found_commands[cmd] = path
        except Exception:
            pass

# 2. Run --help or -h for found commands
log("\n--- Running --help and -h for Found CLIs ---")
for cmd, path in found_commands.items():
    for flag in ['--help', '-h']:
        log(f"\nRunning: {cmd} {flag}")
        try:
            res = subprocess.run([cmd, flag], capture_output=True, text=True, timeout=10)
            log(f"Return Code: {res.returncode}")
            log("STDOUT:")
            log(res.stdout)
            log("STDERR:")
            log(res.stderr)
        except Exception as e:
            log(f"Error running {cmd} {flag}: {e}")

# 3. Check for binary files or executables in /home/sanchit/ or system that could run LLMs
log("\n--- Scanning /home/sanchit/ and System for LLM Executables/Binaries ---")

home_dir = "/home/sanchit"
log(f"Scanning directory: {home_dir}")
visited_count = 0
found_binaries = []

# To avoid infinite recursion or running into permission issues, let's limit walk to depth 4
# and limit total files scanned to 15000.
max_depth = 4
max_files = 15000

def get_depth(path, base_path):
    return path.count(os.sep) - base_path.count(os.sep)

try:
    for root, dirs, files in os.walk(home_dir):
        # Filter directories to avoid huge standard ones
        dirs[:] = [d for d in dirs if d not in ['.cache', '.git', '.rustup', '.cargo', '.npm', '.node_modules', '.local', '.vscode', '.idea']]
        
        # Check depth
        depth = get_depth(root, home_dir)
        if depth > max_depth:
            dirs[:] = []  # Don't go deeper
            continue
            
        for file in files:
            visited_count += 1
            if visited_count > max_files:
                log(f"Reached max file limit ({max_files}). Stopping walk.")
                break
                
            file_path = os.path.join(root, file)
            lower_name = file.lower()
            is_relevant_name = any(kw in lower_name for kw in ['llm', 'gemini', 'antigravity', 'agent', 'completion'])
            
            try:
                # Check if it is a symlink first
                if os.path.islink(file_path):
                    continue
                # Check if executable
                is_exec = os.access(file_path, os.X_OK) and not os.path.isdir(file_path)
                
                if is_relevant_name or is_exec:
                    # Check first few bytes for ELF magic number
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        try:
                            with open(file_path, 'rb') as f:
                                magic = f.read(4)
                                is_elf = (magic == b'\x7fELF')
                            
                            if is_elf:
                                log(f"Found ELF Binary: {file_path} (Name match: {is_relevant_name})")
                                found_binaries.append((file_path, "ELF Binary"))
                            elif is_exec:
                                # Read first line to check shebang
                                try:
                                    with open(file_path, 'r', errors='ignore') as f:
                                        first_line = f.readline().strip()
                                    if first_line.startswith("#!"):
                                        log(f"Found Executable Script: {file_path} (Shebang: {first_line})")
                                        found_binaries.append((file_path, f"Script ({first_line})"))
                                    else:
                                        log(f"Found Executable: {file_path}")
                                        found_binaries.append((file_path, "Executable"))
                                except Exception:
                                    log(f"Found Executable: {file_path} (Could not read shebang)")
                                    found_binaries.append((file_path, "Executable"))
                            elif is_relevant_name:
                                size = os.path.getsize(file_path)
                                # Only report if it's not a huge media/log file, or if it's text
                                if size < 1024 * 1024:  # under 1MB
                                    log(f"Found Relevant File: {file_path} (Size: {size} bytes)")
                                    found_binaries.append((file_path, f"Relevant File (size={size})"))
                        except Exception:
                            pass
            except Exception:
                pass
        if visited_count > max_files:
            break
except Exception as e:
    log(f"Error during os.walk of {home_dir}: {e}")

log(f"Scan complete. Visited {visited_count} files in {home_dir}.")

# Also check system paths like /usr/bin, /usr/local/bin, /opt for antigravity/gemini/agent files
system_paths = ['/usr/bin', '/usr/local/bin', '/opt']
log("\n--- Checking specific system paths for target keywords ---")
for sp in system_paths:
    if os.path.exists(sp):
        log(f"Checking system path: {sp}")
        try:
            for item in os.listdir(sp):
                if any(kw in item.lower() for kw in ['antigravity', 'gemini', 'agent']):
                    item_path = os.path.join(sp, item)
                    log(f"Found system item: {item_path}")
        except Exception as e:
            log(f"Error checking system path {sp}: {e}")

# Write output to file
with open(output_file, 'w') as f:
    f.writelines(lines)
print(f"Results written to {output_file}")
