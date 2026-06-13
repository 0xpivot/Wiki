---
tags: [web, advanced, enterprise, deserialization, vapt]
difficulty: advanced
module: "80 - Enterprise Web Apps: WebLogic, ColdFusion, Liferay"
topic: "80.06 Attacking Microsoft SharePoint Servers"
---

# Attacking Microsoft SharePoint Servers

## 1. Introduction to SharePoint in the Enterprise

Microsoft SharePoint is a colossal web-based collaborative platform that integrates with Microsoft Office. Launched in 2001, it is primarily sold as a document management and storage system, but the product is highly configurable and usage varies substantially among organizations. From a penetration testing and adversary simulation perspective, SharePoint represents one of the highest-value targets within an enterprise network. Compromising a SharePoint server often yields access to sensitive corporate documents, strategic plans, HR records, and financial data. Furthermore, because SharePoint integrates deeply with Active Directory, Microsoft SQL Server, and Microsoft Exchange, it acts as an ideal pivot point for lateral movement and privilege escalation.

### 1.1 The Attack Surface
SharePoint's architecture is monolithic and complex. It relies heavily on ASP.NET, Windows Communication Foundation (WCF), and extensive XML processing. The massive attack surface encompasses:
- **Authentication Interfaces:** NTLM, Kerberos, SAML, and Forms-Based Authentication (FBA).
- **Web Services and APIs:** SOAP endpoints (`_vti_bin`), REST APIs (`_api`), and legacy FrontPage Server Extensions.
- **Deserialization Endpoints:** Features relying on ViewState or XML serialization to maintain state across its distributed farm architecture.
- **Business Logic:** Workflows, custom web parts, and third-party integrations.

The complexity of the platform often leads to misconfigurations or unpatched vulnerabilities that can be leveraged for Remote Code Execution (RCE) and data exfiltration.

## 2. Architectural Overview and Attack Flow Diagram

Understanding the topology of a SharePoint Farm is crucial for exploiting it. A typical deployment involves Web Front End (WFE) servers, Application servers, and Database (SQL) servers.

```ascii
+---------------------------------------------------------+
|                Microsoft SharePoint Farm                |
+-------------------+-----------------+-------------------+
|                   |                 |                   |
|   +---------------+-------+  +------+-----------------+ |
|   |   Web Front End (WFE) |  |   Application Server   | |
|   | - IIS / ASP.NET       |  | - Search Services      | |
|   | - WCF Endpoints       |  | - Excel/Word Services  | |
|   | - Forms/ViewState     |  | - Business Data Conn.  | |
|   +-------+---------------+  +------+-----------------+ |
|           |                         |                   |
|           | (HTTP/SOAP)             | (WCF/RPC)         |
|           v                         v                   |
|   +---------------------------------------------------+ |
|   |                  Database Tier                    | |
|   |            (Microsoft SQL Server)                 | |
|   | - Config DB, Content DBs, Service DBs             | |
|   +---------------------------------------------------+ |
+---------------------------------------------------------+

                 [ Attack Flow Example: Deserialization ]

 [ Attacker ]
      |
      | 1. Identify exposed endpoint (e.g., Picker.aspx)
      |    Requires knowing a vulnerable parameter
      v
 [ WFE IIS Server ]
      |
      | 2. Submit malicious serialized payload in XML/JSON
      |    (e.g., LosFormatter / BinaryFormatter gadget)
      v
 [ ASP.NET Runtime ]
      |
      | 3. Unsafe Deserialization
      |    TypeConfuseDelegate or ActivitySurrogateSelector
      v
 [ System.Diagnostics.Process ] --> Exec (cmd.exe /c "powershell -enc...")
      |
      | 4. Reverse Shell or C2 Beacon triggered!
      v
 [ Attacker C2 ]
```

## 3. Deep Dive into SharePoint Deserialization Vulnerabilities

The most devastating vulnerabilities in SharePoint history are related to unsafe deserialization. Because SharePoint processes complex objects to maintain state and coordinate actions across the farm, developers historically relied on formatters that inherently trust the data they deserialize.

### 3.1 CVE-2019-0604: XMLSerializer and Picker.aspx

CVE-2019-0604 is an iconic RCE vulnerability in SharePoint that arises from the failure to sanitize user input prior to passing it to an insecure `XmlSerializer`. This flaw was highly exploited in the wild by advanced persistent threats (APTs) and ransomware operators.

**The Vulnerability Mechanism:**
The vulnerability lies in the `ItemPicker` control, which is used to select items from a list. Specifically, the `PickerEntity` class instances are serialized and deserialized when navigating the UI. The endpoint `/_layouts/15/Picker.aspx` accepts an argument called `ctl00$PlaceHolderDialogBodySection$ctl05$hiddenSpanData` which contains XML data. 

When the server processes this data, it utilizes a custom deserializer that eventually instantiates objects based on the XML type attributes. If an attacker specifies a type that results in arbitrary method invocation during its instantiation or property setting, they can achieve RCE.

**Exploitation Steps:**
1. Identify a reachable `Picker.aspx` or similar endpoint (e.g., `EntityEditor.aspx`).
2. Generate a payload using the `TypeConfuseDelegate` or similar gadget chain. The payload must be carefully wrapped in XML matching the `PickerEntity` structure.
3. The server attempts to deserialize the object. During the deserialization process, the gadget chain is triggered, leading to the execution of arbitrary commands under the context of the IIS application pool (typically `NT AUTHORITY\NETWORK SERVICE` or a dedicated domain service account).

### 3.2 CVE-2020-1147: .NET Core and DataSet Deserialization

This vulnerability affected multiple .NET applications, including SharePoint, due to the unsafe deserialization of XML arrays using the `DataSet` and `DataTable` types. SharePoint uses these types heavily when querying backend SQL databases and returning results.

**The Vulnerability Mechanism:**
When SharePoint receives a SOAP request that includes a serialized `DataSet`, it blindly reconstructs the schema and data. A malicious `DataSet` can embed a serialized payload within its schema definitions. When the `DataSet` is populated, the malicious payload is deserialized via `BinaryFormatter`.

**Exploitation Steps:**
1. Target SOAP endpoints such as `/_vti_bin/lists.asmx` or other WCF services.
2. Construct a SOAP envelope containing an `xs:schema` payload carrying a base64-encoded `BinaryFormatter` gadget chain (e.g., `TextFormattingRunProperties`).
3. Send the SOAP request to the server, which triggers the deserialization and executes the payload.

### 3.3 CVE-2023-29357: Elevation of Privilege via JWT Authentication Bypass

This vulnerability is a critical authentication bypass that allows an unauthenticated attacker to assume the privileges of any SharePoint user, including the Farm Administrator. When chained with other vulnerabilities (like CVE-2023-24955 for RCE), it yields full server compromise.

**The Vulnerability Mechanism:**
SharePoint utilizes JSON Web Tokens (JWT) for OAuth authentication, particularly when interacting with add-ins and external applications. The vulnerability stems from how SharePoint validates the signature of the incoming JWT. Under specific conditions, an attacker can manipulate the algorithm header (e.g., switching `RS256` to `none` or using a misconfigured key validation) and forge a valid token for the administrative user (`0#.w|domain\admin`).

**Exploitation Steps:**
1. Obtain the target SharePoint site's `realm` (usually a GUID) by querying the `/_vti_bin/client.svc` endpoint and examining the `WWW-Authenticate` header.
2. Forge a JWT containing the target administrator's UPN (User Principal Name), the target site's URL, and the appropriate audience claim.
3. Use the forged JWT in the `Authorization: Bearer <token>` header to access restricted API endpoints, such as `/_api/web/siteusers` or administrative configuration pages.
4. Chain this administrative access with an authenticated RCE vulnerability or configuration change to execute code.

## 4. Attacking SharePoint APIs and Web Services

Beyond deserialization, SharePoint exposes a massive amount of functionality through its APIs. Even without RCE, these endpoints can leak catastrophic amounts of data.

### 4.1 The REST API (`/_api/`)
The SharePoint REST API allows users to interact with lists, libraries, and user profiles. A common attack vector is leveraging excessive permissions. Often, the default `Everyone` or `NT AUTHORITY\Authenticated Users` groups have read access to highly sensitive lists.

**Enumerating Users:**
```http
GET /_api/Web/SiteUsers HTTP/1.1
Host: sharepoint.target.local
Accept: application/json;odata=verbose
```
This endpoint dumps all users, groups, and service accounts registered on the site, providing excellent material for password spraying or targeted phishing.

**Searching for Secrets:**
The Search API (`/_api/search/query`) is immensely powerful. An attacker can use it to search across all documents they have access to in the farm.
```http
GET /_api/search/query?querytext='password OR credentials OR secret' HTTP/1.1
Host: sharepoint.target.local
Accept: application/json;odata=verbose
```

### 4.2 FrontPage Server Extensions (FPSE) and SOAP APIs
Legacy endpoints like `/_vti_bin/owssvr.dll` and `/_vti_bin/ListData.svc` often bypass modern WAF rules or logging mechanisms. Attackers can use these endpoints to download entire document libraries in bulk using RPC over HTTP.

## 5. Post-Exploitation and Lateral Movement

Once code execution is achieved on a SharePoint WFE, the objective shifts to credential theft, farm persistence, and lateral movement.

### 5.1 Extracting Farm Passwords
The SharePoint Configuration Database (SQL Server) stores the credentials for various service accounts, including the Farm Account. While these are encrypted, the key to decrypt them is stored locally on the WFE servers.

Attackers with administrative access to the WFE can execute PowerShell scripts leveraging the SharePoint Object Model (`Microsoft.SharePoint.dll`) to decrypt and dump these passwords:
```powershell
Add-Type -Path "C:\Program Files\Common Files\Microsoft Shared\Web Server Extensions\16\ISAPI\Microsoft.SharePoint.dll"
$farm = [Microsoft.SharePoint.Administration.SPFarm]::Local
# Iterate through managed accounts to retrieve plaintext passwords
```

### 5.2 Modifying ASPX Pages for Persistence
SharePoint stores many configuration files and master pages within the virtual directories or the Content Database. An attacker can upload a malicious `.aspx` web shell (like Chopper or a custom ASP.NET shell) to a document library and bypass security restrictions if `Custom Script` is enabled in the tenant or farm settings.

Furthermore, attackers can modify the `web.config` file or drop malicious DLLs into the Global Assembly Cache (GAC) or the `bin` directory of the web application, ensuring stealthy persistence that survives server reboots and IIS resets.

### 5.3 Server-Side Request Forgery (SSRF)
SharePoint's Webhook integration and external data source connections (Business Data Connectivity - BDC) are historically vulnerable to SSRF. An attacker can force the SharePoint server to make HTTP requests to internal network endpoints, bypassing network segmentation and accessing internal metadata services (e.g., AWS IMDS `169.254.169.254`) or internal administrative panels.

## 6. Defensive Strategies and Hardening

Defending SharePoint requires a defense-in-depth approach due to its complexity.

1. **Patch Management:** Given the severity of deserialization flaws, installing Cumulative Updates (CUs) and security patches immediately is non-negotiable.
2. **Least Privilege:** The IIS Application Pools should run under dedicated, restricted Managed Service Accounts (gMSA) rather than highly privileged domain accounts.
3. **Web Application Firewall (WAF):** Deploy rules specifically looking for `BinaryFormatter` signatures (e.g., `AAEAAAD/////`) or malicious XML structures.
4. **Disable Legacy APIs:** If FPSE or legacy SOAP endpoints are not required, disable them in IIS to reduce the attack surface.
5. **Monitor Object Model Usage:** Enable logging for anomalous PowerShell executions on the SharePoint WFEs that load `Microsoft.SharePoint.dll`.

## 7. Chaining Opportunities
- **Authentication Bypass to RCE:** Combine CVE-2023-29357 (Auth Bypass) with CVE-2023-24955 (Authenticated RCE via workflow compilation) for full unauthenticated remote code execution.
- **RCE to Domain Admin:** Extract the SharePoint Farm Admin account credentials via the SharePoint Object Model PowerShell API, which often has local admin rights on the SQL server or excessive privileges in Active Directory.
- **SSRF to Cloud Compromise:** Exploit SSRF in the Webhook API to query the cloud metadata service, extract IAM temporary credentials, and pivot into the cloud control plane.

## 8. Related Notes
- [[02 - Deserialization Attacks in .NET Environments]]
- [[07 - Exploiting Atlassian Jira and Confluence]]
- [[10 - Exploiting JBoss and WildFly Application Servers]]
- [[12 - Enterprise Identity Management and Kerberos Abuse]]
- [[09 - Spring Framework Vulnerabilities Spring4Shell]]
