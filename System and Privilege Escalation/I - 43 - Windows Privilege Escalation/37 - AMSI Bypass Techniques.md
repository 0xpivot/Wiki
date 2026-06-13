---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.37 AMSI Bypass Techniques"
---

# AMSI Bypass Techniques

## Introduction
The Anti-Malware Scan Interface (AMSI) is a vendor-neutral security standard introduced by Microsoft in Windows 10. AMSI provides an API that applications can call to request an antivirus scan of a memory buffer or a file. Its primary objective is to combat script-based malware and obfuscated payloads.

Before AMSI, malicious PowerShell scripts, VBScripts, or JavaScripts could easily evade traditional Antivirus (AV) by using heavy obfuscation, dynamic execution, or loading directly into memory (fileless malware). AMSI intercepts these scripts at runtime, *after* they have been de-obfuscated by the script engine but *before* they are executed, passing the clear-text content to the registered AV provider (like Windows Defender) for evaluation.

Bypassing AMSI is a critical requirement for executing modern offensive tools (like Mimikatz, BloodHound, or Empire payloads) in memory on modern Windows systems.

## How AMSI Works

AMSI is implemented primarily through a dynamic-link library called `amsi.dll`. When a scripting engine (like `powershell.exe`, `wscript.exe`, or `cscript.exe`) is launched, the OS injects `amsi.dll` into the process memory space.

When the script engine is about to evaluate a block of code, it calls the `AmsiScanBuffer` or `AmsiScanString` functions exported by `amsi.dll`. 
1. The script engine passes the code to `AmsiScanBuffer`.
2. `amsi.dll` forwards this buffer via Remote Procedure Call (RPC) to the Anti-Malware service (e.g., Windows Defender service).
3. The AV engine evaluates the buffer against its signatures and heuristics.
4. The AV engine returns a result code (e.g., `AMSI_RESULT_CLEAN` or `AMSI_RESULT_DETECTED`).
5. If detected, the script engine terminates execution and throws a malicious content error.

## ASCII Architecture Diagram

```text
+---------------------------------------------------------------+
|                    AMSI Architecture Flow                     |
|                                                               |
|  +--------------------+        +-------------------------+    |
|  | PowerShell Engine  |        |        amsi.dll         |    |
|  |                    |        |                         |    |
|  | 1. Reads Script    |        | 3. Exports              |    |
|  | 2. De-obfuscates   | -----> |    AmsiScanBuffer()     |    |
|  |                    |        |                         |    |
|  +--------------------+        +----------+--------------+    |
|                                           |                   |
|                                    4. RPC | Call              |
|                                           v                   |
|                                +-------------------------+    |
|                                | Anti-Malware Provider   |    |
|                                | (e.g., Windows Defender)|    |
|                                |                         |    |
|                                | 5. Evaluates Signatures |    |
|                                +----------+--------------+    |
|                                           |                   |
|                                 6. Return | Result            |
|                                           v                   |
|  +--------------------+        +-------------------------+    |
|  | Execution Result   | <----- | AMSI_RESULT_CLEAN or    |    |
|  | Blocked/Allowed    |        | AMSI_RESULT_DETECTED    |    |
|  +--------------------+        +-------------------------+    |
+---------------------------------------------------------------+
```

## Bypass Methodologies

Because `amsi.dll` is loaded into the *userland* memory space of the process the attacker controls (e.g., the PowerShell session), the attacker has the ability to manipulate it. 

### 1. PowerShell Reflection (The Matt Graeber Method)
This was one of the earliest and most famous bypasses. It uses PowerShell reflection to find the `AmsiUtils` class within the .NET framework and modifies the `amsiInitFailed` field. If this field is set to `$true`, AMSI assumes its initialization failed and gracefully exits without scanning anything.

*Historic Example (Now heavily signatured):*
```powershell
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)
```
*Modern variants heavily obfuscate the string 'AmsiUtils' and 'amsiInitFailed' to bypass static string checks before the reflection executes.*

### 2. Memory Patching (Hooking `AmsiScanBuffer`)
This is the most robust and common approach today. Since `amsi.dll` is loaded in the process memory, an attacker can find the memory address of the `AmsiScanBuffer` function and overwrite its initial instructions. 

By overwriting the start of the function with assembly instructions that immediately return `AMSI_RESULT_CLEAN` (usually the hex value `0x80070057` or simply zeroing out the error register), the AV engine is never called.

*Conceptual Flow:*
1. Load `amsi.dll` into memory using `LoadLibrary`.
2. Find the address of `AmsiScanBuffer` using `GetProcAddress`.
3. Change memory protection using `VirtualProtect` to `PAGE_EXECUTE_READWRITE`.
4. Overwrite the first few bytes of the function with a custom assembly stub (e.g., `mov eax, 0x80070057; ret`).
5. Restore memory protection.

*This can be done via C# inline compilation, PowerShell, or compiled loaders (C++).*

### 3. Forcing an AMSI Error
If `amsi.dll` crashes or throws an exception during a scan, it often fails open, allowing the script to execute. Attackers can pass malformed buffers or manipulate environment variables to intentionally break the AMSI implementation.

### 4. Bypassing the Context
AMSI uses a context structure to identify the session. By manipulating or corrupting this context pointer in memory, subsequent calls to `AmsiScanBuffer` will fail, effectively bypassing the scan.

### 5. Obfuscation of the Bypass Itself
The Catch-22 of AMSI bypasses is that the bypass code itself must pass an AMSI scan before it can execute and disable AMSI.
Therefore, attackers must:
- Use string concatenation (e.g., `'Am' + 'siUtils'`).
- Use Base64 encoding for variables.
- Use dynamic function resolution.
- Modify the byte array patches to avoid known signatures.

## Detection and Mitigation

Defending against AMSI bypasses is a cat-and-mouse game between red teams and Microsoft.

1.  **EDR Telemetry:** Modern Endpoint Detection and Response (EDR) solutions monitor the integrity of critical DLLs in memory. EDRs employ userland API hooking themselves to watch for calls to `VirtualProtect` targeting `amsi.dll`. If an attacker tries to patch `AmsiScanBuffer`, the EDR intercepts the action and kills the process.
2.  **Kernel Callbacks:** Advanced security tools use kernel-level callbacks (e.g., `PsSetCreateProcessNotifyRoutine`) to monitor process creation and inject their own telemetry *before* the attacker has a chance to patch memory.
3.  **Strict Application Whitelisting:** AppLocker/WDAC forces PowerShell into Constrained Language Mode (CLM). CLM completely disables the use of Reflection and direct memory manipulation APIs (like `VirtualProtect`), rendering almost all AMSI memory patching techniques ineffective.
4.  **Script Block Logging:** Enable Event ID 4104. Even if AMSI is bypassed for blocking execution, the script block logging might still capture the de-obfuscated script content before the bypass completes, providing vital forensic data.

## Chaining Opportunities
- AMSI must almost always be bypassed immediately after bypassing the [[36 - Bypassing PowerShell Execution Policy]] when dropping into a PowerShell environment.
- Required to load tools like Mimikatz into memory for advanced credential theft, paving the way for [[33 - NTDS.dit Extraction]].
- Bypassing AMSI allows for the execution of advanced C2 (Command and Control) framework stagers in memory.

## Related Notes
- [[36 - Bypassing PowerShell Execution Policy]]
- [[39 - Windows Defender Evasion Basics]]
- [[35 - AppLocker and WDAC Bypass]]
- [[10 - Windows Privilege Escalation Basics]]
