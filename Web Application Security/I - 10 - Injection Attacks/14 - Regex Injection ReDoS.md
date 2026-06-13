---
tags: [vapt, injection, advanced]
difficulty: advanced
module: "10 - Injection Attacks"
topic: "10.14 Regex Injection (ReDoS)"
---

# 10.14 — Regex Injection (ReDoS)

## What is ReDoS?

ReDoS (Regular Expression Denial of Service) exploits the "catastrophic backtracking" behavior of certain regex patterns when matched against specially crafted input. The server's regex engine spends exponential time processing the input → server thread hangs → DoS.

```
HOW BACKTRACKING WORKS:
  Regex: (a+)+$
  Input: aaaaaaaaaaaaaaaaaab
  
  Engine tries all combinations of how to group the a's:
  - (a)(a)(a)...(a)b → no match, backtrack
  - (aa)(a)(a)...(a)b → no match, backtrack
  - ... exponential combinations!
  
  For 20 a's + 'b': ~1 million backtrack steps!
  For 30 a's + 'b': ~1 billion steps → HANG!
```

---

## Vulnerable Regex Patterns (Evil Regex)

```
PATTERNS THAT CAUSE CATASTROPHIC BACKTRACKING:
  (a+)+           → repeated groups with overlapping matches
  ([a-zA-Z]+)*    → same structure
  (a|aa)+         → alternation with overlap
  (a*)+$          → kleene star inside kleene star
  
REAL-WORLD VULNERABLE EXAMPLES:
  Email validation: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
    → Attack input: aaaaaaaaaa@aaaaaaaaaa! (ends with non-matching char)
    
  URL validation: ^(https?://)[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(/.*)?$
    → Attack input: https://aaaaaaaaaaaaaaaaaaaaaaaaaaaa! 
  
  Any regex with nested quantifiers: (X+)+, (X|XX)+
```

---

## ReDoS Attack Payloads

```
FIND THE VULNERABLE PATTERN FIRST:
  If app validates email:
    Vulnerable pattern: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
  
  ATTACK INPUT:
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa@example.com! (many a's + invalid at end)
    
  HOW TO CRAFT:
    1. Fill the "main matching part" with many valid chars
    2. Append an INVALID character at the end (so it fails to match)
    3. Engine must backtrack through all combinations!
    
  EXAMPLES:
    Email field: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa@a.b!
    Username: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!
    Password field (complex validator): Aaaa1111aaaaaaaaaaaaaaaaaaa!
```

---

## Detecting ReDoS Vulnerability

```bash
# STEP 1: IDENTIFY INPUT FIELDS WITH VALIDATION:
# Any field with server-side validation (email, phone, username, URL)

# STEP 2: MEASURE NORMAL RESPONSE TIME:
curl -w "%{time_total}" "https://target.com/register" -d "email=test@test.com"
# e.g., 0.1 seconds

# STEP 3: INJECT REDOS PAYLOAD:
curl -w "%{time_total}" "https://target.com/register" \
  -d "email=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa@aaaaaaaaaaaaaaaa.com!"
# If response takes 5+ seconds → ReDoS!

# STEP 4: INCREMENTAL TEST:
# 10 a's → fast, 20 a's → medium, 30 a's → very slow = exponential = ReDoS!

# TOOL - VULN-REGEX-DETECTOR:
# Analyzes regex patterns for vulnerability:
# https://github.com/nicowillis/vuln-regex-detector
node --timeout 10000 vulnRegexDetector.js "(a+)+" 
```

---

## Impact

```
REDOS IMPACT:
  Single-threaded apps: One ReDoS request = app hangs!
  Multi-threaded: Multiple requests = all threads hang = DoS!
  
  Node.js: SINGLE-THREADED! One ReDoS → entire Node.js app hangs!
  Python (single-threaded event loop frameworks like FastAPI): Same!
  
  Java/multi-threaded: Multiple requests needed but still achievable!

SEVERITY:
  Medium (affects availability only, no data leak)
  High (if app is critical infrastructure)
```

---

## Testing Regex Injection (Separate Concept)

```
REGEX INJECTION (different from ReDoS):
  When user input is used AS PART OF A REGEX pattern:
  
  Vulnerable code:
  pattern = "/^" + user_input + "$/";
  if (field.match(pattern)) { ... }
  
  INJECT:
  user_input = .* (matches everything!)
  user_input = )()|( (breaks regex)
  user_input = foo|bar (add alternatives)
  
  EFFECT:
  Bypass pattern matching
  Cause ReDoS via user-controlled pattern
  Crash the app (invalid regex syntax)
```

---

## Defense

```
PROTECTION AGAINST REDOS:
  1. Use safe regex patterns:
     Avoid nested quantifiers: (a+)+, (a*)*, (a|aa)+
     Use atomic groups (not supported in all engines): (?>a+)
     Use possessive quantifiers: a++ (not in JavaScript!)
  
  2. Set regex timeout:
     Python 3.11+: re.timeout parameter
     Java: custom regex executor with timeout
     Node.js: use 're2' package (linear-time regex engine):
       const RE2 = require('re2');
       const regex = new RE2(/evil-pattern/);
  
  3. Input length limits:
     Limit the length of input before applying regex
     Max length = 255 chars → limits backtracking depth!
  
  4. Use trusted regex libraries:
     re2 (Google's safe regex) — linear time, no backtracking
     Hyperscan (Intel) — SIMD-accelerated, safe
  
  5. Validate regex patterns themselves if user-controlled:
     Use SAFE=yes flag or equivalent

DETECT VULNERABLE PATTERNS:
  vuln-regex-detector (GitHub) — checks your regex for vulnerability
  regexploit (GitHub) — generates ReDoS PoC strings
```

---

## Related Notes
- [[Module 15 - Business Logic]] — DoS via application logic
- [[08 - Log Injection]] — input validation relevance
