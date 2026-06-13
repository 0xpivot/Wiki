---
tags: [vapt, subdomain-takeover, reconnaissance, fingerprinting, intermediate]
difficulty: intermediate
module: "34 - Subdomain Takeover"
topic: "34.03 Fingerprinting Vulnerable Services"
---

# 34.03 Fingerprinting Vulnerable Services

## 1. Introduction to Subdomain Fingerprinting

Finding a subdomain takeover in the wild is a numbers game heavily reliant on precise, fast, and automated enumeration methodologies. You cannot simply guess which subdomains are vulnerable; you must systematically discover subdomains, resolve their DNS records, issue HTTP requests to the active ones, and analyze the responses. 

**Fingerprinting** in this context refers to the process of analyzing HTTP response headers, status codes, and body content to definitively identify both the underlying technology stack (e.g., AWS, GitHub, Fastly) and its current operational state (e.g., Active, Deleted, Suspended).

Because an attacker needs to know exactly *which* third-party service the dangling domain is pointed to in order to claim it, accurate fingerprinting is the most critical phase of the attack lifecycle.

## 2. The Fingerprinting Methodology Pipeline

The pipeline for identifying vulnerable services generally follows four distinct phases. Attempting to skip phases or running them out of order drastically increases the rate of false positives and wasted effort.

### Phase 1: Wide Subdomain Enumeration
The goal is to generate the largest possible list of subdomains for a target.
*   **Passive Reconnaissance:** Querying datasets that already exist without touching the target's infrastructure. Tools like `Amass`, `Subfinder`, and `Assetfinder` query APIs like VirusTotal, SecurityTrails, Censys, and certificate transparency logs (crt.sh).
*   **Active Reconnaissance:** Performing DNS brute-forcing using tools like `Gobuster` or `ffuf` with massive wordlists to find unlinked or undocumented subdomains.

### Phase 2: Mass DNS Resolution
The raw list of subdomains will contain thousands of dead, inactive, or completely fictional entries. The next step is to perform rapid DNS resolution to filter the list down to domains that actually resolve to A or CNAME records.
*   **Tools:** `MassDNS` or `puredns` are the industry standards here, capable of resolving millions of records per minute using lists of public resolvers (like 8.8.8.8, 1.1.1.1).
*   **Wildcard Filtering:** This is a critical step. Many domains use wildcard DNS (`*.company.com` resolves to a single IP). If you don't filter out wildcards, your fingerprinting tools will be flooded with millions of identical, useless responses.

### Phase 3: HTTP Probing
Once you have a list of resolving subdomains, you must interact with them at the application layer. Not all subdomains host web services, and many only respond on specific ports.
*   **Tools:** `httpx` or `httprobe`.
*   **Action:** These tools take the clean list of subdomains and attempt HTTP and HTTPS connections on standard ports (80, 443, 8080, 8443). They capture the status code, content length, title, and underlying web technology.

### Phase 4: Signature Matching (The Fingerprint)
This is where the actual vulnerability identification happens. We take the successful HTTP responses and scan the response bodies and headers for specific, known strings that indicate an unclaimed or deleted service.
*   **Tools:** `Nuclei`, `Subjack`, `Subzy`.

## 3. ASCII Architecture Diagram: The Fingerprinting Pipeline

```text
========================================================================================
                      SUBDOMAIN ENUMERATION & FINGERPRINTING PIPELINE
========================================================================================

   [ OSINT & ACTIVE BRUTEFORCING ]
   (Amass, Subfinder, Assetfinder)
                |
                v
       +-------------------+
       |  Raw Subdomains   |  (e.g., 50,000 subdomains)
       |   list.txt        |
       +-------------------+
                |
                v
     [ MASS DNS RESOLUTION ] <------ Public DNS Resolvers (1.1.1.1, 8.8.8.8)
     (MassDNS, puredns)
                |
                v
       +-------------------+
       | Resolving Domains |  (e.g., 5,000 subdomains with A/CNAME records)
       | resolved.txt      |
       +-------------------+
                |
                v
         [ HTTP PROBING ] <--------- Filter out dead ports and wildcards
         (httpx, httprobe)
                |
                v
       +-------------------+
       | Live Web Services |  (e.g., 1,200 active web endpoints)
       |   live.txt        |
       +-------------------+
                |
                v
     [ SIGNATURE MATCHING ] <------- Scans response bodies for "NoSuchBucket",
     (Nuclei, Subzy)                 "There isn't a GitHub Pages site here", etc.
                |
                v
       +===================+
       |   VULNERABLE      |  (e.g., 2 confirmed Takeover Targets)
       |   SUBDOMAINS      |
       +===================+
```

## 4. The Fingerprint Dictionary (Signatures)

The heart of automated fingerprinting tools is a JSON or YAML file containing a dictionary of signatures. Security researchers constantly update these lists as cloud providers change their error messages. Below is a deep dive into some of the most critical signatures.

### 4.1 Amazon Web Services (AWS) S3
*   **Status Code:** `404 Not Found`
*   **Response Body Signature:** `<Code>NoSuchBucket</Code>`
*   **Analysis:** This is the gold standard. If you see this XML response when visiting a subdomain, it means the DNS routes to AWS, but the specific bucket name requested via the `Host` header does not exist. It is prime for takeover *if* the bucket name is available globally.

### 4.2 GitHub Pages
*   **Status Code:** `404 Not Found`
*   **Response Body Signature:** `There isn't a GitHub Pages site here.`
*   **Analysis:** GitHub is highly reliable for fingerprinting. The error page is explicitly distinct from a standard 404, indicating the custom domain binding is broken or the repository was deleted. 

### 4.3 Heroku
*   **Status Code:** `404 Not Found`
*   **Response Body Signature:** `No such app`
*   **Analysis:** Indicates the Heroku routing mesh cannot find a dyno associated with the domain name. 

### 4.4 Shopify
*   **Status Code:** `404 Not Found`
*   **Response Body Signature:** `Sorry, this shop is currently unavailable.`
*   **Analysis:** Organizations often spin up temporary e-commerce stores for merchandise and then delete them. The DNS remains, pointing to Shopify's edge, presenting a high-risk takeover opportunity.

### 4.5 Fastly
*   **Status Code:** `500 Internal Server Error`
*   **Response Body Signature:** `Fastly error: unknown domain:`
*   **Analysis:** Fastly CDN takeovers are complex. Fastly requires a paid account and manual verification for many domain takeovers, but the fingerprint is highly distinct.

## 5. False Positives and Edge Cases

Automated fingerprinting is notorious for false positives. A penetration tester must manually verify every finding.

1.  **Intentional Sinkholes:** Many organizations explicitly route blocked or decommissioned domains to a generic AWS S3 bucket that they control, which intentionally returns `NoSuchBucket`. Because they own the bucket (perhaps a wildcard bucket or a specifically named one that is just empty), an attacker cannot claim it.
2.  **Service Deprecation:** Sometimes a signature matches, but the cloud provider has discontinued the service or locked down custom domains entirely (e.g., Tumblr, certain legacy PaaS).
3.  **WAF Blocking:** Web Application Firewalls (WAFs) like Cloudflare or Akamai might intercept the automated scan and return a 404 or 403 error page that coincidentally contains text matching a signature, completely throwing off the tooling.
4.  **Name Collisions (S3):** As mentioned in previous notes, an S3 bucket name must match the domain exactly. If the signature is present, but an unrelated third party owns the S3 bucket and simply hasn't configured it to serve web traffic, the takeover will fail.

## 6. Advanced Fingerprinting: Beyond the HTTP Body

While scanning HTTP bodies is standard, advanced fingerprinting involves deeper analysis:
*   **CNAME Record Analysis:** Instead of just looking at the HTTP response, analyze the raw CNAME record. If `sub.target.com` points to `target-promo.unbouncepages.com`, you don't even need to send an HTTP request to know it relies on Unbounce.
*   **SSL/TLS Certificate Analysis:** Sometimes, visiting the HTTPS version of a dangling subdomain will return a certificate belonging to the cloud provider (e.g., `*.herokuapp.com`). This immediately fingerprints the backend architecture, even if the HTTP body is obscured by a load balancer error.
*   **Historical DNS:** Using tools like SecurityTrails to see what the domain *used* to point to can provide immense context if the current responses are obfuscated.

## 7. Chaining Opportunities

*   **[[12 - DNS Reconnaissance]]:** The foundational skills required to build the initial list of subdomains for fingerprinting.
*   **[[11 - Web Application Firewalls (WAF)]]:** Understanding how to bypass WAFs that might be blocking your fingerprinting probes (Phase 3).
*   **[[14 - Automation and Tooling]]:** Integrating Nuclei, Subfinder, and httpx into continuous CI/CD pipelines for offensive security monitoring.

## 8. Related Notes
*   [[01 - What is Subdomain Takeover]]
*   [[02 - CNAME to Unclaimed External Service]]
