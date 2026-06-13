---
tags: [tools, web-testing, utility, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.45 Nmap NSE Scripts Reference"
---

# 59.45 Nmap NSE Scripts Reference

## 1. Introduction and Core Concepts

The Nmap Scripting Engine (NSE) is one of the most powerful and flexible features of Nmap, transforming it from a simple port scanner into a comprehensive vulnerability scanner, network discovery tool, and exploitation framework.

Written in Lua, NSE scripts allow users to automate a wide variety of networking tasks. When Nmap discovers an open port and identifies the running service, it can automatically trigger specific scripts designed to interrogate that exact service. This allows for deep application-layer enumeration, default credential checking, and CVE verification directly during the scanning phase.

### 1.1 Why use NSE?

While tools like Nessus or OpenVAS provide massive vulnerability databases, they are heavy, noisy, and slow. NSE operates directly within Nmap, making it incredibly fast, targeted, and lightweight. Furthermore, its open-source nature means the security community rapidly develops and publishes NSE scripts for zero-day vulnerabilities days (or hours) after disclosure.

### 1.2 Primary Capabilities

*   **Advanced Version Detection**: Pulling detailed metadata, SSL certificates, or banner information that standard version scanning misses.
*   **Vulnerability Detection**: Verifying the presence of critical flaws (e.g., Heartbleed, EternalBlue, MS08-067) without exploiting them destructively.
*   **Brute Forcing**: Performing lightweight dictionary attacks against protocols like SSH, FTP, and HTTP.
*   **Network Discovery**: Querying DNS, SNMP, and SMB for routing tables, usernames, and domain topologies.

## 2. Architectural Overview & Attack Flow

The ASCII diagram below outlines how the Nmap Scripting Engine integrates into the broader Nmap execution lifecycle.

```text
+-------------------+                          +----------------------+
|                   |   [1] Network Packets    |                      |
| Attacker Machine  | -----------------------> |  Target Network/Host |
| (Nmap Engine)     | <----------------------- |  (Various Services)  |
+-------------------+   [2] Responses          +----------------------+
          |
          v
+-----------------------------------------------------------------------+
|                       Nmap Scripting Engine (NSE)                     |
|                                                                       |
|  [3] Execution Phases                                                 |
|  +-----------------------------------------------------------------+  |
|  | 1. Prerule: Network-level setup (e.g., broadcast discovery)     |  |
|  | 2. Hostrule: OS detection, IP-level checks                      |  |
|  | 3. Portrule: Service-specific scripts (e.g., http-vuln-*)       |  |
|  | 4. Postrule: Aggregation, reporting, cleanup                    |  |
|  +-----------------------------------------------------------------+  |
|                                     |                                 |
|  [4] Script Categories v            |                                 |
|  +-----------------------------------------------------------------+  |
|  | Default | Auth | Vuln | Exploit | Discovery | Malware | Brute   |  |
|  +-----------------------------------------------------------------+  |
+-----------------------------------------------------------------------+
```

## 3. Location and Environment Setup

NSE scripts are standard text files with the `.nse` extension. They are typically stored within the Nmap installation directory.

*   **Linux/Kali**: `/usr/share/nmap/scripts/`
*   **Windows**: `C:\Program Files (x86)\Nmap\scripts\`
*   **macOS**: `/usr/local/share/nmap/scripts/` (if using Homebrew)

### 3.1 Updating the Script Database

Nmap maintains a local database (`script.db`) mapping scripts to their respective categories. Always ensure this is updated, especially after manually downloading a new script.

```bash
sudo nmap --script-updatedb
```

## 4. Deep Dive: Script Categories

To manage hundreds of scripts, NSE organizes them into distinct categories. You can run entire categories of scripts simultaneously.

*   **`default`**: A baseline set of scripts run when the `-sC` flag is used. They are fast, reliable, and generally non-intrusive.
*   **`discovery`**: Actively queries the target to uncover more information (e.g., SMB enumeration, SNMP queries).
*   **`intrusive`**: Scripts that are likely to crash the target, consume significant resources, or trigger IDS/IPS alerts.
*   **`vuln`**: Checks for specific, known vulnerabilities (e.g., `smb-vuln-ms17-010`).
*   **`exploit`**: Goes beyond detection and actively attempts to exploit a vulnerability to prove impact.
*   **`brute`**: Performs credential brute-forcing against authentication endpoints.
*   **`safe`**: Scripts guaranteed not to crash services or consume massive bandwidth.

## 5. Comprehensive Command Reference

### 5.1 Basic Execution Syntax

**Run default scripts (`-sC`):**
```bash
nmap -sV -sC 10.0.0.5
```

**Run scripts by category:**
```bash
nmap -sV --script "vuln and safe" 10.0.0.5
```
*(This uses boolean logic to run scripts that are categorized as both vulnerability scanners AND safe to execute).*

**Run a specific script:**
```bash
nmap -p 445 --script smb-vuln-ms17-010 10.0.0.5
```

**Run scripts by wildcard:**
```bash
nmap -p 80,443 --script http-vuln-* 10.0.0.5
```

### 5.2 Passing Arguments to Scripts

Many scripts require or accept user-supplied arguments (e.g., usernames, passwords, specific URIs). This is done using the `--script-args` flag.

```bash
nmap -p 80 --script http-put --script-args http-put.url='/uploads/shell.php',http-put.file='/tmp/shell.php' 10.0.0.5
```

To see what arguments a script accepts, use the help flag:
```bash
nmap --script-help smb-os-discovery
```

## 6. Advanced Usage and Notable Scripts

### 6.1 `http-enum` (Web Directory Brute Forcing)
Acts as a built-in directory brute-forcer (similar to Gobuster or Dirb).
```bash
nmap -sV --script http-enum 10.0.0.5
```

### 6.2 `smb-os-discovery` and `smb-enum-users`
Crucial for Active Directory and Windows penetration testing. These extract the precise Windows build, hostname, domain name, and existing user accounts over NULL sessions.
```bash
nmap -p 139,445 --script smb-os-discovery,smb-enum-users 10.0.0.5
```

### 6.3 SSL/TLS Auditing (`ssl-enum-ciphers`)
Checks for weak cryptographic ciphers (e.g., RC4, DES) and protocols (SSLv3, TLS 1.0) on the target.
```bash
nmap -p 443 --script ssl-enum-ciphers 10.0.0.5
```

## 7. Troubleshooting and Limitations

*   **Timeouts**: Intrusive or Brute-force scripts can take hours to complete. Use `--host-timeout` or limit the dictionary sizes via `--script-args` to manage execution times.
*   **False Positives**: The `vuln` category relies heavily on banner grabbing and specific responses. WAFs or reverse proxies can skew these responses, leading to false positives. Always verify critical findings manually.
*   **Debugging**: If a script fails silently, use the `--script-trace` or `-d` (debug) flags to see the raw Lua output and network transmission logs.

## 8. Defensive Mitigation and Remediation

1.  **Harden Services**: The effectiveness of NSE scripts highlights the need for fundamental hardening. Disable SMBv1, disable null sessions, and restrict SNMP public strings.
2.  **Continuous Monitoring**: Blue teams should run Nmap with the `vuln` script category regularly against their own perimeter to catch missing patches before attackers do.
3.  **IDS/IPS Signatures**: Configure Intrusion Detection Systems to recognize the default user-agents and network signatures of common Nmap scripts (though sophisticated attackers will spoof these).

## 9. Chaining Opportunities

*   **[[05 - Network Reconnaissance]]**: Utilizing Nmap as the foundational step before launching deeper tools.
*   **[[06 - Server Message Block (SMB) Exploitation]]**: Finding MS17-010 via NSE, then exploiting it via Metasploit.
*   **[[25 - Active Directory Enumeration]]**: Using NSE to pull domain data prior to using BloodHound.

## 10. Related Notes

*   [[40 - Nmap Port Scanning Techniques]]
*   [[50 - Metasploit Framework Reference]]
*   [[99 - Penetration Testing Cheatsheet]]
