---
tags: [vapt, methodology, legal, beginner]
difficulty: beginner
module: "04 - VAPT Methodology"
topic: "04.12 Legal and Ethical Considerations"
---

# 04.12 — Legal and Ethical Considerations

## What is it?

Security testing without authorization is illegal in most jurisdictions. Understanding the legal landscape protects you from prosecution and civil liability. Ethics in security work goes beyond legality — it's about responsible disclosure, minimizing harm, and maintaining the trust that makes the security community function.

---

## Key Laws by Region

```
UNITED STATES:
  Computer Fraud and Abuse Act (CFAA):
    "Unauthorized access to a computer" = criminal offense
    Penalties: 1-20 years prison depending on damage
    
    Key point: "Unauthorized" = no explicit permission
    Even accessing publicly available data without permission can violate CFAA!
    (This is controversial — overbroad law)
    
    Authorization = signed agreement, explicit permission, or bug bounty policy

EUROPEAN UNION:
  EU Directive on Attacks Against Information Systems (2013/40/EU)
  Budapest Convention on Cybercrime
  GDPR: Accessing personal data → privacy violation!
  
  Each EU country also has its own laws:
  UK: Computer Misuse Act 1990 (CMA) — unauthorized access = criminal
  Germany: StGB §202a — data espionage
  France: Code pénal 323 — unauthorized system access

INDIA:
  Information Technology Act 2000, Section 43:
    Unauthorized access = civil liability
  Section 66: Computer-related offenses = criminal
  
  Written authorization from system owner is essential!
```

---

## What Authorization Looks Like

```
MINIMUM REQUIRED:
  1. Written permission (email is enough for bug bounty)
  2. Scope clearly defined
  3. Signed by someone with authority to grant it
  
  For bug bounty:
    Program policy = authorization
    Printed page + logged-in account = your evidence
    Save the policy page! (Screenshot with date)
  
  For pentest:
    Signed contract + Rules of Engagement = authorization
    Keep physical/digital copy accessible during testing
    Store in secure location

EDGE CASES:
  "I own the company so I can test anything" — but hosting on AWS?
  → AWS requires separate notification for testing their infrastructure!
  → AWS Penetration Testing Policy: many services allowed, some require prior approval
  
  Testing through Cloudflare, Akamai, Fastly?
  → You may need to notify them separately
  → Their WAF = their infrastructure = different rules
  
  ALWAYS: Verify that every IP/domain in scope actually belongs to the target.
```

---

## Responsible Disclosure (Coordinated Vulnerability Disclosure)

```
RESPONSIBLE DISCLOSURE PROCESS:
  
  1. FIND vulnerability
  
  2. NOTIFY vendor/owner:
     - Email security@company.com or security@domain.com
     - Or use their bug bounty platform
     - Include: vulnerability details, proof of concept, impact assessment
     - Do NOT post publicly yet!
  
  3. WAIT for response:
     - Give them time to fix (typically 90 days is industry standard)
     - Google Project Zero: 90 days hard deadline
     - CERT/CC: 45 days
     - Negotiate if more time needed (complex fix)
  
  4. COLLABORATE on fix:
     - Answer questions
     - Verify fix works
     - Agree on disclosure timeline
  
  5. DISCLOSE publicly:
     - After fix is deployed
     - Or after 90 days (even if unpatched — to warn public!)
     - Give credit to company for fixing
     - CVE can be requested through MITRE

  WITHOUT DISCLOSURE PROCESS:
  ✗ Posting on Twitter immediately = irresponsible
  ✗ Selling to vulnerability brokers (without trying disclosure) = grey area/illegal
  ✗ Exploiting for personal gain = definitely illegal
```

---

## Ethical Principles

```
1. MINIMIZE HARM:
   Only do what's necessary to prove the vulnerability.
   Don't dump the entire database when extracting one row proves SQLi.
   Don't access private user data when you can prove access with your own.
   
2. DO NOT ACCESS WHAT YOU DON'T NEED:
   Proving SSRF doesn't require reading private files.
   Proving XSS doesn't require stealing other users' cookies.
   Document impact theoretically when possible.

3. PROTECT DATA YOU ENCOUNTER:
   If you accidentally access real user data:
   - Stop immediately
   - Don't save or copy it
   - Report to client
   - Delete any cached copies
   
4. REPORT PROMPTLY:
   Critical vulnerabilities → immediate notification
   Don't wait until final report delivery for critical findings
   
5. DON'T DAMAGE SYSTEMS:
   Never deploy ransomware or destructive payloads to prove impact
   Never DoS target servers (even if technically possible)
   Always clean up: remove shells, accounts, files after testing

6. CONFIDENTIALITY:
   NDA/confidentiality agreement is standard
   Don't discuss client findings publicly without permission
   Even bug bounty disclosures require vendor approval
```

---

## Data Handling Rules

```
DURING ENGAGEMENT:
  - Collect only what's necessary for the engagement
  - Store in encrypted form (encrypted drive, password-manager)
  - Don't store on unencrypted devices
  - Don't sync to personal cloud storage

SCREENSHOTS AND EVIDENCE:
  - Blur or crop out PII (names, emails, SSNs) in screenshots
  - Exception: if PII exposure IS the finding (show one example, blur others)
  - Password hashes: show existence but don't actually crack in report

AFTER ENGAGEMENT:
  - Securely delete all captured data per RoE
  - Report confirms data destruction
  - Retain only the final report (agreed with client)
```

---

## Safe Harbor Clauses

```
WHAT IS SAFE HARBOR?
  Some bug bounty programs include "safe harbor" language:
  
  "We won't pursue legal action against researchers who test in good faith
  and follow our responsible disclosure policy."
  
  IMPORTANT: Not all programs have this!
  Some companies have sued researchers despite finding real vulnerabilities!
  
  BEFORE TESTING: Read the policy carefully.
  Look for: "we will not pursue legal action" or "good faith" language.
  If absent → be extra careful or ask for written confirmation.
  
  Best practice: Email security team, confirm testing is permitted,
  keep that email as evidence of implicit authorization.
```

---

## Quick Legal Checklist

```
BEFORE STARTING:
  [ ] Do I have written authorization? (contract, RoE, or bug bounty policy)
  [ ] Is the target in scope?
  [ ] Do I know who to contact in an emergency?
  [ ] Have I verified target IP/domain belongs to client?
  [ ] Am I aware of local laws governing this testing?
  
DURING TESTING:
  [ ] Am I staying in scope?
  [ ] Am I minimizing impact/access?
  [ ] Am I documenting authorization evidence?
  [ ] If I find critical vuln → notifying client immediately?
  
AFTER TESTING:
  [ ] Have I cleaned up all artifacts?
  [ ] Have I deleted/secured captured data?
  [ ] Have I followed responsible disclosure?
```

---

## Related Notes
- [[01 - VAPT vs Pentest vs Red Team]] — engagement context
- [[02 - Rules of Engagement]] — authorization documents
- [[08 - Reporting Phase]] — disclosure in reports
