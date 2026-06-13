---
tags: [cloud, basics, foundations, vapt]
difficulty: beginner
module: "74 - Cloud Foundations Identity and Access"
topic: "74.10 Cloud Storage Basics S3 Blobs Buckets"
---

# Cloud Storage Basics: S3, Blobs, and Buckets

## Introduction to Cloud Object Storage
Cloud Object Storage is arguably the most fundamental and widely used service in modern cloud computing. Unlike traditional block storage (hard drives attached to a VM) or file storage (NFS/SMB network shares with deep directory trees), object storage is designed for massive scalability, unstructured data, and access over the internet via HTTP/REST APIs.

### The Core Terminology
While cloud providers use different names, the architecture is identical:
- **AWS:** S3 (Simple Storage Service) -> Uses **Buckets** and **Objects**.
- **Azure:** Azure Blob Storage -> Uses **Storage Accounts**, **Containers**, and **Blobs**.
- **GCP:** Google Cloud Storage (GCS) -> Uses **Buckets** and **Objects**.

### Object Storage Paradigm
- **Flat Namespace:** There are no true "directories" or "folders" in object storage. An object named `images/2026/photo.jpg` is a single object with a long string name. The slashes are merely an illusion parsed by the console UI to make it look like a folder structure.
- **Metadata:** Objects are stored alongside robust, customizable metadata (key-value pairs) rather than traditional file attributes.
- **Immutability:** Objects are generally immutable. You don't "edit" a 5GB video file in a bucket; you overwrite it entirely with a new version.

---

## Storage Access Control Mechanisms

Because object storage is internet-facing by design, securing it is paramount. Misconfigured storage is responsible for some of the largest data breaches in history. Access is evaluated by a complex engine checking multiple layers of policies.

### The Access Resolution Flow Visualized

```text
+------------------------+
|   Client / Attacker    |
+-----------+------------+
            |
            | 1. Request Object (GET /bucket/file.txt)
            v
+-----------+------------+
|  Cloud Storage Engine  |
|   (AWS S3/Azure/GCP)   |
+-----------+------------+
            | 2. Identity Context Extracted
            |    (Anonymous vs Authenticated)
            v
+-----------+------------+        +--------------------+
|   Access Evaluation    |        | 1. Org Policies    |
|   (Deny vs Allow)      +------> | 2. Bucket Policies |
|                        |        | 3. IAM Policies    |
+-----------+------------+        | 4. ACLs            |
            |                     +--------------------+
            | 3. Decision
            v
    +-------+-------+
    |               |
+---v---+       +---v---+
| DENY  |       | ALLOW |
+-------+       +---+---+
                    |
                    v
            +-------+-------+
            |  Data Object  |
            | (Encrypted?)  |
            +---------------+
```

### 1. Identity-Based IAM Policies
Attached to users or roles (e.g., "Alice is allowed to read from `my-corporate-bucket`"). Effective for internal cloud infrastructure.

### 2. Resource-Based Policies (Bucket Policies)
Attached directly to the bucket. These are incredibly powerful because they dictate *who* can access the bucket, regardless of their IAM permissions.
- Used heavily for cross-account access or granting public access.
- Example: An S3 Bucket policy that denies all `s3:PutObject` requests unless the object is uploaded with AES256 encryption.

### 3. Access Control Lists (ACLs)
A legacy mechanism applied at the bucket OR individual object level.
- Highly discouraged in modern environments because they create fragmented, invisible access rules. (AWS explicitly recommends disabling ACLs and relying solely on IAM/Bucket Policies).

### 4. Block Public Access (BPA)
A master kill-switch implemented by AWS (and mirrored by others) at the Account or Bucket level. If BPA is enabled, it forcefully overrides any Bucket Policy or ACL that attempts to make data public.

---

## Temporary Delegated Access (Pre-signed URLs & SAS Tokens)

Applications often need to allow users to upload or download a file directly to/from cloud storage without routing massive payloads through the application server.

### AWS / GCP: Pre-signed URLs
The application backend uses its highly privileged IAM role to generate a cryptographically signed URL. This URL is given to the client.
- The client makes an HTTP request directly to the S3/GCS bucket using this URL.
- The URL encodes the permitted action (`GET` or `PUT`) and an expiration timer (e.g., 15 minutes).
- **Vulnerability:** If an attacker intercepts a pre-signed URL, they can use it before it expires. If a pre-signed URL is generated for a `PUT` operation without enforcing file type restrictions in the backend, attackers can upload malware.

### Azure: Shared Access Signatures (SAS Tokens)
Similar to pre-signed URLs but significantly more granular. A SAS token is appended to the Blob URL.
- Can restrict by IP address, specific protocols (HTTPS only), specific permissions (Read, Write, Delete, List), and time windows.
- **Account SAS vs. Service SAS vs. User Delegation SAS:** User Delegation SAS is the most secure as it relies on Entra ID credentials rather than the master Storage Account Key.

---

## Data Encryption at Rest

Cloud providers offer robust encryption to ensure that even if physical drives are stolen from a datacenter, the data remains unreadable.

1. **Provider-Managed Keys (SSE-S3 / Platform Managed):** The easiest method. The cloud provider generates, rotates, and manages the AES-256 encryption keys transparently.
2. **Customer-Managed Keys (SSE-KMS / CMK):** The customer creates a key in AWS KMS, Azure Key Vault, or GCP Cloud KMS. This is highly secure because the key itself has its own IAM policy. Even if an attacker has an S3 policy allowing `s3:GetObject`, if they don't *also* have `kms:Decrypt` permission for the key encrypting that object, access is denied.
3. **Customer-Provided Keys (SSE-C):** The customer passes their own raw encryption key via HTTP headers with every read/write request. The cloud provider encrypts the data in RAM and throws the key away.

---

## Common Attack Vectors in Cloud Storage

### 1. Publicly Exposed Buckets
The most notorious cloud vulnerability. If a bucket policy contains `"Principal": "*"` and `"Action": "s3:GetObject"`, the entire contents of the bucket are accessible to anyone on the internet via a web browser.

### 2. S3 Bucket Enumeration
Attackers use tools to brute-force bucket names (since bucket names share a global DNS namespace). If they find a bucket and it allows the `s3:ListBucket` action publicly, they map the entire file structure looking for secrets, PII, or database backups.

### 3. Ransomware via Misconfigured Versioning
If a bucket does not have versioning enabled, an attacker with write access can overwrite all objects with encrypted blobs and demand a ransom. If MFA-Delete is not enabled, they can delete the objects permanently.

### 4. Over-permissive SAS Tokens
In Azure environments, developers sometimes generate Account-level SAS tokens with no expiration date and commit them to source code. This acts as a permanent skeleton key to the entire storage account.

## Chaining Opportunities
- [[06 - Cloud Identity and Access Management IAM Basics]]
- [[07 - Understanding AWS Policies Roles and Users]]
- [[08 - Understanding Azure Active Directory Entra ID Basics]]
- [[09 - Understanding GCP Service Accounts and IAM]]

## Related Notes
- [[01 - API1 — Broken Object Level Authorization (BOLA)]]
