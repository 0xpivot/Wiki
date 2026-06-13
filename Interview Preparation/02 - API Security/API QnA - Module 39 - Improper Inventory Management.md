---
tags: [interview, api-security, qna, scenario]
difficulty: expert
module: "Interview Prep - API Security"
topic: "QnA - API Module 39"
---

# Threat Hunting & Offensive Engineering: Improper Inventory Management

## Custom ASCII Diagram

```text
    [ Attack Surface ]
            |
    +-------+-------+-------+-------+
    |               |               |
[ Prod App ]   [ Staging ]     [ Legacy v1 ]
  (Secure)      (Ignored)     (Forgotten, Unpatched)
    |               |               |
    |               |               +<--- 1. Attacker Discovers via Subdomain Enum
    |               |                     (legacy.corp.com)
    |               |               
    |               +<--- 2. Attacker finds exposed debug endpoints
    |                     (staging.corp.com/debug)
    |
    v
[ Internal Corporate Network / Database ]
    ^               ^               ^
    |               |               |
    +---------------+---------------+
          Shared Backend DB
      (The weak link compromises all)
```

## Formal Technical Questions

### Q1: Define "Shadow IT" and explain why it presents a critical challenge to Threat Hunters and Red Teams.
**Answer:**
Shadow IT refers to any software, application, cloud instance, or infrastructure deployed within an organization without the explicit knowledge, approval, or oversight of the centralized IT/Security department.

**The Challenge:**
For Red Teams, Shadow IT is the ultimate soft target. Because security teams don't know it exists, it bypasses standard security controls: it isn't covered by vulnerability scanners, it lacks endpoint detection (EDR), it misses patch management cycles, and its logs are not forwarded to the SIEM. 
For Threat Hunters, it presents a massive blind spot. If an attacker breaches a forgotten marketing WordPress site hosted on an unsanctioned DigitalOcean droplet, the hunter has zero telemetry to detect the initial foothold. The first alert might only trigger when the attacker pivots from the unmonitored environment into the corporate network via a forgotten VPN tunnel.

### Q2: What is "Zombie Infrastructure," and how does it differ from traditional unpatched systems?
**Answer:**
Zombie Infrastructure refers to environments, APIs, or servers that were officially sanctioned and deployed (unlike Shadow IT) but have been completely abandoned. They serve no current business purpose but were never properly decommissioned. Common examples include `v1` backend services kept alive "just in case" for backward compatibility, or staging databases from a project completed three years ago.

**The Difference:**
Traditional unpatched systems are known, actively used, and their risks are generally accepted or tracked. Zombie infrastructure is uniquely dangerous because no one is maintaining or monitoring it. Since it was once sanctioned, it often retains high-level privileges—such as active database credentials, trusted IAM roles, or peering connections to production networks. Attackers target zombies because exploiting them rarely triggers operational alarms (no user complaints if a zombie crashes).

### Q3: Explain the methodology of Attack Surface Management (ASM) and continuous reconnaissance in combating improper inventory.
**Answer:**
ASM is the continuous discovery, inventory, and monitoring of an organization's external-facing assets. To combat improper inventory, security teams must adopt an attacker's reconnaissance methodology.

**The Methodology:**
1. **Seed Gathering**: Collecting the root domains, ASNs, and public IP blocks owned by the organization.
2. **Horizontal Enumeration**: Using tools like Amass, Sublist3r, and Chaos to brute-force and scrape subdomains. Monitoring Certificate Transparency (CT) logs to instantly detect when developers request TLS certificates for new, unannounced subdomains.
3. **Vertical Enumeration**: Port scanning the discovered assets, grabbing banners, and fingerprinting technologies using Nuclei or Wappalyzer to map the stack.
4. **Change Detection**: ASM is not a point-in-time assessment. It must run continuously. The system alerts security teams when a new port opens on a known IP, a new subdomain appears in DNS, or a previously secure asset suddenly exposes a `.git` directory, immediately flagging potential inventory anomalies.

## Scenario-Based Questions

### Q1: You are on a Red Team engagement. You have performed extensive OSINT and subdomain enumeration on the target, `corp.local`. You discover `uat-backend.corp.local`, which appears to be a User Acceptance Testing environment. How do you leverage this staging environment to attack production?
**Answer:**
Staging and UAT environments are notorious for improper inventory management and poor security hygiene because developers treat them as safe sandboxes.

**Exploitation Strategy:**
1. **Lower Security Controls**: Staging environments frequently lack WAFs, rate limiting, and strict authentication. I will attack the UAT application for low-hanging fruit like SQL Injection or Insecure Direct Object References (IDOR) that might have been patched in production.
2. **Shared Secrets**: The most critical flaw is credential reuse. Developers often use the same database passwords, JWT signing keys, or AWS access keys in UAT as they do in production. If I achieve Local File Inclusion (LFI) or gain access to UAT source code, I will extract these secrets.
3. **Infrastructure Peering**: Staging environments are rarely isolated at the network level. Once I compromise the UAT server via an unpatched vulnerability, I will use it as a pivot point. Since it is considered internal infrastructure, firewalls often permit the UAT server to communicate directly with the production database or internal CI/CD pipelines, allowing me to bypass perimeter defenses entirely.

### Q2: As an Incident Responder, you trace a data breach back to a legacy application hosted on a forgotten AWS EC2 instance. The instance was not in the official asset inventory. What steps do you take to identify how it was deployed and prevent future occurrences?
**Answer:**
Discovering compromised zombie infrastructure requires forensic reconstruction of the cloud environment.

**Investigation:**
1. **CloudTrail Forensics**: I will query AWS CloudTrail logs (retained centrally in an S3 bucket or SIEM) using the Instance ID. I will search for the original `RunInstances` event to identify the IAM user or role that deployed it, the exact timestamp, and the subnet it resides in.
2. **Network Mapping**: I will analyze VPC Flow logs to determine what other internal resources this forgotten instance was communicating with prior to and during the breach, mapping the attacker's pivot paths.

**Prevention:**
1. **Implement Tagging Policies**: Enforce strict Resource Tagging via AWS Organizations. Any EC2 instance spun up without mandatory tags (e.g., `Owner`, `Project`, `DecommissionDate`) is automatically terminated by a Lambda function.
2. **Deploy Cloud Security Posture Management (CSPM)**: Integrate a CSPM tool to continuously inventory the cloud footprint and alert on "orphaned" assets—instances with low CPU utilization over long periods or instances lacking required EDR agents.

## Deep-Dive Defensive Questions

### Q1: Develop a strategy using DNS logs and Certificate Transparency to proactively identify Shadow IT deployments.
**Answer:**
Security teams can turn passive telemetry into an automated Shadow IT detection engine.

**The Strategy:**
1. **Certificate Transparency (CT) Monitoring**: I will deploy a script that continuously subscribes to CT log streams (e.g., certstream). It will regex match our organization's domain names (`*.company.com`). Whenever a developer spins up a rogue server and requests a Let's Encrypt certificate for `dev-testing.company.com`, the security team receives a Slack alert in real-time.
2. **DNS Passive Reconnaissance**: I will ingest our internal DNS resolver logs into the SIEM.
```splunk
index=dns sourcetype=stream:dns 
| stats count by query, src_ip 
| where query LIKE "%company.com" 
| lookup asset_inventory host AS query OUTPUT is_known 
| where is_known="false"
```
By cross-referencing internal DNS requests made by employees against our official CMDB (Configuration Management Database), we can flag when internal users are navigating to internal domains that the security team has no record of, immediately highlighting undocumented assets.

### Q2: How does a robust CI/CD pipeline mitigate the risks of Zombie Infrastructure?
**Answer:**
Zombie infrastructure usually occurs as a result of manual deployments (e.g., an engineer spinning up a VM via a web console and forgetting it). 

Integrating infrastructure deployment strictly into a CI/CD pipeline (Infrastructure as Code - IaC) solves this via lifecycle management:
1. **Ephemeral Environments**: The pipeline can be configured to provision testing environments dynamically when a Pull Request is opened, and *automatically destroy* the infrastructure (via `terraform destroy`) when the PR is merged or closed. The infrastructure cannot become a zombie because its lifecycle is tied strictly to the code branch.
2. **Single Source of Truth**: When infrastructure is defined in Git (GitOps), the repository serves as a living, auditable inventory. If a service needs to be deprecated, the code is removed from the repository, and the pipeline automatically tears down the associated cloud resources, leaving no orphaned assets behind.

## Real-World Attack Scenario

**The Forgotten Marketing Subdomain**

During a widespread ransomware campaign, a Fortune 500 company was breached without any phishing or sophisticated zero-day exploits.

**The Flaw:**
Three years prior, the marketing team hired a third-party vendor to run a temporary promotional campaign. The IT team created a DNS record `promo.target.com` pointing to the vendor's Azure infrastructure. After the campaign ended, the vendor deleted the Azure instance, but the DNS CNAME record remained active in the target's Route53 configuration.

**The Attack:**
1. The attacker ran an automated subdomain takeover tool (like `subzy` or `nuclei`) against `target.com`.
2. The tool identified `promo.target.com` as a dangling DNS record pointing to an unclaimed Azure App Service.
3. The attacker created an Azure account and claimed the exact app service name.
4. The attacker deployed a highly convincing phishing page mirroring the target's employee login portal on the `promo.target.com` domain.
5. Because the domain was a legitimate, trusted subdomain of the company, it bypassed all internal email filters and SSL reputation checks.
6. Employees, trusting the URL, entered their credentials, which the attacker harvested to access the internal VPN and deploy ransomware.

## Chaining Opportunities

- **Subdomain Takeover + Session Hijacking**: Using a taken-over subdomain to read broad-scoped cookies (e.g., `Set-Cookie: session=xyz; Domain=.company.com`).
- **Zombie Infrastructure + Deserialization**: Targeting forgotten `v1` backend endpoints that still accept insecure serialized objects.
- **Shadow IT + Default Credentials**: Finding undocumented internal instances running default installations of Apache Airflow or Jenkins.
- **Unpatched Staging + SSRF**: Exploiting an unpatched SSRF vulnerability in a forgotten UAT environment to extract production AWS metadata credentials.

## Related Notes
- [[17 - Continuous Attack Surface Management]]
- [[29 - CloudTrail Forensics]]
- [[38 - Subdomain Takeovers in Cloud Environments]]
- [[44 - Securing the Software Development Lifecycle]]
