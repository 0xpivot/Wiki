---
tags: [vapt, methodology, beginner]
difficulty: beginner
module: "04 - VAPT Methodology"
topic: "04.09 Black Box vs Grey Box vs White Box"
---

# 04.09 — Black Box vs Grey Box vs White Box

## What is it?

These terms describe how much information the tester is given about the target before starting. The "box" refers to the target system — how transparent it is to the tester. Each approach has different strengths, limitations, and use cases.

---

## Comparison

```
┌───────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
│               │ Black Box            │ Grey Box             │ White Box            │
├───────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ Information   │ None                 │ Partial              │ Full                 │
│ given         │ (URL/IP only)        │ (credentials, docs)  │ (source, design)     │
├───────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ Simulates     │ External attacker    │ Insider threat /     │ Internal audit /     │
│               │ with no knowledge   │ compromised user     │ developer review     │
├───────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ Time needed   │ Most (recon needed)  │ Medium               │ Least (skip recon)   │
├───────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ Coverage      │ Lowest               │ Medium               │ Highest              │
├───────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ Real-world    │ Most realistic       │ Good balance         │ Least realistic      │
│ accuracy      │ but misses hidden    │                      │ (attacker rarely has │
│               │ functionality        │                      │ source code)         │
├───────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ Cost          │ Highest              │ Medium               │ Lowest (per hour)    │
│               │ (time = money)       │                      │                      │
└───────────────┴──────────────────────┴──────────────────────┴──────────────────────┘
```

---

## Black Box Testing

```
WHAT YOU GET: Just the URL or IP address.
              "Test our application at app.target.com"
              
WHAT YOU DO:
  Phase 1: Full recon (OSINT, subdomain enum, tech fingerprint)
  Phase 2: Scan everything → map full attack surface
  Phase 3: Test systematically
  
ADVANTAGES:
  ✓ Simulates real external attacker
  ✓ Tests security from attacker's perspective
  ✓ Identifies what's discoverable from outside
  
DISADVANTAGES:
  ✗ Might miss functionality hidden behind auth
  ✗ More time spent on recon (which might be known info to client)
  ✗ More expensive (time = money)
  ✗ Might miss internal logic flaws

BEST FOR:
  - External-facing web apps
  - When testing perimeter security
  - Compliance testing (simulating external attacker)
```

---

## Grey Box Testing

```
WHAT YOU GET: 
  - User credentials (standard account + maybe admin account)
  - API documentation (Swagger, Postman collection)
  - Network topology overview
  - Sometimes: tech stack info, but not source code
  
WHAT YOU DO:
  Skip external recon → jump straight to authenticated testing
  Map all functionality with access to credentials
  Test authorization (can user A access user B's data?)
  
ADVANTAGES:
  ✓ More realistic than white box (still missing some context)
  ✓ Better coverage than black box (authenticated testing)
  ✓ More time-efficient
  ✓ Tests both authenticated and unauthenticated attack surface
  
DISADVANTAGES:
  ✗ Still doesn't catch code-level vulnerabilities easily
  ✗ May miss issues only visible in source code

BEST FOR:
  - Most web application VAPT engagements (most common!)
  - When client wants both external and authenticated testing
  - Bug bounty programs (you have account, not source)
```

---

## White Box Testing

```
WHAT YOU GET:
  - Complete source code
  - Architecture documentation
  - Database schema
  - Network diagrams
  - Admin credentials
  - All API documentation
  - Infrastructure configs
  
WHAT YOU DO:
  Code review + dynamic testing
  Look for logic flaws in source code
  Map attack surface from inside-out
  
ADVANTAGES:
  ✓ Highest coverage possible
  ✓ Can find vulnerabilities that would take months black box
  ✓ Can identify vulnerabilities that aren't externally reachable
  ✓ Best for finding business logic flaws
  
DISADVANTAGES:
  ✗ Not realistic (attackers rarely have source code)
  ✗ Might create false sense of security (what about what's NOT in scope?)
  ✗ Requires tester with code review skills

BEST FOR:
  - Code review engagements
  - Pre-launch security reviews
  - High-security applications (banking, healthcare)
  - When budget allows for thorough review
```

---

## Hybrid Approach (Most Common in Practice)

```
TYPICAL ENTERPRISE PENTEST:

Phase 1 (Black Box): 
  External attack simulation
  What can attacker discover without any access?
  
Phase 2 (Grey Box):
  Authenticated testing with standard user account
  How far can a regular employee/user go?
  
Phase 3 (Grey Box + Partial White):
  Admin account testing
  API documentation review
  
RESULT: Most comprehensive coverage within time/budget constraints!
```

---

## Bug Bounty = Almost Always Black Box

```
BUG BOUNTY PROGRAMS:
  You get: program scope, maybe a test account
  You don't get: source code, architecture docs
  
  → Effectively grey box (test account) or black box (no account)
  
  This is why bug hunters focus on:
  - Passive recon (crt.sh, Shodan, GitHub)
  - JavaScript analysis (endpoints, API keys in client-side code!)
  - Endpoint discovery (ffuf, arjun)
  - Behavioral analysis (how does the app respond to inputs?)
```

---

## Related Notes
- [[01 - VAPT vs Pentest vs Red Team]] — engagement types
- [[10 - Bug Bounty vs Pentest]] — bug bounty specifics
- [[02 - Rules of Engagement]] — what info clients provide
