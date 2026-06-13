---
tags: [threat-hunting, endpoint, windows, sysmon, vapt]
difficulty: intermediate
module: "89 - Endpoint Threat Hunting: Windows, Sysmon, EDR"
topic: "89.15 MacOS and Linux Endpoint Hunting Basics"
---

# 89.15 MacOS and Linux Endpoint Hunting Basics

## Introduction to Non-Windows Endpoint Hunting

While Windows dominates corporate enterprise environments, macOS is increasingly ubiquitous among developers and executives, and Linux remains the undisputed king of cloud infrastructure and server environments. Threat actors adapt to these architectures. As a result, threat hunters cannot rely solely on Windows-centric tools like Sysmon and the Windows Registry; they must master the disparate logging mechanisms and execution environments of POSIX-compliant systems.

Hunting on macOS and Linux requires fundamentally different approaches due to their differing kernel architectures, user-mode constructs, and telemetry frameworks. While the goals remain the same—identifying anomalous process execution, unauthorized network connections, and hidden persistence mechanisms—the artifacts are entirely different.

## Linux Telemetry and Hunting

Linux logging historically relied on unstandardized text files scattered across `/var/log` (syslog, auth.log). While these remain important, modern Linux threat hunting relies on deeper kernel-level visibility.

### 1. Auditd (The Traditional Standard)
The Linux Audit subsystem (`auditd`) is the traditional mechanism for security monitoring. It hooks directly into the kernel to monitor system calls (syscalls), file access, and process execution.
- **Rules:** Administrators define rules in `/etc/audit/audit.rules` instructing the kernel what to log. For example, logging all executions of `/bin/sh` or any modifications to `/etc/passwd`.
- **Limitations:** Auditd is notorious for its severe performance overhead. Complex rule sets can drastically slow down high-throughput servers. Additionally, it is vulnerable to bypasses if an attacker gains root and unloads the rules.

### 2. eBPF (The Modern Standard)
Extended Berkeley Packet Filter (eBPF) has revolutionized Linux observability and security. Unlike auditd, which relies on static kernel hooks, eBPF allows security tools to run sandboxed programs dynamically inside the operating system kernel.
- **How it works:** An eBPF program is compiled to bytecode and injected into the kernel. The kernel verifies the code is safe (won't crash the system) and attaches it to specific kernel functions, tracepoints, or network events.
- **Advantage:** It is highly performant and incredibly granular. Modern Linux EDRs and hunting tools (like Cilium Tetragon or Falco) use eBPF to monitor process executions, network socket creations, and file writes with negligible overhead. Because the eBPF program runs in the kernel, user-mode malware cannot easily evade or blind it.

### Linux Persistence Mechanisms to Hunt
- **Cron Jobs:** The classic persistence mechanism. Hunt for unusual entries in `/etc/crontab`, `/var/spool/cron/crontabs/`, and `/etc/cron.d/`. Attackers often use obscure timing intervals or base64 encode the payload.
- **Systemd Services:** Modern Linux systems use `systemd` to manage services. Attackers create malicious service files (`.service`) in `/etc/systemd/system/` or `~/.config/systemd/user/` to ensure their payload runs on boot.
- **SSH Keys:** Dropping an attacker's public key into a user's `~/.ssh/authorized_keys` file allows persistent, password-less access.
- **RC Scripts and Profile:** Modifying `/etc/profile`, `~/.bashrc`, or `~/.bash_profile` ensures malware executes whenever a user logs in.

## macOS Telemetry and Hunting

macOS, built on the XNU kernel (a hybrid of Mach and BSD), presents a unique challenge due to Apple's aggressive push toward system lockdown (System Integrity Protection - SIP) and user privacy, which sometimes hinders forensic visibility.

### 1. Unified Logging System (ULS)
Introduced in macOS Sierra, ULS replaces disparate text logs with a high-performance, compressed binary format. It captures massive amounts of data from the OS and applications.
- **Hunting:** Analysts use the `log` command-line utility to query the ULS (e.g., `log show --predicate 'eventMessage contains "sudo"'`). It is highly voluminous, so hunting requires precise predicates to filter the noise.

### 2. Endpoint Security Framework (ESF)
Apple deprecated traditional kernel extensions (kexts) for security products, introducing the Endpoint Security Framework (ESF). ESF provides a user-space C API for monitoring system events.
- **How it works:** An ESF client (like an EDR or a tool like Objective-See's BlockBlock) subscribes to events such as `ES_EVENT_TYPE_NOTIFY_EXEC` (process creation) or `ES_EVENT_TYPE_AUTH_OPEN` (file access).
- **Advantage:** ESF is the gold standard for macOS telemetry today, providing deep, reliable insights into process trees and file modifications without risking kernel panics.

### macOS Persistence Mechanisms to Hunt
- **LaunchDaemons and LaunchAgents:** The macOS equivalent of Windows Services and Scheduled Tasks. Configuration `plist` (Property List) files are stored in `/Library/LaunchDaemons` (run as root on boot) and `/Library/LaunchAgents` (run as user on login). Attackers frequently drop malicious plists here.
- **Login Items:** User-configured applications that start on login.
- **Browser Extensions:** Malicious extensions in Safari or Chrome, often used for credential harvesting or AdWare.
- **Profiles:** Configuration profiles (`.mobileconfig`) used in MDM can be abused to proxy traffic, install root certificates, or enforce malicious settings.

## ASCII Diagram: eBPF vs. Auditd Architecture

The following diagram highlights why modern Linux endpoint hunting favors eBPF over the traditional Auditd architecture, specifically regarding efficiency and event filtering.

```text
+-----------------------------------------------------------------------------------------+
|                          Linux Telemetry: Auditd vs. eBPF                               |
+-----------------------------------------------------------------------------------------+

  [User Space]                                          [User Space]
  +------------------+                                  +------------------+
  |  Auditd Daemon   | <---- High Volume of Data ----   | eBPF EDR Sensor  |
  +------------------+     (All unfiltered events)      +------------------+
           ^                                                      ^
           |                                                      | Low Volume, Highly Filtered Data
           |                                                      |
  =========|======================================================|========================
           |                                                      |
  [Kernel Space]                                        [Kernel Space]
           |                                                      |
  +------------------+                                  +------------------+
  |  Audit Hooks     |                                  |   eBPF Program   |
  | (Static, Rigid)  |                                  | (Dynamic, Smart) |
  +------------------+                                  +------------------+
           |                                                      |
           v                                                      v
  +----------------------------------------------------------------------------------+
  |                               System Calls (execve, open, connect)               |
  +----------------------------------------------------------------------------------+
```
*Note: Auditd passes large amounts of data to user space for filtering, causing high overhead. eBPF runs custom filtering logic directly inside the kernel, passing only relevant, actionable alerts to the user-space sensor, minimizing CPU usage and latency.*

## Real-World Attack Scenario

### The Incident
A DevOps engineer reported that their macOS workstation was running unusually hot, and the battery was draining rapidly. The security team initiated a hunt to identify potential compromise.

### The Attack Progression
1. **Initial Access:** The engineer had downloaded a pirated developer tool (a cracked IDE) from an untrusted forum. The DMG file contained an installer that was secretly a trojan.
2. **Execution:** When the user ran the installer, macOS Gatekeeper warned the user, but the user right-clicked and selected "Open," bypassing the protection.
   - *Telemetry:* ESF captured an `ES_EVENT_TYPE_NOTIFY_EXEC` event for the malicious installer.
3. **Persistence:** The installer script silently dropped a hidden binary into `~/Library/Application Support/.sys-update` and created a LaunchAgent plist file at `~/Library/LaunchAgents/com.apple.updater.plist` to ensure the binary ran every time the engineer logged in.
   - *Telemetry:* ESF captured `ES_EVENT_TYPE_NOTIFY_RENAME` and `ES_EVENT_TYPE_NOTIFY_CREATE` events in the `LaunchAgents` directory.
4. **Execution (Impact):** The binary was an XMRig cryptominer. It immediately began consuming 90% of the CPU cycles to mine Monero.

### The Hunt and Remediation
The threat hunter used an ESF-backed EDR console to query the workstation.
- They started by searching for high CPU utilization processes and identified `.sys-update`.
- They queried the process lineage for `.sys-update`, tracing it back to the `launchd` process (indicating persistence).
- They searched the ESF telemetry for any file modifications targeting `/Library/LaunchAgents` or `~/Library/LaunchAgents` within the last 48 hours. This surfaced the `com.apple.updater.plist` file creation.
- The analyst analyzed the plist, found the path to the hidden binary, isolated the Mac, deleted the LaunchAgent and the binary, and instructed the user to rebuild their workstation.

## Hunting Strategies and Command Line Tools

### Linux Hunting
- **Find Suspicious Processes:** `ps auxww --sort=-%cpu` (look for high CPU, random names). `ls -al /proc/*/exe` (find deleted binaries still running in memory, a classic sign of malware).
- **Network Connections:** `ss -tupan` or `netstat -tulpn`. Look for unusual ports or reverse shells holding connections to unknown IPs.
- **Audit System Logs:** `grep "Failed password" /var/log/auth.log` (brute force attempts). `cat /root/.bash_history` (look for attacker commands if they forgot to clear history).

### macOS Hunting
- **Enumerate Persistence:** Use tools like `KnockKnock` or `BlockBlock` (from Objective-See) to easily enumerate all LaunchDaemons, LaunchAgents, and Login Items.
- **Inspect Network Traffic:** `lsof -i -P -n | grep LISTEN` (find listening ports). `nettop` provides an interactive, top-like view of network activity per process.
- **Check File Signatures:** Apple enforces code signing. `codesign -dv --verbose=4 /path/to/binary` can verify if a running process is legitimately signed by Apple or an identified developer, or if it is ad-hoc signed (highly suspicious for system binaries).

## Chaining Opportunities
- **Initial Access -> Persistence:** On both platforms, initial access via a web exploit or phishing is immediately followed by establishing persistence via Cron/systemd (Linux) or LaunchAgents/Daemons (macOS).
- **Execution -> Defense Evasion:** Attackers on Linux will often execute their payload and immediately delete the binary from disk (`rm -f payload`). The process continues running in memory, making file-system scans useless.
- **Privilege Escalation -> Credential Access:** Gaining root (Linux) or elevating to root (macOS) allows attackers to dump SSH keys, access keychain data (macOS), or modify `/etc/shadow` (Linux) for further lateral movement.

## Related Notes
- [[12 - Endpoint Detection and Response EDR Telemetry Analysis]]
- [[10 - Persistence Mechanisms in Windows OS]]
- [[04 - Living Off The Land Binaries (LOLBins)]]
- [[13 - Hunting for Fileless Malware and In-Memory Execution]]
- [[06 - Introduction to Digital Forensics and Incident Response DFIR]]
