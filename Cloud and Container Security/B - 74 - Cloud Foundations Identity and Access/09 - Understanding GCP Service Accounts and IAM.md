---
tags: [cloud, basics, foundations, vapt]
difficulty: beginner
module: "74 - Cloud Foundations Identity and Access"
topic: "74.09 Understanding GCP Service Accounts and IAM"
---

# Understanding GCP Service Accounts and IAM

## Introduction to Google Cloud IAM
Google Cloud Platform (GCP) Identity and Access Management (IAM) lets administrators authorize who can take action on specific resources. While it shares conceptual similarities with AWS and Azure, GCP IAM is uniquely structured around a strict, hierarchical inheritance model and heavily emphasizes the use of Service Accounts for all programmatic access.

GCP IAM does not natively maintain its own directory of users. Instead, it relies entirely on Google Workspace (formerly G Suite) or Cloud Identity to manage human identities, federating access seamlessly.

---

## The GCP Resource Hierarchy

To understand GCP IAM, you must first understand the Resource Hierarchy. In GCP, policies flow downwards. A permission granted at a higher level is unconditionally inherited by all lower levels.

1. **Organization:** The root node (e.g., `example.com`). Policies applied here affect all folders and projects company-wide.
2. **Folders:** Logical groupings, often used to map to company departments (e.g., "Engineering", "Finance") or environments ("Production", "Staging"). Folders can be nested.
3. **Projects:** The core logical boundary in GCP. All compute, storage, and networking resources *must* belong to a project. Billing is tied to projects.
4. **Resources:** The individual entities (Compute Engine instances, Cloud Storage buckets, BigQuery datasets).

### The Hierarchy and Inheritance Visualized

```text
+-------------------------------------------------------------+
|                      Organization                           |
|                      (example.com)                          |
+------------------------------+------------------------------+
                               | Inherits Policies
                               v
+------------------------------+------------------------------+
|                        Folder (Prod)                        |
|   IAM: Group 'prod-admins' -> Role: roles/editor            |
+------------------------------+------------------------------+
                               | Inherits Policies
                               v
+------------------------------+------------------------------+
|                     Project (web-backend)                   |
|   IAM: SA 'app-sa' -> Role: roles/storage.objectAdmin       |
+------------------------------+------------------------------+
                               | Inherits Policies
                               v
+------------------------------+------------------------------+
|                Resource (Cloud Storage Bucket)              |
|   IAM: user 'alice' -> Role: roles/storage.objectViewer     |
+------------------------------+------------------------------+

Resulting Access on the Storage Bucket:
- prod-admins: Editor (Inherited from Folder)
- app-sa: Object Admin (Inherited from Project)
- alice: Object Viewer (Applied explicitly at Resource-level)
```
*Note: Because permissions are additive, you cannot apply an "Allow" at the Folder level and easily override it with a "Deny" at the Project level using standard IAM. (Though GCP recently introduced Deny Policies to handle this exact scenario).*

---

## Core GCP IAM Concepts

An IAM Policy in GCP is a collection of bindings. A binding binds one or more **Members** to a single **Role**.

### 1. Members (The "Who")
- **Google Account:** Individual users (`user@gmail.com` or `alice@example.com`).
- **Google Group:** A collection of accounts. Highly recommended for assigning permissions to humans.
- **Service Account:** An identity for applications and VMs (e.g., `my-app@my-project.iam.gserviceaccount.com`).
- **Google Workspace Domain:** Grants access to anyone within a specific domain.

### 2. Roles (The "What")
A role is a collection of permissions (e.g., `compute.instances.start`).
- **Basic (Primitive) Roles:** `Owner`, `Editor`, `Viewer`. These are legacy roles that apply to almost all GCP services. **They are extremely dangerous** due to their broad scope and should be avoided in production. (e.g., `Editor` can delete almost anything in the project).
- **Predefined Roles:** Fine-grained, service-specific roles managed by Google (e.g., `roles/compute.networkAdmin`, `roles/storage.objectViewer`).
- **Custom Roles:** User-defined roles created by cherry-picking specific API permissions to strictly enforce least privilege.

---

## Deep Dive: GCP Service Accounts (SAs)

Service Accounts are the lifeblood of machine-to-machine communication in GCP. They act as both an **Identity** (a principal that can be assigned roles) and a **Resource** (a target that can have permissions assigned to it, dictating who can act as the SA).

### Types of Service Accounts
1. **User-Managed:** Created and managed by cloud administrators for custom applications.
2. **Default Service Accounts:** Automatically created when enabling services (e.g., the Compute Engine default SA). **Danger:** By default, the Compute Engine default SA is granted the primitive `Editor` role on the entire project. This is a massive security risk.
3. **Google-Managed:** Internal accounts used by GCP services to communicate with each other behind the scenes.

### Service Account Authentication

Unlike AWS Roles which are inherently assumed, GCP SAs can authenticate in multiple ways:

1. **Service Account Keys:** RSA public/private key pairs downloaded as a JSON file.
   - *Risk:* These are long-lived, highly sensitive secrets. If a developer accidentally commits a SA JSON key to GitHub, an attacker can authenticate to GCP as that SA permanently (until the key is revoked).
2. **Attached to Compute (Metadata Server):** VMs, Cloud Run, and GKE nodes can have an SA attached to them. The application fetches temporary, short-lived OAuth 2.0 access tokens from the local GCP Metadata API (`http://metadata.google.internal`).
3. **Service Account Impersonation:** A user or another SA can be granted the `Service Account Token Creator` role. This allows them to request short-lived credentials for the target SA without ever downloading a JSON key.
4. **Workload Identity Federation:** Allows external workloads (AWS, Azure, GitHub Actions) to impersonate a GCP Service Account using OIDC tokens, entirely eliminating the need to export and manage long-lived JSON keys.

---

## Common Attack Vectors in GCP IAM

### 1. Default Service Account Abuse
If an attacker compromises a compute instance running with the default Compute Engine SA, they instantly inherit the `roles/editor` role. They can move laterally to any resource in the project, modify infrastructure, and access sensitive data.

### 2. Service Account Privilege Escalation
If a developer assigns the `roles/iam.serviceAccountUser` role to a principal along with permissions to create compute instances (`compute.instances.create`), the attacker can create a new VM, attach a highly privileged SA (like project Owner) to the VM, log into the VM, and extract the Owner token via the metadata server.

### 3. SSRF to Metadata API
If a web application hosted on GCP is vulnerable to Server-Side Request Forgery (SSRF), an attacker can force the application to make a GET request to `http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token` (bypassing the `Metadata-Flavor: Google` header requirement if the SSRF allows header injection or via certain edge cases). This returns the temporary access token for the VM's service account, granting the attacker cloud access.

## Chaining Opportunities
- [[06 - Cloud Identity and Access Management IAM Basics]]
- [[07 - Understanding AWS Policies Roles and Users]]
- [[08 - Understanding Azure Active Directory Entra ID Basics]]

## Related Notes
- [[10 - Cloud Storage Basics S3 Blobs Buckets]]
