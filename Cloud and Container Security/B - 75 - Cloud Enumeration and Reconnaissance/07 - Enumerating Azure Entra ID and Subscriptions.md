---
tags: [cloud, basics, enumeration, vapt]
difficulty: beginner
module: "75 - Cloud Enumeration and Reconnaissance"
topic: "75.07 Enumerating Azure Entra ID and Subscriptions"
---

# Enumerating Azure Entra ID and Subscriptions

## 1. Introduction to Azure Reconnaissance
Microsoft Azure presents a uniquely complex attack surface because it inextricably links cloud infrastructure (Azure Resource Manager - ARM) with identity and access management (Microsoft Entra ID, formerly Azure Active Directory). Unlike AWS, where IAM is tightly contained within the AWS platform, Entra ID serves as the identity provider not just for Azure cloud resources, but also for Microsoft 365, Teams, SharePoint, and countless integrated third-party applications.

In a VAPT context, enumerating Azure involves two distinct but overlapping theaters:
1. **The Identity Plane (Entra ID)**: Enumerating users, groups, service principals, app registrations, and directory roles.
2. **The Resource Plane (Azure RM / Subscriptions)**: Enumerating virtual machines, storage accounts, Key Vaults, and role assignments (RBAC) across management groups and subscriptions.

Understanding how to query both planes and finding the intersections where an Entra ID identity is granted privileges over an Azure RM resource is the key to executing successful lateral movement and privilege escalation in Microsoft environments.

## 2. Core Architectural Concepts
Before utilizing enumeration tools, one must understand the structural hierarchy of an Azure environment.

- **Entra ID Tenant**: The dedicated instance of Entra ID representing an organization. It houses the identity directory.
- **Global Administrator**: The highest privilege in Entra ID. By default, they do *not* have access to Azure Subscriptions, but they can trivially elevate themselves to have it (via User Access Administrator).
- **Subscriptions**: Logical containers used to provision Azure resources and handle billing. A tenant can have many subscriptions.
- **Management Groups**: Containers used to manage access, policy, and compliance across multiple subscriptions.
- **Resource Groups**: Logical groupings of resources within a subscription.
- **Service Principals & App Registrations**: Non-human identities used by applications to interact with Entra ID or Azure resources. These are massive targets for attackers.

## 3. Enumeration Architecture Diagram
The following ASCII diagram illustrates the separation and connection between the Identity Plane and the Resource Plane, and where enumeration tools typically interface.

```mermaid
graph TD
    subgraph MICROSOFT CLOUD ENVIRONMENT
        subgraph IDENTITY PLANE: Entra ID <br/> Graph API / Azure AD Graph
            A[Global Admin] --> B[Users & Groups]
            B --> C[App Registrations & Service Principals]
        end
        subgraph RESOURCE PLANE: Azure RM <br/> Azure Resource Manager API
            D[Root Management Group Azure] --> E[Subscriptions]
            E --> F[Resource Groups VMs, KeyVault, Storage Accounts]
        end
        A -- Role Assignments Elevate Access --> D
        B -- Azure RBAC e.g., Owner, Contributor --> E
        C -- Azure RBAC --> F
    end
```

## 4. Initial Access and Authentication
To enumerate Azure, an attacker needs a valid token. This token can be obtained via:
- Phishing (obtaining a user's password and bypassing MFA).
- Illicit Consent Grants (tricking a user into authorizing a malicious App Registration).
- Device Code Phishing (tricking a user into authenticating a device flow request).
- Extracting tokens from a compromised workstation (`%LOCALAPPDATA%\Microsoft\TokenBroker`).
- Compromising an Azure VM with a Managed Identity (similar to AWS IMDS).

Once credentials or tokens are obtained, you can authenticate using the Azure CLI (`az cli`) or PowerShell modules (`Az` or `AzureAD` modules).

```bash
# Login via Azure CLI (Interactive)
az login

# Login using a Service Principal (Client ID and Secret)
az login --service-principal -u <app-id> -p <password> --tenant <tenant-id>

# Login via Device Code (Excellent for avoiding conditional access policies tied to browsers)
az login --use-device-code
```

## 5. Phase 1: Enumerating the Identity Plane (Entra ID)
By default, **any user in Entra ID can read the entire directory**. This includes reading the metadata of all other users, groups, and application registrations. This default configuration makes Entra ID an enumeration goldmine.

The primary endpoint for querying this data is the **Microsoft Graph API**.

### 5.1 Using Azure CLI for Identity Enumeration
While Graph API scripts are more robust, the Azure CLI is often used for quick checks.

**Who am I?**
```bash
az ad signed-in-user show
```

**Listing Users**
```bash
az ad user list --query "[].{UserPrincipalName:userPrincipalName, Title:jobTitle}" --output table
```

**Listing Groups and Memberships**
```bash
az ad group list --output table
# To find members of a high-value group:
az ad group member list --group "Domain Admins" --output table
```

**Listing App Registrations and Service Principals**
Service Principals are critical because they often hold secrets or certificates that can be extracted, leading to privilege escalation.
```bash
az ad sp list --all --output table
```

### 5.2 Deep Graph API Enumeration using ROADtools
For comprehensive identity enumeration, manual CLI commands are insufficient. **ROADtools** (developed by Dirk-jan Mollema) is the premier suite for Entra ID reconnaissance.

The `roadrecon` module authenticates to Azure, downloads the entire Entra ID directory via the Graph API, and stores it in a local SQLite database.

```bash
# Authenticate using device code flow
roadrecon auth --device-code

# Gather all Entra ID data
roadrecon gather

# Launch the local web GUI to analyze the data
roadrecon gui
```
**What to look for in ROADrecon:**
- **Privileged Roles:** Who holds `Global Administrator`, `Privileged Authentication Administrator`, or `User Access Administrator`?
- **App Registrations:** Look for apps with explicit passwords or certificates configured. If you compromise an owner of an app, you can add your own password to the app and authenticate as it.
- **Dynamic Groups:** Groups whose membership is determined by attributes (e.g., "Department=IT"). Modifying your user's attributes could grant membership to privileged groups.

## 6. Phase 2: Enumerating the Resource Plane (Subscriptions)
Once you have mapped the identity layer, you must determine what cloud infrastructure those identities control. This involves querying Azure Resource Manager (ARM).

### 6.1 Discovering Subscriptions
A user may belong to a tenant but have zero access to any Azure subscriptions. Alternatively, they might have access to dozens.
```bash
# List all subscriptions accessible to the current context
az account list --all --output table

# Set the active subscription for subsequent commands
az account set --subscription <Subscription-ID>
```

### 6.2 Enumerating Role-Based Access Control (RBAC)
Azure RBAC defines who can manage resources. You need to identify what role your compromised user holds (Reader, Contributor, Owner, or custom roles).

```bash
# List role assignments for the current subscription
az role assignment list --all --output json

# To see who has access to a specific Resource Group:
az role assignment list --resource-group "Prod-DB-RG"
```
**High-Value Targets in RBAC:**
- **Owner / Contributor:** Can modify resources. Contributors cannot grant access to others, but Owners can.
- **Virtual Machine Contributor:** Can execute commands on VMs via `RunCommand`, leading to systemic compromise.
- **Key Vault Contributor:** Can alter access policies of Key Vaults to read stored secrets.

### 6.3 Enumerating Resources
With access to a subscription, the next step is listing the actual infrastructure.

**List all Resource Groups:**
```bash
az group list --output table
```

**List all Virtual Machines:**
```bash
az vm list --output table
```

**List Storage Accounts:**
Storage accounts often contain VHDs, database backups, or scripts with hardcoded credentials.
```bash
az storage account list --output table
```

**List Key Vaults:**
Key Vaults store passwords, API keys, and certificates.
```bash
az keyvault list --output table
```

## 7. Automated Resource Enumeration Tools

### 7.1 MicroBurst
MicroBurst (by NetSPI) is a suite of PowerShell scripts specifically designed for Azure penetration testing.
```powershell
Import-Module .\MicroBurst.psm1
# Authenticate
Connect-AzAccount
# Run comprehensive discovery
Invoke-AzDomainRecon
Invoke-EnumerateAzureBlobs
```
MicroBurst is exceptional at automatically identifying unauthenticated Azure Blobs, dumping accessible Key Vaults, and finding automation account runbooks that contain plaintext passwords.

### 7.2 Stormspotter
Stormspotter creates an "attack graph" of Azure subscriptions and Entra ID environments. It operates similarly to BloodHound but is heavily optimized for Azure Resource Manager objects and RBAC relationships. It visually plots how an attacker might pivot from a low-level service principal in one subscription to an Owner role in another via nested resource groups and role assignments.

### 7.3 BloodHound (AzureHound)
BloodHound supports Azure via the AzureHound data collector. It collects both Entra ID relationships (like App Roles and Directory Roles) and Azure RM role assignments, linking them together in a neo4j graph database to find multi-step privilege escalation paths (e.g., User A -> Owns App B -> App B is Contributor on Subscription C -> Subscription C contains VM D).

## 8. Identifying Privilege Escalation Vectors during Enumeration
During enumeration, you are actively hunting for specific misconfigurations that allow privilege escalation:
- **Owned App Registrations:** If the user owns an App Registration, you can generate a new client secret for it and authenticate as the Service Principal.
- **Key Vault Access Policies:** Even if you are just a "Contributor" on a resource group containing a Key Vault, you can modify the access policy to grant yourself "Get" permissions on secrets, effectively stealing them.
- **Managed Identities on VMs:** If you have "Virtual Machine Contributor" rights, you can use the `az vm run-command` to execute a script on the VM that curls the Azure Instance Metadata Service (IMDS), stealing the token of any Managed Identity attached to that VM.
- **Automation Accounts:** Enumerating Automation Account runbooks often reveals scripts that use RunAs accounts or hardcoded credentials to perform maintenance tasks.

## 9. Defense and Detection Mechanisms
Azure provides robust logging for enumeration activities, primarily through **Azure Monitor** and **Microsoft Sentinel**.
- **Entra ID Audit Logs:** Logs all Graph API calls, directory reads, and authentications. Massive spikes in directory enumeration by tools like ROADrecon will generate anomalies.
- **Azure Activity Logs:** Logs all ARM API calls (e.g., `List keys`, `Get Role Assignments`). 
- **Microsoft Defender for Cloud:** Triggers native alerts for known enumeration techniques, such as "Suspicious Azure role assignment detected" or "Anomalous multiple resource access attempts".

**Evasion:** To minimize noise, attackers should use Graph API queries targeting specific objects rather than downloading the entire directory, and utilize device code authentication from reputable IP ranges to bypass identity protection risk triggers.

## 10. Conclusion
Enumerating Azure requires navigating the complex interplay between the Entra ID identity plane and the Azure Resource Manager infrastructure plane. A comprehensive enumeration phase using a combination of the Azure CLI, Microsoft Graph API, and tools like ROADrecon and BloodHound is absolutely critical for mapping attack paths, locating hidden secrets, and ultimately compromising the Azure ecosystem.

---
## Chaining Opportunities
- **[[09 - Cloud Metadata Services IMDS Overview]]**: Tokens extracted from Azure VM IMDS can be directly plugged into `az login` to enumerate the resources accessible by the VM's Managed Identity.
- **[[16 - Azure Privilege Escalation Paths]]**: The data gathered from ROADrecon and AzureHound directly feeds into executing escalation techniques like Key Vault dumping and RunCommand abuse.
- **[[21 - Exploiting Azure Storage and SAS Tokens]]**: Enumeration of storage accounts leads directly to hunting for open blobs or misconfigured Shared Access Signatures (SAS).

## Related Notes
- [[02 - Identity and Access Management Concepts]]
- [[13 - Azure Activity Log and Sentinel for Attackers]]
- [[26 - Attacking Azure Functions and Logic Apps]]
