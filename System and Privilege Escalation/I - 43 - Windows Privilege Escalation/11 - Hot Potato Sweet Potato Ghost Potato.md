---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.11 More Potatoes"
---

# More Potatoes: Hot, Sweet, Ghost, and Beyond

## Overview
While Juicy Potato, Rogue Potato, and PrintSpoofer are the most famous tools for abusing `SeImpersonatePrivilege`, the "Potato" family is vast and continually expanding. The core concept—coercing a SYSTEM process into authenticating to an attacker-controlled listener to steal its token—remains constant. However, the methods of coercion evolve as Microsoft patches older techniques. This document explores the historical foundations and modern permutations of these attacks, specifically focusing on Hot Potato, Sweet Potato, Ghost Potato, and the overarching implications of these variations. Understanding the entire taxonomy of Potato attacks is crucial for red teamers encountering diverse, patched, or uniquely configured Windows environments where the standard tools fail.

## Hot Potato (The Predecessor)
Hot Potato is the grandfather of the modern token impersonation suite. Unlike its successors, which rely heavily on DCOM or RPC, Hot Potato utilized a complex chain of distinct vulnerabilities and features inherent in Windows networking and the Web Proxy Auto-Discovery (WPAD) protocol.

### The Hot Potato Chain
Hot Potato did not strictly require `SeImpersonatePrivilege` in the same way modern Potatoes do; it was a more systemic abuse of local network behavior.
1. **Local NBNS Spoofing:** Windows systems historically broadcast NetBIOS Name Service (NBNS) requests to resolve hostnames on the local network. Hot Potato starts by flooding the local system with fake NBNS responses, specifically targeting the resolution of "WPAD" (Web Proxy Auto-Discovery).
2. **WPAD Exploitation:** By successfully spoofing the WPAD hostname to point to the local machine (127.0.0.1), the attacker tricks Windows into downloading a malicious PAC (Proxy Auto-Configuration) file served by the attacker.
3. **HTTP to SMB NTLM Relay:** The PAC file forces all outbound HTTP traffic from the system (including highly privileged SYSTEM processes like Windows Update) to be routed through the attacker's local HTTP listener.
4. **NTLM Relay:** When a SYSTEM process attempts to connect, it authenticates using NTLM. The attacker's HTTP server intercepts this NTLM authentication and relays it to a local SMB service.
5. **Command Execution:** The relayed SYSTEM authentication is used against the local SMB service to create a scheduled task or service, executing arbitrary code as `NT AUTHORITY\SYSTEM`.

### Microsoft's Patching of Hot Potato
Microsoft effectively killed Hot Potato with several patches, primarily MS16-075, which prevented NTLM relaying from HTTP to SMB on the same machine. Furthermore, enhancements to NBNS handling and WPAD resolution made the initial spoofing unreliable or impossible on modern Windows versions (Windows 10/Server 2016+).

## Sweet Potato (The All-in-One Toolkit)
As the number of Potato exploits grew, managing the different tools, CLSIDs, and OS compatibility requirements became cumbersome. Sweet Potato was developed as a unified C# framework that bundles multiple potato techniques into a single executable.

### Capabilities of Sweet Potato
Sweet Potato dynamically detects the operating system version and the available privileges to select the optimal coercion and impersonation strategy. It integrates:
- **Juicy Potato functionality:** Using DCOM for older systems.
- **PrintSpoofer functionality:** Using the Print Spooler service for newer systems.
- **WinRM abuse:** Leveraging the Windows Remote Management service as another coercion vector.
- **EfsRpc (PetitPotam local):** Abusing the Encrypting File System Remote Protocol (MS-EFSR) to coerce authentication locally.

By rewriting these exploits in C#, Sweet Potato provides a significant operational advantage: it can be easily executed in-memory via tools like Cobalt Strike's `execute-assembly`, entirely bypassing disk-based detection mechanisms that frequently flag traditional C++ compiled potato executables.

## Ghost Potato (Evasion and BITS Abuse)
Ghost Potato represents a shift towards evasive execution. Standard Potato attacks often spawn a new process (`CreateProcessWithTokenW`), which is highly scrutinized by Endpoint Detection and Response (EDR) agents. Spawning `cmd.exe` or a reverse shell from a web worker process is a massive red flag.

### The Ghost Potato Methodology
Ghost Potato attempts to avoid process creation altogether by utilizing token manipulation and code injection techniques.
1. **Coercion via BITS:** Ghost Potato often abuses the Background Intelligent Transfer Service (BITS) COM objects for coercion, providing an alternative to DCOM or PrintSpoofer.
2. **Token Duplication:** It acquires the SYSTEM token via the standard `ImpersonateNamedPipeClient` route.
3. **Thread Pool Injection / Thread Hijacking:** Instead of spawning a new process, Ghost Potato uses the stolen SYSTEM token to impersonate a thread within an *existing* privileged process or injects a payload into a process that is already running under the SYSTEM context.
4. **EDR Evasion:** Because no new process is created, process tree analysis tools and behavioral EDR rules that look for anomalous child processes are effectively bypassed. The execution blends into the background noise of the operating system.

## ASCII Diagram: The Evolution of Potato Exploits

```text
Time        Technique          Vector                      Mitigation
---------------------------------------------------------------------------------
Older       Hot Potato         NBNS Spoofing -> WPAD ->    MS16-075 (Cross-protocol
                               HTTP to SMB NTLM Relay      Relay blocked locally)
  |               |
  v               v
            Rotten Potato      DCOM Coercion ->            Restricted DCOM Object
            Juicy Potato       Local RPC Listener          Binding to 127.0.0.1
  |               |                                        (Win 10 1809 / Server 2019)
  v               v
            Rogue Potato       DCOM Coercion ->            Requires external
                               Remote RPC Forwarding       Network Routing
  |               |
  v               v
            PrintSpoofer       Print Spooler RPC ->        Disable Print Spooler /
                               Local Named Pipe            Patching specific APIs
  |               |
  v               v
            Sweet Potato       Unified C# Framework        Standard EDR process
                               (Multiple Vectors)          creation telemetry
  |               |
  v               v
Modern      Ghost Potato       BITS / DCOM -> Token ->     Advanced Memory Scanning /
            GodPotato          Thread Injection /          API Hooking (Token APIs)
                               Evasion
```

## GodPotato (The Modern Behemoth)
GodPotato deserves a special mention as it currently stands as one of the most reliable and persistent tools in the modern arsenal. It exploits the `IStorage` interface of DCOM, fundamentally bypassing the RPC SS mitigations that crippled Juicy Potato. 
- It sets up a fake local COM server.
- It triggers a DCOM activation that forces the system to interact with this fake server.
- The interaction inherently passes an impersonation token over the local RPC/COM channel, allowing GodPotato to capture it without needing named pipes or external routing.
- It works flawlessly across Windows Server 2012 through Server 2022 and Windows 10/11, making it a "go-to" standard when `SeImpersonatePrivilege` is identified.

## Strategic Selection in Penetration Testing
Choosing the right Potato is a matter of situational awareness:
1. **Legacy Systems (< Server 2019):** Juicy Potato is highly reliable if CLSIDs are known.
2. **Modern Systems with Print Spooler:** PrintSpoofer is fast, elegant, and self-contained.
3. **Hardened Modern Systems (Spooler Disabled):** GodPotato is the current gold standard due to its abuse of fundamental DCOM mechanics that are difficult for Microsoft to patch without breaking backward compatibility.
4. **High-Security Environments (EDR Present):** Ghost Potato or custom implementations utilizing Sweet Potato's memory-safe execution combined with thread hijacking are necessary to avoid process creation telemetry.

## Defenses and Mitigations
Defending against the extended Potato family requires systemic hardening:
1. **Disable Unnecessary Services:** BITS, Print Spooler, and WebClient are frequently abused for coercion. Disable them if not explicitly required.
2. **Strict Least Privilege:** Never grant `SeImpersonatePrivilege` to service accounts unless absolutely critical. Utilize gMSAs.
3. **RPC Filters:** Implement RPC filtering to restrict what processes can interact with DCOM and RPC endpoints locally.
4. **Advanced EDR:** Rely on EDRs capable of detecting memory injection, thread context manipulation, and anomalous API usage (`ImpersonateLoggedOnUser`, `SetThreadToken`), rather than just process creation events.

## Chaining Opportunities
- Sweet Potato's in-memory execution capabilities pair perfectly with Command and Control (C2) frameworks like [[12 - Cobalt Strike Artifacts]] and [[13 - Covenant]].
- Utilize Ghost Potato techniques after bypassing initial endpoint defenses detailed in [[06 - Antivirus and AMSI Evasion]].
- Essential follow-up step after exploiting unpatched web applications described in [[02 - Web Application RCE to Privesc]].

## Related Notes
- [[09 - Token Impersonation]]
- [[10 - JuicyPotato RoguePotato PrintSpoofer]]
- [[01 - Active Directory Delegation]]
- [[04 - Privileges and Rights Escalation]]
