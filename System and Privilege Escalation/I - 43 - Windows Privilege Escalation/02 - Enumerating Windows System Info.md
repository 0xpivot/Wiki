---
tags: [windows, privesc, pentesting, red-team]
difficulty: intermediate
module: "43 - Windows Privilege Escalation"
topic: "43.02 Enumerating Windows System Info"
---

# Enumerating Windows System Info

## Introduction

The foundation of any successful privilege escalation attempt on a Windows system is comprehensive enumeration. Before a single exploit is compiled or a payload is generated, you must thoroughly understand the environment in which you are operating. Enumeration provides the critical context needed to identify vulnerabilities, misconfigurations, and potential attack paths. 

System enumeration is divided into several categories:
1.  **Operating System and Architecture Identification**
2.  **User and Group Information**
3.  **Network Configuration**
4.  **Running Processes and Services**
5.  **Installed Software and Patch Levels**
6.  **Hunting for Sensitive Files and Credentials**

This note covers the manual command-line techniques used to gather this information, relying purely on Living Off The Land (LOTL) binaries built into Windows.

---

## 1. Operating System and Architecture Identification

Knowing the exact operating system version, build number, and architecture is crucial. Exploits that work on Windows Server 2012 R2 might crash a Windows Server 2019 system. Similarly, deploying a 32-bit reverse shell payload on a 64-bit architecture can lead to execution failures or unexpected behavior.

### Systeminfo
The `systeminfo` command provides a comprehensive overview of the host.

```cmd
C:\> systeminfo

Host Name:                 WIN-SRV-2019
OS Name:                   Microsoft Windows Server 2019 Standard
OS Version:                10.0.17763 N/A Build 17763
OS Manufacturer:           Microsoft Corporation
OS Configuration:          Standalone Server
OS Build Type:             Multiprocessor Free
Registered Owner:          Windows User
Registered Organization:
Product ID:                00000-00000-00000-AAAAA
Original Install Date:     10/12/2021, 10:14:32 AM
System Boot Time:          11/5/2023, 8:22:10 AM
System Manufacturer:       VMware, Inc.
System Model:              VMware Virtual Platform
System Type:               x64-based PC
Processor(s):              2 Processor(s) Installed.
```
*Key takeaways here:* The OS is Windows Server 2019, Build 17763, and the System Type is an `x64-based PC`. 

### Querying the Architecture specifically
If you only need the architecture quickly, you can query environmental variables:

```cmd
C:\> echo %PROCESSOR_ARCHITECTURE%
AMD64
```
*Note: AMD64 refers to the 64-bit extension of the x86 architecture, meaning the system is 64-bit. `x86` would indicate a 32-bit system.*

### Windows Management Instrumentation (WMI)
You can also use `wmic` to pull specific OS data in a cleaner format:

```cmd
C:\> wmic os get name, version, architecture
Architecture  Name                                                              Version
64-bit        Microsoft Windows Server 2019 Standard|C:\Windows|\Device\Harddisk0\Partition2  10.0.17763
```

---

## 2. User and Group Information

Understanding your current context is the next step. Who are you? What privileges do you hold? Who else is on the system?

### Current User Context
The `whoami /all` command is arguably the most important initial command to run. It reveals your SID, your group memberships, and your explicit privileges.

```cmd
C:\> whoami /all

USER INFORMATION
----------------

User Name             SID
===================== ==============================================
windomain\svc_apache S-1-5-21-394823901-382910382-382910382-1002

GROUP INFORMATION
-----------------

Group Name                             Type             SID          Attributes
====================================== ================ ============ ==================================================
Everyone                               Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                          Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\SERVICE                   Well-known group S-1-5-6      Mandatory group, Enabled by default, Enabled group
CONSOLE LOGON                          Well-known group S-1-2-1      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users       Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization         Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group
LOCAL                                  Well-known group S-1-2-0      Mandatory group, Enabled by default, Enabled group

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                               State
============================= ========================================= ========
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled
SeImpersonatePrivilege        Impersonate a client after authentication Enabled
SeCreateGlobalPrivilege       Create global objects                     Enabled
```
*Key Takeaway:* In this output, the presence of `SeImpersonatePrivilege` is a massive red flag for defenders and a golden ticket for attackers. This privilege can be abused using tools like PrintSpoofer or RoguePotato to execute commands as SYSTEM.

### Enumerating Local Users
To see all local user accounts:

```cmd
C:\> net user
User accounts for \\WIN-SRV-2019

-------------------------------------------------------------------------------
Administrator            DefaultAccount           Guest
svc_apache               WDAGUtilityAccount
The command completed successfully.
```

To view details about a specific user (e.g., checking if an account is disabled or when it was last logged in):
```cmd
C:\> net user svc_apache
```

### Enumerating Local Groups
To view all local groups:
```cmd
C:\> net localgroup
```

To see who is a member of the local Administrators group:
```cmd
C:\> net localgroup Administrators
Alias name     Administrators
Comment        Administrators have complete and unrestricted access to the computer/domain

Members

-------------------------------------------------------------------------------
Administrator
Domain Admins
The command completed successfully.
```

---

## 3. Network Configuration

Network configuration helps map out the host's internal and external connectivity. It reveals dual-homed systems, active connections, and listening ports, which might indicate internally bound services (like a database running on `127.0.0.1:3306`) that were not visible from the outside.

### Interface Configuration
```cmd
C:\> ipconfig /all
```
This shows IP addresses, subnets, gateways, and DNS servers. It helps identify if the machine sits on multiple networks (e.g., an internet-facing DMZ and an internal management VLAN).

### Routing Table
```cmd
C:\> route print
```
Reviewing the routing table can identify hidden subnets that the machine has explicit routes to, which are prime targets for pivoting.

### Active Connections and Listening Ports
The `netstat` command is vital for finding internal services.

```cmd
C:\> netstat -ano

Active Connections

  Proto  Local Address          Foreign Address        State           PID
  TCP    0.0.0.0:80             0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       892
  TCP    0.0.0.0:445            0.0.0.0:0              LISTENING       4
  TCP    127.0.0.1:3306         0.0.0.0:0              LISTENING       2044
  TCP    192.168.1.50:49211     10.10.10.5:443         ESTABLISHED     3120
```
*Key Takeaway:* Port 3306 (MySQL) is listening strictly on `127.0.0.1`. This means it was inaccessible during external port scanning but is fully accessible locally. If MySQL is running as SYSTEM or has weak credentials, it becomes a local privesc vector. The `PID` column allows you to correlate the port with a specific process.

---

## 4. Running Processes and Services

Identifying what is currently running on the system is critical. A vulnerable third-party application or a misconfigured service is often the path to SYSTEM.

### Tasklist
```cmd
C:\> tasklist /V
```
The `/V` flag provides verbose output, which includes the user context under which the process is running. However, low-privileged users often cannot see the owner of processes running under other accounts.

### WMIC Process Enumeration
A more powerful way to enumerate processes is using WMI:
```cmd
C:\> wmic process get caption, executablepath, commandline
```
This output is incredibly valuable because `commandline` might reveal passwords or tokens passed as arguments to a process upon startup.

### Service Enumeration
Services are critical targets because they often run as `NT AUTHORITY\SYSTEM`.
To see all started services:
```cmd
C:\> net start
```

For more detailed information, `wmic` is preferred:
```cmd
C:\> wmic service get name, displayname, pathname, startmode
```
This command output is the foundation for finding Unquoted Service Paths and Modifiable Service Binaries.

---

## 5. Installed Software and Patch Levels

Knowing what software is installed can lead to identifying known local privilege escalation CVEs for third-party apps. Missing Windows patches indicate the potential for kernel exploits.

### Listing Installed Software
Software installed via Windows Installer can be queried:
```cmd
C:\> wmic product get name, version, vendor
```
*Note: `wmic product` can be very slow and sometimes causes MSIs to self-repair, creating unnecessary noise. Alternatively, querying the registry is safer and faster.*

Registry check for 64-bit software:
```cmd
C:\> reg query HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall /s | findstr /i "DisplayName"
```
Registry check for 32-bit software on a 64-bit system:
```cmd
C:\> reg query HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall /s | findstr /i "DisplayName"
```

### Checking Patch Levels (Hotfixes)
Identifying missing patches allows an attacker to compile a specific kernel exploit (e.g., MS16-032, CVE-2021-36934).
```cmd
C:\> wmic qfe get Caption, Description, HotFixID, InstalledOn
```
```text
Caption                                 Description      HotFixID   InstalledOn
http://support.microsoft.com/?kbid=4535680  Security Update  KB4535680  10/12/2021
http://support.microsoft.com/?kbid=4580325  Update           KB4580325  10/12/2021
```
You can cross-reference the `HotFixID` with exploit databases or tools like `Windows-Exploit-Suggester` to find applicable vulnerabilities.

---

## 6. Hunting for Sensitive Files and Credentials

Often, the fastest path to administrative privileges isn't a complex exploit, but rather finding a plain-text password left behind by an administrator.

### The File System Search
Searching the file system for files containing the word "password" or "pass".

```cmd
C:\> dir /s /b *pass* == *cred* == *vnc* == *.config*
C:\> findstr /si password *.xml *.ini *.txt *.config
```

### Common High-Value Files
Attackers routinely check standard locations for unattended installation files and scripts:
- `C:\sysprep.inf`
- `C:\sysprep\sysprep.xml`
- `C:\Windows\system32\sysprep.inf`
- `C:\Windows\Panther\Unattend\Unattended.xml`
- `C:\Windows\Panther\Unattended.xml`

These XML files are used for bulk provisioning Windows machines and often contain the local administrator password encoded in base64.

### Checking the Registry for AutoLogon
If the machine is configured to automatically log in, the credentials might be stored in plain text in the registry.
```cmd
C:\> reg query "HKLM\SOFTWARE\Microsoft\Windows NT\Currentversion\Winlogon"
```
Look for `DefaultUserName`, `DefaultDomainName`, and `DefaultPassword`.

### Windows Credential Manager
Sometimes credentials are saved in the Windows Credential Manager. You can query these using `cmdkey`.
```cmd
C:\> cmdkey /list

Currently stored credentials:

    Target: Domain:interactive=WIN-SRV-2019\Administrator
    Type: Domain Password
    User: WIN-SRV-2019\Administrator
```
If credentials are saved, you might be able to execute commands as that user via `runas`:
```cmd
C:\> runas /savecred /user:WIN-SRV-2019\Administrator "cmd.exe /c reverse_shell.exe"
```

---

## Enumeration Methodology Summary Diagram

```text
+--------------------------------------------------------------------------+
|                      SYSTEM ENUMERATION TREE                             |
+--------------------------------------------------------------------------+
                               |
            +------------------+------------------+
            |                  |                  |
    +-------v-------+  +-------v-------+  +-------v-------+
    | System Context|  | User Context  |  | Network Context|
    +-------+-------+  +-------+-------+  +-------+-------+
            |                  |                  |
            |                  |                  |
      systeminfo          whoami /all        ipconfig /all
      wmic os             net users          netstat -ano
      wmic qfe            net localgroup     route print
            |                  |                  |
            +------------------+------------------+
                               |
            +------------------+------------------+
            |                  |                  |
    +-------v-------+  +-------v-------+  +-------v-------+
    | Running State |  | Installed Apps|  | Loot / Creds   |
    +-------+-------+  +-------+-------+  +-------+-------+
            |                  |                  |
            |                  |                  |
       tasklist /v        wmic product      dir /s /b *pass*
       wmic process       reg query apps    sysprep.xml files
       wmic service                         reg query Winlogon
```

## Chaining Opportunities
- **Vulnerability Identification:** The output of `wmic service` feeds directly into identifying [[03 - Unquoted Service Paths]] and [[05 - Modifiable Service Binaries]].
- **Exploitation Execution:** Missing hotfixes identified via `wmic qfe` will dictate which Kernel exploits can be leveraged for ultimate elevation.
- **Pivoting:** Discovering internal listening ports via `netstat` informs the need for Port Forwarding and [[Lateral Movement Overview]].

## Related Notes
- [[01 - Windows PrivEsc Methodology Overview]]
- [[03 - Unquoted Service Paths]]
- [[04 - Weak Service Permissions]]
- [[05 - Modifiable Service Binaries]]
- [[Token Privileges and Abuse]]
