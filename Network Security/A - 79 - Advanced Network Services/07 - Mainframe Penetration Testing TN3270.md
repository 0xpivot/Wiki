---
tags: [network, advanced, ics, scada, sap, vapt]
difficulty: advanced
module: "79 - Advanced Network Services: ICS, SCADA, Mainframes, SAP"
topic: "79.07 Mainframe Penetration Testing TN3270"
---

# 79.07 Mainframe Penetration Testing TN3270

## 1. Introduction to Mainframes and TN3270

Despite the rise of cloud computing, IBM Mainframes running z/OS remain the backbone of the world's largest financial institutions, government agencies, and airlines. These systems handle immense volumes of transaction processing with unparalleled reliability. However, from a penetration testing perspective, they represent a highly obscure, specialized, and often poorly understood attack surface.

The primary method for interactive administrative and user access to a mainframe is through terminal emulation. Historically, this was done via physical IBM 3270 terminal hardware. Today, this access is provided over IP networks using the **TN3270 protocol** (Telnet 3270).

TN3270 operates similarly to standard Telnet but is designed specifically to transport the complex data streams required to render the 3270 screen format (which is block-oriented rather than character-oriented) and handle EBCDIC encoding, unlike the ASCII encoding used by almost everything else.

## 2. Mainframe Architecture and Subsystems Overview

To test a mainframe, one must understand its core components:
-   **z/OS**: The operating system itself.
-   **VTAM (Virtual Telecommunications Access Method)**: The networking subsystem. It acts as a switchboard. When you connect via TN3270, VTAM presents a menu or prompt allowing you to connect to various applications.
-   **TSO/E (Time Sharing Option/Extensions)**: The primary interactive command-line environment for administrators and programmers. It is akin to a Unix shell.
-   **CICS (Customer Information Control System)**: A transaction processing server. Applications written in COBOL or PL/I run here. It handles millions of transactions per second (e.g., ATM withdrawals).
-   **RACF (Resource Access Control Facility)**: The security subsystem (though ACF2 or TopSecret might be used instead). It controls user authentication, access to datasets (files), and authorization for commands.
-   **JCL (Job Control Language)**: A scripting language used to submit batch jobs to the operating system.

## 3. Reconnaissance and Enumeration

### 3.1 Network Discovery
Mainframe TN3270 services typically listen on TCP ports **23** or **992** (for TN3270E over TLS).
```bash
# Basic Nmap scan for TN3270 services
nmap -p 23,992 -sV -sC <Target_IP>
```
Nmap includes several excellent NSE scripts specifically for mainframes (developed largely by the "Mainframe Hacker Society" and researchers like Soldier of Fortran).

### 3.2 Extracting the VTAM Screen
When you connect to a TN3270 port, you are usually greeted by a VTAM screen. This screen often leaks information such as the Sysplex name, the LPAR (Logical Partition) name, and instructions on which applications are available.

You can use a terminal emulator like `x3270` (for Linux X11) or `c3270` (for curses-based terminal) to interact manually.
```bash
c3270 <Target_IP>:23
```

### 3.3 Application Enumeration
From the VTAM screen, an attacker attempts to access different applications by typing their common identifiers.
Typical commands entered at the VTAM screen:
-   `LOGON APPLID(TSO)` or simply `TSO` -> Attempts to reach the TSO environment.
-   `CICS`, `CICS1`, `CICP` -> Attempts to reach CICS environments.
-   `IMS` -> Attempts to reach the Information Management System.

Nmap can automate this VTAM enumeration:
```bash
nmap --script tn3270-screen,tn3270-info -p 23 <Target_IP>
```

## 4. Exploitation Vectors

### 4.1 Unencrypted Communications
If TN3270 is running over port 23 without TLS, all traffic, including user IDs and passwords, is transmitted in cleartext (though encoded in EBCDIC). An attacker with a network tap can passively capture mainframe credentials.
Wireshark can decode TN3270 traffic natively, translating EBCDIC to ASCII for readability.

### 4.2 User Enumeration
Mainframe security products (RACF, ACF2) often exhibit distinct behaviors depending on whether a user ID exists or not.
For example, in TSO, attempting to log in with a valid but incorrect password might yield a different error message or take a different amount of time compared to an invalid user ID. This allows an attacker to build a list of valid usernames.

```bash
nmap --script tso-enum --script-args tso-enum.users=users.txt -p 23 <Target_IP>
```

### 4.3 Brute Forcing and Password Spraying
Mainframes frequently enforce strict password lockouts (e.g., 3 failed attempts). Therefore, traditional brute-forcing is highly disruptive and easily detected.
**Password Spraying** is the preferred method. In a password spray, the attacker tries one common password (e.g., `SUMMER2026`) against a large list of valid user IDs.

Mainframe passwords have historical limitations:
-   Often limited to exactly 8 characters.
-   Historically case-insensitive (uppercase only).
-   Must start with an alphabetic character.

Tools like Hydra support TN3270 brute-forcing, but specialized tools or Nmap scripts are often more reliable due to the complex screen-scraping required to interpret login success/failure on 3270 terminals.

### 4.4 Default Credentials in CICS
CICS environments sometimes have default diagnostic or administrative transactions enabled with default credentials or no authentication required.
For instance, the `CEMT` (CICS Master Terminal) transaction allows an administrator to inquire about and alter the state of the CICS system. If left unprotected, an attacker can shut down the application or alter its configuration.
The `CEBR` (CICS Temporary Storage Browse) transaction can allow reading of temporary data queues, which might contain sensitive transactional data.

## 5. Post-Exploitation: The TSO Environment and JCL

### 5.1 Gaining a TSO Session
If an attacker successfully compromises a user's credentials, they will log into TSO. The interface is rudimentary and command-driven.
The first goal is to assess privileges.
-   `LU <username>`: List User information. Shows RACF group memberships.
-   `ISPF`: Launches the Interactive System Productivity Facility, a menu-driven interface that is much easier to navigate than raw TSO.

### 5.2 Submitting JCL for Code Execution
The most powerful mechanism for execution on a mainframe is submitting JCL (Job Control Language). JCL scripts define programs to be executed, the datasets (files) they require, and where to send the output.

An attacker can write JCL to execute arbitrary UNIX shell commands on the underlying z/OS UNIX System Services (USS) environment.

**Example Malicious JCL:**
```jcl
//ATTACK   JOB (ACCT),'HACKER',CLASS=A,MSGCLASS=X
//STEP1    EXEC PGM=BPXBATCH,PARM='SH id; uname -a; cat /etc/passwd'
//STDOUT   DD SYSOUT=*
//STDERR   DD SYSOUT=*
```
*Explanation:* This job uses the `BPXBATCH` program to drop into the USS shell and execute the `id`, `uname -a`, and `cat /etc/passwd` commands. The output is directed to the system output queue (`SYSOUT=*`).

The attacker would submit this job and then check the Spool (using the `SDSF` utility in ISPF) to view the execution results.

### 5.3 FTP to Mainframe (RCE via JCL)
A fascinating attack vector exists if the mainframe runs an FTP service. Mainframe FTP servers can be instructed to submit files directly to the Internal Reader (INTRDR), meaning uploaded files are executed as JCL jobs.

```bash
ftp <Target_IP>
Connected to <Target_IP>.
220-FTP SERVER IBM z/OS
Name: myuser
331 Send password please.
Password: mypassword
230 myuser is logged on.
ftp> quote site filetype=jes
200 SITE command was accepted
ftp> put malicious_job.jcl
200 Port request OK.
125 Sending Job to JES internal reader
250 Transfer completed successfully.
```
This technique provides rapid Remote Code Execution (RCE) without needing to navigate the complex 3270 terminal interface, provided the attacker has valid credentials.

## 6. Privilege Escalation

Privilege escalation on a mainframe generally involves bypassing RACF controls.
1.  **APF Authorized Libraries**: If an attacker has write access to a dataset (library) that is APF (Authorized Program Facility) authorized, they can upload a malicious program. APF-authorized programs can bypass all system security controls.
2.  **Weak Dataset Permissions**: Misconfigured RACF profiles might allow normal users to alter critical system configurations (e.g., SYS1.PARMLIB) or RACF databases directly.
3.  **Exploiting Unix System Services (USS)**: If the attacker drops into the USS environment via `BPXBATCH`, standard Unix privilege escalation techniques (SUID binaries, misconfigured cron jobs) can sometimes be applied.

## 7. Defense and Mitigation

-   **Enforce TN3270E with TLS**: Port 23 should be disabled. All terminal emulation must be forced over port 992 using strong TLS configurations to prevent credential sniffing.
-   **Strong Authentication**: Implement Multi-Factor Authentication (MFA) for all mainframe access. IBM RACF supports MFA integration.
-   **Strict Password Policies**: Enforce complex passwords and migrate away from legacy 8-character limits if the system supports modern password phrases.
-   **Minimize VTAM Information Leakage**: Configure VTAM to display a generic banner rather than listing available applications and system architecture details.
-   **Restrict JCL Submission**: Use RACF profiles to strictly limit which users are authorized to submit jobs to the internal reader, especially via FTP (`JES` filetype).
-   **Audit APF Libraries**: Regularly audit and strictly control write access to all APF-authorized datasets.

## 8. ASCII Diagram: TN3270 Attack Flow

```text
+-----------------------+                            +-----------------------------------------------+
|    Attacker Machine   |                            |               IBM z/OS Mainframe              |
|                       |                            |                                               |
| 1. Nmap Recon (p.23)  |                            |  +-----------------------------------------+  |
| 2. VTAM Enumeration   |----(Cleartext TN3270)----->|  |              VTAM Subsystem             |  |
| 3. Password Spraying  |                            |  |  (Displays Logon Screen / App List)     |  |
| 4. c3270 Terminal Emul|                            |  +-----------------------------------------+  |
+-----------------------+                            |       |                   |                   |
           |                                         |       v                   v                   |
           | (If FTP available)                      |  +----------+       +-----------+             |
           +----------(FTP Port 21)----------------->|  |   CICS   |       |   TSO/E   |             |
                      (SITE FILETYPE=JES)            |  | (Transac)|       | (Admin)   |             |
                                                     |  +----------+       +-----------+             |
                                                     |                           |                   |
                                                     |                           v                   |
                                                     |                     +-----------+             |
                                                     |                     |   JES2/3  |             |
                                                     |                     | (Job Exec)|             |
                                                     |                     +-----------+             |
                                                     |                           |                   |
                                                     |                           v                   |
                                                     |                 +-------------------+         |
                                                     |                 | USS (UNIX Shell)  |         |
                                                     |                 | - RCE achieved    |         |
                                                     |                 +-------------------+         |
                                                     +-----------------------------------------------+
```

## 9. Chaining Opportunities
-   **[[35 - Network Protocol Analyzers and Wireshark]]**: Deep packet inspection and EBCDIC translation are required to reverse engineer legacy custom protocols or extract credentials from unencrypted TN3270 traffic.
-   **[[42 - Unix Privilege Escalation]]**: Once JCL execution drops the attacker into the z/OS UNIX System Services (USS) shell, standard Unix local privilege escalation tactics can be employed.
-   **[[55 - Custom Scripting for Pentesting]]**: Exploiting mainframes heavily relies on writing custom Python scripts utilizing libraries like `py3270` to automate screen-scraping and interaction, as standard web or network tools fail against the 3270 data stream.

## 10. Related Notes
-   [[18 - Legacy System Penetration Testing]]
-   [[28 - Enterprise Architecture and Defense in Depth]]
-   [[50 - Secure File Transfer Protocols]]
