---
tags: [cloud, basics, foundations, vapt]
difficulty: beginner
module: "74 - Cloud Foundations Identity and Access"
topic: "74.08 Understanding Azure Active Directory Entra ID Basics"
---

# Understanding Azure Active Directory (Entra ID) Basics

## Introduction to Microsoft Entra ID
Microsoft Entra ID (formerly known as Azure Active Directory or Azure AD) is Microsoft’s cloud-based identity and access management service. It is crucial to understand that **Entra ID is NOT simply Windows Server Active Directory (AD) running in the cloud.** While they share a name and both handle identity, their architectures, protocols, and use cases are fundamentally different.

- **Legacy AD:** Uses Kerberos, NTLM, LDAP. Hierarchical OUs. Designed for LAN environments.
- **Entra ID:** Uses SAML 2.0, OAuth 2.0, OpenID Connect (OIDC), REST/Graph APIs. Flat directory structure. Designed for the web and cloud.

Entra ID is the central identity provider not just for Azure cloud infrastructure, but also for Microsoft 365 (Office, Exchange, Teams) and thousands of third-party SaaS applications.

---

## Azure Architecture Hierarchy

To understand access control in Azure, one must understand its structural hierarchy. Azure separates identity management from resource management into two distinct planes.

### The Identity Plane (Entra ID Tenant)
A **Tenant** represents a single organization in Entra ID (e.g., `contoso.onmicrosoft.com`). It contains the directory of users, groups, and application registrations.

### The Resource Plane (Azure Cloud)
This hierarchy manages the actual cloud resources (VMs, databases, networks).
1. **Management Groups:** Provide a governance scope above subscriptions. Used to apply Azure Policies and RBAC across multiple subscriptions.
2. **Subscriptions:** The primary billing and logical boundary. Resources must belong to a subscription.
3. **Resource Groups:** Logical containers within a subscription holding related resources for an application.
4. **Resources:** The actual instances (e.g., a specific Virtual Machine or Storage Account).

### Visualizing the Azure Flow

```mermaid
graph TD
    subgraph Tenant Directory / Entra ID
        A[Global Admin] -->|Elevate access to Azure Resources| B[Management Group Root]
        C[Entra ID Roles]
    end
    subgraph Management Group Root
        subgraph Subscription e.g., Prod
            subgraph Resource Group Web-App
                D[Virtual Machine Owner]
                E[Storage Account Reader]
            end
        end
    end
```

---

## Two Distinct RBAC Systems: Entra ID Roles vs. Azure RBAC

A massive source of confusion (and security vulnerabilities) is the existence of two completely separate role-based access control systems in the Microsoft ecosystem.

### 1. Entra ID Roles (Directory Roles)
These roles control access to the **Identity Plane** (Tenant administration, Microsoft 365 services, billing).
- **Global Administrator:** The supreme master of the tenant. Analogous to AWS Root. Can manage all identities and reset user passwords.
- **Privileged Role Administrator:** Can assign Entra ID roles to others.
- **User Administrator:** Can create and manage standard users.
- *Crucially, an Entra ID Global Administrator does NOT automatically have access to Azure Subscriptions and resources. However, they possess a built-in switch to "elevate access," allowing them to grant themselves User Access Administrator over the root Management Group, effectively taking over the entire cloud infrastructure.*

### 2. Azure RBAC (Resource Roles)
These roles control access to the **Resource Plane** (Subscriptions, Resource Groups, VMs, Storage). Azure RBAC uses the `Role Assignment` model: `Principal + Role Definition + Scope`.
- **Owner:** Full access to manage all resources AND the ability to assign access to others (modify IAM).
- **Contributor:** Full access to manage all resources, but CANNOT assign access to others or modify RBAC.
- **Reader:** Can view resources but cannot make any modifications.

---

## Principals in Azure

### Users and Groups
Identities synced from on-premises AD (via Entra Connect) or cloud-only identities created natively in Entra ID.

### App Registrations and Service Principals
When an application needs to access Entra ID or Azure APIs, it requires an identity.
1. **App Registration:** The globally unique definition of the application. It acts as a template.
2. **Service Principal:** The local instantiation (or "instance") of the App Registration within a specific tenant. This is the actual identity that is assigned roles and permissions.
- Authenticates via Client Secrets (passwords) or Certificates.

### Managed Identities
The Azure equivalent of AWS IAM Roles attached to EC2. It eliminates the need to manage Service Principal credentials manually.
- **System-Assigned:** Tied to the lifecycle of a specific Azure resource. If the VM is deleted, the identity is automatically destroyed.
- **User-Assigned:** A standalone identity that can be attached to one or multiple resources.

---

## Conditional Access Policies (CAPs)

Conditional Access is the zero-trust policy engine of Entra ID. Instead of simply relying on a password, it evaluates real-time signals before making an access decision.
- **Signals:** Who is the user? What is their IP? Are they on a managed Intune device? Is the sign-in flagged as high risk by Microsoft Threat Intelligence?
- **Decision:** Block access, grant access, or require additional verification.
- **Enforcement:** Enforce MFA, require a compliant device, or force a password reset.

---

## Common Attack Vectors in Entra ID

### 1. Illicit Consent Grants
Phishing attacks where an attacker tricks a user into granting an attacker-controlled multi-tenant application permissions to read their emails or access their files (via OAuth consent prompts). This bypasses MFA entirely.

### 2. Pass-the-PRT (Primary Refresh Token)
If an attacker compromises a user's Windows device that is Entra-joined, they can extract the PRT from memory (similar to Pass-the-Hash). The PRT acts as a master SSO token, allowing the attacker to access Azure resources without needing the password or triggering MFA.

### 3. Service Principal Secret Abuse
Developers frequently hardcode Service Principal client secrets in code repositories. Because Service Principals often bypass Conditional Access Policies (like MFA), leaking a secret provides a reliable, persistent backdoor for attackers.

## Chaining Opportunities
- [[06 - Cloud Identity and Access Management IAM Basics]]
- [[07 - Understanding AWS Policies Roles and Users]]
- [[09 - Understanding GCP Service Accounts and IAM]]

## Related Notes
- [[10 - Cloud Storage Basics S3 Blobs Buckets]]
