---
tags: [interview, api-security, qna, scenario]
difficulty: expert
module: "Interview Prep - API Security"
topic: "QnA - API Module 37"
---

# Threat Hunting & Offensive Engineering: Server Side Request Forgery (SSRF)

## Custom ASCII Diagram

```text
 [ Attacker ]                                   [ Target Infrastructure ]
      |                                                   |
      | 1. Malicious Payload (url=http://169.254.169.254) |
      |-------------------------------------------------->|
      |                                            [ Web Server ]
      |                                              /       \
      |                                             /         \
      |               2. Server parses payload     /           \
      |                  and fetches requested    /             \
      |                  internal resource       /               \
      |                                         v                 v
      |                               [ AWS Metadata ]      [ Internal Admin ]
      |                               [ 169.254...   ]      [ 10.0.0.5:8080  ]
      |                                         |                 |
      |               3. Internal Resource      |                 |
      |                  returns sensitive      |                 |
      |                  data to Web Server     |                 |
      |                                         +--------+--------+
      |                                                  |
      | 4. Web Server returns internal                   |
      |    data in HTTP Response to Attacker             |
      |<-------------------------------------------------+
      |
[ Exfiltrated IAM Credentials ]
```

## Formal Technical Questions

### Q1: Differentiate between In-band SSRF, Blind SSRF, and Semi-Blind SSRF. How does your exploitation methodology change for each?
**Answer:**
- **In-band (Basic) SSRF**: The application takes the attacker-supplied URL, makes the request, and reflects the full response back to the attacker in the HTTP response. Exploitation is straightforward: I point the payload at an internal service (e.g., `http://localhost:6379`) or cloud metadata endpoints and immediately read the output.
- **Semi-Blind SSRF**: The application does not return the full response body, but the response behavior (status codes, response times, or error messages) changes based on the internal request's success. My methodology shifts to enumeration. I can map internal networks by observing HTTP 200 vs 500 errors or time delays, allowing me to discover open ports and internal subnets.
- **Blind SSRF**: The application makes the backend request, but returns absolutely no feedback to the attacker. The HTTP response is identical regardless of the backend result. Exploitation requires Out-of-Band (OOB) techniques. I force the server to make a request to an external server I control (e.g., using Burp Collaborator or a custom DNS server) to confirm the vulnerability. From there, I attempt to chain it with vulnerabilities like remote code execution via internal tools (e.g., attacking an internal Redis or Memcached instance via protocol smuggling).

### Q2: Explain DNS Rebinding in the context of bypassing SSRF protections.
**Answer:**
DNS Rebinding is an advanced technique used to bypass SSRF filters that validate the host IP address before making the request. 

**The Mechanism:**
1. The server receives a URL from the attacker: `http://attacker.com/data`.
2. The server's validation logic performs a DNS lookup for `attacker.com`.
3. The attacker's custom DNS server responds with a benign, external IP (e.g., `8.8.8.8`) and a very short Time-to-Live (TTL) of 0 seconds.
4. The server validates `8.8.8.8`, ensuring it is not a private IP (like `127.0.0.1` or `169.254.169.254`), and passes the validation check.
5. The server's application logic then attempts to fetch the URL. Because the TTL expired, the system's resolver issues a second DNS query.
6. This time, the attacker's DNS server responds with the malicious internal IP (e.g., `127.0.0.1`).
7. The server makes the HTTP request to the internal IP, successfully bypassing the initial filter.

### Q3: How can a Threat Hunter identify SSRF attempts targeting Cloud environments?
**Answer:**
Threat hunting for SSRF in AWS/GCP/Azure environments focuses heavily on monitoring traffic to the Instance Metadata Service (IMDS).
1. **Network Flow Logs**: Query VPC Flow Logs for any traffic originating from the application servers destined for `169.254.169.254` (AWS/Azure) or `metadata.google.internal`. While some legitimate processes access metadata, sudden spikes or requests originating from the web application process (rather than orchestration agents) are highly suspicious.
2. **WAF & Reverse Proxy Logs**: Search for URLs or parameters containing metadata IP equivalents, including obfuscated variations:
   - Dotted decimal: `169.254.169.254`
   - Integer: `2852039166`
   - Hex: `0xA9FEA9FE`
   - Octal: `0251.0376.0251.0376`
3. **IAM Credential Usage Anomaly**: Once an attacker extracts the temporary STS token via SSRF, they will use it externally. Hunters should monitor CloudTrail for `ConsoleLogin` or API calls using IAM roles associated with EC2 instances, specifically looking for source IPs that originate outside the corporate VPC.

## Scenario-Based Questions

### Q1: You are on a Red Team engagement. You discover a web application feature that generates PDF reports from user-supplied HTML. How do you approach testing this for SSRF, and what is your ultimate objective?
**Answer:**
PDF generators (like wkhtmltopdf, Puppeteer, or headless Chrome) are notorious for SSRF vulnerabilities because they parse HTML and actively fetch external resources like images, iframes, and stylesheets.

**Testing Methodology:**
1. **Initial Injection**: I would inject basic HTML tags designed to force external network requests to my controlled server:
   - `<img src="http://attacker.com/ping">`
   - `<iframe src="http://attacker.com/iframe">`
   - `<link rel=attachment href="http://attacker.com/link">`
2. **Protocol Analysis**: By observing my server logs, I can identify the User-Agent of the PDF engine to tailor my payloads.
3. **Internal Pivoting**: If the external request succeeds, I change the payload to target local infrastructure:
   - `<iframe src="http://127.0.0.1:8080/admin">`
   - `<iframe src="file:///etc/passwd">` (Testing for Local File Inclusion via SSRF)

**Ultimate Objective:**
My primary goal is to achieve Remote Code Execution or critical data exfiltration. If the service is running in AWS, I will inject `<iframe src="http://169.254.169.254/latest/meta-data/iam/security-credentials/">` to exfiltrate the IAM role keys via the generated PDF. Alternatively, I will attempt to hit internal unauthenticated services, such as Docker APIs or internal Jenkins instances, to trigger remote builds and execute code.

### Q2: As an Incident Responder, you receive an alert that an attacker successfully extracted AWS credentials via SSRF. The attacker's IP is external. What are your immediate containment and eradication steps?
**Answer:**
The situation is critical because the attacker holds valid IAM STS tokens and can operate outside our network perimeter.

**Containment:**
1. **Revoke Compromised Credentials**: Immediately identify the IAM role attached to the compromised EC2 instance. I will attach an inline deny-all policy (`"Effect": "Deny", "Action": "*"`) to the specific IAM role session to kill the attacker's access instantly.
2. **Rotate Role Tokens**: I will force a rotation of the credentials on the instance, ensuring the application continues to function with new keys while the stolen ones remain dead.
3. **Block Attacker IP**: Null-route the attacker's external IP at the edge firewall and WAF to stop further SSRF attempts.

**Eradication & Recovery:**
1. **Audit CloudTrail**: I will immediately query AWS CloudTrail for all actions performed by the compromised STS token (`userarn` matching the assumed role). I need to determine if the attacker created backdoor IAM users, modified security groups, or accessed S3 buckets containing PII.
2. **Patch the Vulnerability**: Coordinate with the development team to implement strict input validation and deploy a network-level control (like migrating to IMDSv2, which requires session tokens and blocks simple GET-based SSRF).

## Deep-Dive Defensive Questions

### Q1: Describe the architectural differences between IMDSv1 and IMDSv2 in AWS, and explain exactly why IMDSv2 stops classic SSRF attacks.
**Answer:**
IMDSv1 operates on a simple Request/Response model using HTTP GET requests. If an attacker finds an SSRF vulnerability, they can simply command the server to issue a GET request to `http://169.254.169.254/latest/meta-data/...` and receive the credentials.

IMDSv2 introduces a session-oriented approach requiring HTTP `PUT` requests and specific headers.
To get credentials in IMDSv2, a client must:
1. Issue a `PUT` request to `/latest/api/token` with the header `X-aws-ec2-metadata-token-ttl-seconds`.
2. Retrieve the token from the response.
3. Issue a subsequent `GET` request to the metadata endpoint, including the newly acquired token in the `X-aws-ec2-metadata-token` header.

**Why it stops SSRF:**
Most SSRF vulnerabilities (especially those in PDF generators, image processors, or basic URL fetchers) only allow the attacker to control the URL and the HTTP method (usually `GET`). Attackers rarely have the ability to inject custom HTTP headers or issue complex `PUT` requests followed by reading and reusing a token in a secondary request. Therefore, enforcing IMDSv2 at the hypervisor level neutralizes 99% of SSRF-to-Cloud-Metadata exploit chains.

### Q2: How can egress filtering and zero-trust networking mitigate the impact of Blind SSRF?
**Answer:**
Blind SSRF is dangerous because it allows attackers to probe the internal network without direct feedback. Egress filtering and zero-trust architectures neutralize this post-exploitation phase.

1. **Egress Filtering**: By default, web application servers should operate in a "default-deny" outbound network posture. If an application only needs to communicate with a specific external payment gateway, firewall rules (e.g., iptables, AWS Security Groups) should block all outbound connections except to that gateway's IP range. If an attacker triggers a Blind SSRF, the server physically cannot reach out to the attacker's OOB server or arbitrary internal IP addresses.
2. **Zero-Trust**: Inside the network, mutual TLS (mTLS) and strict identity-based access controls should be enforced. Even if an attacker uses SSRF to command the web server to reach out to an internal Jenkins box, the Jenkins box will reject the request unless the web server presents a valid cryptographic identity demonstrating it is *authorized* to communicate with Jenkins.

## Real-World Attack Scenario

**The Capital One Paradigm: SSRF to Data Breach**

In one of the most infamous breaches, an attacker leveraged an SSRF vulnerability in a misconfigured Web Application Firewall (ModSecurity).

**The Attack Execution:**
1. **Reconnaissance**: The attacker identified a server hosting the WAF that allowed arbitrary HTTP requests via a specific parameter.
2. **SSRF Exploitation**: The attacker sent a payload instructing the WAF to query the AWS IMDS (`169.254.169.254`). Because the WAF was running on an EC2 instance with excessive IAM permissions, it successfully fetched the STS tokens for the `WAF-Role`.
3. **Exfiltration of Keys**: The in-band SSRF returned the temporary access key, secret key, and session token directly to the attacker's terminal.
4. **Cloud Exploitation**: The attacker configured their local AWS CLI with the stolen keys. Because the `WAF-Role` had over-permissive read access to S3, the attacker ran `aws s3 sync` to download terabytes of customer credit card application data from internal buckets.

**Lessons Learned:** 
The breach highlighted three critical failures: An application layer vulnerability (SSRF), a lack of defense-in-depth (IMDSv1 was enabled), and a violation of least privilege (the web server role had massive S3 read permissions).

## Chaining Opportunities

- **SSRF + CRLF Injection**: Using Carriage Return Line Feed injection to smuggle custom HTTP headers into the backend request, bypassing protections or escalating to protocol smuggling.
- **SSRF + Redis/Memcached**: Hitting internal key-value stores to overwrite serialized session objects, leading to Remote Code Execution via deserialization.
- **SSRF + Reflected XSS**: Forcing the server to fetch a malicious payload from an attacker-controlled domain and reflecting it into the victim's browser context.
- **SSRF + DNS Rebinding**: Bypassing strict IP allowlists to access internal loopback addresses.

## Related Notes
- [[14 - Advanced Cloud Threat Hunting]]
- [[21 - Abusing PDF Renderers]]
- [[33 - IAM Privilege Escalation Paths]]
- [[50 - Bypassing Network Segmentation]]
