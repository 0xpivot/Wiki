---
tags: [network, basics, enumeration, vapt]
difficulty: beginner
module: "71 - Network Enumeration Scanning and Sniffing"
topic: "71.04 Nmap Scripting Engine NSE Basics"
---

# Nmap Scripting Engine (NSE) Basics

## Introduction

While Nmap is fundamentally a port scanner and version detection tool, its true power as a comprehensive vulnerability assessment framework lies in the Nmap Scripting Engine (NSE). The NSE allows users to write (and share) scripts using the Lua programming language to automate a vast array of networking tasks. 

NSE transforms Nmap from a passive reconnaissance tool into an active vulnerability scanner, exploitation framework, and advanced enumeration utility. Scripts can interact with discovered services, brute-force credentials, discover misconfigurations, and even trigger known exploits.

## The Architecture of NSE

NSE scripts are written in Lua, a lightweight, fast, embeddable scripting language. They interface with Nmap's core C++ engine through specialized bindings. This architecture provides the scripts with high-performance networking capabilities, parallel execution, and direct access to Nmap's internal data structures (like the list of open ports, identified services, host states, and MAC addresses).

Scripts are typically located in the `/usr/share/nmap/scripts/` directory on Linux systems. Nmap comes pre-packaged with over 600 scripts covering protocols ranging from HTTP and SMB to obscure SCADA systems and databases.

### Script Categories

To manage this massive library, scripts are categorized based on their intended function and the risk associated with running them. A single script can belong to multiple categories. The primary categories include:

- **default:** The scripts run when using the `-sC` or `-A` flags. These are deemed safe, fast, and highly reliable (e.g., grabbing HTTP titles, enumerating basic SMB info).
- **safe:** Scripts that will not crash a service, consume large amounts of bandwidth, or cause significant network noise.
- **intrusive:** Scripts that might crash the target, consume significant system resources, or are highly likely to be flagged and blocked by an IDS/IPS.
- **vuln:** Scripts designed specifically to check for the presence of known, specific vulnerabilities (e.g., checking for MS17-010 EternalBlue or OpenSSL Heartbleed).
- **exploit:** Scripts that go beyond checking and actively attempt to exploit a vulnerability, often attempting to drop a payload or spawn a shell.
- **auth:** Scripts that deal with authentication mechanics, often attempting to bypass them or enumerate supported methods.
- **brute:** Scripts that perform brute-force or dictionary credential guessing against services like SSH, FTP, SNMP, or HTTP Basic Auth.
- **discovery:** Scripts aimed at discovering more about the network infrastructure, such as querying DNS servers for zone transfers, enumerating SNMP trees, or identifying SMB shares and users.

## Using the Nmap Scripting Engine

### Running Default Scripts
The simplest way to use NSE is to run the default set of scripts using the `-sC` flag. This is equivalent to `--script=default`.

```bash
nmap -sC -p 80,443,445 10.10.10.5
```

### Running Specific Scripts or Categories
You can specify individual scripts by name, or entire categories using the `--script` flag. The `.nse` extension can optionally be omitted.

```bash
# Run a specific script by name
nmap --script smb-os-discovery.nse -p 445 10.10.10.5

# Run all scripts in the 'vuln' category
nmap --script vuln 10.10.10.5

# Run multiple categories or specific scripts simultaneously
nmap --script "default,safe,ftp-anon" -p 21 10.10.10.5
```

### Pattern Matching and Boolean Logic
Nmap supports complex expressions to select which scripts to run. You can use wildcards (`*`) and boolean operators (`and`, `or`, `not`). This is highly useful for customizing scans to avoid certain behaviors.

```bash
# Run all HTTP scripts EXCEPT those categorized as intrusive or brute-force
nmap --script "http-* and not (intrusive or brute)" -p 80 10.10.10.5

# Run scripts that are either in the 'vuln' or 'exploit' category, and related to SMB
nmap --script "(vuln or exploit) and smb-*" -p 445 10.10.10.5
```

### Passing Arguments to Scripts
Many scripts accept arguments to customize their behavior. For example, a brute-force script needs to know which wordlists to use, or an HTTP spider script might need a specific root path to start from. Arguments are passed using the `--script-args` flag.

```bash
# Run an HTTP brute force script, supplying custom usernames and passwords files
nmap --script http-brute -p 80 --script-args userdb=users.txt,passdb=passwords.txt 10.10.10.5

# Pass arguments to a specific script when running multiple scripts
nmap --script smb-enum-shares --script-args smbusername=admin,smbpass=secret 10.10.10.5

# Provide an argument file instead of typing them inline
nmap --script-args-file my_args.txt ...
```

## Anatomy of an NSE Script

While writing NSE scripts is an advanced topic, understanding their structure helps in troubleshooting and selecting the right tools. A standard NSE script contains several key sections:

1. **Description (`description`):** A string outlining what the script does.
2. **Categories (`categories`):** A table listing the categories the script belongs to.
3. **Dependencies (`dependencies`):** Other scripts that must run before this one.
4. **Rule (`rule` / `portrule` / `hostrule`):** A Lua function that determines *if* the script should run against a target. For example, a `portrule` might check if the port is open and the detected service is 'http'. If the rule returns true, the action function is executed.
5. **Action (`action`):** The core logic of the script. This function interacts with the target, sends network payloads, parses responses, and returns the output string that Nmap displays to the terminal.

## Visualizing NSE Execution

```ascii
+-------------------+                                  +-------------------+
|      Nmap Core    |                                  |   Target System   |
|  (Discovers Open  |                                  |    (Port 445)     |
|   Port 445, SMB)  |                                  |                   |
+-------------------+                                  +-------------------+
          |
          v
+-------------------+
|   NSE Scheduler   |
| Evaluates rules:  |
| "Does smb-vuln-   |
| ms17-010 apply?"  |
+-------------------+
          |
          | [Rule = True]
          v
+-------------------+                                  +-------------------+
|   NSE Script      |        --- Craft SMB Probe ---   |                   |
| smb-vuln-ms17-010 |--------------------------------->|  Evaluates packet |
|   (Lua Engine)    |<---------------------------------|  Returns response |
+-------------------+        --- SMB Response ---      +-------------------+
          |
          | Parses response
          | Identifies vulnerability signature
          v
+-------------------+
|   Nmap Output     |
| "VULNERABLE:      |
| MS17-010 Eternal- |
| Blue detected."   |
+-------------------+
```

## Advanced Debugging and Tracing

When an NSE script fails to run, or produces unexpected results, Nmap provides powerful debugging flags.

- `--script-trace`: Prints all incoming and outgoing network traffic generated strictly by the NSE scripts (ignoring standard Nmap port scan traffic). This is invaluable for seeing exactly what HTTP requests or SMB packets the Lua script is sending.
- `-d` / `-dd`: Increases the general Nmap debugging level, showing why a script's rule did or did not trigger.

```bash
# Debug why an HTTP script isn't triggering properly
nmap --script http-title --script-trace -p 80 10.10.10.5
```

## Updating and Expanding the NSE Library

The NSE library is constantly evolving as new vulnerabilities are discovered. It is critical to keep the script database updated.

```bash
# Update the local script database (does not download new scripts, just rebuilds the index)
sudo nmap --script-updatedb
```

To get the latest scripts, you should update the Nmap package via your OS package manager (e.g., `apt update && apt upgrade nmap`), or manually download individual `.nse` scripts from reliable sources (like the official Nmap GitHub repository or Exploit-DB) and place them in the `/usr/share/nmap/scripts/` directory, followed by running `--script-updatedb`.

## Common and Powerful NSE Scripts

- `http-enum`: Enumerates common web application directories and files, functioning similarly to DirBuster or Gobuster, but built directly into your port scan.
- `smb-os-discovery`: Extracts detailed OS information, computer name, domain name, and system time over the SMB protocol. Extremely useful in Active Directory environments.
- `ftp-anon`: Checks if an FTP server allows anonymous logins and lists the root directory if successful.
- `ssl-enum-ciphers`: Evaluates the SSL/TLS configuration of a server, grading the supported ciphers and checking for weaknesses like SWEET32, POODLE, or weak key exchanges.
- `dns-zone-transfer`: Attempts to perform a full DNS zone transfer (`AXFR`) against a DNS server to retrieve all domain records.

## Chaining Opportunities
- **Service Enumeration Output:** NSE scripts heavily rely on accurate service detection. It is best practice to run `-sV` alongside NSE scripts to ensure the scripts trigger correctly based on the service banner, rather than just the port number. See [[03 - Nmap Service and OS Detection]].
- **Exploitation Frameworks:** If a script in the `vuln` category identifies a critical flaw (e.g., `smb-vuln-ms08-067`), the immediate next step is launching a framework like Metasploit to exploit that specific vulnerability and gain a reverse shell.

## Related Notes
- [[02 - Nmap Port Scanning Techniques TCP UDP]]
- [[03 - Nmap Service and OS Detection]]
