---
tags: [active-directory, basics, foundations, vapt]
difficulty: beginner
module: "66 - AD Foundations and Core Concepts"
topic: "66.14 User Account Control UAC in AD Environments"
---

# User Account Control (UAC) in AD Environments

User Account Control (UAC) is a fundamental security component in Microsoft Windows that mitigates the impact of malware and prevents unauthorized system changes. Introduced in Windows Vista, UAC ensures that all users—even those in the local `Administrators` group—run applications with standard user privileges until an administrator explicitly authorizes an elevation.

In Active Directory VAPT (Vulnerability Assessment and Penetration Testing), understanding UAC is critical because it directly impacts remote execution, lateral movement, and privilege escalation techniques.

## The Concept of Split Tokens

When a user who is a member of the local `Administrators` group logs into a Windows machine, the Local Security Authority (LSA) creates **two** access tokens for the user:

1.  **Filtered Token (Medium Integrity):** This token has administrative privileges stripped away. The standard desktop shell (`explorer.exe`) and most applications launch using this token.
2.  **Elevated Token (High Integrity):** This token contains full administrative privileges. It is kept inactive and is only attached to a process when the user consents to a UAC prompt (Run as Administrator).

Standard users who are not in the administrators group only receive a single standard token.

### Integrity Levels (Mandatory Access Control)
Windows assigns Integrity Levels to processes and objects to prevent lower-integrity processes from interacting with higher-integrity ones.
*   **System Integrity:** Kernel, LSASS, System services.
*   **High Integrity:** Elevated administrator processes (e.g., an elevated Command Prompt).
*   **Medium Integrity:** Standard user processes (e.g., standard Command Prompt, File Explorer).
*   **Low Integrity:** Sandboxed processes (e.g., Web browser renderers).

## UAC in the Context of Remote Access

This is where UAC becomes incredibly relevant to penetration testers. UAC behaves differently depending on how you are accessing the machine (locally via GUI vs. remotely via SMB/WMI/WinRM) and what kind of account you are using (Local Admin vs. Domain Admin).

### The Remote UAC Restrictions

When you attempt to connect to a machine remotely (e.g., using `wmiexec.py`, `psexec`, or WinRM) using an administrative account, Windows applies remote UAC restrictions.

1.  **Domain Accounts (e.g., Domain Admins):**
    If you use a Domain account that is a member of the local Administrators group, **Remote UAC is disabled**. Windows grants the remote session the High Integrity elevated token automatically.
    *   *Attacker perspective:* If you compromise a Domain Admin or a domain user in the local admins group, lateral movement via SMB/WMI will succeed seamlessly.

2.  **Local Accounts (e.g., `.\Administrator` or `.\ITAdmin`):**
    If you use a Local account to authenticate over the network, **Remote UAC is enabled**. Windows restricts the network session to the Filtered (Medium Integrity) token.
    *   *Attacker perspective:* Even if you have the password for a local user who is in the Administrators group, your remote commands (like `wmiexec`) will fail with `ACCESS_DENIED` because you cannot interactively click the UAC prompt over RPC/SMB to elevate your token.

### Exceptions to Remote UAC
*   **The Built-in Administrator Account (RID 500):** By default, the true built-in `.\Administrator` account bypasses UAC entirely, even remotely. You can always use this account for lateral movement if it is active.
*   **`LocalAccountTokenFilterPolicy`:** If a sysadmin creates this registry key and sets it to `1` (`HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System`), it completely disables Remote UAC for all local administrative accounts. This is a massive boon for attackers.

## ASCII Diagram: Remote UAC Authentication Flow

```text
+-------------------------------------------------------------------------+
|                  REMOTE AUTHENTICATION ATTEMPT (SMB/WMI)                |
+-------------------------------------------------------------------------+
                                   |
                                   v
                      [ IS ACCOUNT A LOCAL ADMIN? ]
                      /                           \
                   YES                            NO
                   /                                \
                  v                                  v
    [ WHAT TYPE OF ACCOUNT? ]                  [ ACCESS DENIED ]
           /                 \                 (Standard user cannot
      DOMAIN ACCOUNT      LOCAL ACCOUNT         run remote admin tasks)
           |                   |
           v                   v
[ REMOTE UAC DISABLED ]  [ IS ACCOUNT BUILT-IN ADMIN (RID 500)? ]
   Token = HIGH                /                        \
   Exec = SUCCESS             YES                       NO
                              /                          \
                             v                            v
                  [ REMOTE UAC DISABLED ]     [ IS LocalAccountToken... = 1? ]
                     Token = HIGH                      /                 \
                     Exec = SUCCESS                  YES                 NO
                                                     /                    \
                                                    v                      v
                                         [ REMOTE UAC DISABLED ]  [ REMOTE UAC ENABLED ]
                                            Token = HIGH             Token = MEDIUM
                                            Exec = SUCCESS           Exec = ACCESS_DENIED
```

## Bypassing UAC (Local Escalation)

If an attacker gains a shell as a local administrator, but it is running in Medium Integrity, they must perform a **UAC Bypass** to obtain a High Integrity shell. 

UAC bypasses typically exploit auto-elevating binaries. Microsoft ships certain binaries (like `EventVwr.exe`, `Fodhelper.exe`, `ComputerDefaults.exe`) that bypass the UAC prompt automatically because they are signed by Microsoft and located in trusted directories.

**Mechanism:** Many of these binaries query the user's `HKEY_CURRENT_USER` (HKCU) registry hive for specific configuration paths before executing system tasks. Because standard users have write access to their own HKCU hive, an attacker can plant a malicious command in a specific registry key. When the auto-elevating binary runs, it reads the attacker's command and executes it with High Integrity, bypassing the prompt.

**Example: Fodhelper UAC Bypass**
```powershell
# 1. Create the registry structure
New-Item "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Force
# 2. Set the malicious payload (e.g., a reverse shell)
Set-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "(default)" -Value "cmd.exe /c start evil.exe"
# 3. Set the DelegateExecute property to trick fodhelper
Set-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "DelegateExecute" -Value ""
# 4. Execute the auto-elevating binary
C:\Windows\System32\fodhelper.exe
```

## Defensive Considerations & Detection

*   **Never set `LocalAccountTokenFilterPolicy` to 1.** Doing so allows attackers who crack local admin hashes to effortlessly spread laterally across the environment.
*   **Leave the Built-in Administrator (RID 500) Disabled.** Use alternative, uniquely named local admin accounts. Since they are not RID 500, they are subject to Remote UAC, hindering lateral movement.
*   **Monitor Registry Modifications:** Alert on processes modifying `HKCU:\Software\Classes\*` followed by the execution of known auto-elevating binaries.
*   **UAC Settings:** Set UAC to "Always Notify". This forces prompt generation even for Windows binaries, severely crippling auto-elevation bypass techniques.

---

## Real-World Attack Scenario

During a red team engagement, an attacker compromises a user's machine who has local administrator privileges, but their initial shell is running in a Medium Integrity context due to UAC protections. When the attacker attempts to dump credentials from LSASS or interact with system-level services, access is repeatedly denied. To circumvent this, the attacker identifies a UAC auto-elevate vulnerability in a built-in Windows binary (e.g., `fodhelper.exe`). They write a custom payload path to the `HKCU\Software\Classes\ms-settings\Shell\Open\command` registry key and execute `fodhelper.exe`. The binary auto-elevates without prompting the user and spawns the attacker's payload in a High Integrity context, allowing them to extract LSASS memory and proceed with the exploitation chain.

## Chaining Opportunities

*   **Initial Access to Privilege Escalation**: After landing on a host via Phishing (Medium Integrity), if the user is a local admin, execute a UAC bypass to gain High Integrity. From High Integrity, you can dump LSASS using Mimikatz. See [[22 - Pass the Hash and Credential Dumping]].
*   **Lateral Movement**: When spraying credentials, checking if `LocalAccountTokenFilterPolicy` is enabled dictates whether `wmiexec` or `psexec` will succeed with local non-RID-500 accounts.

## Related Notes
*   [[13 - Local Administrator vs Domain Administrator]]
*   [[22 - Pass the Hash and Credential Dumping]]
*   [[25 - Lateral Movement Windows Management Instrumentation WMI]]
