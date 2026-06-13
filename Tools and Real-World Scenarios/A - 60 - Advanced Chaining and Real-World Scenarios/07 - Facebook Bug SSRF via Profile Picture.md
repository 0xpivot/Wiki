---
tags: [bug-bounty, chaining, real-world, vapt]
difficulty: advanced
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.07 Facebook Bug SSRF"
---

# 60.07 Facebook Bug: SSRF via Profile Picture Fetcher

## 1. Introduction

Server-Side Request Forgery (SSRF) is a critical vulnerability that allows an attacker to coerce a server-side application into making HTTP requests to an arbitrary domain of the attacker's choosing. While SSRF can be used to port scan internal networks or pivot into an organization's intranet, its most devastating modern application is querying cloud metadata endpoints to extract high-privileged IAM credentials.

One of the most classic and thoroughly studied real-world examples of SSRF occurred in a social media giant's architecture (similar to a famous bug disclosed to Facebook/Meta). The vulnerability resided in the seemingly innocuous feature of updating a user's profile picture by providing a remote URL instead of directly uploading an image file.

This document dissects the technical mechanics of how image-fetching utilities become vulnerable to SSRF, the complex bypasses required to defeat enterprise-grade WAFs, and the theoretical exploitation flow that leads to a critical cloud infrastructure compromise.

## 2. Architecture and Data Flow

In a microservices architecture, the main web application rarely handles resource-intensive tasks like image processing. Instead, it delegates these tasks to a dedicated microservice.

### The Attack Flow Diagram

```text
+-------------------+                                  +-----------------------+
|                   |                                  |                       |
|   Attacker (Bob)  | ====(1) Update Profile Pic====>  |  Main Web WAF / API   |
|                   |     URL: http://169.254...       |  Gateway (Frontend)   |
+--------+----------+                                  +-----------+-----------+
         |                                                         |
         ^                                                         | (2) Passes URL Validation
         |                                                         |     Forwards to Backend
         |                                                         v
         |                                             +-----------------------+
         |                                             |                       |
         |                                             |  Image Fetcher Micro- |
         |                                             |  service (Backend)    |
         |                                             +-----------+-----------+
         |                                                         |
         | (4) Returns Profile Image containing                    | (3) HTTP GET to target
         |     AWS Metadata/Keys instead of a PNG                  v
         |                                             +-----------------------+
         |                                             |                       |
         +=============================================|  AWS IMDSv1           |
                                                       |  (169.254.169.254)    |
                                                       +-----------------------+
```

## 3. Vulnerability Mechanics

The core vulnerability stems from a disconnect between the frontend validation logic and the backend execution logic.

1.  **Frontend Validation:** The main API gateway receives the request `POST /api/profile/picture { "url": "http://example.com/image.jpg" }`. It might apply a naive regular expression to ensure the string begins with `http://` or `https://` and ends with a valid image extension.
2.  **Backend Execution:** The Image Fetcher Microservice receives the URL. Utilizing a library like `libcurl` or Python's `requests`, it initiates an HTTP GET request to the provided URL. It assumes that if the frontend passed it, the URL is safe.

If an attacker provides an internal IP address (e.g., `127.0.0.1` targeting a local Redis instance, or `169.254.169.254` targeting the AWS metadata service), the backend service blindly executes the request.

### Vulnerable Code Snippet (Python/Celery Backend)

```python
import requests
from celery import Celery

app = Celery('image_tasks', broker='redis://localhost:6379/0')

@app.task
def fetch_and_process_image(user_id, target_url):
    try:
        # FLAW: No validation on target_url's destination IP
        # The service blindly fetches whatever URL is provided.
        response = requests.get(target_url, timeout=5)
        
        if response.status_code == 200:
            # Save the raw response content as the user's profile picture
            save_to_s3(user_id, response.content)
            return True
            
    except requests.exceptions.RequestException:
        return False
```

## 4. The Exploit Step-by-Step

Exploiting an SSRF in a mature application like Facebook requires bypassing multiple layers of defense. The attacker's goal is to force the server to fetch `http://169.254.169.254/latest/meta-data/iam/security-credentials/`.

### Step 1: Initial Discovery
The attacker notices the profile picture update feature accepts a `url` parameter. They test it by providing a URL to a webhook they control (e.g., `https://webhook.site/xyz`). They receive a GET request from an AWS IP address, confirming the backend service is fetching external URLs.

### Step 2: Hitting the Blacklist
The attacker attempts to supply `http://127.0.0.1` or `http://169.254.169.254`. The application immediately rejects the request with a `400 Bad Request` or `Validation Error`. The application clearly has a blacklist in place preventing direct access to private IP spaces.

### Step 3: Bypassing the Blacklist (Obfuscation)
The attacker attempts standard IP obfuscation techniques:
- Decimal representation: `http://2852039166` (resolves to 169.254.169.254)
- Hexadecimal representation: `http://0xa9fea9fe`
- IPv6 mapping: `http://[::ffff:169.254.169.254]`

If the regex is poorly written, one of these might bypass the WAF.

### Step 4: Bypassing the Blacklist (DNS Rebinding)
If obfuscation fails, the attacker employs DNS Rebinding.
1. The attacker configures a custom DNS server for `attacker.com`.
2. They set the TTL (Time-To-Live) for `rebind.attacker.com` to `0` seconds.
3. The attacker submits `http://rebind.attacker.com/latest/meta-data/`.
4. **Validation Phase:** The WAF asks the DNS server for the IP of `rebind.attacker.com`. The attacker's DNS server replies with a benign IP: `8.8.8.8`. The WAF sees a public IP, approves the request, and sends it to the backend.
5. **Execution Phase:** The backend microservice attempts to fetch the URL. Because the TTL was 0, it must perform a new DNS lookup. This time, the attacker's DNS server replies with `169.254.169.254`.
6. The backend successfully connects to the metadata service.

### Step 5: Data Exfiltration
The backend saves the response from the metadata service (which is JSON text containing AWS keys) as a `.jpg` file in the attacker's profile. The attacker simply navigates to their profile, downloads the "image," opens it in a text editor, and extracts the `AccessKeyId`, `SecretAccessKey`, and `Token`.

## 5. Advanced Bypasses: The Open Redirect Trick

Another common bypass mechanism relies on trusting an external domain that contains an Open Redirect.
Suppose the application validates that the URL *must* belong to a trusted partner domain, e.g., `https://trusted-partner.com`.
If the attacker finds an open redirect on the partner's site (`https://trusted-partner.com/login?redirect=http://169.254.169.254`), they can submit this URL.

The frontend validates the domain matches `trusted-partner.com` and allows it. The backend makes the request, receives an HTTP 302 redirect, and its HTTP client (like `requests`) blindly follows the redirect directly to the internal metadata service.

## 6. Real-World Consequences

An SSRF bug in an image fetcher is not just a high-severity finding; in AWS environments running IMDSv1, it is an immediate, critical-severity path to complete cloud compromise. With the stolen IAM credentials, the attacker can:
- List and download all S3 buckets (Massive Data Breach).
- Terminate EC2 instances (Denial of Service).
- Spin up unauthorized infrastructure for cryptomining (Resource Hijacking).
- Modify Route53 DNS records to hijack customer traffic.

## 7. Secure Coding and Remediation

Fixing SSRF robustly requires a defense-in-depth approach.

### Secure Code Snippet (Python/Requests with SSRF Protection)
```python
import requests
import socket
import ipaddress
from urllib.parse import urlparse

def is_safe_url(url):
    try:
        parsed_url = urlparse(url)
        # 1. Enforce HTTP/HTTPS only
        if parsed_url.scheme not in ['http', 'https']: return False
        
        # 2. Resolve the IP address
        ip_addr = socket.gethostbyname(parsed_url.hostname)
        ip_obj = ipaddress.ip_address(ip_addr)
        
        # 3. Check if the IP is private or loopback
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
            return False
            
        return True
    except (socket.gaierror, ValueError):
        return False

def fetch_image_securely(target_url):
    if not is_safe_url(target_url):
        raise ValueError("Unsafe URL detected")
        
    # 4. Disable redirects to prevent WAF bypasses via Open Redirects
    response = requests.get(target_url, timeout=5, allow_redirects=False)
    return response.content
```

### Infrastructure Remediation
1.  **Network Segmentation:** Place the Image Fetcher microservice in an isolated subnet (VPC) with strict egress firewall rules (Security Groups) that explicitly deny routing to internal IP ranges (10.0.0.0/8) and the metadata IP (169.254.169.254).
2.  **IMDSv2 Migration:** In AWS, mandate the use of Instance Metadata Service Version 2 (IMDSv2). IMDSv2 requires a specific `PUT` request to generate a token, which must then be included in a custom header (`X-aws-ec2-metadata-token`) for subsequent `GET` requests. It is practically impossible to force an application to generate this complex sequence of requests via a standard URL-based SSRF.

## 8. Chaining Opportunities

- **SSRF to RCE via Redis:** If the application runs a local Redis instance without authentication (common on `127.0.0.1:6379`), the attacker can use the SSRF to send Redis commands. Using the `dict://` or `gopher://` protocol (if supported by the backend fetcher), the attacker can overwrite authorized SSH keys or crontabs, achieving Remote Code Execution.
- **SSRF + Open Redirect:** Utilizing a low-severity open redirect on the application's main domain to bypass SSRF whitelist filters, escalating the open redirect to critical severity.

## 9. Related Notes

- [[03 - Server-Side Request Forgery (SSRF) Mastery]]
- [[12 - Advanced DNS Rebinding Techniques]]
- [[15 - Securing AWS IAM and Metadata Services]]
- [[06 - HackerOne Disclosed Reports Top 10]]
