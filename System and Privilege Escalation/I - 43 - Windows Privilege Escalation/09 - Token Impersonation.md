---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.09 Token Impersonation"
---

# Token Impersonation

## Overview
Token impersonation is one of the most critical and heavily abused mechanisms in the Windows operating system for privilege escalation. In a typical Windows environment, access tokens are used to describe the security context of a process or thread. When an attacker gains access to a system with specific privileges—such as `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege`—they can exploit these capabilities to impersonate higher-privileged tokens (like NT AUTHORITY\SYSTEM) and execute code with elevated permissions. This technique is extremely prevalent in post-exploitation frameworks and is fundamentally linked to the architecture of the Windows security model.

Access tokens are objects that describe the security context of a process or thread. They contain the identity and privileges of the user account associated with the process or thread. When a user logs on, the system verifies the user's password by comparing it with information stored in a security database. If the password is authenticated, the system produces an access token. Every process executed on behalf of that user has a copy of this access token.

## Anatomy of Access Tokens
To understand token impersonation, one must deeply understand the anatomy of access tokens. An access token includes:
- **User SID (Security Identifier):** The unique identifier for the user.
- **Group SIDs:** SIDs for the groups the user belongs to.
- **Privileges:** The privileges held by the user or the user's groups.
- **Logon SID:** A SID that identifies the current logon session.
- **Primary vs. Impersonation Tokens:** A primary token is typically assigned to a process, while an impersonation token is typically assigned to a thread.

### Primary Tokens
Primary tokens are associated with a process. When a process is created, the Windows kernel assigns it a primary token that dictates the security context for that entire process. Any child processes spawned will, by default, inherit a copy of the parent's primary token.

### Impersonation Tokens
Impersonation tokens, on the other hand, are associated with threads. Windows allows individual threads within a process to operate under a different security context than the process itself. This is heavily utilized in client-server architectures where a server process (running as SYSTEM) needs to process requests on behalf of a client (running as a standard user). The thread handling the request will "impersonate" the client's token to ensure that the client cannot access resources they shouldn't be able to reach.

## Token Impersonation Levels
Windows defines four levels of token impersonation, which dictate what the server thread can do with the client's token:
1. **Anonymous (`SecurityAnonymous`):** The server cannot obtain identification information about the client, nor can it impersonate the client. It essentially hides the client's identity.
2. **Identification (`SecurityIdentification`):** The server can obtain information about the client, such as security identifiers and privileges, but it cannot impersonate the client to access objects. This is useful for auditing or access checks without acting on behalf of the client.
3. **Impersonation (`SecurityImpersonation`):** The server can impersonate the client's security context on its local system. The server cannot pass this token to another machine over the network. This is the sweet spot for local privilege escalation.
4. **Delegation (`SecurityDelegation`):** The most powerful level. The server can impersonate the client's security context on local systems and can also pass the token to remote systems over the network. This requires Active Directory delegation configurations.

## The Role of Privileges
To perform token impersonation effectively as an attacker, the compromised account must hold specific privileges. The two most critical ones are `SeImpersonatePrivilege` and `SeAssignPrimaryTokenPrivilege`.

### SeImpersonatePrivilege
This privilege allows a process to impersonate a token after it has been duplicated or acquired. It is commonly granted to the Local Service, Network Service, and local Administrators groups. If an attacker compromises a service account running with this privilege (such as IIS), they can coerce a higher-privileged account (like SYSTEM) to authenticate to a rogue service they control, capture the token, and use `SeImpersonatePrivilege` to execute code as SYSTEM.

### SeAssignPrimaryTokenPrivilege
This privilege allows a user to assign a primary token to a newly created process. It is required to call functions like `CreateProcessAsUser`. While slightly different from `SeImpersonatePrivilege`, it is often used in tandem or as an alternative when creating a fully detached process under a new security context.

## Attack Methodology
The general methodology for a token impersonation attack involves the following steps:
1. **Identify Privileges:** Verify if the current context has `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege` using `whoami /priv`.
2. **Coerce Authentication:** Force a privileged process (like the Print Spooler or a DCOM object) to authenticate to a named pipe or RPC endpoint controlled by the attacker.
3. **Capture the Token:** When the privileged process connects, the attacker's server thread impersonates the client, thereby acquiring an impersonation token of the privileged entity.
4. **Duplicate the Token:** The impersonation token is duplicated and converted into a primary token if a new process needs to be spawned.
5. **Execute Code:** The duplicated token is used to create a new process (e.g., cmd.exe or a reverse shell payload) running under the privileged context.

## Technical Implementation (C++ Windows API)
Understanding the underlying Windows API calls is crucial for understanding how tools like incognito and the Potato family work under the hood.

```cpp
#include <windows.h>
#include <iostream>

void ImpersonateAndExecute() {
    HANDLE hToken = NULL;
    HANDLE hDuplicateToken = NULL;
    STARTUPINFO si = { sizeof(STARTUPINFO) };
    PROCESS_INFORMATION pi;

    // 1. Acquire a handle to a process running as SYSTEM (e.g., winlogon.exe)
    // Requires SeDebugPrivilege to open the process with PROCESS_QUERY_INFORMATION
    HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION, FALSE, 1234); // Replace 1234 with actual PID
    
    // 2. Open the access token associated with the process
    if (OpenProcessToken(hProcess, TOKEN_DUPLICATE | TOKEN_ASSIGN_PRIMARY | TOKEN_QUERY, &hToken)) {
        
        // 3. Duplicate the token to create a primary token
        if (DuplicateTokenEx(hToken, MAXIMUM_ALLOWED, NULL, SecurityImpersonation, TokenPrimary, &hDuplicateToken)) {
            
            // 4. Create a new process using the duplicated SYSTEM token
            if (CreateProcessWithTokenW(hDuplicateToken, LOGON_WITH_PROFILE, L"C:\\Windows\\System32\\cmd.exe", NULL, 0, NULL, NULL, &si, &pi)) {
                std::cout << "Successfully spawned cmd.exe as SYSTEM!" << std::endl;
            }
            CloseHandle(hDuplicateToken);
        }
        CloseHandle(hToken);
    }
    CloseHandle(hProcess);
}
```
*Note: The above code is a conceptual representation and requires appropriate privileges (like `SeDebugPrivilege` or `SeImpersonatePrivilege` depending on the acquisition method) to succeed.*

## ASCII Diagram: Token Impersonation Flow

```text
+---------------------+                            +----------------------+
| Privileged Process  |                            |   Attacker Process   |
| (e.g., SYSTEM)      |                            | (e.g., IIS AppPool)  |
+---------------------+                            +----------------------+
          |                                                   |
          | 1. Connects to attacker-controlled Named Pipe     |
          |-------------------------------------------------->|
          |                                                   |
          |                                                   | 2. ImpersonateNamedPipeClient()
          |                                                   |    (Requires SeImpersonatePrivilege)
          |                                                   |
          |                                                   | 3. Thread now runs as SYSTEM
          |                                                   |    (Impersonation Token)
          |                                                   |
          |                                                   | 4. OpenThreadToken()
          |                                                   |    DuplicateTokenEx() -> Primary Token
          |                                                   |
          |                                                   | 5. CreateProcessWithTokenW()
          |                                                   v
                                                   +----------------------+
                                                   |    New Process       |
                                                   |    (cmd.exe)         |
                                                   | Context: SYSTEM      |
                                                   +----------------------+
```

## Practical Scenarios & Tooling
In practical penetration testing, token impersonation is rarely performed manually via C++ programs compiled on the fly. Instead, automated tools and post-exploitation frameworks are utilized.

### Incognito (Metasploit / Standalone)
Incognito is a classic tool that automates the process of enumerating available tokens on a system and allowing the attacker to impersonate them. It is integrated into Meterpreter.
```bash
meterpreter > use incognito
meterpreter > list_tokens -u
meterpreter > impersonate_token "NT AUTHORITY\\SYSTEM"
```
The effectiveness of incognito heavily relies on the tokens currently available in memory. If an administrator recently logged in or a service running as SYSTEM is active, their tokens might be accessible if the attacker has `SeDebugPrivilege`.

### The Potato Suite
When `SeImpersonatePrivilege` is available (common in service accounts like SQL Server or IIS), but no high-privileged tokens are casually lying around in memory, attackers use the "Potato" exploits. These tools actively coerce SYSTEM to authenticate, thereby generating a token on demand.
- **Juicy Potato:** Exploits DCOM object instantiation to coerce authentication.
- **Rogue Potato:** Bypasses patches to Juicy Potato by using RPC over SMB.
- **PrintSpoofer:** Exploits the Print Spooler service to write a token to a named pipe.

## Defenses and Mitigations
Defending against token impersonation requires a defense-in-depth approach, primarily focusing on the principle of least privilege and hardening the OS environment.
1. **Remove SeImpersonatePrivilege:** Ensure that service accounts, especially those exposed to external input (like web servers and database engines), are not granted `SeImpersonatePrivilege` unless absolutely necessary.
2. **Use Managed Service Accounts:** Implement Group Managed Service Accounts (gMSAs) which abstract password management and often run with restricted privilege sets compared to traditional service accounts.
3. **Patching:** Keep the Windows operating system fully patched. Many token impersonation vectors (like specific DCOM or RPC coercion techniques) are regularly patched by Microsoft.
4. **Disable Unnecessary Services:** Services like the Print Spooler, which are heavily abused for coercion, should be disabled on servers where they are not required (e.g., Domain Controllers, Web Servers).
5. **Endpoint Detection and Response (EDR):** Modern EDR solutions monitor API calls like `CreateProcessWithTokenW` and `DuplicateTokenEx`, especially when invoked from suspicious processes like IIS worker processes or SQL Server executing xp_cmdshell.

## Advanced Considerations: Token Manipulation
Beyond simple impersonation, attackers with sufficient privileges can perform token manipulation to evade detection. This involves:
- **Filtering Privileges:** Removing privileges from a token to create a "restricted token" before launching a process, which might bypass certain security checks or sandboxing.
- **Token Stealing via Kernel Exploits:** If an attacker achieves kernel execution, they can directly manipulate the `EPROCESS` structures in memory, copying the token pointer from the SYSTEM process to their own process, completely bypassing user-land API checks and EDR hooks.
- **Primary Token Replacement:** Using native undocumented APIs like `NtSetInformationProcess` to hot-swap the primary token of a running process, avoiding the creation of a new process which might be heavily scrutinized by EDR.

## Extended Deep Dive: Understanding Security Identifiers (SIDs)
A Security Identifier (SID) is a unique value of variable length used to identify a security principal or security group in Windows operating systems. Well-known SIDs that identify generic groups and generic users are critical during token impersonation analysis.
- `S-1-5-18`: Local System
- `S-1-5-19`: NT Authority (LocalService)
- `S-1-5-20`: Network Service
- `S-1-5-32-544`: Administrators group

When an attacker evaluates a token for impersonation, they are primarily looking for tokens that contain the `S-1-5-18` SID or the `S-1-5-32-544` group SID. The presence of these SIDs dictates the ultimate power of the stolen token. 

The security subsystem (LSASS) uses the SIDs in the access token to check against the Discretionary Access Control List (DACL) of the target object. If the impersonated token has a SID that matches an ALLOW ACE (Access Control Entry) in the DACL, access is granted.

## Chaining Opportunities
- Can be combined with [[10 - JuicyPotato RoguePotato PrintSpoofer]] to weaponize `SeImpersonatePrivilege`.
- Useful after exploiting a web application via RCE to escape the IIS AppPool context (see [[02 - Web Application RCE to Privesc]]).
- Token manipulation can be a follow-up action after a successful [[08 - Kernel Exploit]] to map the SYSTEM token cleanly.

## Related Notes
- [[10 - JuicyPotato RoguePotato PrintSpoofer]]
- [[11 - Hot Potato Sweet Potato Ghost Potato]]
- [[04 - Privileges and Rights Escalation]]
- [[01 - Active Directory Delegation]]
