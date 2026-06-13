---
tags: [vapt, methodology, beginner]
difficulty: beginner
module: "04 - VAPT Methodology"
topic: "04.01 VAPT vs Penetration Testing vs Red Team"
---

# 04.01 — VAPT vs Penetration Testing vs Red Team

## What is it?

Understanding the differences between VAPT, penetration testing, and red team engagements is essential before starting any security assessment. Each serves a different purpose, has different scope, and uses different techniques.

---

## Comparison

```
┌─────────────────┬─────────────────────────┬──────────────────────────┬────────────────────────┐
│                 │ VAPT                    │ Penetration Test         │ Red Team               │
├─────────────────┼─────────────────────────┼──────────────────────────┼────────────────────────┤
│ Goal            │ Find & assess all vulns │ Exploit specific vulns   │ Simulate real attacker │
│ Breadth         │ Wide (everything)       │ Medium (defined scope)   │ Narrow (specific goal) │
│ Depth           │ Shallow-Medium          │ Medium-Deep              │ Deep                   │
│ Time            │ Days-Weeks              │ Days-Weeks               │ Weeks-Months           │
│ Knowledge       │ Automated + manual      │ Manual + creative        │ Full adversary sim     │
│ Report          │ List of all vulns       │ Exploited paths + chains │ Attack narrative       │
│ Audience        │ Management, compliance  │ Security team, devs      │ CISO, Board            │
│ Typical Client  │ Compliance, SME         │ Pre-launch, large co     │ Enterprise, gov        │
└─────────────────┴─────────────────────────┴──────────────────────────┴────────────────────────┘
```

---

## VAPT (Vulnerability Assessment and Penetration Testing)

```
WHAT IT IS:
  Combination of two activities:
  1. Vulnerability Assessment: systematic discovery of all vulnerabilities
     (automated scanning + manual review)
  2. Penetration Testing: exploiting a subset of found vulnerabilities
     to prove impact
  
  GOAL: Give client a comprehensive list of vulnerabilities with severity ratings
        and proof-of-concept exploits for critical ones.
  
  ANALOGY: A building security inspector who checks all doors and windows
           AND tries to pick the lock on the most important ones.
  
  OUTCOME: Prioritized vulnerability list with severity (CVSS scores)
           and remediation recommendations.
```

---

## Penetration Testing

```
WHAT IT IS:
  Goal-oriented security assessment — find a specific path to a target:
    - "Can an external attacker reach the payment database?"
    - "Can a contractor employee escalate to domain admin?"
  
  FOCUS: Depth over breadth. Missing some vulnerabilities is acceptable
         if you prove the critical path is (or isn't) exploitable.
  
  ANALOGY: A burglar hired to check if they can steal the safe — 
           they don't care about the unlocked back window if the
           safe is what they're after.
  
  OUTCOME: Attack narrative showing the exploitation path taken,
           vulnerabilities used, and business impact.
```

---

## Red Team Exercise

```
WHAT IT IS:
  Simulates a real advanced persistent threat (APT) against an organization.
  The target (defenders/blue team) doesn't know the assessment is happening.
  
  GOALS:
    - Test detection capabilities (can blue team detect us?)
    - Test incident response (how do they react?)
    - Find attack paths that bypass all defenses
  
  TECHNIQUES:
    - Physical access (badge cloning, tailgating)
    - Phishing campaigns (spear phishing with custom lures)
    - Living off the land (using built-in tools, no malware)
    - C2 infrastructure (command and control)
  
  ANALOGY: Hiring actual robbers to test your bank's security 
           while your security guards don't know it's a test.
  
  OUTCOME: Detailed attack playbook, detection gaps, IR gaps.
```

---

## Which Applies in This Vault?

```
THIS VAULT COVERS:
  Web VAPT / Penetration Testing scope:
  ✓ Web application vulnerabilities (SQLi, XSS, SSRF, etc.)
  ✓ API security (REST, GraphQL, SOAP)
  ✓ Network infrastructure assessment
  ✓ Methodology from recon to report
  ✓ Tool usage (Burp Suite, Nmap, SQLMap, etc.)
  
  NOT COVERED (red team specific):
  ✗ Physical security
  ✗ Social engineering campaigns at scale
  ✗ C2 framework deployment and evasion
  ✗ Active Directory full exploitation
  (Though VAPT methodology here serves as foundation for all)
```

---

## Related Notes
- [[02 - Rules of Engagement]] — defining scope and permissions
- [[09 - Black Box vs Grey Box vs White Box]] — testing knowledge level
- [[10 - Bug Bounty vs Pentest]] — other engagement types
- [[12 - Legal and Ethical Considerations]] — authorization requirements
