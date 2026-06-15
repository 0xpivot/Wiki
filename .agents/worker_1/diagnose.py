import socket
import os
import sys
import shutil

def probe_ports():
    ports = [11434, 8000, 8080, 8081, 9000, 5000, 8082, 8083]
    open_ports = []
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            result = s.connect_ex(('127.0.0.1', port))
            if result == 0:
                open_ports.append(port)
    return open_ports

def get_running_processes():
    processes = []
    # Read /proc to get processes on Linux without external dependencies
    if not os.path.exists('/proc'):
        return ["/proc not available"]
    
    keywords = ['ollama', 'vllm', 'llama', 'python', 'model', 'server', 'runner']
    for pid_dir in os.listdir('/proc'):
        if pid_dir.isdigit():
            try:
                cmdline_path = os.path.join('/proc', pid_dir, 'cmdline')
                if os.path.exists(cmdline_path):
                    with open(cmdline_path, 'rb') as f:
                        content = f.read().replace(b'\x00', b' ').decode('utf-8', errors='ignore').strip()
                        if content:
                            # Check if any keyword matches
                            if any(kw in content.lower() for kw in keywords):
                                processes.append(f"PID {pid_dir}: {content}")
            except Exception:
                continue
    return processes

def get_python_packages():
    packages = []
    try:
        # Python 3.8+
        import importlib.metadata
        dists = importlib.metadata.distributions()
        for d in dists:
            packages.append(f"{d.metadata['Name']}=={d.version}")
    except Exception:
        try:
            import pkg_resources
            for d in pkg_resources.working_set:
                packages.append(f"{d.project_name}=={d.version}")
        except Exception as e:
            packages.append(f"Error listing packages: {str(e)}")
    return sorted(packages)

def check_cli_tools():
    tools = ['ollama', 'llama-cli', 'curl', 'wget', 'python3', 'python', 'pip', 'pip3']
    found = {}
    for tool in tools:
        path = shutil.which(tool)
        found[tool] = path if path else "Not found"
    return found

def main():
    report = []
    report.append("=== LOCAL ENVIRONMENT DIAGNOSTICS ===")
    
    report.append("\n--- Open Ports Probed ---")
    open_ports = probe_ports()
    if open_ports:
        report.append(f"Open ports: {open_ports}")
    else:
        report.append("No common LLM/server ports are open (probed: 11434, 8000, 8080, 8081, 9000, 5000, 8082, 8083)")
        
    report.append("\n--- Running Processes (matching LLM/python keywords) ---")
    procs = get_running_processes()
    if procs:
        report.extend(procs)
    else:
        report.append("No running processes matching keywords found.")
        
    report.append("\n--- CLI Tools ---")
    tools = check_cli_tools()
    for tool, path in tools.items():
        report.append(f"{tool}: {path}")
        
    report.append("\n--- Installed Python Packages ---")
    pkgs = get_python_packages()
    # Filter for interesting packages related to LLMs or text generation
    llm_related = ['openai', 'anthropic', 'transformers', 'torch', 'ollama', 'huggingface', 'langchain', 'llama-cpp', 'urllib', 'requests', 'aiohttp']
    interesting = []
    for pkg in pkgs:
        name = pkg.split('==')[0].lower()
        if any(r in name for r in llm_related):
            interesting.append(pkg)
            
    report.append("Interesting packages:")
    if interesting:
        report.extend(interesting)
    else:
        report.append("None found")
        
    report.append("\nAll packages:")
    report.extend(pkgs)
    
    output_path = '/home/sanchit/Notes/VAPT/.agents/worker_1/diagnose_output.txt'
    with open(output_path, 'w') as f:
        f.write('\n'.join(report))
    print(f"Diagnostics report written to {output_path}")

if __name__ == '__main__':
    main()
