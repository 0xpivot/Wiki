---
tags: [vapt, subdomain-takeover, reconnaissance, dns, beginner]
difficulty: beginner
module: "34 - Subdomain Takeover"
topic: "34.01 What is Subdomain Takeover?"
---

# 34.01 What is Subdomain Takeover?

## 1. Introduction and Core Concepts

Subdomain takeover is a high-impact, logically complex vulnerability that occurs when a DNS record (most commonly a CNAME) points to a third-party service or resource that has been deleted, abandoned, or was never claimed by the original domain owner. Because the DNS record still exists and actively routes traffic to the external provider, an attacker can sign up for that external provider, claim the dangling resource name, and effectively take full control over the content served at the target's subdomain.

To truly understand why this happens, we must dig deeply into the intersection of **Domain Name System (DNS) architecture** and **cloud-based virtual hosting**. Subdomain takeover is not a vulnerability in the application code itself; rather, it is a structural flaw in IT asset management, specifically the failure to synchronize DNS record lifecycles with the lifecycle of the underlying infrastructure they point to.

When organizations move quickly, spinning up landing pages, documentation portals, or marketing campaigns on services like AWS S3, GitHub Pages, or Heroku, they create DNS records linking their brand (`promo.company.com`) to the provider (`company-promo.s3.amazonaws.com`). When the campaign ends, developers often delete the S3 bucket to save costs but forget to notify network administrators to remove the CNAME record. This creates the "dangling" state.

## 2. The Mechanics of the Attack

The mechanics rely entirely on how web browsers, DNS resolvers, and cloud edge routers handle requests. Let's break down the exact flow of a request to a dangling subdomain.

1. **The User Request**: A user (or an automated script, or a victim receiving a phishing link) attempts to visit `https://promo.company.com`.
2. **DNS Resolution**: The user's browser queries their local DNS resolver. The resolver checks the authoritative name servers for `company.com` and asks for the records associated with `promo`.
3. **The Dangling CNAME**: The authoritative server replies with a CNAME record: `promo.company.com IN CNAME company-promo.s3.amazonaws.com`.
4. **Secondary Resolution**: The resolver now queries AWS's authoritative servers to find the IP address for `company-promo.s3.amazonaws.com`. It receives an IP belonging to the AWS S3 regional load balancer.
5. **The HTTP Request**: The user's browser establishes a TCP connection and a TLS handshake (if applicable) with the AWS IP, and sends an HTTP request containing the header `Host: promo.company.com`.
6. **Cloud Routing**: The AWS load balancer inspects the `Host` header. It looks up its internal routing tables for a bucket named `company-promo` or bound to the domain `promo.company.com`.
7. **The Error**: Because the company deleted the bucket, AWS finds no matching routing rules. It returns a `404 Not Found` with the specific message `NoSuchBucket`.

**The Attack Phase:**
An attacker constantly scans the internet for these specific `NoSuchBucket` errors (or equivalent errors across hundreds of PaaS/SaaS providers). Upon finding one, the attacker logs into their own AWS account, creates an S3 bucket named `company-promo`, and configures it to serve arbitrary content. 

Now, when step 6 occurs, AWS *does* find a routing rule—the attacker's rule. The attacker is now serving content on `promo.company.com`.

## 3. ASCII Architecture Diagram: The DNS and Routing Flow

```text
========================================================================================
                          SUBDOMAIN TAKEOVER ARCHITECTURE
========================================================================================

   [ VICTIM / USER ]
          |
          | 1. Requests http://promo.company.com
          v
   +-------------------+       2. DNS Lookup         +-------------------------+
   |   Local DNS /     | --------------------------> | Target's Authoritative  |
   |   ISP Resolver    | <-------------------------- | DNS Server (Route53,etc)|
   +-------------------+       3. Returns CNAME      +-------------------------+
          |                       (company-promo.s3.amazonaws.com)
          |
          | 4. Resolves CNAME to AWS Load Balancer IPs
          v
   +-------------------+
   |   User Browser    |
   |  (Host: promo...) |
   +-------------------+
          |
          | 5. HTTP GET / HTTP/1.1
          |    Host: promo.company.com
          v
   +-------------------------------------------------------------+
   |                  CLOUD PROVIDER EDGE ROUTER                 |
   |                       (e.g., AWS S3)                        |
   |-------------------------------------------------------------|
   | Does 'company-promo' exist?                                 |
   |                                                             |
   | [SCENARIO A: DELETED/DANGLING]                              |
   |   --> No bucket found.                                      |
   |   --> Return 404 NoSuchBucket                               |
   |                                                             |
   | [SCENARIO B: ATTACKER CLAIMED]                              |
   |   --> Attacker created bucket 'company-promo'               |
   |   --> Route traffic to ATTACKER BUCKET                      |
   +-------------------------------------------------------------+
          |
          v
   +-------------------+
   | ATTACKER'S ASSET  |  <--- Attacker serves malicious JS,
   | (Under Attacker's |       Phishing Pages, or intercepts
   |  AWS Account)     |       OAuth Tokens/Cookies!
   +-------------------+
```

## 4. Deep Dive into the Impact

A common misconception among junior penetration testers is that a subdomain takeover simply allows for website defacement. While defacement is a reputational risk, the actual technical impact is fundamentally catastrophic, heavily compromising the target organization's security posture.

### 4.1 Cookie Stealing and Session Hijacking
Web applications frequently utilize cookies for session management. When defining cookies, developers can set the `Domain` attribute. If an authentication cookie is set with `Domain=.company.com`, the browser will automatically append this cookie to *every* request made to *any* subdomain of `company.com`. If an attacker controls `promo.company.com`, they can deploy a script that simply logs all incoming requests. As soon as an authenticated victim visits `promo.company.com`, the attacker receives their highly sensitive session cookies and can instantly hijack their account.

### 4.2 Cross-Origin Resource Sharing (CORS) Bypasses
Modern web applications use CORS to define which origins are permitted to read data via XMLHttpRequest or the Fetch API. To simplify configuration, many developers implement overly permissive CORS policies like wildcard subdomains (e.g., `Access-Control-Allow-Origin: https://*.company.com`). If an attacker takes over `promo.company.com`, they automatically bypass the CORS restrictions. They can host a malicious script on the subverted domain that sends asynchronous requests to the main application (`api.company.com`) to extract sensitive user data, PII, or API keys, bypassing all Same-Origin Policy (SOP) defenses.

### 4.3 OAuth Whitelist Bypasses
OAuth flows (like "Sign in with Google" or internal SSO) rely on a `redirect_uri` to send the authentication token back to the application. To prevent tokens from being sent to malicious sites, the Identity Provider (IdP) validates the `redirect_uri` against a pre-approved whitelist. Very often, administrators use wildcard whitelisting for convenience (e.g., `*.company.com/*`). An attacker controlling a subdomain can initiate an OAuth flow, set the `redirect_uri` to their controlled subdomain, and steal the user's OAuth authorization codes or access tokens.

### 4.4 Phishing and Brand Impersonation
The most immediate and visually obvious attack is phishing. Because the URL in the browser genuinely reads `promo.company.com`, and because the attacker can easily generate a valid SSL/TLS certificate (using Let's Encrypt, or relying on the PaaS provider's automated TLS), the padlock icon appears green and valid. To the average user, and even to trained employees, the site is 100% legitimate. Attackers can deploy exact clones of the company's SSO login page to harvest employee credentials.

### 4.5 Content Security Policy (CSP) Bypasses
CSP is a powerful defense-in-depth mechanism against Cross-Site Scripting (XSS). A strong CSP might restrict script execution to specific trusted sources, such as `script-src 'self' *.company.com`. If an attacker takes over a subdomain, they are suddenly inside the perimeter of the trusted script sources. They can host a malicious payload on `promo.company.com/malware.js` and inject it into a vulnerable parameter on the main site, completely bypassing the CSP.

## 5. Defense and Mitigation Strategies

Remediation of subdomain takeovers requires a combination of immediate tactical fixes and long-term strategic shifts in infrastructure management.

*   **Immediate Remediation:** The fastest way to fix an identified dangling subdomain is to simply delete the offending DNS record. If the record is needed but the resource is temporarily unavailable, it should be modified to point to a safe, internal sinkhole or a static maintenance page controlled strictly by the organization.
*   **Infrastructure as Code (IaC):** Organizations should strongly avoid manual creation of DNS records. By coupling DNS management and resource provisioning within IaC tools like Terraform or CloudFormation, the destruction of an S3 bucket or Heroku app will automatically trigger the deletion of the associated CNAME record.
*   **Continuous Monitoring:** Implement continuous monitoring of DNS zone files. Tools can be configured to regularly fetch all subdomains and verify that the endpoints they point to are active and controlled by the organization. Any subdomain returning an NXDOMAIN or an unclaimed service signature should trigger an immediate high-priority alert to the security operations center (SOC).
*   **Domain Verification:** Modern PaaS providers are mitigating this vulnerability on their end by requiring domain verification (usually via TXT records) before allowing a tenant to bind a custom domain. However, this is not implemented universally.

## 6. Chaining Opportunities

Subdomain takeover is rarely the end goal; it is often the foundation for a much larger attack chain:
*   **[[04 - Cross-Site Scripting (XSS)]]:** Chained to bypass CSP restrictions if the vulnerable subdomain is whitelisted in the CSP `script-src`.
*   **[[05 - Cross-Origin Resource Sharing (CORS) Vulnerabilities]]:** Exploited to extract data if the API allows cross-origin requests from `*.target.com`.
*   **[[06 - OAuth Vulnerabilities]]:** Used to hijack OAuth tokens by exploiting wildcard `redirect_uri` validation.
*   **[[07 - Server-Side Request Forgery (SSRF)]]:** Can be used to bypass SSRF protection blacklists that only allow requests to internal `*.company.com` domains.

## 7. Related Notes
*   [[02 - CNAME to Unclaimed External Service]] - Deep dive into PaaS and SaaS misconfigurations.
*   [[03 - Fingerprinting Vulnerable Services]] - How to discover and identify dangling records in the wild.
*   [[12 - DNS Reconnaissance]] - Core concepts on enumerating the DNS records that make this attack possible.
