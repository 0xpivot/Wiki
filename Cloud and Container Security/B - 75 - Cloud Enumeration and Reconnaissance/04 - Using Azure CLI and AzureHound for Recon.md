---
tags: [cloud, basics, enumeration, vapt]
difficulty: beginner
module: "75 - Cloud Enumeration and Reconnaissance"
topic: "75.04 Using Azure CLI and AzureHound for Recon"
---

# Using Azure CLI and AzureHound for Reconnaissance

## 1. Introduction to Azure Reconnaissance

Microsoft Azure has a fundamentally different architecture compared to AWS. Azure heavily relies on Microsoft Entra ID (formerly Azure Active Directory) for identity and access management. The hierarchy in Azure flows from the Tenant (Directory) -> Management Groups -> Subscriptions -> Resource Groups -> Resources.

For a penetration tester, enumerating Azure requires understanding both the infrastructure (Virtual Machines, Key Vaults, Blob Storage) and the highly complex Entra ID RBAC (Role-Based Access Control) relationships. The Azure CLI (`az`) is the primary tool for querying this infrastructure, while `AzureHound` is used to map out the intricate, hidden relationships that can lead to privilege escalation.

## 2. Architecture and Attack Flow

```text
+---------------------+        +-------------------------+        +---------------------------+
|   Attacker / VAPT   |        |   Azure CLI &           |        |   Azure Cloud / Entra ID  |
|   Professional      |        |   AzureHound            |        |   (Target Tenant)         |
+---------------------+        +-------------------------+        +---------------------------+
           |                               |                                |
           | 1. az login (interactive or   |                                |
           |    service principal)         |                                |
           |------------------------------>|                                |
           |                               |                                |
           | 2. az account show            |                                |
           |<------------------------------|                                |
           |                               |                                |
           | 3. Enumerate Subscriptions    |                                |
           |    and Resource Groups        |                                |
           |--------------------------------------------------------------->|
           |                               |                                |
           | 4. Run AzureHound             |                                |
           |    (Invoke-AzureHound)        |                                |
           |--------------------------------------------------------------->|
           |                               |                                |
           | 5. Extract JSON data files    |                                |
           |    (users, roles, groups)     |                                |
           |<---------------------------------------------------------------|
           |                               |                                |
           | 6. Import to BloodHound UI    |                                |
           |    & identify attack paths    |                                |
           |------------------------------>|                                |
```

## 3. The "How": Detailed Methodology with Azure CLI

### Step 1: Authentication
You can authenticate using a standard user account or a Service Principal (the Azure equivalent of an AWS IAM Role/Service Account).

```bash
# Interactive browser login
$ az login

# Service Principal login (using Client ID and Secret)
$ az login --service-principal -u <app-id> -p <password> --tenant <tenant-id>
```

### Step 2: "Who Am I?" and Tenant Context
```bash
# Get current account and tenant details
$ az account show
```
Example Output:
```json
{
  "environmentName": "AzureCloud",
  "id": "11111111-2222-3333-4444-555555555555",
  "isDefault": true,
  "name": "Production Subscription",
  "state": "Enabled",
  "tenantId": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
  "user": {
    "name": "attacker@compromised-domain.com",
    "type": "user"
  }
}
```

### Step 3: Enumerating Subscriptions and Resource Groups
Resources in Azure are organized into Resource Groups, which sit inside Subscriptions.
```bash
# List all subscriptions you have access to
$ az account list --output table

# List Resource Groups in the current subscription
$ az group list --output table
```

### Step 4: Enumerating Key Resources
```bash
# List Virtual Machines and their public IPs
$ az vm list-ip-addresses --output table

# List Storage Accounts (Azure's equivalent to S3 buckets)
$ az storage account list

# List Key Vaults (Often contain secrets and certificates)
$ az keyvault list
```

## 4. Deep Dive: AzureHound and BloodHound

While `az` is great for listing resources, it is terrible at visualizing complex RBAC relationships. This is where **AzureHound** comes in.

AzureHound is the data collector for BloodHound, specifically designed for Microsoft Azure and Entra ID. It queries the Microsoft Graph API and Azure Resource Manager (ARM) to extract users, groups, apps, service principals, devices, tenant properties, subscriptions, resource groups, and VMs.

### Executing AzureHound
AzureHound can be run as a standalone binary or a PowerShell script.

```bash
# Run AzureHound using a Service Principal
$ ./azurehound -u "app-id" -p "password" -t "tenant-id" list --tenant "tenant-id"
```
This command will reach out to Azure and generate multiple JSON files:
- `users.json`
- `groups.json`
- `roles.json`
- `devices.json`
- `tenant.json`

### BloodHound Analysis
Once the JSON files are generated, you import them into the BloodHound GUI. BloodHound uses a Neo4j graph database to map relationships.
Pentesters look for edges like:
- `AZOwns`: A user owns a service principal.
- `AZHasRole`: A user has a specific RBAC role.
- `AZContributor`: A user has contributor rights over a resource group.

By finding a path from a compromised low-privilege user to a high-privilege role (like `Global Administrator` or `Subscription Owner`), attackers can systematically escalate privileges.

## 5. Tools of the Trade

- **Azure CLI (`az`)**: The official command-line tool.
- **AzureHound**: The data collector for BloodHound in Azure environments.
- **MicroBurst**: A PowerShell toolkit for attacking Azure, containing modules for discovering resources, extracting secrets, and privilege escalation.
- **Stormspotter**: An Azure-specific attack graph tool similar to BloodHound, developed by Azure Security.

## 6. Case Studies / Examples

**Case Study: The Run Command Pivot**
An attacker gains "Contributor" access to a Resource Group containing a Virtual Machine. Using the Azure CLI, the attacker utilizes the `Run Command` feature to execute arbitrary code on the VM without needing SSH or RDP access:
```bash
$ az vm run-command invoke \
    --resource-group target-rg \
    --name target-vm \
    --command-id RunShellScript \
    --scripts "cat /etc/shadow"
```
If the VM has a Managed Identity attached, the attacker can use this script execution to curl the Azure Metadata endpoint and steal the Managed Identity token, pivoting to further resources.

## 7. Mitigation and Defense

### Principle of Least Privilege
Limit the use of "Owner" and "Contributor" roles at the Subscription level. Assign roles at the Resource Group or individual Resource level instead.

### Entra ID Conditional Access
Implement Conditional Access policies requiring MFA for all users, especially when authenticating from untrusted IP addresses. This severely hinders an attacker's ability to use stolen credentials.

### Monitor Graph API Usage
Monitor logs for excessive queries against the Microsoft Graph API, which often indicates an AzureHound execution.

## 8. Chaining Opportunities
- **[[01 - OSINT for Cloud Assets Domain to Cloud IP]]**: Mapping custom Azure domains back to the tenant.
- **Managed Identity Extraction**: Using execution access on Azure VMs to steal metadata tokens.
- **Key Vault Dumping**: Using discovered permissions to dump secrets from `az keyvault`.

## 9. Related Notes
- [[01 - OSINT for Cloud Assets Domain to Cloud IP]]
- [[03 - Using AWS CLI for Reconnaissance]]
- [[05 - Using GCP CLI gcloud for Reconnaissance]]
