---
tags: [vapt, subdomain-takeover, defense, dns, beginner]
difficulty: beginner
module: "34 - Subdomain Takeover"
topic: "34.08 Defense - Remove Dangling DNS Records"
---

# Defending Against Subdomain Takeover: Removing Dangling DNS Records

## 1. Introduction

Subdomain takeover is a critical vulnerability that stems directly from infrastructure management failures rather than application code flaws. Unlike SQL Injection or Cross-Site Scripting, which require complex input validation, Subdomain Takeover is an operational security failure. It occurs when a DNS record points to a third-party service (like AWS S3, Heroku, or Azure Traffic Manager) that has been deprovisioned, leaving the DNS record "dangling."

Defending against this attack requires a paradigm shift from traditional application security to robust Cloud Infrastructure and Identity Management. The primary defense mechanism is conceptually simple: **Remove Dangling DNS Records**. However, executing this consistently at enterprise scale—across hundreds of AWS accounts, Azure subscriptions, and decentralized development teams—is incredibly complex.

This document explores the root causes of dangling DNS records, preventative engineering practices, and continuous monitoring strategies necessary to eradicate subdomain takeovers from modern infrastructure.

## 2. The Core Problem: The Disconnect Between Cloud Resources and DNS

The root cause of subdomain takeover is the asynchronous lifecycle management between two distinct systems:
1. **The Cloud Resource**: The actual compute, storage, or platform resource (e.g., an EC2 instance, an S3 bucket, a GitHub Pages repository).
2. **The DNS Zone**: The authoritative name servers (e.g., Route53, Cloudflare, Bind) that direct traffic from a human-readable domain to the cloud resource.

When a developer spins up a new service, they typically provision the cloud resource first, then create a CNAME or A record pointing to it. This process is highly visible. However, when a project is deprecated, the developer often deletes the cloud resource to save costs but forgets to remove the associated DNS record, as DNS changes are often managed by a different team or require separate change requests.

### 2.1 The Vulnerable Lifecycle

1. **Creation**: Dev creates S3 bucket `marketing-assets-123.s3.amazonaws.com`.
2. **DNS Binding**: Network team creates CNAME `assets.company.com -> marketing-assets-123.s3.amazonaws.com`.
3. **Deprecation**: Campaign ends. Dev deletes the S3 bucket to save $5/month.
4. **The Dangling State**: `assets.company.com` still points to the non-existent bucket.
5. **Takeover**: An attacker creates an S3 bucket named `marketing-assets-123` in their own AWS account, instantly gaining control over `assets.company.com`.

## 3. ASCII Diagram: The Vulnerable vs. Secure Cloud Lifecycle

The following diagram illustrates the difference between an unmanaged (vulnerable) lifecycle and a secure, Infrastructure-as-Code (IaC) managed lifecycle.

```text
============= VULNERABLE LIFECYCLE (Manual Management) =============

 [Dev Team] ---Deletes Resource---> [AWS S3 / Azure App] (Resource Gone)
                                             ^
                                             | (Dangling Pointer)
 [Net Team] ---Forgets to Update--> [DNS Zone (Route53)] (CNAME still exists)
                                             |
 [Attacker] ---Claims Name--------> [Attacker's AWS S3]  <--- TAKEOVER SUCCESS!


============== SECURE LIFECYCLE (IaC / GitOps Management) ==============

 [Dev Team] ---Commits 'terraform destroy'---> [Git Repository]
                                                      |
                                                      v
                                            [CI/CD Pipeline (Jenkins/Actions)]
                                                      |
                          +---------------------------+---------------------------+
                          |                                                       |
                          v                                                       v
         [Destroys AWS S3 Resource]                               [Removes Route53 CNAME]
         (Resource Gone)                                          (DNS Record Purged)

 Result: No Dangling Records. The attacker has nothing to point to.
```

## 4. Preventative Measures: Engineering for Security

The most effective way to handle subdomain takeovers is to prevent dangling records from being created in the first place.

### 4.1 Infrastructure as Code (IaC)

The gold standard for defense is managing both cloud resources and DNS records within the same Infrastructure as Code (IaC) definitions (e.g., Terraform, AWS CloudFormation, Pulumi).

By defining a web application and its DNS record in the same Terraform module, you ensure that their lifecycles are tightly coupled. When the module is destroyed (`terraform destroy`), Terraform automatically issues the API calls to delete the S3 bucket *and* the Route53 CNAME record simultaneously.

### 4.2 Centralized DNS Management and GitOps

Organizations should move away from manual "ClickOps" in DNS management portals. Instead, DNS zones should be managed via a GitOps workflow. Changes to DNS require a pull request, code review, and automated deployment. This provides an audit trail of who created what record, making it easier to track down the owners of abandoned subdomains during security audits.

Furthermore, enforcing "Least Privilege" at the IAM level ensures that developers cannot manually mutate DNS records outside the pipeline. By restricting `route53:ChangeResourceRecordSets` strictly to the CI/CD deployment roles, human error is systematically removed from the equation.

### 4.3 Implementing "Domain Verification"

Many modern cloud providers have recognized the subdomain takeover threat and implemented preventative measures on their end. As a defender, you should configure your services to utilize these features:

- **Custom Domain Verification**: Providers like Azure App Service and GitHub Pages require you to prove ownership of the domain before they allow traffic to route to your service. They typically require you to add a specific `TXT` record (e.g., `asuid.assets.company.com`) containing a unique verification token.
- **Enforcing Verification**: If an attacker tries to claim your dangling CNAME on a provider that enforces TXT verification, the takeover will fail because the attacker cannot modify your authoritative DNS zone to add the required TXT token.

### 4.4 Managing Orphaned A Records and Elastic IPs

While CNAME takeovers are the most common, A record takeovers via ephemeral IPs are increasingly relevant and harder to track.
- **The Threat**: If a DNS A record points to an AWS Elastic IP (EIP) or Azure Static IP, and the administrator releases that IP back into the public pool without deleting the DNS record, an attacker can continuously spin up new cloud instances until they are randomly assigned the targeted, vulnerable IP.
- **The Defense**: IP addresses should be treated as highly mutable assets unless strictly reserved. Implement strict policies forbidding the release of EIPs until all associated DNS dependencies have been thoroughly audited and removed. Use AWS Config rules or Azure Policy to monitor for unattached Elastic IPs.

## 5. Detective Measures: Continuous Monitoring

Even with strict IaC policies, manual interventions occur, and legacy infrastructure exists. Therefore, continuous monitoring is mandatory to catch what prevention misses.

### 5.1 Internal DNS Auditing (White-Box Scanning)

Unlike attackers who must rely on brute-force enumeration and external resolution, defenders have access to the authoritative zone files. Tools can be deployed internally to continuously parse the entire DNS zone and verify the operational status of the targets.

- **Automated Scrubbing Scripts**: Organizations can write Python or Go scripts that run daily, iterate through every CNAME record in Route53/Cloudflare, and verify if the target resolves properly. If a CNAME points to an `NXDOMAIN` or a known 3rd-party error page, the script alerts the security team via Slack or PagerDuty.
- **Using dnsReaper**: As mentioned in the tooling section, Punk Security's `dnsReaper` is excellent for this. It can be provided with read-only AWS/Azure API keys, allowing it to fetch all DNS records and automatically cross-reference them against internal and external cloud assets to find dangling pointers without sending a single external HTTP request.

### 5.2 External Attack Surface Management (EASM)

For massive organizations with fragmented IT environments, utilizing an EASM platform or continuous bug bounty programs ensures that any dangling records that slip through internal audits are caught by external security researchers. Running tools like `Nuclei` on a scheduled cron job against known corporate assets is a practical, low-cost implementation of EASM.

## 6. Incident Response: Handling a Subdomain Takeover

If a subdomain takeover is detected or reported by a bug bounty hunter, immediate, precise action is required to minimize the blast radius.

### 6.1 Containment and Eradication

1. **Delete the DNS Record Immediately**: The absolute fastest way to stop the attack is to delete the dangling CNAME or A record from your DNS zone. This severs the connection between your domain and the attacker's infrastructure. It takes time for DNS caches to clear globally (depending on the TTL), but it is the critical first step.
2. **Contact the Cloud Provider**: If the attacker is actively hosting malicious content (phishing, malware) on the hijacked service, contact the abuse department of the cloud provider (e.g., AWS Trust & Safety) with proof of domain ownership. They can suspend the attacker's account and tear down the malicious resource from their end.

### 6.2 Impact Assessment

Once contained, the security team must rigorously assess what the attacker could have done while they controlled the subdomain. A subdomain takeover is rarely just a defacement; it's a foothold.
- **Cookie Theft**: Did the main application (`company.com`) issue wildcard session cookies (`Domain=.company.com`)? If so, the attacker could have stolen user sessions via XSS on the taken-over domain. All user sessions across the organization may need to be forcefully invalidated.
- **CORS Misuse**: Was the taken-over subdomain whitelisted in any CORS configurations on your critical internal APIs? If so, the attacker could have executed Cross-Origin requests on behalf of authenticated users, leading to data exfiltration.
- **Phishing Campaigns**: Did the attacker use the trusted domain to launch spear-phishing campaigns against employees or customers? Monitor email gateways, DMARC reports, and threat intelligence feeds for signs of abuse.
- **OAuth Callbacks**: Was the subdomain registered as a valid callback URL in OAuth applications (e.g., "Sign in with Google" or "Sign in with Azure AD")? The attacker could have intercepted OAuth tokens, granting them persistent access to user accounts.

### 6.3 Post-Incident Review

Following the incident, the organization must conduct a blameless root-cause analysis to determine why the cloud resource was deleted without the corresponding DNS record. The findings should drive the implementation of IaC, tighter IAM controls, or improved CI/CD pipeline automation to prevent recurrence.

## 7. Chaining Opportunities

Defending against subdomain takeover inherently neutralizes several complex attack chains:
- **Preventing XSS Escalation**: A takeover provides a reliable, persistent execution environment for JavaScript within the organization's domain trust boundary, completely bypassing Same-Origin Policy (SOP) restrictions for sibling domains. Removing dangling records kills this attack vector entirely.
- **Securing Trust Boundaries**: Many internal security mechanisms (like SSO bypasses, VPN split-tunneling, or WAF rules) implicitly trust any traffic originating from `*.internal.company.com`. Preventing takeovers ensures these trust boundaries remain uncompromised.

## 8. Related Notes
- [[01 - Introduction to Subdomain Takeover]]
- [[07 - Tools]]
- [[09 - Cloud Provider Specific Defenses (AWS)]]
- [[10 - Cloud Provider Specific Defenses (Azure)]]
