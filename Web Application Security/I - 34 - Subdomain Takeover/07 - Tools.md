---
tags: [vapt, subdomain-takeover, tooling, nuclei, subjack, intermediate]
difficulty: intermediate
module: "34 - Subdomain Takeover"
topic: "34.07 Tools - subjack, nuclei, can-i-take-over-xyz"
---

# Subdomain Takeover Tooling: Subjack, Nuclei, and can-i-take-over-xyz

## 1. Introduction

Subdomain takeover is a devastating vulnerability that occurs when a DNS record points to a service that has been decommissioned or deleted, leaving the endpoint "dangling." Because the underlying service is no longer claimed by the original owner, an attacker can register the resource on the third-party provider and effectively hijack the subdomain. While the conceptual basis of this attack is straightforward—identify dangling records and register them—the practical execution at scale requires robust, highly accurate tooling.

In modern Bug Bounty programs and corporate Red Teaming, scopes can encompass tens of thousands, or even millions, of subdomains. Manually resolving each one and inspecting the HTTP response or DNS status is an exercise in futility. Thus, the security community has developed a suite of tools designed to automate the detection of dangling records and verify whether they are vulnerable to takeover.

This document provides a deep, technical dive into the standard toolkit for subdomain takeover detection, focusing on the foundational knowledge base `can-i-take-over-xyz`, the dedicated scanner `subjack`, and the highly extensible engine `Nuclei`. We will explore their internal mechanisms, configuration files, and how they parse DNS responses to minimize false positives.

## 2. The Core Foundation: EdOverflow's `can-i-take-over-xyz`

Before examining the active scanners, it is crucial to understand where they get their intelligence. Almost every modern subdomain takeover tool relies on the research centralized in the `can-i-take-over-xyz` repository maintained by EdOverflow and the security community.

### 2.1 What is `can-i-take-over-xyz`?

The `can-i-take-over-xyz` repository is not a scanner itself; rather, it is a comprehensive, open-source database of cloud providers and third-party services that tracks their susceptibility to subdomain takeover. It provides the "fingerprints"—the specific HTTP responses, DNS statuses (like `NXDOMAIN`), and error messages that indicate a service is unregistered and available for claim.

### 2.2 The Anatomy of a Fingerprint

A fingerprint is essentially a set of conditions that must be met for a subdomain to be considered vulnerable. These conditions typically include:
- **CNAME Target**: The typical domain pattern used by the provider (e.g., `*.herokuapp.com`, `*.s3.amazonaws.com`).
- **HTTP Response Body**: Specific strings returned by the provider when an unregistered endpoint is accessed (e.g., `There is no app configured at that hostname`, `NoSuchBucket`).
- **HTTP Status Code**: Often `404 Not Found`, though some providers return `403 Forbidden` or `500 Internal Server Error`.
- **NXDOMAIN Status**: Some takeovers do not rely on an HTTP response. Instead, they occur when the CNAME target resolves to `NXDOMAIN`, indicating the target domain itself does not exist (common in Azure Traffic Manager or AWS Elastic Beanstalk takeovers).

### 2.3 Challenges and Edge Cases

The repository also meticulously documents edge cases:
- **Vulnerable vs. Not Vulnerable**: Services are categorized. Some providers have implemented strict domain verification (e.g., requiring a TXT record for ownership verification), making takeovers impossible even if a dangling CNAME exists.
- **Edge Cases**: Instances where the fingerprint string might appear legitimately, or where a provider uses dynamic error pages.
- **Service Evolution**: Cloud providers update their infrastructure. A fingerprint that worked in 2020 might be obsolete today. The repository is constantly updated to reflect these changes.

## 3. Tool Workflow Architecture

The following ASCII diagram illustrates the generalized architecture of how these automation tools operate when fed a list of subdomains.

```text
+---------------------+
|   Subdomain List    |  (e.g., subdomains.txt)
+----------+----------+
           |
           v
+---------------------+
|   DNS Resolution    |  <-- Tool queries authoritative / recursive resolvers
|      Engine         |
+----------+----------+
           |
           v
   [Is there a CNAME or A record pointing to a known 3rd-party?]
           |
     +-----+-----+
     |           |
   [NO]        [YES]
     |           |
   [Skip]        v
         +---------------------+
         | HTTP / HTTPS Prober |  <-- Tool sends GET requests to the endpoint
         +---------+-----------+
                   |
                   v
         +---------------------+
         | Fingerprint Matcher |  <-- Compares response against known signatures
         | (e.g., fingerprints)|      (from can-i-take-over-xyz)
         +---------+-----------+
                   |
             +-----+-----+
             |           |
          [Match]     [No Match]
             |           |
             v           v
    +----------------+ [Mark as Safe / Review]
    | Flag as VULN   |
    | (Takeover Pos) |
    +----------------+
```

This pipeline emphasizes that DNS resolution is the primary filter, followed by HTTP probing as the secondary verification step. This prevents the scanner from spamming HTTP requests to targets that are demonstrably not vulnerable based purely on DNS records.

## 4. Deep Dive into `Subjack`

`Subjack` is a fast, specialized subdomain takeover tool written in Go by `haccer`. It is designed specifically to read a list of subdomains and aggressively match them against a set of JSON-formatted fingerprints.

### 4.1 Installation and Basic Usage

Subjack can be compiled and installed easily using Go:
```bash
go install github.com/haccer/subjack@latest
```

A standard comprehensive scan looks like this:
```bash
subjack -w subdomains.txt -t 100 -timeout 30 -o results.txt -ssl -c ~/fingerprints.json
```
- `-w`: Wordlist of subdomains (the target scope).
- `-t`: Number of concurrent threads (performance tuning).
- `-timeout`: Timeout in seconds for HTTP requests.
- `-o`: Output file to log discovered vulnerabilities.
- `-ssl`: Forces HTTPS requests. Many cloud providers only return their default "unregistered" error page over HTTPS or have strict HTTP-to-HTTPS redirects. If you omit this, you may miss findings.
- `-c`: Points to a custom `fingerprints.json` file.

### 4.2 The `fingerprints.json` Architecture

Subjack relies on a configuration file named `fingerprints.json`. This file acts as the translation layer, converting the findings from `can-i-take-over-xyz` into a machine-readable format for the scanner.

Example of a Subjack fingerprint payload:
```json
[
  {
    "service": "GitHub Pages",
    "cname": ["github.io"],
    "fingerprint": "There isn't a GitHub Pages site here.",
    "nxdomain": false,
    "status": "Vulnerable",
    "http_status": 404
  },
  {
    "service": "Heroku",
    "cname": ["herokuapp.com"],
    "fingerprint": "No such app",
    "nxdomain": false,
    "status": "Vulnerable",
    "http_status": 404
  }
]
```
The scanner checks if the CNAME matches the array. If it does, it requests the page. If the `fingerprint` string is present in the response body, it triggers an alert.

### 4.3 Advanced Configuration and Pitfalls

- **Custom Fingerprints**: Relying solely on the default `fingerprints.json` is a mistake for advanced operators. Many private or undocumented enterprise services have specific error strings. Security researchers often maintain their own, highly curated `fingerprints.json` files tailored to the specific infrastructure of the target they are assessing.
- **The `-a` Flag**: By default, Subjack only checks subdomains that have a CNAME pointing to one of the targets in the JSON file. If a cloud provider uses A records instead (e.g., an Anycast IP associated with an unregistered service), Subjack will silently ignore it. The `-a` flag tells Subjack to check *every* subdomain, regardless of its CNAME status, which drastically increases scan time but uncovers complex takeovers that rely purely on A records.
- **The `-m` Flag**: When enabled, it checks for the presence of the fingerprint in the HTTP response, but it bypasses the CNAME checks completely. This is useful for black-box environments where DNS resolution might be spoofed or obfuscated behind a CDN or proxy layer.

## 5. Deep Dive into `Nuclei`

While Subjack is a specialized standalone tool, ProjectDiscovery's `Nuclei` is a generalized vulnerability scanner driven by YAML templates. Over the years, Nuclei has become the industry standard for subdomain takeover detection due to its incredible extensibility, speed, and active community maintaining the templates.

### 5.1 Why Nuclei Excels at Subdomain Takeover

1. **Templating System**: Instead of a massive monolithic JSON file, Nuclei uses modular YAML templates. The `takeovers/` directory in the `nuclei-templates` repository contains hundreds of individual templates for different services, making version control and updates vastly superior.
2. **Multi-Protocol Support**: Nuclei isn't limited to HTTP. It has templates for DNS-based takeovers (checking specifically for `NXDOMAIN` statuses) and even TCP-based interactions.
3. **Complex Matching Logic**: Nuclei can perform complex regex matching, logical AND/OR operations on matchers, and extract specific parts of the response, heavily reducing false positives.

### 5.2 Anatomy of a Nuclei Takeover Template

Consider a simplified Nuclei template for an AWS S3 bucket takeover:

```yaml
id: aws-bucket-takeover
info:
  name: AWS S3 Bucket Subdomain Takeover
  author: pdteam
  severity: high
  description: An S3 bucket subdomain takeover was detected.
  tags: takeover,aws,s3
requests:
  - method: GET
    path:
      - "{{BaseURL}}"
    matchers-condition: and
    matchers:
      - type: word
        words:
          - "NoSuchBucket"
          - "The specified bucket does not exist"
        condition: or
      - type: status
        status:
          - 404
      - type: word
        words:
          - "s3.amazonaws.com"
        part: host
```

**Key Elements:**
- `matchers-condition: and`: Requires all subsequent matcher blocks to evaluate to true. The response must be a 404 AND contain the string AND the host must match.
- `words`: The specific string sourced from `can-i-take-over-xyz`.
- `part: host`: This is crucial. It ensures that the engine only flags this if the CNAME or domain itself actually relates to AWS, preventing false positives if a random corporate application happens to output the string "NoSuchBucket" naturally.

### 5.3 Executing Nuclei for Takeovers

To run Nuclei specifically for subdomain takeovers, bypassing other vulnerability checks:
```bash
nuclei -l subdomains.txt -t takeovers/ -o nuclei_takeovers.txt
```
Using the `-t takeovers/` flag restricts the scan entirely to the takeover templates, ensuring high speed.

### 5.4 Automating DNS Workflows with Nuclei

Advanced bug hunters often chain `dnsx` with `Nuclei`. Because hitting hundreds of thousands of dead endpoints with HTTP requests is slow and noisy, they first resolve CNAMEs locally:

```bash
cat subdomains.txt | dnsx -cname -resp | grep -iE 'amazonaws|herokuapp|github|azure' | awk '{print $1}' > filtered_subs.txt
nuclei -l filtered_subs.txt -t takeovers/
```
This pipeline drastically reduces the scope to only domains pointing to known vulnerable provider networks, optimizing the engagement.

## 6. Alternative Tools and Ecosystem

While Subjack and Nuclei are prominent, several other tools serve niche roles in the community:

### 6.1 Subzy
Written in Go, `subzy` acts similarly to Subjack but offers slightly different parsing logic and output formats (like native JSON output, which is great for ingestion into vulnerability management systems, Elasticsearch, or Jira).

```bash
subzy run --targets subdomains.txt --concurrency 100
```

### 6.2 dnsReaper
Developed by Punk Security, `dnsReaper` approaches the problem not just from the outside (black-box), but from the inside (white-box). It can ingest AWS, Azure, and Cloudflare API credentials, read the entire DNS zone file internally, and immediately flag dangling records without relying solely on external resolution or HTTP brute-forcing. This makes it an exceptional tool for Blue Teams and defensive posture management.

## 7. False Positives and Manual Verification

No automated tool is flawless. The heavy reliance on string matching means false positives are entirely inevitable. An experienced VAPT professional must validate the results.

### 7.1 Common Causes of False Positives

1. **WAF Blocks**: A Web Application Firewall (like Cloudflare or AWS WAF) might block the scanner's User-Agent, returning a 403 Forbidden. If a specific fingerprint relies on a 403 status code without stringent body matching, the tool might flag it erroneously.
2. **Wildcard DNS**: If a domain has a wildcard DNS record (`*.example.com` -> `A 1.2.3.4`), the tool might interpret the resolution as a potential takeover target, especially if the default fallback page at `1.2.3.4` matches a generic error.
3. **Internal Application Errors**: Developers sometimes hardcode strings like "Not Found" or "Does Not Exist" in their custom 404 error handlers, inadvertently mimicking cloud provider errors and tricking scanners.

### 7.2 The Manual Verification Process

When a tool flags a takeover, a professional VAPT engineer **must** manually verify it before drafting a report.

1. **DNS Verification**: Use `dig` or `host` to confirm the CNAME chain exists and points where the tool says it does.
   ```bash
   dig +short dev.example.com
   dig +short CNAME dev.example.com
   ```
2. **HTTP Verification**: Use `curl` to view the raw HTTP response, ensuring you mimic a normal browser User-Agent if necessary. Check the headers to confirm the provider (e.g., `Server: AmazonS3`).
   ```bash
   curl -i -s -k https://dev.example.com -H "User-Agent: Mozilla/5.0"
   ```
3. **Attempting the Claim**: For bug bounty scenarios or authorized red teams, the definitive proof is successfully registering the resource. Create an AWS S3 bucket with the exact name, or initialize a GitHub Pages repository, and place a harmless proof-of-concept (POC) file (e.g., `poc.html` or `poc.txt` with a benign text string) at the root.

## 8. Chaining Opportunities

Subdomain takeover tools are not just for finding high-severity standalone bugs; they act as reconnaissance engines for devastating complex chains:
- **Cookie Stealing**: If a tool flags a takeover on `dev.example.com`, and the main application at `example.com` scopes session cookies to `.example.com` (wildcard scope), an attacker can hijack sessions by hosting a malicious script on the taken-over domain.
- **CORS Misconfigurations**: Identifying a taken-over subdomain that is whitelisted in an API's Cross-Origin Resource Sharing (CORS) policy (`Access-Control-Allow-Origin: https://dev.example.com`) allows for cross-origin data exfiltration.
- **Oauth Whitelists**: Often, developer subdomains are inadvertently whitelisted for OAuth callbacks. An attacker controlling the domain can steal OAuth tokens intended for internal applications.

## 9. Related Notes
- [[01 - Introduction to Subdomain Takeover]]
- [[02 - CNAME Records and DNS Resolution]]
- [[08 - Defense - Remove Dangling DNS Records]]
- [[12 - Advanced Exploitation and Post-Takeover]]
