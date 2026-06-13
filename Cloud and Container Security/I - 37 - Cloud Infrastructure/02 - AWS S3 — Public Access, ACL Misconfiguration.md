---
tags: [aws, s3, storage, data-leakage, misconfiguration]
difficulty: intermediate
module: "37 - Cloud Infrastructure"
topic: "37.02 AWS S3"
---

# AWS S3 — Public Access and ACL Misconfigurations

## 1. Introduction to Amazon S3
Amazon Simple Storage Service (S3) is an object storage service offering industry-leading scalability, data availability, security, and performance. While S3 is secure by default (since April 2023, all new S3 buckets have Block Public Access enabled by default), legacy buckets or deliberate, poorly managed configuration changes frequently lead to massive data breaches.

In cloud penetration testing, S3 is one of the most lucrative targets due to its common use for storing sensitive backups, PII, source code, and configuration files.

## 2. S3 Access Control Mechanisms
Understanding how access is granted to an S3 object is critical for identifying vulnerabilities. S3 uses a combination of several policies to determine authorization:
1. **Identity-Based Policies (IAM Policies)**: Attached to IAM users, groups, or roles.
2. **Resource-Based Policies (Bucket Policies)**: Attached directly to the S3 bucket. They define who can access the bucket and its objects globally.
3. **Access Control Lists (ACLs)**: A legacy access control mechanism. Bucket ACLs and Object ACLs can grant read/write permissions to other AWS accounts or predefined groups (like `AllUsers` or `AuthenticatedUsers`).
4. **S3 Block Public Access**: An overarching setting (at the bucket or account level) that overrides all other policies to forcefully block public access.

## 3. ASCII Architecture Diagram: S3 Data Exfiltration Flow

```text
    [ Internet / Unauthenticated User ]
             |
             |  1. Discovers S3 bucket name
             |     (e.g., via DNS brute-force, GitHub scanning)
             v
    [ Target S3 Bucket: "company-backups-prod" ]
             |
             |  2. Attempts unauthenticated GET / LIST
             +-----------------------------------------+
             |                                         |
      [ Check ACLs ]                            [ Check Bucket Policy ]
      - AllUsers: READ?                         - Principal: *
      - AuthenticatedUsers: READ?               - Action: s3:GetObject
             |                                         |
             +--------------------+--------------------+
                                  |
                                  |  3. Misconfiguration found
                                  v
                       [ Access Granted ]
                                  |
                                  |  4. Attacker lists contents
                                  |     aws s3 ls s3://company-backups-prod/
                                  v
                      [ Objects Enumerated ]
                      - database-dump.sql
                      - config.json (contains AWS keys)
                      - user-data.csv
                                  |
                                  |  5. Exfiltration
                                  v
                      [ Data Downloaded ]
```

## 4. Common Misconfigurations & Exploitation

### 4.1. Public Read/List Access
The most common issue is a bucket policy or ACL that grants the `s3:ListBucket` or `s3:GetObject` permission to `*` (everyone).
- **Exploitation via CLI**:
  An attacker can list the contents anonymously:
  ```bash
  aws s3 ls s3://vulnerable-bucket-name --no-sign-request
  ```
  And download the contents:
  ```bash
  aws s3 cp s3://vulnerable-bucket-name/database.sql . --no-sign-request
  ```
- **Bucket Policy Example (Vulnerable)**:
  ```json
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Principal": "*",
              "Action": ["s3:GetObject", "s3:ListBucket"],
              "Resource": [
                  "arn:aws:s3:::vulnerable-bucket-name",
                  "arn:aws:s3:::vulnerable-bucket-name/*"
              ]
          }
      ]
  }
  ```

### 4.2. Authenticated Users ACL (`Any AWS User`)
A highly misunderstood S3 ACL group is the `AuthenticatedUsers` group. Many administrators believe this refers to authenticated users *within their own AWS account*. In reality, it means **any authenticated AWS user in the world**.
- **Exploitation**: An attacker simply uses their own valid AWS credentials (from an entirely unrelated free-tier account) to access the bucket.
  ```bash
  aws s3 ls s3://vulnerable-bucket-name --profile my-attacker-account
  ```

### 4.3. Bucket Writable (Public Write)
If a bucket allows public `s3:PutObject`, an attacker can upload arbitrary files.
- **Impacts**:
  1. **Malware Distribution / Defacement**: If the bucket hosts a static website, the attacker can overwrite `index.html` or upload malware.
  2. **Ransomware / Data Destruction**: Attackers can overwrite existing files with encrypted versions or delete them.
  3. **Cost Exhaustion (Denial of Wallet)**: Uploading massive amounts of data to rack up storage charges for the victim.
- **Exploitation**:
  ```bash
  aws s3 cp malicous.html s3://vulnerable-bucket-name/index.html --no-sign-request
  ```

### 4.4. s3:PutBucketPolicy Exploitation
If an attacker finds an IAM credential or misconfiguration that grants `s3:PutBucketPolicy`, they can rewrite the bucket policy to grant themselves full control, potentially locking out the actual administrators (if they don't have root access).
- **Exploitation**:
  ```bash
  aws s3api put-bucket-policy --bucket target-bucket --policy file://malicious-policy.json
  ```

## 5. Reconnaissance and Enumeration
How do attackers find vulnerable buckets in the first place?
1. **Subdomain Enumeration & DNS Parsing**: Tools like `sublist3r` or `amass`. CNAMEs often point directly to S3 buckets.
2. **Certificate Transparency Logs**: Extracting domain names and testing for associated buckets.
3. **Open-Source Tools**:
   - `Cloud_enum`: Hunts for public resources in AWS, Azure, and GCP.
   - `S3Scanner`: Scans a list of bucket names to find open buckets and dump their contents.
   - `Bucket_finder`: A classic tool for discovering S3 buckets.
4. **Brute Forcing Permutations**: Attackers use company names combined with common suffixes (e.g., `company-prod`, `company-backups`, `company-assets`) to guess bucket names.
5. **GitHub Recon**: Developers frequently hardcode S3 URLs in open-source repositories.

## 6. Advanced Attacks: S3 Ransomware
In cases where an attacker obtains IAM credentials with `s3:PutObject` and `s3:DeleteObject`, but perhaps lacks other escalation vectors, they might execute an S3 ransomware attack.
- The attacker downloads all objects.
- The attacker encrypts the objects locally and uploads them.
- The attacker deletes the original objects.
- *Note on Versioning*: If S3 Versioning is enabled, the victim can simply restore the previous versions. However, if the attacker also has `s3:DeleteObjectVersion` and `s3:PutBucketVersioning`, they can disable versioning and permanently destroy the backups.

## 7. Remediation and Best Practices
1. **Enable S3 Block Public Access (BPA)**: This should be enabled at the Account level. It overrides any overly permissive ACLs or bucket policies, serving as a failsafe against accidental exposure.
2. **Disable ACLs**: AWS now recommends using S3 Object Ownership to disable ACLs entirely and rely solely on IAM and Bucket Policies for access control.
3. **Implement Least Privilege**: Ensure bucket policies and IAM roles only allow access to specific IP addresses (using `aws:SourceIp`), VPCs (using `aws:sourceVpce`), or specific IAM roles.
4. **Enable CloudTrail Data Events**: By default, CloudTrail only logs management events. To detect data exfiltration, you must enable Data Event logging for S3 (though this incurs additional costs).
5. **Use Macie**: Amazon Macie uses machine learning to automatically discover, classify, and protect sensitive data in S3.

## 8. Conclusion
S3 bucket misconfigurations are low-hanging fruit in cloud security assessments, yet they yield some of the highest impact findings. The complexity of overlapping access control mechanisms (IAM vs. Policies vs. ACLs) frequently leads to human error. Thorough enumeration and understanding of evaluation logic are essential for identifying these risks.

---

## Chaining Opportunities
- **[[01 - AWS IAM — Roles, Policies, Misconfigurations]]**: Exposed AWS Access Keys found within publicly readable S3 buckets are the most common entry point for IAM privilege escalation.
- **[[06 - AWS SecretsManager Parameter Store — Misconfigured Access]]**: Configuration files `.env` stored in S3 might point to SecretsManager ARNs and provide the required execution roles.
- **[[03 - AWS EC2 — Metadata Service (IMDS) Exploitation]]**: An EC2 SSRF might lead to retrieving a role that has S3 read access, turning an SSRF into an S3 data breach.

## Related Notes
- [[04 - AWS Lambda — Privilege Escalation, Event Injection]]
- [[07 - AWS CloudTrail — Disabling Logging]]
