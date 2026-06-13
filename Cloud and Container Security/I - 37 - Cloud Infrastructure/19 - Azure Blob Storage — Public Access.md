---
tags: [cloud, azure, blob-storage, public-access, data-leak]
difficulty: beginner
module: "37 - Cloud Infrastructure"
topic: "37.19 Azure Blob Storage"
---

# Azure Blob Storage — Public Access and Data Leakage

Azure Blob Storage is Microsoft's object storage solution for the cloud, analogous to AWS S3 or GCP Cloud Storage. It is designed to store massive amounts of unstructured data, such as text or binary data. Due to misconfigurations—often stemming from a misunderstanding of Azure's access control hierarchy—Blob Storage is a frequent source of massive data breaches. Attackers actively scan for publicly accessible storage accounts to extract sensitive PII, source code, database backups, and credentials.

## 1. Architectural Deep Dive: The Storage Hierarchy

Understanding how Azure manages storage is critical to understanding how it is misconfigured.

*   **Storage Account**: The top-level administrative container. It provides a unique namespace in Azure for your data (e.g., `mystorageaccount.blob.core.windows.net`).
*   **Container**: A grouping of a set of blobs, similar to a directory in a file system or a "bucket" in AWS S3. A storage account can contain unlimited containers.
*   **Blob**: The actual file or object (e.g., `backup.sql`, `photo.jpg`).

### The Public Access Levels

The root cause of most Azure Blob data leaks is the misconfiguration of the **Public Access Level** at the Container level. There are three settings:

1.  **Private (no anonymous access)**: *Secure default.* Access requires explicit authentication (Azure AD or an Access Key).
2.  **Blob (anonymous read access for blobs only)**: *Dangerous.* Anyone with the exact URL of a blob can read it. However, they *cannot* list the contents of the container. The attacker must guess the exact filenames.
3.  **Container (anonymous read access for containers and blobs)**: *Catastrophic.* Anyone can read individual blobs AND list all blobs within the container. An attacker simply queries the container with `?restype=container&comp=list` to get an XML directory listing of every file.

### ASCII Architecture Diagram

```text
+-------------------------------------------------------------------------+
|                        Azure Storage Account                            |
|                        (companydata.blob.core...)                       |
|                                                                         |
|  +---------------------------+        +------------------------------+  |
|  | Container: 'public-assets'|        | Container: 'db-backups'      |  |
|  | Access Level: Blob        |        | Access Level: Container      |  |
|  |                           |        |                              |  |
|  | - logo.png                |        | - prod-db-2026.bak           |  |
|  | - css/styles.css          |        | - secrets.json               |  |
|  +---------------------------+        +------------------------------+  |
+-------------------------------------------------------------------------+
             ^                                         ^
             | Attacker knows exact URL                | Attacker uses List API
             | GET /logo.png                           | GET /?restype=container&comp=list
             v                                         v
+---------------------------+           +---------------------------------+
|         Attacker          |           |            Attacker             |
| (Retrieves single image)  |           | (Gets full XML listing of files)|
+---------------------------+           +---------------------------------+
```

## 2. Exploitation Methodology

### 2.1 Discovery and Enumeration

Because storage account names form the subdomain of `blob.core.windows.net`, they must be globally unique. Attackers use tools to brute-force and permute company names to discover existing storage accounts.

**Tools for Discovery:**
*   **Microburst (Invoke-EnumerateAzureBlobs)**: A PowerShell toolkit specifically designed for Azure attacks. It uses permutation lists to guess account names and container names.
*   **Cloud_enum**: A multi-cloud OSINT tool that checks for S3, Azure Blobs, and GCP buckets.
*   **DNS Brute-forcing**: Resolving permutations like `[company]dev.blob.core.windows.net`.

If an account is discovered (i.e., DNS resolves), the next step is discovering containers. Attackers test common container names: `backup`, `logs`, `public`, `vhds`, `data`, `web`.

### 2.2 Exploiting 'Container' Level Access

If a container is configured with "Container" level public access, the attacker simply appends the listing parameters to the URL.

```http
GET https://vulnerablecorp.blob.core.windows.net/backups?restype=container&comp=list HTTP/1.1
Host: vulnerablecorp.blob.core.windows.net
```

**Response:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<EnumerationResults ServiceEndpoint="https://vulnerablecorp.blob.core.windows.net/" ContainerName="backups">
  <Blobs>
    <Blob>
      <Name>2026-production-database.bak</Name>
      <Properties>
        <Content-Length>5368709120</Content-Length>
      </Properties>
    </Blob>
    <Blob>
      <Name>admin-passwords.txt</Name>
      ...
    </Blob>
  </Blobs>
</EnumerationResults>
```
The attacker can parse this XML and download every file directly.

### 2.3 Exploiting 'Blob' Level Access (Blind Guessing)

If the access level is "Blob", the List API (`?restype=container&comp=list`) will return a `404 Not Found` or `401 Unauthorized` error regarding the container listing.

However, the files are still public. The attacker must brute-force or guess the exact file names. They might use intelligent guessing based on context (e.g., `index.html`, `config.json`, `backup.zip`) or search GitHub for hardcoded URLs pointing to that container.

## 3. The Danger of Shared Access Signatures (SAS)

Even if a container is set to "Private," developers often use **Shared Access Signatures (SAS)** to grant temporary access. A SAS token is a cryptographically signed query string attached to the blob URL.

**Example SAS URL:**
```text
https://myaccount.blob.core.windows.net/private/data.csv?sp=r&st=2026-01-01T00:00:00Z&se=2026-12-31T00:00:00Z&spr=https&sv=2022-11-02&sr=b&sig=a1b2c3d4e5f6...
```

**The Vulnerability:**
*   **Over-permissive Scope**: Developers often create a SAS token for the entire Account or Container, rather than a specific Blob (`sr=c` instead of `sr=b`).
*   **Over-permissive Rights**: Developers grant Write (`sp=w`), Delete (`sp=d`), or List (`sp=l`) permissions when only Read (`sp=r`) is needed.
*   **Infinite Expiration**: Creating SAS tokens that do not expire for 100 years.
*   **Token Leakage**: These URLs are frequently pasted into internal wikis, hardcoded into client-side JavaScript, or sent over email. If an attacker finds a highly privileged SAS token, they can completely compromise the storage account, bypassing Azure AD entirely.

## 4. Attacking the Storage Account Keys

At the account level, Azure provides two **Storage Account Keys** (Key1 and Key2). These are root-level master passwords for the entire storage account.
If an attacker discovers an Account Key (e.g., leaked in a GitHub repository or extracted from a misconfigured Azure Function), they have full administrative control over all containers and blobs within that account.

Using the Azure CLI to dump data with an Account Key:
```bash
az storage blob download-batch \
    --destination ./loot \
    --source backups \
    --account-name vulnerablecorp \
    --account-key [BASE64_ACCOUNT_KEY]
```

## 5. Defense and Remediation

Securing Azure Blob Storage requires a shift from relying purely on developer diligence to enforcing organizational constraints.

1.  **Disable Public Access at the Account Level**: Azure introduced a global setting at the Storage Account level: `Allow Blob Public Access`. Set this to **False**. This overrides any container-level settings and mathematically prevents accidental public exposure.
2.  **Azure Policy Constraints**: Enforce an Azure Policy across the organization that denies the creation of storage accounts with `Allow Blob Public Access` set to True.
3.  **Use Managed Identities**: Stop using Storage Account Keys and SAS tokens in application code. Applications (like Web Apps or VMs) should use Azure AD Managed Identities to authenticate securely to Blob Storage via RBAC.
4.  **Network Isolation**: Use Azure Private Link/Private Endpoints to expose the storage account only to specific Virtual Networks (VNets), completely removing it from the public internet.
5.  **Microsoft Defender for Storage**: Enable this feature to detect anomalous access patterns, such as a sudden spike in data extraction from a suspicious IP address.

## 6. Forensics and Detection

*   **Storage Analytics Logging**: Azure Storage does not log read operations by default. You must enable **Storage Analytics Logging** or **Azure Monitor resource logs** to track who is accessing the data.
*   **Hunt for Anonymous Access**: Query Azure Monitor logs for `AuthenticationType="Anonymous"`. Any high volume of data transferred (measured via `ResponseHeaderSize` and `ResponseBodySize`) under an anonymous context is a massive red flag.
*   **SAS Token Abuse**: Search logs for `AuthenticationType="SAS"`. Investigate the `CallerIpAddress` and cross-reference it with the expected consumer of that token. Anomalous geographical locations indicate a leaked SAS URL.

## Chaining Opportunities

*   **[[20 - Azure Function Apps — Exposed Secrets]]**: Function Apps frequently store their execution state and configuration in Blob Storage. If the storage is public, an attacker can extract the function's source code and secrets.
*   **[[02 - Cloud OSINT and Reconnaissance]]**: The methodologies used to discover the `blob.core.windows.net` subdomains in the first place.
*   **[[12 - Data Exfiltration Techniques]]**: Using publicly writable Blob storage (misconfigured SAS) as a staging ground to exfiltrate data *out* of a compromised network.

## Related Notes

*   [[14 - AWS S3 Bucket Misconfigurations]] - The direct AWS equivalent to this vulnerability.
*   [[07 - Continuous Cloud Security Posture Management (CSPM)]] - Tools and strategies to automatically detect public buckets at scale.

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

## Appendix A: Exploiting Storage via Azure CLI and REST API

### Enumerating a Discovered Storage Account
When a storage account is discovered via OSINT or brute-forcing, an attacker can use the Azure CLI to attempt to list the containers. If anonymous access is allowed, the CLI will retrieve the list.
```bash
# Attempting to list containers anonymously
az storage container list \
    --account-name targetstorage \
    --auth-mode login \
    --output table
```

### Downloading Data via REST API
If the CLI is unavailable, attackers can use simple `curl` commands to interact with the Blob REST API.
```bash
# Downloading a specific blob anonymously
curl -O "https://targetstorage.blob.core.windows.net/public-backups/database-dump.sql"

# Uploading a file (If misconfigured SAS token allows write)
curl -X PUT -T malicious_payload.exe \
    -H "x-ms-blob-type: BlockBlob" \
    "https://targetstorage.blob.core.windows.net/public-backups/malicious_payload.exe?sv=...&sig=..."
```

## Appendix B: Automation and CI/CD Security
A common vector for leaked Storage Account Keys is CI/CD pipelines. Developers often hardcode keys into GitHub Actions workflows, GitLab CI scripts, or Terraform state files to facilitate automated deployments.
*   **Prevention**: Use OIDC (OpenID Connect) federation between GitHub Actions and Azure AD. This allows the CI/CD pipeline to request short-lived tokens using a Service Principal without ever storing a long-lived credential.

## Appendix C: Data Exfiltration Methodologies
Attackers frequently use publicly writable Azure Blob containers (either via a leaked SAS token or misconfigured container access) as a staging ground for data exfiltration. Because Azure storage URLs (`*.blob.core.windows.net`) are highly trusted by corporate firewalls and often whitelisted, traffic flowing to them blends seamlessly with legitimate business operations.
Defenders must ensure that egress filtering is capable of inspecting TLS traffic (SSL Decryption) or that network boundaries enforce strict Tenant Restrictions, ensuring corporate devices can only connect to the organization's approved Azure AD tenants and storage accounts.
