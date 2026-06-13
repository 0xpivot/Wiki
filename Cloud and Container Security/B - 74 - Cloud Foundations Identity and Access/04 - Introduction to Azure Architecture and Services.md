---
tags: [cloud, basics, foundations, vapt]
difficulty: beginner
module: "74 - Cloud Foundations Identity and Access"
topic: "74.04 Introduction to Azure Architecture and Services"
---

# 74.04 Introduction to Azure Architecture and Services

## 1. Executive Summary
Microsoft Azure is the second-largest public cloud provider, deeply integrated with the Microsoft ecosystem and heavily favored by enterprises already reliant on Windows Server, Active Directory, and Microsoft 365. For a VAPT professional, Azure presents a unique threat landscape. While it shares conceptual similarities with AWS, its architecture, identity management (Entra ID), and authorization mechanisms (RBAC) are profoundly different. A deep understanding of the Azure Resource Manager (ARM) hierarchy and the intricate relationship between Entra ID and Azure resources is essential for identifying misconfigurations, privilege escalation vectors, and lateral movement paths.

## 2. Microsoft Azure Global Infrastructure
Azure's infrastructure is organized to ensure data residency, compliance, and high availability.

### 2.1 Geographies and Regions
- **Geography:** A discrete market typically containing two or more regions that preserves data residency and compliance boundaries (e.g., United States, Europe).
- **Region:** A set of data centers deployed within a latency-defined perimeter and connected through a dedicated regional low-latency network (e.g., `East US`, `North Europe`). Azure pairs regions within the same geography (e.g., East US and West US) to enable cross-region replication for disaster recovery.

### 2.2 Availability Zones (AZs)
Similar to AWS, Availability Zones are physically separate locations within an Azure region. Each zone is made up of one or more data centers equipped with independent power, cooling, and networking.

## 3. Azure Resource Manager (ARM) and Hierarchy
Azure Resource Manager (ARM) is the deployment and management service for Azure. It provides a management layer that enables you to create, update, and delete resources in your Azure account. Crucially, access control (RBAC) is applied at various scopes within the ARM hierarchy. Understanding this hierarchy is the key to understanding Azure permissions.

### 3.1 The Four Levels of Scope
1. **Management Groups:** These are containers that help manage access, policy, and compliance across multiple subscriptions.
2. **Subscriptions:** A logical container used to provision resources in Azure. It serves as a billing boundary and an access control boundary. Trust is established with a single Microsoft Entra ID (Azure AD) tenant.
3. **Resource Groups (RGs):** A logical container into which Azure resources (web apps, databases, storage accounts) are deployed and managed. Resources that share the same lifecycle are usually grouped here.
4. **Resources:** The actual individual services being used (e.g., a Virtual Machine, a Blob Storage account, a SQL Database).

*Security Implication:* Permissions in Azure flow downwards. If an attacker compromises an identity with "Contributor" access at the Subscription level, they inherently have "Contributor" access to every Resource Group and Resource within that subscription.

## 4. ASCII Diagram: Azure Resource Management Hierarchy

```text
+-------------------------------------------------------------------------------+
|                       AZURE RESOURCE MANAGER HIERARCHY                        |
+-------------------------------------------------------------------------------+
|                                                                               |
|                     [ Microsoft Entra ID (Tenant) ]                           |
|                      (Identity & Access Boundary)                             |
|                                     |                                         |
|                                     v                                         |
|                       [ Root Management Group ]                               |
|                                     |                                         |
|               +---------------------+---------------------+                   |
|               |                                           |                   |
|               v                                           v                   |
|   [ Management Group A ]                      [ Management Group B ]          |
|   (e.g., Production)                          (e.g., Development)             |
|               |                                           |                   |
|               v                                           v                   |
|     [ Subscription 1 ]                          [ Subscription 2 ]            |
|     (Billing Boundary)                          (Billing Boundary)            |
|               |                                           |                   |
|       +-------+-------+                                   v                   |
|       |               |                           [ Resource Group C ]        |
|       v               v                                   |                   |
| [ Res Group A ] [ Res Group B ]                           v                   |
|       |               |                             [ Azure VM ]              |
|       v               v                                                       |
| [ Storage Act ] [ Azure SQL DB ]                                              |
|                                                                               |
+-------------------------------------------------------------------------------+
```

## 5. Core Azure Services & Security Posture

### 5.1 Compute Services
- **Azure Virtual Machines:** IaaS instances running Windows or Linux.
  - *Pentesting focus:* Run Command execution, custom script extensions, and Managed Identity token extraction via the Azure IMDS endpoint (`169.254.169.254`).
- **Azure App Service:** A fully managed PaaS for building, deploying, and scaling web apps.
  - *Pentesting focus:* Subdomain takeovers (dangling CNAMEs pointing to `.azurewebsites.net`), exposed environment variables containing credentials, and misconfigured authentication (Easy Auth).
- **Azure Functions:** Serverless compute service (FaaS).
- **Azure Kubernetes Service (AKS):** Managed Kubernetes offering.

### 5.2 Storage Services
- **Azure Storage Accounts:** A massive scalable object store for text and binary data. It encompasses Blob Storage (like S3), File Storage, Queue Storage, and Table Storage.
  - *Pentesting focus:* Discovering publicly exposed Blob containers (Anonymous read access), extracting Shared Access Signatures (SAS) tokens that provide overly broad access, and listing storage account access keys.

### 5.3 Networking Services
- **Virtual Network (VNet):** The fundamental building block for private networks in Azure.
- **Network Security Groups (NSGs):** Act as virtual firewalls to filter network traffic to and from Azure resources in a VNet.
- **Application Security Groups (ASGs):** Enable configuring network security as a natural extension of an application's structure.
- **Azure Firewall:** A managed, cloud-based network security service.

## 6. Azure Identity and Access Management (Entra ID)
Azure identity is fundamentally different from AWS IAM. It relies on **Microsoft Entra ID** (formerly Azure Active Directory). 

### 6.1 Microsoft Entra ID vs. Windows Server AD
Entra ID is not just a cloud version of on-premises Active Directory. It is an identity and access management service built for HTTP/REST APIs. It uses protocols like SAML 2.0, OpenID Connect, and OAuth 2.0, whereas on-premise AD relies on Kerberos and NTLM.

### 6.2 Entra ID Roles vs. Azure RBAC Roles
This distinction is a massive source of confusion and security vulnerabilities:
- **Entra ID Roles (Directory Roles):** Control access to identity resources and SaaS applications (e.g., Global Administrator, User Administrator, Exchange Administrator). They manage the tenant.
- **Azure RBAC Roles (Resource Roles):** Control access to Azure resources via ARM (e.g., Owner, Contributor, Reader). They manage the subscriptions and VMs.
- *The Bridge:* A user can be a Global Administrator in Entra ID but have zero access to an Azure Subscription, unless they explicitly elevate their access using a specific toggle that grants them "User Access Administrator" at the root scope.

### 6.3 Identities and Service Principals
- **Users:** Human identities.
- **App Registrations & Service Principals:** When an application needs to access resources, it requires an identity. You create an App Registration, which generates a Service Principal in the tenant.
  - *Pentesting focus:* Attackers target leaked Client IDs and Client Secrets associated with high-privileged Service Principals.
- **Managed Identities:** Azure's equivalent to AWS IAM Roles for compute resources. The system automatically manages the creation and rotation of credentials. A VM with a System-Assigned Managed Identity can authenticate to Azure Key Vault or Blob Storage without any hardcoded credentials.

## 7. Azure Native Security Tools
- **Microsoft Defender for Cloud (formerly Azure Security Center):** A Cloud Security Posture Management (CSPM) and Cloud Workload Protection Platform (CWPP). It provides secure score, policy compliance, and threat alerts.
- **Microsoft Sentinel:** A scalable, cloud-native SIEM and SOAR solution.
- **Azure Key Vault:** Used to safeguard cryptographic keys and secrets (like connection strings and passwords) used by cloud applications and services.
  - *Pentesting focus:* If an attacker compromises a VM, they will attempt to extract its Managed Identity token and use it to dump secrets from the Key Vault.

## 8. VAPT Perspective: Initial Attack Vectors in Azure

### 8.1 Illicit Consent Grants (Phishing)
Because Entra ID relies heavily on OAuth, a primary attack vector is registering a malicious application and tricking a user into granting it permissions.
- The attacker sends a phishing email with a link to log in via Microsoft.
- The user logs in and is presented with a prompt: "App 'Document Viewer' wants to read your emails and access your files."
- If the user clicks "Accept", the attacker receives an OAuth token granting them API access to the user's Microsoft 365 data, bypassing MFA entirely.

### 8.2 Subdomain Takeover
Azure App Services, Traffic Manager profiles, and Storage Accounts often use custom domain names pointing to an Azure-provided subdomain (e.g., `company.azurewebsites.net`). If the resource is deleted but the DNS CNAME record remains, an attacker can register that exact Azure subdomain and host malicious content, effectively hijacking the company's subdomain.

### 8.3 Automation Account & Runbook Exploitation
Azure Automation provides cloud-based automation and configuration. Runbooks often contain hardcoded credentials or utilize Run As accounts with extensive Subscription permissions.
- *Vector:* An attacker with low-level access might be able to read runbook code or edit a runbook to execute malicious PowerShell commands under the context of a highly privileged Managed Identity.

## 9. Privilege Escalation and Lateral Movement in Azure
- **Role Assignments:** Identifying over-permissive custom RBAC roles (e.g., permissions like `Microsoft.Authorization/roleAssignments/write` which allows the attacker to make themselves an Owner of the subscription).
- **Lateral Movement:** Pivoting from a compromised on-premises AD environment to the Azure Cloud via compromised Azure AD Connect synchronization accounts (e.g., extracting the AD DS Connector account credentials or manipulating the sync process).
- **Pass-the-PRT:** Extracting the Primary Refresh Token (PRT) from a compromised Windows endpoint that is Hybrid Azure AD joined, allowing the attacker to authenticate to Azure services as the user while bypassing MFA constraints.

## 10. Chaining Opportunities
- **[[02 - Cloud Shared Responsibility Model]]**: Applying the model to Azure PaaS (App Services) versus Azure IaaS (Virtual Machines) to determine the exact penetration testing boundaries.
- **[[01 - Introduction to Cloud Computing IaaS PaaS SaaS]]**: Understanding how Azure implements PaaS and SaaS (Microsoft 365) integrations.

## 11. Related Notes
- [[03 - Introduction to AWS Architecture and Services]]
- [[05 - Introduction to GCP Architecture and Services]]
- Azure Managed Identities and Token Extraction
- Exploiting OAuth and Illicit Consent Grants
