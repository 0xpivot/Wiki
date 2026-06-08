---
tags: [vapt, methodology, beginner]
difficulty: beginner
module: "04 - VAPT Methodology"
topic: "04.02 Rules of Engagement (RoE) and Scope"
---

# 04.02 — Rules of Engagement (RoE) and Scope

## What is it?

Rules of Engagement (RoE) are the formal agreement between the penetration tester and the client that defines WHAT can be tested, HOW it can be tested, WHEN, and any restrictions. Without a signed RoE, any security testing is illegal — even if you own the company.

---

## Why RoE Matters

```
WITHOUT RoE:
  You test target.com without permission.
  Even if you mean well → Computer Fraud and Abuse Act (CFAA) violation!
  Potential arrest, prosecution, civil lawsuit.
  
  REAL CASES:
  - Aaron Swartz (MIT network) — faced federal charges
  - Marcus Hutchins (WannaCry hero) — arrested despite saving internet
  - Pen testers arrested mid-engagement without proper paperwork!

WITH SIGNED RoE:
  Legal protection for the tester.
  Clear expectations for both parties.
  Proof that testing was authorized.
```

---

## Key Elements of a Rules of Engagement Document

```
1. SCOPE:
   - In-scope targets: 192.168.1.0/24, target.com, *.target.com
   - Out-of-scope: payment.target.com, prod-db.target.com
   - Specific applications: [Web app URL], [API endpoint]
   
2. TESTING WINDOW:
   - Allowed hours: Mon-Fri 09:00-17:00 UTC
   - Excluded dates: holidays, deployment windows
   
3. PERMITTED TECHNIQUES:
   - Network scanning: Yes/No
   - Exploitation: Yes (limited) / No
   - DoS testing: NEVER (unless explicit)
   - Social engineering: Out of scope
   - Physical access: Out of scope
   
4. EMERGENCY CONTACTS:
   - Client emergency contact: John Smith, +1-555-xxx-xxxx
   - "Stop testing immediately if called"
   - Escalation procedure if critical vuln found
   
5. DATA HANDLING:
   - What to do with captured data
   - Data destruction at end of engagement
   - NDA coverage
   
6. TOOLS ALLOWED:
   - Burp Suite, Nmap, SQLMap: Yes
   - Metasploit: Yes (limited)
   - Custom exploits: With prior approval
```

---

## Scope Definitions

```
IN-SCOPE vs OUT-OF-SCOPE:

IN SCOPE:
  ✓ https://app.target.com  (primary target)
  ✓ https://api.target.com  (API target)
  ✓ 10.10.10.0/24          (internal network segment)
  ✓ All subdomains of target.com (if wildcard scope)

OUT OF SCOPE:
  ✗ https://payment.target.com  (PCI DSS compliant — separate assessment)
  ✗ Third-party services (Stripe, Salesforce hosted on their infra)
  ✗ IP addresses not belonging to target
  ✗ Other customers of a multi-tenant app

IMPORTANT: If you find a vulnerability in out-of-scope system,
           STOP, document it, REPORT to client immediately.
           DO NOT exploit — even if you could!
```

---

## Bug Bounty Programs (Self-Service RoE)

```
Bug bounty programs are publicly published RoE:

EXAMPLE: HackerOne program for target.com
  Scope:
  ✓ *.target.com
  ✓ API: api.target.com
  
  Out of scope:
  ✗ store.target.com (different team, not covered)
  ✗ Automated scanning (rate limiting, DoS concerns)
  ✗ Physical attacks
  
  Rewards:
  Critical: $10,000 - $50,000
  High: $2,500 - $10,000
  Medium: $500 - $2,500
  Low: $100 - $500

READ THE PROGRAM POLICY CAREFULLY before testing anything!
Testing out-of-scope = no reward + potential legal action.
```

---

## Sample Scope Verification

```bash
# Verify target IP belongs to client (confirm before testing!):
whois target.com | grep -i "registrant\|admin\|tech"

# Verify IP range belongs to target:
whois 192.168.1.1  # Get organization name
# Should match client's organization!

# Check if third-party hosting (Cloudflare, AWS, etc.):
nslookup target.com
# If IP belongs to Cloudflare → you're testing Cloudflare too! 
# Need Cloudflare testing permission separately!

# DNS: who owns the domain:
dig +short target.com
host target.com
```

---

## What To Do When You Find Critical Vulnerability

```
PROCESS:
1. STOP active exploitation immediately
2. Document what you found (screenshots, logs)
3. Call emergency contact NOW (don't wait for report)
4. Describe: what was found, what data could be exposed
5. Ask: continue testing or pause?
6. Note time and conversation details
7. Include in final report with "immediately reported" note

NEVER:
- Access data you don't need to prove vulnerability
- Keep a copy of accessed data
- Leverage vuln for personal gain
- Broadcast on social media before patched
```

---

## Related Notes
- [[01 - VAPT vs Pentest vs Red Team]] — scope of different engagements
- [[12 - Legal and Ethical Considerations]] — legal framework for testing
- [[08 - Reporting Phase]] — documenting findings
