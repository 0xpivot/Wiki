---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.10 ProxyNotShell and OWASSRF"
---

# ProxyNotShell and OWASSRF

## 1. Introduction to ProxyNotShell and OWASSRF

Following the catastrophic impacts of ProxyLogon and ProxyShell, Microsoft Exchange was hit again in late 2022 by a new set of vulnerabilities dubbed "ProxyNotShell" (CVE-2022-41040 & CVE-2022-41082) and subsequently "OWASSRF" (CVE-2022-41080).

These exploits share architectural similarities with ProxyShell but have one key difference: they **require authentication** (any valid domain user credentials). Once authenticated, an attacker can leverage an SSRF vulnerability to access the backend PowerShell remoting service and exploit a deserialization flaw to achieve Remote Code Execution (RCE) as `NT AUTHORITY\SYSTEM`.

Because these require valid credentials, they are often chained with brute-force, password spraying, or initial access phishing campaigns.

## 2. Deep Dive: The Vulnerabilities

### ProxyNotShell
1. **CVE-2022-41040 (SSRF)**: An authenticated Server-Side Request Forgery vulnerability in the Autodiscover endpoint. An attacker can craft a request that forces the Exchange server to route requests to backend APIs.
2. **CVE-2022-41082 (RCE)**: A Remote Code Execution vulnerability in the Exchange PowerShell backend. By routing through the SSRF, the attacker accesses the PowerShell endpoint and exploits a deserialization vulnerability within the WS-Management (WinRM) handler.

### OWASSRF
When Microsoft provided mitigation rules for ProxyNotShell (URL rewrites targeting Autodiscover), attackers quickly discovered a bypass: **CVE-2022-41080**. Instead of using the Autodiscover endpoint for the SSRF, attackers used the Outlook Web Access (OWA) frontend to perform the same SSRF, completely bypassing the ProxyNotShell WAF rules, and then chained it with the same backend RCE (CVE-2022-41082).

## 3. Architecture and Attack Flow

```text
+-------------------------------------------------------------------------------------------------------+
|                                    ProxyNotShell / OWASSRF Flow                                       |
+-------------------------------------------------------------------------------------------------------+
|                                                                                                       |
|  [ Attacker (Authenticated User) ]                                                                    |
|       |                                                                                               |
|       | 1. HTTP GET /autodiscover/autodiscover.json?@foo.com/powershell/?X-Rps-CAT=...                |
|       |    OR (OWASSRF bypass)                                                                        |
|       | 1. HTTP GET /owa/user@domain.com/powershell                                                   |
|       v                                                                                               |
|  [ Exchange Frontend (CAS) ]                                                                          |
|       |                                                                                               |
|       | 2. SSRF vulnerability triggered. Request routed to backend /powershell.                       |
|       v                                                                                               |
|  [ Exchange Backend (PowerShell WinRM) ]                                                              |
|       |                                                                                               |
|       | 3. WinRM session established.                                                                 |
|       | 4. Attacker sends malicious serialized XML object (Deserialization flaw).                     |
|       v                                                                                               |
|  [ Exchange Command Processor (w3wp.exe) ]                                                            |
|       |                                                                                               |
|       | 5. Deserialization triggers object instantiation, resulting in command execution.             |
|       | 6. Executes command as NT AUTHORITY\SYSTEM.                                                   |
|       v                                                                                               |
|  [ Attacker ] <--- Reverse Shell / Command Output                                                     |
|                                                                                                       |
+-------------------------------------------------------------------------------------------------------+
```

## 4. Comprehensive Exploitation Walkthrough

Unlike ProxyShell's file-write approach, ProxyNotShell relies on PowerShell object deserialization for direct code execution, meaning it often doesn't drop a webshell immediately but executes commands directly in memory.

### Step 1: Initial Authentication

The attacker needs credentials. This can be a low-privileged user, a compromised service account, or credentials bought from an Initial Access Broker (IAB).

### Step 2: Triggering the SSRF

**ProxyNotShell Vector**:
```http
GET /autodiscover/autodiscover.json?@foo.com/powershell/?X-Rps-CAT=... HTTP/1.1
Host: mail.target.com
Authorization: Basic <base64_credentials>
```

**OWASSRF Vector (WAF Bypass)**:
```http
GET /owa/victim@target.com/powershell HTTP/1.1
Host: mail.target.com
Authorization: Basic <base64_credentials>
```

The OWA vector was particularly dangerous because administrators confidently applied the Autodiscover URL rewrite rules thinking they were safe, only to be breached via OWA.

### Step 3: PowerShell Remoting Deserialization (CVE-2022-41082)

Once connected to the backend `/powershell` endpoint via the SSRF, the attacker initiates a WinRM session. The protocol communicates using SOAP and serialized XML objects.

The vulnerability exists in how the Exchange backend deserializes certain management objects. By injecting a crafted XML payload containing a malicious `.NET` object chain (often built using tools like `ysoserial.net` with the `TypeConfuseDelegate` gadget), the deserializer executes the payload during the object reconstruction phase.

The payload usually spawns `cmd.exe` or `powershell.exe` as a child process of `w3wp.exe` (the IIS worker process) running under the `SYSTEM` context.

### Step 4: Code Execution and Payload Delivery

The attacker typically executes a command to:
- Download and execute a Cobalt Strike beacon.
- Add a new local administrator.
- Dump LSASS.
- Exfiltrate the Active Directory database via ntdsutil.

## 5. Bypassing Mitigations: The Cat and Mouse Game

Microsoft's initial response to ProxyNotShell was to release IIS URL Rewrite rules blocking requests containing `.*autodiscover\.json.*\@.*Powershell.*`. 

Attackers continuously refined their payloads to bypass these regex rules.
- They changed the casing: `PoWeRsHeLl`
- They used different encoding schemes.
- Ultimately, they abandoned Autodiscover entirely and shifted to OWASSRF (`/owa/`), rendering the Autodiscover rules completely useless.

This emphasizes that WAF rules and URL rewrites are only temporary bandaids for architectural vulnerabilities. Patching the underlying code is the only permanent fix.

## 6. Post-Exploitation Tactics

With SYSTEM access, the server is fully compromised. Threat actors (notably the Play ransomware group) utilized OWASSRF extensively.

Standard post-exploitation activities include:
- Plink / Chisel reverse tunnels.
- AnyDesk / ScreenConnect installation for persistent GUI access.
- Execution of BloodHound to map the domain.
- Lateral movement via SMB to Domain Controllers.

## 7. Mitigations

1. **Apply Security Updates**: Install the November 2022 Security Updates (or later) which patch both the SSRF and the RCE vulnerabilities natively in the code.
2. **Disable Remote PowerShell**: For users who do not need it, disable Remote PowerShell access:
   ```powershell
   Set-User "user" -RemotePowerShellEnabled $false
   ```
3. **MFA and Conditional Access**: Because these exploits require authentication, enforcing MFA on all internet-facing Exchange endpoints (OWA, ECP) significantly raises the barrier to entry, preventing attackers from using basic stolen credentials.

## 8. Detections and Forensics

### IIS Logs (OWASSRF)

Monitor IIS logs for authenticated requests targeting `/owa/` but appending `/powershell`.

```kusto
W3CIISLog
| where csUriStem startswith "/owa/" and csUriStem endswith "/powershell"
| where csMethod == "GET" or csMethod == "POST"
| where scStatus == 200
| project TimeGenerated, cIP, csUsername, csUriStem, scStatus
```

### Process Creation (EDR/Sysmon)

Monitor for suspicious child processes spawned by the IIS worker process (`w3wp.exe`), especially when the command line includes `cmd.exe`, `powershell.exe`, or encoded payloads.

```kusto
DeviceProcessEvents
| where InitiatingProcessFileName =~ "w3wp.exe"
| where FileName in~ ("cmd.exe", "powershell.exe", "certutil.exe", "rundll32.exe")
| project TimeGenerated, DeviceName, InitiatingProcessCommandLine, FileName, ProcessCommandLine
```

### Event Logs

Check the Exchange Management logs and PowerShell operational logs for unusual WinRM activity or deserialization errors. Look for Event ID 400 in the `Windows PowerShell` event log showing bizarre host applications.


## Real-World Attack Scenario
## Real-World Attack Scenario: OWASSRF Deserialization

**The Context:** A ransomware affiliate has purchased a set of valid, low-privileged Active Directory credentials (`sales_rep:Summer2023!`) from a dark web market. The target organization has patched ProxyLogon and ProxyShell and implemented WAF rules specifically blocking the ProxyNotShell Autodiscover SSRF vector. However, they have not applied the latest Exchange Cumulative Updates that fix the underlying code vulnerabilities.

**The Reconnaissance:** 
The attacker verifies the credentials work by logging into the external Outlook Web Access (OWA) portal. They attempt the standard ProxyNotShell Autodiscover SSRF payload, but the WAF blocks it. Knowing the architecture, the attacker pivots to the OWASSRF bypass vector.

**The Execution:**
1. **OWA SSRF Trigger:** The attacker crafts an authenticated HTTP GET request using the compromised credentials, but targets the OWA endpoint directly: `/owa/sales_rep@target.com/powershell`. 
2. **Bypassing the WAF:** Because the WAF rules were narrowly scoped to `/autodiscover/`, this request sails through. The Exchange frontend processes the OWA request and, due to the underlying SSRF flaw, improperly routes it to the backend PowerShell remoting service.
3. **WinRM Deserialization:** Now connected to the backend `/powershell` endpoint, the attacker establishes a WinRM session. They transmit a highly obfuscated, malicious serialized XML payload generated via `ysoserial.net` (using a `TypeConfuseDelegate` gadget).
4. **In-Memory Execution:** When the Exchange Command Processor (`w3wp.exe`) attempts to deserialize the XML object, the gadget chain triggers. The deserialization flaw allows the attacker to execute arbitrary code during the object reconstruction phase, completely bypassing normal PowerShell execution policies.
5. **Reverse Shell:** The payload executes a base64-encoded PowerShell command that downloads and executes a Cobalt Strike stager directly into memory.

**The Outcome:**
The attacker bypassed the protective WAF rules by using the OWA endpoint instead of Autodiscover. Utilizing only a standard user's credentials, they achieved `NT AUTHORITY\SYSTEM` Remote Code Execution entirely in memory, dropping no webshells to disk. The Cobalt Strike beacon calls back to the attacker's C2 server, granting them full interactive control over the Exchange server to begin lateral movement and ransomware deployment.

## 9. Chaining Opportunities

- **[[13 - Password Spraying and Brute Force]]**: Use password spraying against OWA to obtain the initial credentials required for this exploit.
- **[[12 - Lateral Movement via DCOM and WMI]]**: Pivot from the Exchange server to domain controllers.
- **[[19 - Web Shells and IIS Exploitation]]**: Deep dive into IIS process execution contexts.
- **[[23 - Abusing Active Directory Certificate Services (AD CS)]]**: Extract Exchange machine certificates post-exploitation.

## 10. Related Notes

- [[08 - ProxyLogon Chaining]]
- [[09 - ProxyShell Chaining]]
- [[21 - Active Directory Defense and Auditing]]
