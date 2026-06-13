---
tags: [cloud, basics, enumeration, vapt]
difficulty: beginner
module: "75 - Cloud Enumeration and Reconnaissance"
topic: "75.02 Discovering Exposed Cloud Storage S3 Scanner"
---

# Discovering Exposed Cloud Storage: S3 Scanner

## 1. Introduction to Exposed Cloud Storage

Amazon Simple Storage Service (S3) is one of the most widely used cloud storage solutions in the world. Developers use S3 to store backups, application assets, user uploads, logs, and sometimes even sensitive configuration files or source code. 

However, misconfigured S3 buckets remain one of the leading causes of massive data breaches. When an administrator inadvertently grants public read or write access to an S3 bucket, anyone on the internet can access or modify the data within it. Discovering these exposed buckets is a critical phase in cloud penetration testing.

### The Scope of the Problem
- **Data Leaks**: PII, credentials, API keys, and proprietary source code exposed.
- **Malware Distribution**: Publicly writable buckets can be used to host malware or replace legitimate application assets (e.g., JavaScript files) with malicious versions.
- **Ransomware**: Attackers can delete or encrypt data in publicly writable buckets.

## 2. Architecture and Attack Flow

```text
+---------------------+        +-------------------------+        +---------------------------+
|   Attacker / VAPT   |        |   S3 Enumeration Tools  |        |   AWS S3 Infrastructure   |
|   Professional      |        |   (S3Scanner, etc.)     |        |   (Target Organization)   |
+---------------------+        +-------------------------+        +---------------------------+
           |                               |                                |
           | 1. Generate bucket name list  |                                |
           |    (permutations, OSINT)      |                                |
           |------------------------------>|                                |
           |                               |                                |
           | 2. Send HTTP HEAD/GET reqs    |                                |
           |    to <name>.s3.amazonaws.com |                                |
           |--------------------------------------------------------------->|
           |                               |                                |
           | 3. Parse HTTP Status Codes    |                                |
           |    (200 OK, 403 Forbidden,    |                                |
           |     404 Not Found)            |                                |
           |<---------------------------------------------------------------|
           |                               |                                |
           | 4. Identify open buckets      |                                |
           |<------------------------------|                                |
           |                               |                                |
           | 5. List bucket contents &     |                                |
           |    download sensitive data    |                                |
           |--------------------------------------------------------------->|
           |                               |                                |
           | 6. Test for Write Access      |                                |
           |    (Upload test file)         |                                |
           |--------------------------------------------------------------->|
```

## 3. The "How": Detailed Methodology

### Bucket Naming Conventions
AWS S3 bucket names must be globally unique across all of AWS. Therefore, companies often use predictable naming patterns.
Common patterns include:
- `companyname-prod`
- `companyname-dev`
- `companyname-backups`
- `companyname-assets`
- `companyname-logs`

### Enumeration Techniques
1. **Passive OSINT**: Finding bucket names in GitHub repositories, JavaScript source code, or CNAME records.
2. **Brute-forcing / Permutations**: Using tools to generate thousands of potential bucket names and checking if they exist.

### HTTP Status Codes for S3
When interacting with S3 via HTTP, the status codes reveal the bucket's existence and permissions:
- `200 OK`: Bucket exists and allows public access (Read/List).
- `403 Forbidden`: Bucket exists but is private (Access Denied).
- `404 Not Found`: Bucket does not exist (or the name is available).
- `301 Moved Permanently`: Bucket exists but is in a different region.

## 4. Deep Dive: The XML Response of an Open Bucket

When you visit a publicly listable S3 bucket in a browser or via `curl`, AWS returns an XML document outlining the contents of the bucket.

Example Request:
```bash
$ curl http://example-company-assets.s3.amazonaws.com/
```

Example Response:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
  <Name>example-company-assets</Name>
  <Prefix></Prefix>
  <Marker></Marker>
  <MaxKeys>1000</MaxKeys>
  <IsTruncated>false</IsTruncated>
  <Contents>
    <Key>database-backup-2023.sql</Key>
    <LastModified>2023-10-01T12:00:00.000Z</LastModified>
    <ETag>&quot;d41d8cd98f00b204e9800998ecf8427e&quot;</ETag>
    <Size>10485760</Size>
    <StorageClass>STANDARD</StorageClass>
  </Contents>
  <Contents>
    <Key>config/settings.json</Key>
    <LastModified>2023-10-02T14:30:00.000Z</LastModified>
    <ETag>&quot;a1b2c3d4e5f6g7h8i9j0&quot;</ETag>
    <Size>2048</Size>
    <StorageClass>STANDARD</StorageClass>
  </Contents>
</ListBucketResult>
```

From this XML, an attacker can extract the `Key` values and append them to the bucket URL to download the files:
`http://example-company-assets.s3.amazonaws.com/database-backup-2023.sql`

## 5. Tools of the Trade

### `S3Scanner`
S3Scanner is a popular tool that finds open S3 buckets and dumps their contents.
```bash
# Scan a list of bucket names
$ s3scanner scan -f buckets.txt

# Dump contents of an open bucket
$ s3scanner dump --bucket example-company-assets
```

### `cloud_enum`
Generates permutations of a keyword and checks for S3 buckets, Azure Blobs, and GCP storage.
```bash
$ python3 cloud_enum.py -k companyname
```

### `awscli`
The official AWS CLI is incredibly useful for testing permissions.
```bash
# List contents (Requires unauthenticated access)
$ aws s3 ls s3://example-company-assets --no-sign-request

# Test for Write Access (Upload a file)
$ echo "VAPT Test" > test.txt
$ aws s3 cp test.txt s3://example-company-assets/test.txt --no-sign-request

# Download an entire bucket
$ aws s3 sync s3://example-company-assets ./local-dir --no-sign-request
```

## 6. Anatomy of a Vulnerable Bucket Policy

Why do buckets become public? Usually because of a misconfigured S3 Bucket Policy.
Below is an example of a policy that grants full public Read access to anyone on the internet:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::example-company-assets/*"
    },
    {
      "Sid": "PublicListBucket",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::example-company-assets"
    }
  ]
}
```
The `Principal: "*"` combined with `Action: "s3:GetObject"` and `"s3:ListBucket"` is the root cause.

## 7. Mitigation and Defense

### Block Public Access (BPA)
AWS provides a feature called "Block Public Access" at both the bucket and account levels. When enabled, it overrides any bucket policies or ACLs that attempt to grant public access.

### IAM and Least Privilege
Ensure that only specific IAM roles have access to the bucket. Avoid using wildcards (`*`) in the `Principal` field.

### Continuous Auditing
Use tools like AWS Macie, AWS Config, and CloudTrail to monitor for public buckets and sensitive data exposure.

## 8. Chaining Opportunities
- **[[01 - OSINT for Cloud Assets Domain to Cloud IP]]**: Discovering the bucket names via CNAME records.
- **[[03 - Using AWS CLI for Reconnaissance]]**: Using AWS CLI to extract data from the buckets.
- **Web Application Attacks**: Replacing hosted JavaScript files in a public bucket to execute XSS or drive-by downloads on users of the web application.

## 9. Related Notes
- [[01 - OSINT for Cloud Assets Domain to Cloud IP]]
- [[03 - Using AWS CLI for Reconnaissance]]
- [[04 - Using Azure CLI and AzureHound for Recon]]
- [[05 - Using GCP CLI gcloud for Reconnaissance]]
