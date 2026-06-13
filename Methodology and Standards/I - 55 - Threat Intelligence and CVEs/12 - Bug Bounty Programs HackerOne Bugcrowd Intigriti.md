---
tags: [threat-intel, cve, research, vapt]
difficulty: advanced
module: "55 - Threat Intelligence and CVEs"
topic: "55.12 Bug Bounty Programs"
---

# Bug Bounty Programs (BBPs)

## 1. Introduction to the Bug Bounty Ecosystem
A Bug Bounty Program (BBP) is a proactive security initiative where organizations incentivize independent security researchers (often called "hunters") to discover and report vulnerabilities in their software, applications, or infrastructure. In exchange for actionable, in-scope vulnerability reports, researchers receive financial rewards (bounties), swag, or reputation points.

BBPs have revolutionized offensive security testing. Unlike traditional penetration testing, which relies on a small team with a fixed timeframe and methodology, crowdsourced security leverages the diverse skill sets, continuous effort, and sheer scale of thousands of researchers worldwide. This continuous testing model aligns perfectly with Agile and CI/CD development lifecycles, where code changes are deployed daily.

## 2. Platform Nuances and Ecosystem Players

The ecosystem is dominated by several major platforms, each offering different features, target audiences, and operational models.

### HackerOne (H1)
- **Overview:** One of the largest and most prominent platforms. It hosts programs for tech giants, government entities (e.g., Hack the Pentagon), and vast open-source projects.
- **Reputation System:** Utilizes a complex "Signal" and "Impact" system. High signal means reports are generally valid; high impact means the bugs found are severe. Points dictate invitations to lucrative private programs.
- **Features:** Offers HackerOne Clear (background-checked researchers), HackerOne Pentest (structured compliance testing), and highly competitive live hacking events (LHEs) where top researchers gather physically to hack a target over a weekend.

### Bugcrowd
- **Overview:** A major competitor to HackerOne, known for its Crowdcontrol platform and diverse client base, including heavy presence in the automotive and healthcare sectors.
- **Reputation System:** Uses a tiering system based on points and accuracy. Researchers move up ranks, unlocking private invitations and specialized testing pools.
- **Features:** Strong focus on "Next Gen Pen Test" offerings, integrating traditional compliance reporting with crowdsourced hunting. They also utilize an intricate Vulnerability Rating Taxonomy (VRT) that standardizes severity across all their managed programs.

### Intigriti
- **Overview:** A rapidly growing European platform that has gained massive popularity for its strong community ties.
- **Reputation System:** Focuses strongly on community engagement, transparency, and fast triage times.
- **Features:** Known for stringent adherence to European data protection laws (GDPR) and unique challenges/CTFs that bypass traditional web testing, encouraging researchers to focus on deeply technical browser mechanics or logic flaws.

### YesWeHack and Synack
- **YesWeHack:** Another major European player, heavily focused on sovereignty, localized data compliance, and serving EU-based enterprises and government entities.
- **Synack:** Operates on a highly vetted, private model. Researchers (the Synack Red Team - SRT) must pass rigorous technical interviews, identity verification, and background checks. Synack guarantees a baseline of testing via its "Missions" system alongside traditional bug bounties.

## 3. The Triage Process and Economics

The core engine of any BBP is the triage process. Triagers act as intermediaries between the researcher and the organization's internal security team, filtering the signal from the noise.

```text
+-----------------------------------------------------------------------------------+
|                        BUG BOUNTY SUBMISSION & TRIAGE FLOW                        |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  +--------------+                                                                 |
|  |  Researcher  |                                                                 |
|  +------+-------+                                                                 |
|         | 1. Submit Report via Platform                                           |
|         v                                                                         |
|  +--------------+   2. Platform Triage                                            |
|  |  Platform    |---+ (Validate PoC, Scope, Duplicates, VRT/CVSS)                 |
|  |  Triager     |   |                                                             |
|  +------+-------+<--+                                                             |
|         | 3. Triaged & Forwarded                                                  |
|         v                                                                         |
|  +--------------+   4. Internal Validation                                        |
|  | Organization |---+ (Confirm Risk, Assess Business Impact, Prioritize)          |
|  |  Sec Team    |   |                                                             |
|  +------+-------+<--+                                                             |
|         | 5. Accepted & Reward Assigned                                           |
|         v                                                                         |
|  +--------------+                                                                 |
|  | Payout & Fix |--> Patch Deployed --> Re-testing Requested --> Resolved         |
|  +--------------+                                                                 |
|                                                                                   |
|  Edge Cases and Terminations:                                                     |
|  - N/A (Not Applicable): Feature, not a bug, or accepted business risk.           |
|  - OOS (Out of Scope): Valid bug, but on an asset not covered by the policy.      |
|  - Duplicate: Valid bug, but previously reported by another researcher.           |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

### The Triage Workflow
1. **Initial Review:** The platform's triager reviews the report for completeness, reproduces the issue using the provided PoC, and verifies that the asset is within scope.
2. **De-duplication:** The triager checks internal databases to ensure the vulnerability hasn't already been reported. If it has, the new report is marked as a duplicate (Dupe).
3. **Escalation:** Valid, unique reports are passed to the customer's security team.
4. **Validation and Bountying:** The customer confirms the business impact, assigns an internal Jira ticket, and assigns a bounty based on their payout matrix.

### Economics of Bug Bounties
Bug bounties operate on a highly competitive, winner-takes-all economic model. Only the *first* researcher to submit a valid bug gets paid. This drives a race to exploit newly discovered attack surfaces or recently published CVEs (1-days). Researchers must balance the time spent on deep, complex research (high reward, high risk of finding nothing) versus finding low-hanging fruit quickly (low reward, high risk of duplication).

## 4. Scope and Policy Details

The Program Policy is the foundational document of any BBP. It defines the rules of engagement and sets legal boundaries.

### In-Scope vs. Out-of-Scope (OOS)
- **In-Scope Assets:** Specific domains (e.g., `app.example.com`), wildcard domains (`*.example.com`), mobile apps (iOS/Android), or specific APIs that are eligible for bounties.
- **Out-of-Scope Assets:** Third-party services, staging environments, or recently acquired companies might be strictly OOS. Finding a critical RCE on an OOS asset typically results in no payout and a negative reputation hit.
- **OOS Vulnerability Types:** Most programs explicitly exclude certain attack classes to prevent disruption or focus resources on critical flaws, such as:
  - Denial of Service (DoS/DDoS)
  - Social Engineering / Phishing attacks against employees
  - Physical Security bypasses
  - Clickjacking on pages with no sensitive actions
  - Missing security headers without a demonstrable exploit path

### Safe Harbor
A robust BBP policy includes a Safe Harbor clause, guaranteeing that the organization will not pursue legal action against researchers who adhere to the policy guidelines, even if they accidentally cause minor disruption. This ensures legal protection and encourages good-faith hacking.

## 5. Reconnaissance for Bug Bounties

Because thousands of researchers examine the same main applications, success in bug bounties heavily relies on superior reconnaissance (recon) to find forgotten, unlinked, or legacy assets.

### Horizontal vs. Vertical Correlation
- **Horizontal Correlation:** Finding related domains owned by the same entity (e.g., discovering that `example-corp.com` also owns `example-cloud.net` via WHOIS data, ASN lookups, Favicon hashing, or reverse WHOIS).
- **Vertical Correlation:** Deep enumeration of subdomains within a specific domain. This involves brute-forcing, certificate transparency (CT) log analysis, permutation generation, and scraping search engines.

### Continuous Monitoring and Automation
Top hunters automate their recon. They run distributed infrastructure that continuously monitors target ASNs and domains for changes—new subdomains, newly open ports, or changes in HTTP responses. When a developer spins up a new staging server or deploys an unauthenticated internal dashboard, an automated alert notifies the hunter, giving them a head start before the rest of the community finds it.

## 6. Report Writing and CVSS Context

A poorly written report can lead to a rejected or downgraded bug. A high-quality report includes:
- **Clear Title:** Summarizing the vulnerability and the affected asset.
- **Vulnerability Description:** What the flaw is and the underlying mechanism.
- **Reproduction Steps:** Explicit, step-by-step instructions. If a custom script or specific HTTP request is required, it must be included.
- **Impact Analysis:** This is the most critical section. Researchers must demonstrate *business impact*. An XSS on a static page is low impact; an XSS that steals session cookies of an administrator and leads to account takeover is high impact.
- **CVSS Score:** Researchers should provide a Common Vulnerability Scoring System (CVSS) calculation. BBPs heavily utilize CVSS (v3.1 or v4.0) to standardize payouts. For example, a CVSS of 9.0-10.0 (Critical) corresponds to the highest bounty tier.

## 7. Handling the Psychology of Duplicates

Receiving a "Duplicate" status is the most frustrating aspect of bug bounties. It means the researcher spent hours finding a valid, high-impact bug, only to learn someone else found it days or hours earlier. Managing the psychological toll of continuous duplicates—often called "hunter burnout"—is a significant challenge in the community. Mitigation strategies include focusing on private programs (smaller pool of researchers), focusing on deep logic flaws rather than automated scanner findings, or pivoting to entirely different target types (e.g., reverse engineering mobile apps instead of web testing).

## 8. Advanced Strategies: Chaining and Escalation
The most lucrative bounties are awarded for chained exploits. A single vulnerability in isolation might be low impact, but combined with another, it can be devastating. For example, a simple Open Redirect (often OOS or low payout) might be chained with an SSRF (Server-Side Request Forgery) to bypass internal network protections, escalating a $100 bug into a $10,000 Critical finding. Researchers must always ask: "What else can I do with this access?"

## 9. Chaining Opportunities
- Reports from [[11 - Vulnerability Disclosure Process]] often overlap with BBPs, as organizations may transition a standard VDP into a paid BBP to attract more talent.
- BBPs are the primary hunting ground for identifying [[15 - IOCs Indicators of Compromise]] when researchers accidentally uncover active threat actor campaigns or backdoors during their testing.
- Successful BBPs require rapid response to newly published CVEs, tying deeply into the concepts of [[14 - 1-Day vs 0-Day Research Concepts]]. Exploiting N-days quickly across wide scopes is a primary revenue driver for many hunters.

## 10. Related Notes
- [[11 - Vulnerability Disclosure Process]]
- [[13 - Patch Diffing Finding Vulns]]
- [[14 - 1-Day vs 0-Day Research Concepts]]
- [[15 - IOCs Indicators of Compromise]]
- [[04 - Web Application Firewalls (WAF) Bypass]]
