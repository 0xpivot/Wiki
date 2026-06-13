---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.36 PowerShell Execution Policy"
---

# Bypassing PowerShell Execution Policy

## Introduction
The PowerShell Execution Policy is a safety feature in Windows that controls the conditions under which PowerShell loads configuration files and runs scripts. **It is crucial to understand that the Execution Policy is not a security boundary.** Microsoft explicitly states that it is a safety measure designed to prevent users from accidentally executing malicious or poorly written scripts, rather than a robust security control designed to stop a determined attacker.

Because it is a safety feature, bypassing the Execution Policy is relatively trivial. However, understanding how to bypass it gracefully is a fundamental skill for any penetration tester or red teamer working in a Windows environment.

## Understanding Execution Policies
PowerShell determines whether a script can run based on the defined execution policy. The policy can be set at various scopes (MachinePolicy, UserPolicy, Process, CurrentUser, LocalMachine).

Common policy states include:
*   **Restricted:** Default setting. No scripts can be run. Only interactive commands are allowed.
*   **AllSigned:** Only scripts signed by a trusted publisher can be run.
*   **RemoteSigned:** Downloaded scripts must be signed by a trusted publisher. Local scripts do not need a signature.
*   **Unrestricted:** Any script can run. Warns before running downloaded scripts.
*   **Bypass:** Nothing is blocked, and there are no warnings or prompts.

## ASCII Architecture Diagram

```text
+---------------------------------------------------------------+
|             PowerShell Execution Policy Concept               |
|                                                               |
|  +----------------+           +--------------------------+    |
|  | User/Attacker  |           | PowerShell Host Engine   |    |
|  | runs script.ps1|           | (powershell.exe)         |    |
|  +-------+--------+           +----------+---------------+    |
|          |                               |                    |
|          v                               v                    |
|  +-------------------------------------------------------+    |
|  |                  Execution Policy Check               |    |
|  |  [Scope Check: Process -> CurrentUser -> LocalMachine]|    |
|  +---------------------------+---------------------------+    |
|                              |                                |
|        +---------------------+---------------------+          |
|        |                     |                     |          |
|        v                     v                     v          |
|  [Restricted]          [RemoteSigned]         [Bypass]        |
|  (Blocks Script)     (Checks Signature)     (Allows Script)   |
|        |                     |                     |          |
|        v                     v                     v          |
|  +-----------+         +-----------+         +-----------+    |
|  | Failure   |         | Pass/Fail |         | Success!  |    |
|  +-----------+         +-----------+         +-----------+    |
+---------------------------------------------------------------+
```

## Bypass Techniques

Because the Execution Policy is checked by `powershell.exe` when it starts or evaluates a script, an attacker can manipulate the environment, arguments, or the way the script is parsed to bypass the restrictions.

### 1. Command-Line Argument Bypass
The most straightforward and common method is to simply pass the `-ExecutionPolicy Bypass` (or `-ep bypass`) flag when launching the PowerShell executable. This sets the execution policy for the current *Process* scope, which overrides all other user or machine policies.

```cmd
powershell.exe -ExecutionPolicy Bypass -File C:\temp\malicious_script.ps1
```
*Alternatively, using `-ep bypass` is a common shorthand.*

### 2. Passing Script Content via standard input (Stdin)
Instead of executing a `.ps1` file (which triggers the policy check), an attacker can pipe the contents of the script directly into the standard input of the `powershell.exe` process. PowerShell evaluates the piped input as interactive commands, which bypasses the script execution restrictions.

```cmd
type C:\temp\malicious_script.ps1 | powershell.exe -noprofile -
```
*Alternatively:*
```cmd
Get-Content .\malicious_script.ps1 | PowerShell.exe -noprofile -
```

### 3. The `Invoke-Expression` (IEX) technique
Similar to piping, you can read the contents of the script file into a variable as a string, and then execute that string using `Invoke-Expression`.

```cmd
powershell -c "IEX (Get-Content C:\temp\malicious_script.ps1 -Raw)"
```

### 4. Encoding the Payload
Attackers can encode the entire script in Base64 and pass it directly to `powershell.exe` using the `-EncodedCommand` flag. This avoids writing a `.ps1` file to disk entirely and treats the execution as an interactive command.

1.  *Encode the command (e.g., in a Linux terminal):*
    ```bash
    echo -n "Write-Host 'Bypassed!'" | iconv -t UTF-16LE | base64 -w 0
    ```
2.  *Execute on Windows:*
    ```cmd
    powershell.exe -EncodedCommand VwByAGkAdABlAC0ASABvAHMAdAAgACcAQgB5AHAAYQBzAHMAZQBkACEAJwA=
    ```

### 5. Overwriting the AuthorizationManager
This is an advanced in-memory bypass. PowerShell uses the `AuthorizationManager` to determine if a script should run. By clearing or replacing this object within the current session, the policy enforcement is effectively disabled.

```powershell
Set-Item "function:\Global:AuthZ" -Value { return $true }
```
*Or more complex memory patching if advanced logging/EDR blocks simple variable overrides.*

### 6. Changing CurrentUser or Process Scope via Registry/Command
Even as a standard user, you can change the Execution Policy for your own scope (`CurrentUser`) or the current process.

```powershell
Set-ExecutionPolicy Bypass -Scope CurrentUser -Force
```
*Note: This might be blocked by Group Policy (MachinePolicy), which takes precedence.*

## Detection and Mitigation

Since Execution Policy is not a security boundary, relying on it to stop attackers is a fundamental flaw. Defenses must focus on visibility and robust enforcement.

1.  **Do Not Rely on Execution Policy:** Understand that it stops accidental errors, not targeted attacks.
2.  **AppLocker and WDAC:** Implement Application Whitelisting (WDAC or AppLocker). When AppLocker is enabled, PowerShell automatically drops into **Constrained Language Mode (CLM)**. CLM drastically reduces the capabilities of PowerShell, blocking direct .NET API access, COM object creation, and many advanced exploitation techniques, rendering most offensive scripts useless even if the Execution Policy is bypassed.
3.  **PowerShell Logging:**
    - **Script Block Logging (Event ID 4104):** Crucial for capturing the actual content of scripts executed, including heavily obfuscated or base64 encoded payloads (it logs the de-obfuscated payload just before execution).
    - **Module Logging (Event ID 4103):** Captures pipeline execution details.
    - **Transcription Logging:** Records all input and output of a PowerShell session to a text file on a secure network share.
4.  **AMSI (Anti-Malware Scan Interface):** Ensure AMSI is functioning. AMSI hooks into PowerShell and scans the script content *after* de-obfuscation but *before* execution.
5.  **EDR Monitoring:** Monitor command lines for arguments like `-ep bypass`, `-ExecutionPolicy Bypass`, `-EncodedCommand`, and unusual piping into `powershell.exe`.

## Chaining Opportunities
- Bypassing the execution policy is almost always the first step before running enumeration scripts like `PowerUp.ps1` or `BloodHound` ingestors.
- It is a necessary prerequisite for performing [[37 - AMSI Bypass Techniques]] if the AMSI bypass is written in PowerShell.
- It facilitates the execution of LOLBins [[34 - LOLBins]] via PowerShell wrapper scripts.

## Related Notes
- [[35 - AppLocker and WDAC Bypass]]
- [[37 - AMSI Bypass Techniques]]
- [[10 - Windows Privilege Escalation Basics]]
- [[39 - Windows Defender Evasion Basics]]
