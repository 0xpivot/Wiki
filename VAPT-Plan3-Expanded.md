# VAPT Vault — Plan 3: Deep Expansion
> Expands 7 modules with 600+ additional topics
> Status: [ ] not started | [x] done | [~] in progress
> Parent plan: [[VAPT-Vault-Plan]]

---

## MODULE 43-EX — Windows Privilege Escalation (Full) (85 topics)

### Enumeration and Information Gathering
- [ ] W01 WinPEAS — Full Usage and Output Interpretation
- [ ] W02 PowerUp — PowerShell PrivEsc Enumeration
- [ ] W03 Seatbelt — System Triage and Security Checks
- [ ] W04 Sherlock — Missing Patches Detection
- [ ] W05 JAWS — Just Another Windows Script
- [ ] W06 Manual Enumeration Checklist (whoami, systeminfo, net commands)
- [ ] W07 Environment Variables — Leaking Sensitive Data
- [ ] W08 Installed Software Enumeration (wmic product, reg query)
- [ ] W09 Network Connections and Routing (netstat, route print, arp -a)
- [ ] W10 Listening Ports — Finding Internal Services

### Service-Based Escalation
- [ ] W11 Unquoted Service Paths — Detection and Exploitation
- [ ] W12 Weak Service DACL — sc.exe and accesschk.exe
- [ ] W13 Modifiable Service Binary Path
- [ ] W14 Service Running as SYSTEM with Weak Permissions
- [ ] W15 Creating a Malicious Service
- [ ] W16 Abusing Third-Party Services (AV, monitoring agents)
- [ ] W17 Windows Task Scheduler Abuse — Weak Task Permissions
- [ ] W18 Scheduled Tasks — Creating Persistent Tasks as SYSTEM

### Registry-Based Escalation
- [ ] W19 AlwaysInstallElevated — Registry Check and MSI Exploit
- [ ] W20 Autorun Registry Keys — HKLM vs HKCU
- [ ] W21 Registry Key Weak ACLs — Overwriting Service ImagePath
- [ ] W22 SAM and SYSTEM Registry Hive Extraction
- [ ] W23 Winlogon Credentials in Registry
- [ ] W24 VNC / RealVNC Password in Registry
- [ ] W25 PuTTY Saved Sessions — Registry Credential Leak

### Token and Privilege Abuse
- [ ] W26 Windows Access Tokens — Types (Primary, Impersonation)
- [ ] W27 SeImpersonatePrivilege — Full Exploitation Guide
- [ ] W28 SeAssignPrimaryTokenPrivilege
- [ ] W29 JuicyPotato — CLSID Selection by OS Version
- [ ] W30 RoguePotato — Named Pipe Impersonation
- [ ] W31 PrintSpoofer — SpoolSample via Named Pipes
- [ ] W32 SweetPotato — Combining Multiple Potato Techniques
- [ ] W33 GodPotato — Universal Potato for All Windows Versions
- [ ] W34 Hot Potato — NBNS Spoofing + NTLM Relay
- [ ] W35 Token Impersonation with Incognito (Metasploit Module)
- [ ] W36 Abusing SeBackupPrivilege — Copying Protected Files
- [ ] W37 Abusing SeRestorePrivilege — Writing Protected Files
- [ ] W38 Abusing SeDebugPrivilege — Injecting into SYSTEM Processes
- [ ] W39 Abusing SeTakeOwnershipPrivilege — Taking Ownership of Files
- [ ] W40 Abusing SeLoadDriverPrivilege — Loading Malicious Drivers
- [ ] W41 Abusing SeCreateTokenPrivilege — Creating Tokens
- [ ] W42 Abusing SeManageVolumePrivilege

### UAC Bypass
- [ ] W43 UAC Architecture — Integrity Levels (Low, Medium, High, System)
- [ ] W44 UAC Bypass — fodhelper.exe (Registry)
- [ ] W45 UAC Bypass — eventvwr.exe (Registry)
- [ ] W46 UAC Bypass — sdclt.exe (Registry)
- [ ] W47 UAC Bypass — cmstp.exe (INF File)
- [ ] W48 UAC Bypass — DiskCleanup Scheduled Task
- [ ] W49 UAC Bypass — Mockdirs (Writable Trusted Path)
- [ ] W50 UAC Bypass — UACME Tool (50+ Methods)

### DLL Attacks
- [ ] W51 DLL Hijacking — Safe DLL Search Mode OFF
- [ ] W52 DLL Search Order — Full Windows Path Resolution
- [ ] W53 DLL Side-Loading in Signed Executables
- [ ] W54 DLL Injection — CreateRemoteThread Method
- [ ] W55 Phantom DLL Hijacking — Missing DLLs in System32
- [ ] W56 DLL Planting via Writable PATH Entry

### Credential Harvesting
- [ ] W57 Mimikatz — sekurlsa::logonpasswords
- [ ] W58 Mimikatz — sekurlsa::wdigest (Clear-text Passwords)
- [ ] W59 Mimikatz — lsadump::sam (SAM Hash Dump)
- [ ] W60 Mimikatz — lsadump::secrets (LSA Secrets)
- [ ] W61 Pypykatz — Python Mimikatz Alternative
- [ ] W62 Procdump + Mimikatz — Offline LSASS Dump
- [ ] W63 Task Manager LSASS Dump (GUI Method)
- [ ] W64 comsvcs.dll MiniDump — Fileless LSASS Dump
- [ ] W65 DPAPI — Decrypting Chrome Cookies and Passwords
- [ ] W66 DPAPI — Decrypting WiFi Passwords
- [ ] W67 Windows Vault Credentials (vaultcmd)
- [ ] W68 NTDS.dit + SYSTEM Hive Offline Extraction
- [ ] W69 Volume Shadow Copy — Accessing Protected Files

### AV and EDR Evasion
- [ ] W70 AMSI Architecture — How It Works
- [ ] W71 AMSI Bypass — Memory Patching (AmsiScanBuffer)
- [ ] W72 AMSI Bypass — Reflection Method
- [ ] W73 AMSI Bypass — COM Object Hijack
- [ ] W74 PowerShell Constrained Language Mode Bypass
- [ ] W75 AppLocker Rules — Default Rules and Bypass Paths
- [ ] W76 AppLocker Bypass — Trusted Paths (C:\Windows\Tasks)
- [ ] W77 AppLocker Bypass — InstallUtil, regsvcs, msbuild
- [ ] W78 WDAC (Windows Defender Application Control) Bypass Concepts
- [ ] W79 Windows Defender — Exclusion Abuse
- [ ] W80 Obfuscation — Invoke-Obfuscation, Chameleon

### LOLBins and Living Off the Land
- [ ] W81 certutil — Download, Encode, Decode
- [ ] W82 mshta — HTA Execution
- [ ] W83 regsvr32 — Squiblydoo COM Scriptlet
- [ ] W84 rundll32 — DLL Execution
- [ ] W85 msiexec — Remote MSI Download and Execute

---

## MODULE 44-EX — Linux Privilege Escalation (Full) (75 topics)

### Enumeration Tools and Manual Checks
- [ ] L01 LinPEAS — Full Usage and Output Reading
- [ ] L02 LinEnum — Legacy Enumeration Script
- [ ] L03 linux-exploit-suggester — Kernel CVE Matching
- [ ] L04 linux-smart-enumeration (lse.sh) — Severity Levels
- [ ] L05 pspy — Process Spy Without Root
- [ ] L06 Manual Enumeration Checklist — 50-Point Checklist
- [ ] L07 /etc/passwd and /etc/shadow Analysis
- [ ] L08 /etc/crontab and /var/spool/cron Analysis
- [ ] L09 Network Information — ss, netstat, ip route
- [ ] L10 Interesting Files — find commands for SUID, SGID, World-Writable

### SUID/SGID and GTFOBins
- [ ] L11 GTFOBins — How to Use the Database
- [ ] L12 SUID — bash, sh, dash Exploitation
- [ ] L13 SUID — find (exec command escalation)
- [ ] L14 SUID — nmap (interactive mode, older versions)
- [ ] L15 SUID — vim, vi, nano (shell escape)
- [ ] L16 SUID — python, python3, perl, ruby, lua
- [ ] L17 SUID — cp, mv (overwriting /etc/passwd)
- [ ] L18 SUID — awk, gawk (exec shell)
- [ ] L19 SUID — more, less, man (shell escape via !)
- [ ] L20 SUID — tar, zip (reading files, exec shell)
- [ ] L21 SUID — env, tee, cat, head, tail (file read/write)
- [ ] L22 SUID — git (hook execution)
- [ ] L23 SUID — gcc, make (compile and run as owner)
- [ ] L24 SUID — strace, ltrace (reading process memory)
- [ ] L25 SUID — pkexec (PwnKit CVE-2021-4034)
- [ ] L26 Custom SUID Binaries — Reversing and Exploiting

### Sudo Abuse
- [ ] L27 sudo -l — Reading Sudoers Rules
- [ ] L28 Sudo ALL — Full Root via Shell Command
- [ ] L29 Sudo NOPASSWD — No Password Required
- [ ] L30 Sudo with Specific Command — GTFOBins Sudo Page
- [ ] L31 Sudo Environment Variables — LD_PRELOAD Exploit
- [ ] L32 Sudo Environment Variables — LD_LIBRARY_PATH
- [ ] L33 Sudo with Wildcards (*) — Command Injection
- [ ] L34 Sudo Version-Specific CVEs (Baron Samedit CVE-2021-3156)
- [ ] L35 visudo Misconfiguration — Writing Sudoers File

### Cron Job Exploitation
- [ ] L36 Cron Job — Writable Script Replacement
- [ ] L37 Cron Job — PATH Hijacking (no full path in command)
- [ ] L38 Cron Job — Wildcard Injection with tar
- [ ] L39 Cron Job — Wildcard Injection with rsync
- [ ] L40 Cron Job — Wildcard Injection with chown/chmod
- [ ] L41 pspy — Monitoring Cron Jobs Without Root
- [ ] L42 Anacron — Privilege Escalation via Anacrontab

### Capabilities
- [ ] L43 Linux Capabilities Overview — Full List
- [ ] L44 cap_setuid — Escalating to Root
- [ ] L45 cap_net_bind_service — Binding Privileged Ports
- [ ] L46 cap_net_raw — Packet Sniffing Without Root
- [ ] L47 cap_dac_read_search — Reading Root Files
- [ ] L48 cap_sys_ptrace — Process Injection
- [ ] L49 cap_sys_admin — Container Escape
- [ ] L50 getcap / setcap — Finding and Setting Capabilities

### Kernel Exploits
- [ ] L51 Kernel Exploit Methodology — Check Version → Match CVE → Compile
- [ ] L52 DirtyCow (CVE-2016-5195) — /proc/self/mem Race Condition
- [ ] L53 DirtyPipe (CVE-2022-0847) — Pipe Buffer Overwrite
- [ ] L54 PwnKit (CVE-2021-4034) — pkexec Path Manipulation
- [ ] L55 Baron Samedit (CVE-2021-3156) — Heap Buffer Overflow in sudo
- [ ] L56 Netfilter UAF (CVE-2022-32250)
- [ ] L57 OverlayFS (CVE-2023-0386) — Kernel 6.2
- [ ] L58 Compiling Kernel Exploits on Target (gcc, cross-compile tricks)

### File and Path Abuse
- [ ] L59 Writable /etc/passwd — Adding UID 0 User
- [ ] L60 Writable /etc/sudoers or /etc/sudoers.d/
- [ ] L61 World-Writable Directories in PATH
- [ ] L62 NFS Root Squash Disabled — Mounting and Escalating
- [ ] L63 Weak /tmp Permissions — Symlink Attacks
- [ ] L64 Python/Perl Library Hijacking in Import Path
- [ ] L65 Logrotate Exploitation (logrotten)
- [ ] L66 Writable /etc/cron.d/ or /etc/cron.daily/

### Special Group Memberships
- [ ] L67 docker Group — Mounting Host Root in Container
- [ ] L68 lxd/lxc Group — Container Privilege Escalation
- [ ] L69 disk Group — Reading Raw Block Device (/dev/sda)
- [ ] L70 shadow Group — Reading /etc/shadow
- [ ] L71 adm Group — Reading System Logs
- [ ] L72 video Group — Framebuffer Access
- [ ] L73 sudo Group — Direct Privilege Escalation

### Credential Hunting
- [ ] L74 Bash History — ~/.bash_history, ~/.zsh_history
- [ ] L75 SSH Private Keys — ~/.ssh/id_rsa, authorized_keys

---

## MODULE 45-EX — Post-Exploitation (Full) (65 topics)

### C2 Frameworks
- [ ] P01 Metasploit — Meterpreter Session Management
- [ ] P02 Metasploit — Post Modules (hashdump, enum_system, etc.)
- [ ] P03 Cobalt Strike — Beacon Architecture (concept)
- [ ] P04 Sliver — Open Source C2 Framework
- [ ] P05 Havoc — Modern C2 Framework
- [ ] P06 Mythic — Multi-Agent C2 Framework
- [ ] P07 Villain — C2 over TCP and HTTP
- [ ] P08 Covenant — .NET C2 Framework
- [ ] P09 Empire / Starkiller — PowerShell C2
- [ ] P10 C2 Infrastructure — Redirectors and Domain Fronting
- [ ] P11 C2 Communication — HTTP/S, DNS, ICMP Channels
- [ ] P12 C2 OPSEC — Avoiding Detection

### Situational Awareness
- [ ] P13 First Things to Run After Initial Access
- [ ] P14 User and Group Enumeration
- [ ] P15 Network Topology Discovery (internal subnets)
- [ ] P16 Active Sessions and Logged-in Users (query session, w, who)
- [ ] P17 AV/EDR Detection — Running Products
- [ ] P18 Domain Membership Check
- [ ] P19 Shares and Mapped Drives (net share, net use)
- [ ] P20 Interesting Files — Automated and Manual Search

### Lateral Movement (Extended)
- [ ] P21 Pass-the-Hash — NTLM Authentication Abuse
- [ ] P22 Pass-the-Ticket — Kerberos TGT Reuse
- [ ] P23 Overpass-the-Hash — NTLM Hash to Kerberos Ticket
- [ ] P24 WMI Lateral Movement (wmic, Invoke-WMIMethod, impacket wmiexec)
- [ ] P25 PsExec — Admin Share + Service Creation
- [ ] P26 SMBExec — No Binary Dropped to Disk
- [ ] P27 WinRM / evil-winrm — Remote PowerShell
- [ ] P28 RDP — Hijacking Existing Sessions (tscon)
- [ ] P29 DCOM Lateral Movement (MMC, ShellWindows, Excel)
- [ ] P30 SSH Lateral Movement — Key Reuse, Agent Forwarding
- [ ] P31 Kerberos S4U2Self — Impersonating Users
- [ ] P32 Resource-Based Constrained Delegation (RBCD) Abuse

### Pivoting and Tunneling (Extended)
- [ ] P33 SSH Local Port Forwarding (-L flag)
- [ ] P34 SSH Remote Port Forwarding (-R flag)
- [ ] P35 SSH Dynamic Port Forwarding (-D flag, SOCKS)
- [ ] P36 Chisel — TCP/UDP Tunneling Reference
- [ ] P37 Ligolo-ng — Layer 3 Tunnel Without Proxychains
- [ ] P38 Rpivot — Reverse SOCKS Proxy
- [ ] P39 reGeorg — Web Shell SOCKS Proxy
- [ ] P40 Metasploit route and socks modules
- [ ] P41 DNS Tunneling — iodine, dns2tcp
- [ ] P42 ICMP Tunneling — ptunnel-ng
- [ ] P43 HTTP/S Tunneling — Neo-reGeorg

### Data Exfiltration (Extended)
- [ ] P44 Exfil via DNS (dnscat2, iodine)
- [ ] P45 Exfil via HTTP/S (curl, wget, PowerShell Invoke-WebRequest)
- [ ] P46 Exfil via FTP and SMB
- [ ] P47 Exfil via ICMP (ping exfil)
- [ ] P48 Exfil via Email (SMTP)
- [ ] P49 Exfil via Cloud Storage (S3, Dropbox API, OneDrive)
- [ ] P50 Steganography — Hiding Data in Images
- [ ] P51 Compressing and Encrypting Before Exfil
- [ ] P52 Data Staging — Gathering Before Exfil

### Persistence (Extended)
- [ ] P53 Windows — Registry Run Keys (HKCU, HKLM)
- [ ] P54 Windows — Scheduled Tasks (schtasks /create)
- [ ] P55 Windows — New Service Creation
- [ ] P56 Windows — DLL Hijacking for Persistence
- [ ] P57 Windows — WMI Event Subscriptions (Fileless)
- [ ] P58 Windows — COM Object Hijacking
- [ ] P59 Windows — Boot/Pre-OS Persistence (Bootkit concept)
- [ ] P60 Linux — .bashrc, .bash_profile, .profile Modification
- [ ] P61 Linux — Crontab Entry
- [ ] P62 Linux — SSH Authorized Keys
- [ ] P63 Linux — systemd User Service
- [ ] P64 Linux — /etc/init.d Script
- [ ] P65 Web Shell Persistence — Hiding in Legitimate Files

---

## MODULE 56-EX — Defensive Security (Full) (80 topics)

### Detection Engineering
- [ ] D01 What is Detection Engineering?
- [ ] D02 SIGMA Rules — Writing Detection Rules
- [ ] D03 YARA Rules — Malware Signature Writing
- [ ] D04 Suricata Rules — Network IDS Signatures
- [ ] D05 Snort Rules — IDS Rule Syntax
- [ ] D06 MITRE ATT&CK Mapping to Detections
- [ ] D07 Elastic SIEM — KQL Queries for Attack Detection
- [ ] D08 Splunk — SPL Queries for Security Monitoring
- [ ] D09 Wazuh — Open Source SIEM Setup and Rules
- [ ] D10 Graylog — Log Management and Alerting

### Log Analysis and Sources
- [ ] D11 Windows Event Log — Key Event IDs Reference
- [ ] D12 Event ID 4624 — Successful Logon (Track Lateral Movement)
- [ ] D13 Event ID 4625 — Failed Logon (Brute Force Detection)
- [ ] D14 Event ID 4648 — Explicit Credential Use (Pass-the-Hash)
- [ ] D15 Event ID 4688 — Process Creation (Command Execution)
- [ ] D16 Event ID 4698 — Scheduled Task Created (Persistence)
- [ ] D17 Event ID 4720 — User Account Created (Backdoor)
- [ ] D18 Event ID 4728/4732 — Group Membership Change
- [ ] D19 Event ID 4768/4769/4771 — Kerberos Ticket Events
- [ ] D20 Event ID 7045 — New Service Installed
- [ ] D21 Sysmon — Configuration and Key Events
- [ ] D22 Sysmon Event ID 1 — Process Creation with Command Line
- [ ] D23 Sysmon Event ID 3 — Network Connection
- [ ] D24 Sysmon Event ID 7 — Image Loaded (DLL Tracking)
- [ ] D25 Sysmon Event ID 8 — CreateRemoteThread
- [ ] D26 Sysmon Event ID 10 — Process Access (LSASS)
- [ ] D27 Sysmon Event ID 11 — File Create
- [ ] D28 Sysmon Event ID 13 — Registry Value Set
- [ ] D29 Linux Auditd — Rules and Log Analysis
- [ ] D30 Apache/Nginx Access Log Analysis for Attacks

### Blue Team Tools
- [ ] D31 Velociraptor — DFIR and Threat Hunting Platform
- [ ] D32 TheHive + Cortex — Incident Response Platform
- [ ] D33 MISP — Threat Intelligence Sharing Platform
- [ ] D34 OpenCTI — Cyber Threat Intelligence Platform
- [ ] D35 Shuffle — SOAR Automation Platform
- [ ] D36 Zeek (Bro) — Network Security Monitor
- [ ] D37 NetworkMiner — Passive Network Sniffer
- [ ] D38 Malcolm — Network Traffic Analysis Suite
- [ ] D39 Arkime (Moloch) — Full Packet Capture
- [ ] D40 Rita — BEACON Detection from Zeek Logs

### Forensics (Extended)
- [ ] D41 Digital Forensics — What to Collect and Preserve
- [ ] D42 Memory Forensics — Volatility 3 Full Reference
- [ ] D43 Volatility — imageinfo, pslist, pstree, netscan
- [ ] D44 Volatility — malfind (Injected Code Detection)
- [ ] D45 Volatility — dumpfiles, filescan, cmdline
- [ ] D46 Disk Forensics — Autopsy Full Walkthrough
- [ ] D47 Disk Forensics — Timeline Analysis
- [ ] D48 File System Artifacts — $MFT, $LogFile, $UsnJrnl
- [ ] D49 Windows Artifacts — Prefetch, Shimcache, Amcache
- [ ] D50 Windows Artifacts — LNK Files, Jump Lists, Recent Files
- [ ] D51 Windows Artifacts — Browser History and Downloads
- [ ] D52 Windows Artifacts — Registry Forensics (UserAssist, ShimCache)
- [ ] D53 Linux Forensics — /var/log, auth.log, syslog
- [ ] D54 Linux Artifacts — bash_history, .viminfo, .ssh
- [ ] D55 Network Forensics — PCAP Analysis with Wireshark
- [ ] D56 Email Forensics — Header Analysis, Phishing Investigation
- [ ] D57 Malware Analysis — Static (strings, PEview, Ghidra)
- [ ] D58 Malware Analysis — Dynamic (Any.run, Cuckoo Sandbox)
- [ ] D59 Malware Analysis — Behavioral (procmon, procexp, regmon)
- [ ] D60 Reverse Engineering Basics — x86 Assembly for Analysts

### Incident Response
- [ ] D61 IR Phases — PICERL Detailed Walkthrough
- [ ] D62 IR — Initial Triage Checklist
- [ ] D63 IR — Isolating Compromised Systems
- [ ] D64 IR — Evidence Collection (memory, disk, network)
- [ ] D65 IR — Malware Removal and Remediation
- [ ] D66 IR — Root Cause Analysis
- [ ] D67 IR — Post-Incident Report Writing
- [ ] D68 IR — Ransomware Specific Response
- [ ] D69 IR — Business Email Compromise (BEC) Response
- [ ] D70 IR — Supply Chain Compromise Response

### Hardening (Extended)
- [ ] D71 CIS Benchmark — Level 1 vs Level 2
- [ ] D72 Linux — SSH Hardening (disable root, keys only, fail2ban)
- [ ] D73 Linux — IPTables / nftables Firewall Rules
- [ ] D74 Linux — AppArmor Profile Writing
- [ ] D75 Linux — SELinux Policy Basics
- [ ] D76 Windows — Windows Firewall Advanced Rules
- [ ] D77 Windows — Attack Surface Reduction (ASR) Rules
- [ ] D78 Windows — Credential Guard Configuration
- [ ] D79 Windows — Windows Hello and Passwordless Auth
- [ ] D80 Web — Security Headers Quick-Win Checklist

---

## MODULE 57-EX — OWASP Complete (50 topics)

### OWASP Web Top 10 2021 — Deep Dive Per Item
- [ ] O01 A01 — Broken Access Control — All 12 Sub-Categories
- [ ] O02 A01 — Broken Access Control — Testing Methodology
- [ ] O03 A01 — Broken Access Control — Code Fix Examples
- [ ] O04 A02 — Cryptographic Failures — What Counts as a Failure
- [ ] O05 A02 — Cryptographic Failures — Testing for Weak TLS
- [ ] O06 A02 — Cryptographic Failures — Testing for Weak Storage
- [ ] O07 A03 — Injection — All Injection Types Covered
- [ ] O08 A03 — Injection — Parameterized Queries in 5 Languages
- [ ] O09 A04 — Insecure Design — Threat Modeling Integration
- [ ] O10 A04 — Insecure Design — Secure Design Patterns
- [ ] O11 A05 — Security Misconfiguration — Full Checklist
- [ ] O12 A05 — Security Misconfiguration — Default Credentials List
- [ ] O13 A06 — Vulnerable and Outdated Components — SCA Tools
- [ ] O14 A06 — Vulnerable and Outdated Components — Remediation
- [ ] O15 A07 — Identification and Authentication Failures — Testing
- [ ] O16 A07 — Identification and Authentication Failures — Fix Guide
- [ ] O17 A08 — Software and Data Integrity Failures — CI/CD Risks
- [ ] O18 A08 — Supply Chain Attack Prevention
- [ ] O19 A09 — Security Logging and Monitoring Failures — What to Log
- [ ] O20 A09 — Building a Logging Strategy
- [ ] O21 A10 — Server-Side Request Forgery (SSRF) — Full Test Cases

### OWASP API Top 10 2023 — Deep Dive Per Item
- [ ] O22 API1 — BOLA — Testing All Object References
- [ ] O23 API2 — Broken Authentication — API Key vs JWT vs OAuth
- [ ] O24 API3 — Broken Object Property Level Auth — Mass Assignment
- [ ] O25 API4 — Unrestricted Resource Consumption — Rate Limiting
- [ ] O26 API5 — BFLA — Function-Level Authorization Testing
- [ ] O27 API6 — Unrestricted Sensitive Business Flow Testing
- [ ] O28 API7 — SSRF in API Context
- [ ] O29 API8 — Security Misconfiguration in APIs
- [ ] O30 API9 — Improper Inventory Management — Shadow APIs
- [ ] O31 API10 — Unsafe Consumption of Third-Party APIs

### OWASP Testing Guide (WSTG) Key Sections
- [ ] O32 WSTG — Information Gathering Phase (OTG-INFO-001 to 010)
- [ ] O33 WSTG — Configuration and Deployment Testing
- [ ] O34 WSTG — Identity Management Testing
- [ ] O35 WSTG — Authentication Testing (OTG-AUTHN-001 to 010)
- [ ] O36 WSTG — Authorization Testing (OTG-AUTHZ-001 to 004)
- [ ] O37 WSTG — Session Management Testing
- [ ] O38 WSTG — Input Validation Testing (All Injection Types)
- [ ] O39 WSTG — Error Handling Testing
- [ ] O40 WSTG — Cryptography Testing
- [ ] O41 WSTG — Business Logic Testing (OTG-BUSLOGIC-001 to 009)
- [ ] O42 WSTG — Client-Side Testing (XSS, DOM, Clickjacking)

### OWASP ASVS
- [ ] O43 ASVS Level 1 — Minimum Security Requirements
- [ ] O44 ASVS Level 2 — Standard Application Security
- [ ] O45 ASVS Level 3 — High Assurance Applications
- [ ] O46 ASVS — Using as a Pentest Checklist
- [ ] O47 ASVS vs PCI DSS — Mapping Requirements

### OWASP Secure Coding
- [ ] O48 OWASP Cheat Sheet — Input Validation
- [ ] O49 OWASP Cheat Sheet — Authentication
- [ ] O50 OWASP Cheat Sheet — SQL Injection Prevention

---

## MODULE 59-EX — Complete Tools Reference (Extended) (120 tools)

### Reconnaissance (Extended)
- [ ] T01 Shodan Dorks — Top 50 Security Dorks
- [ ] T02 Google Dorks — Top 100 Security Dorks
- [ ] T03 GitHub Dorks — Secrets and API Key Patterns
- [ ] T04 Censys — Certificate and Host Search Advanced
- [ ] T05 FOFA — Chinese IoT Search Engine Syntax
- [ ] T06 Zoomeye — Search Syntax Reference
- [ ] T07 GreyNoise — Distinguishing Scanners from Attackers
- [ ] T08 LeakIX — Exposed Services and Vulnerabilities
- [ ] T09 BinaryEdge — Attack Surface Discovery
- [ ] T10 Spyse / Hunter.io — Email and Domain OSINT
- [ ] T11 Intelx — Leaked Data Search Engine
- [ ] T12 OSINT Framework — Full Tool Map
- [ ] T13 SpiderFoot — Automated OSINT
- [ ] T14 Creepy — Geolocation OSINT
- [ ] T15 Metagoofil — Document Metadata Extraction

### Web Fuzzing and Discovery (Extended)
- [ ] T16 wfuzz — Classic Web Fuzzer Reference
- [ ] T17 dirsearch — Directory Brute Force
- [ ] T18 dirbuster — GUI Directory Brute Force
- [ ] T19 whatweb — Web Tech Fingerprinting CLI
- [ ] T20 wafw00f — WAF Fingerprinting Tool
- [ ] T21 WPScan — WordPress Vulnerability Scanner
- [ ] T22 droopescan — Drupal/Silverstripe Scanner
- [ ] T23 joomscan — Joomla Scanner
- [ ] T24 CMSeek — CMS Detection and Exploitation
- [ ] T25 Wapiti — Open Source DAST Scanner
- [ ] T26 skipfish — Active Web Application Recon
- [ ] T27 golismero — Web Security Testing Framework
- [ ] T28 w3af — Web Application Attack and Audit Framework
- [ ] T29 testssl.sh — TLS/SSL Testing
- [ ] T30 sslyze — SSL/TLS Analyzer

### Burp Suite Deep Dive
- [ ] T31 Burp Suite — Proxy Setup and FoxyProxy Config
- [ ] T32 Burp Suite — Intercept and Repeater Workflow
- [ ] T33 Burp Suite — Intruder — Sniper, Battering Ram, Pitchfork, Cluster Bomb
- [ ] T34 Burp Suite — Scanner — Active vs Passive Scanning
- [ ] T35 Burp Suite — Sequencer — Token Entropy Analysis
- [ ] T36 Burp Suite — Decoder and Comparer
- [ ] T37 Burp Suite — Collaborator — OOB Detection
- [ ] T38 Burp Suite — Target Scope and Sitemap
- [ ] T39 Burp Suite — Macros for Multi-Step Auth
- [ ] T40 Burp Suite — Extensions — Active Scan++ (enhanced scanner)
- [ ] T41 Burp Suite — Extensions — Autorize (access control testing)
- [ ] T42 Burp Suite — Extensions — JWT Editor
- [ ] T43 Burp Suite — Extensions — Turbo Intruder (high-speed)
- [ ] T44 Burp Suite — Extensions — Logger++ (enhanced logging)
- [ ] T45 Burp Suite — Extensions — Param Miner (cache poisoning)
- [ ] T46 Burp Suite — Extensions — HTTP Request Smuggler
- [ ] T47 Burp Suite — Extensions — Reflected Parameters
- [ ] T48 Burp Suite — Extensions — Retire.js (vulnerable JS)
- [ ] T49 Burp Suite — Extensions — CSRF Scanner
- [ ] T50 Burp Suite — Pro vs Community — Feature Differences

### Exploitation Tools (Extended)
- [ ] T51 searchsploit — Full Flag Reference
- [ ] T52 Metasploit — msfconsole Commands Reference
- [ ] T53 Metasploit — msfvenom Payload Types Reference
- [ ] T54 Metasploit — Post Modules Cheat Sheet
- [ ] T55 Metasploit — Resource Scripts (.rc files)
- [ ] T56 BeEF — Browser Exploitation Framework
- [ ] T57 SET — Social Engineering Toolkit
- [ ] T58 evilginx2 — AiTM Phishing Framework
- [ ] T59 GoPhish — Phishing Campaign Platform
- [ ] T60 sqlninja — SQL Server Exploitation
- [ ] T61 BBQSQL — Blind SQL Injection Framework
- [ ] T62 ghauri — Advanced SQLi Detection and Exploitation
- [ ] T63 xxeinjector — Automated XXE Exploitation
- [ ] T64 oxml_xxe — Office File XXE Payload Generator
- [ ] T65 PayloadsAllTheThings — Cheat Sheet Reference

### Network Exploitation (Extended)
- [ ] T66 enum4linux-ng — SMB Enumeration Deep Dive
- [ ] T67 smbmap — SMB Share Mapping and File Access
- [ ] T68 smbclient — SMB File Access CLI
- [ ] T69 rpcclient — RPC Enumeration (users, groups, SIDs)
- [ ] T70 ldapsearch — LDAP Enumeration
- [ ] T71 windapsearch — Windows LDAP Enumeration
- [ ] T72 kerbrute — Kerberos Username Enumeration and Brute Force
- [ ] T73 GetNPUsers.py — AS-REP Roasting
- [ ] T74 GetUserSPNs.py — Kerberoasting
- [ ] T75 secretsdump.py — Remote SAM/NTDS Dumping
- [ ] T76 wmiexec.py — WMI Command Execution
- [ ] T77 psexec.py — PsExec via Impacket
- [ ] T78 atexec.py — Task Scheduler Execution
- [ ] T79 dcomexec.py — DCOM Lateral Movement
- [ ] T80 reg.py — Remote Registry Manipulation

### Password Tools (Extended)
- [ ] T81 Hashcat — Mode 1000 NTLM Cracking
- [ ] T82 Hashcat — Mode 13100 Kerberoast Cracking
- [ ] T83 Hashcat — Mode 18200 AS-REP Roast Cracking
- [ ] T84 Hashcat — Rule-Based Attacks (best64.rule, OneRuleToRuleThemAll)
- [ ] T85 Hashcat — Hybrid Attacks (wordlist + mask)
- [ ] T86 Hashcat — Mask Attacks (bruteforce by pattern)
- [ ] T87 hashid / haiti — Hash Type Identification
- [ ] T88 hashes.com / crackstation — Online Hash Lookup
- [ ] T89 Default Credentials Databases — SecLists, defaultcreds-cheat-sheet
- [ ] T90 Username Wordlists — statistically-likely-usernames, names

### Cloud Tools (Extended)
- [ ] T91 Pacu — AWS Attack Modules Reference
- [ ] T92 aws-cli — IAM Enumeration Commands
- [ ] T93 aws-cli — S3 Public Bucket Check
- [ ] T94 aws-cli — EC2 Metadata Access
- [ ] T95 gcloud CLI — GCP Security Enumeration
- [ ] T96 az CLI — Azure Security Enumeration
- [ ] T97 AzureHound — BloodHound for Azure AD
- [ ] T98 ROADtools — Azure AD Exploration
- [ ] T99 StormSpotter — Azure Attack Graph
- [ ] T100 CloudMapper — AWS Environment Visualization

### Wireless and Physical Tools
- [ ] T101 aircrack-ng Suite — Full Reference (airmon, airodump, aireplay, aircrack)
- [ ] T102 hcxtools — PMKID and Hash Extraction
- [ ] T103 hcxdumptool — Capturing Hashes Without Clients
- [ ] T104 wifite2 — Automated Wi-Fi Auditing
- [ ] T105 bettercap — Network MITM Framework
- [ ] T106 hostapd-wpe — Evil Twin with WPA2-Enterprise
- [ ] T107 eaphammer — EAP Attacks Toolkit

### Forensics and Defense Tools
- [ ] T108 Volatility 3 — Full Plugin Reference
- [ ] T109 Autopsy — Disk Forensics GUI
- [ ] T110 FTK Imager — Forensic Image Creation
- [ ] T111 KAPE — Kroll Artifact Parser and Extractor
- [ ] T112 CyberChef — Data Transformation and Analysis
- [ ] T113 ExifTool — Metadata Extraction
- [ ] T114 binwalk — Firmware and Binary Analysis
- [ ] T115 Ghidra — NSA Reverse Engineering Tool
- [ ] T116 Cutter / Radare2 — Binary Analysis Framework
- [ ] T117 x64dbg — Windows Debugger for Malware Analysis
- [ ] T118 PEStudio — Static PE Analysis
- [ ] T119 DIE (Detect-It-Easy) — Packer and Compiler Detection
- [ ] T120 Any.run — Interactive Malware Sandbox

---

## MODULE 60-EX — Real-World Scenarios and Case Studies (70 topics)

### Famous CVEs and Exploits — Walkthroughs
- [ ] R01 CVE-2021-44228 — Log4Shell (Log4j RCE) — Full Exploit Chain
- [ ] R02 CVE-2021-26855 — ProxyLogon (Exchange SSRF + RCE)
- [ ] R03 CVE-2021-34473 — ProxyShell (Exchange RCE Chain)
- [ ] R04 CVE-2022-26134 — Confluence OGNL Injection RCE
- [ ] R05 CVE-2022-22965 — Spring4Shell (Spring MVC RCE)
- [ ] R06 CVE-2023-44487 — HTTP/2 Rapid Reset DoS
- [ ] R07 CVE-2023-23397 — Outlook Zero-Click NTLM Hash Leak
- [ ] R08 CVE-2023-34362 — MOVEit SQLi and RCE (cl0p campaign)
- [ ] R09 CVE-2024-3400 — PAN-OS Command Injection (Firewall RCE)
- [ ] R10 CVE-2024-21762 — Fortinet SSL VPN RCE
- [ ] R11 EternalBlue (MS17-010) — SMB RCE Full Walkthrough
- [ ] R12 BlueKeep (CVE-2019-0708) — RDP Pre-Auth RCE
- [ ] R13 Zerologon (CVE-2020-1472) — Full Domain Takeover
- [ ] R14 PrintNightmare (CVE-2021-34527) — Spooler RCE
- [ ] R15 PwnKit (CVE-2021-4034) — Linux Universal PrivEsc

### Bug Bounty Case Studies (Public Disclosures)
- [ ] R16 Facebook — SSRF via Profile Picture URL → Internal Services
- [ ] R17 Facebook — IDOR on Graph API → Mass Account Data
- [ ] R18 Uber — Subdomain Takeover → Full Credential Theft
- [ ] R19 Shopify — Partner API IDOR → Admin Panel Access
- [ ] R20 Twitter — XSS in OAuth Flow → Token Theft
- [ ] R21 GitHub — SSRF via SVG Import → Internal Network Access
- [ ] R22 HackerOne — Stored XSS on Reports → ATO of Any Researcher
- [ ] R23 GitLab — Path Traversal → Source Code Leak (Critical)
- [ ] R24 Yahoo — SQLi in Login → Full DB Dump
- [ ] R25 Starbucks — IDOR on Gift Cards → Unlimited Balance
- [ ] R26 US DoD — SQL Injection → PII of Military Personnel
- [ ] R27 Airbnb — SSRF via PDF Generator → Cloud Metadata → RCE
- [ ] R28 Snapchat — IDOR → Any User's Photo Access
- [ ] R29 Twitch — Source Code Leak via Misconfigured Git
- [ ] R30 Tesla — IDOR → Remote Vehicle Control

### HackTheBox Machine Methodology
- [ ] R31 HTB Methodology — Recon → Foothold → PrivEsc → Proof
- [ ] R32 HTB Easy Machines — Web-Focused Walkthroughs
- [ ] R33 HTB Medium Machines — Chaining Vulnerabilities
- [ ] R34 HTB Hard Machines — Advanced PrivEsc
- [ ] R35 HTB Active Directory Labs — Forest, Active, Cascade, Sauna

### TryHackMe Learning Paths
- [ ] R36 TryHackMe — Jr Penetration Tester Path Overview
- [ ] R37 TryHackMe — SOC Level 1 Path Overview
- [ ] R38 TryHackMe — Web Fundamentals Path
- [ ] R39 TryHackMe — OWASP Top 10 Room
- [ ] R40 TryHackMe — Offensive Pentesting Path

### CTF Methodology
- [ ] R41 CTF — Web Challenge Approach (Source → Params → Auth → Logic)
- [ ] R42 CTF — Crypto Challenges (RSA, XOR, Hash, Base Encoding)
- [ ] R43 CTF — Forensics Challenges (Steg, PCAP, Memory)
- [ ] R44 CTF — Reverse Engineering (Ghidra, strings, ltrace)
- [ ] R45 CTF — Binary Exploitation (BOF, ROP, Format String)
- [ ] R46 CTF — Reporting and Writeup Style

### Full Simulated Engagements
- [ ] R47 Engagement 1 — E-commerce Site (SQLi → Admin → RCE)
- [ ] R48 Engagement 2 — SaaS API (BOLA → Mass Assignment → ATO)
- [ ] R49 Engagement 3 — Cloud-Hosted App (SSRF → IMDSv1 → IAM → Takeover)
- [ ] R50 Engagement 4 — Corporate Network (Nmap → SMB → EternalBlue → AD)
- [ ] R51 Engagement 5 — Internal Web App (LFI → Log Poison → Shell → PrivEsc)
- [ ] R52 Engagement 6 — Mobile App (APK Decompile → API Key → Backend SQLi)
- [ ] R53 Engagement 7 — WordPress Site (WPScan → Plugin CVE → Webshell)
- [ ] R54 Engagement 8 — GraphQL API (Introspection → IDOR → Admin Mutation)
- [ ] R55 Engagement 9 — Active Directory Domain (Kerberoast → Hash Crack → DA)
- [ ] R56 Engagement 10 — Red Team Full Simulation (Phishing → Initial Access → AD Takeover)

### Building Skills
- [ ] R57 Home Lab Setup — VirtualBox/VMware Network Config
- [ ] R58 Vulnerable VMs — DVWA, WebGoat, Metasploitable, VulnHub
- [ ] R59 Practice Platforms — HackTheBox, TryHackMe, PortSwigger, PentesterLab
- [ ] R60 Bug Bounty — Getting Started (Scope, Tools, Methodology)
- [ ] R61 Bug Bounty — Writing a Good Report
- [ ] R62 Bug Bounty — Triage Process and Response
- [ ] R63 Bug Bounty — Maximizing Impact with Chaining
- [ ] R64 Certification Roadmap — CEH → eJPT → OSCP → OSEP → CRTO → CRTE
- [ ] R65 OSCP Exam Methodology and Tips
- [ ] R66 eJPT — Entry Level Certification Guide
- [ ] R67 CRTO — Red Team Ops Certification Guide
- [ ] R68 Bug Bounty Income — Statistics and Realistic Expectations
- [ ] R69 Purple Team Exercise — Running an Internal Simulation
- [ ] R70 Writing a VAPT Training Course — Curriculum Design

---

## PLAN 3 TOTAL

| Module | Topics |
|--------|--------|
| 43-EX Windows PrivEsc (Full) | 85 |
| 44-EX Linux PrivEsc (Full) | 75 |
| 45-EX Post-Exploitation (Full) | 65 |
| 56-EX Defensive Security (Full) | 80 |
| 57-EX OWASP Complete | 50 |
| 59-EX Tools Reference (Extended) | 120 |
| 60-EX Real-World Scenarios | 70 |
| **Plan 3 Total** | **545** |

---

## OVERALL GRAND TOTAL

| Plan | Topics |
|------|--------|
| Plan 1 (VAPT-Vault-Plan.md) — 60 modules | 1,246 |
| Plan 2 (VAPT-Plan2-PortSwigger.md) — 31 topics | 278 labs |
| Plan 3 (this file) — 7 expanded modules | 545 |
| **COMBINED TOTAL** | **1,791 topics + 278 labs** |

---

## Related Files
- [[VAPT-Vault-Plan]] — main 60-module plan (1,246 topics)
- [[VAPT-Plan2-PortSwigger]] — all 278 PortSwigger labs
- [[VAPT-Vault-Spec]] — project decisions and build order
- [[00 - Learning Path]] — master vault index
