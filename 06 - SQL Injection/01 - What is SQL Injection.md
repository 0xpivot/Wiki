---
tags: [vapt, sqli, beginner]
difficulty: beginner
module: "06 - SQL Injection"
topic: "06.01 What is SQL Injection?"
portswigger_labs: "SQL injection"
---

# 06.01 — What is SQL Injection?

## The Core Concept

SQL Injection (SQLi) is a vulnerability that occurs when user-supplied input is inserted directly into a SQL query without sanitization. The attacker's input is interpreted as SQL code instead of data — allowing them to manipulate the query's logic.

```
VULNERABLE CODE (PHP):
  $id = $_GET['id'];                                     // user input
  $query = "SELECT * FROM users WHERE id = " . $id;     // directly concatenated!
  $result = mysqli_query($conn, $query);

LEGITIMATE REQUEST:
  GET /user?id=1
  SQL: SELECT * FROM users WHERE id = 1
  → Returns user with id=1 ✓

INJECTED REQUEST:
  GET /user?id=1 OR 1=1--
  SQL: SELECT * FROM users WHERE id = 1 OR 1=1--
                                          ↑        ↑
                              always true   comment (ignores the rest)
  → Returns ALL users! ✗
```

---

## Why SQL Injection Exists

```
ROOT CAUSE: Mixing code and data

SECURE APPROACH (parameterized query):
  $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
  $stmt->execute([$id]);
  // User input treated as DATA — never interpreted as SQL!
  
VULNERABLE APPROACH (string concatenation):
  $query = "SELECT * FROM users WHERE id = " . $id;
  // User input becomes PART OF THE QUERY — interpreted as SQL!

THINK OF IT LIKE:
  Imagine a waiter writing your order on a note.
  
  SAFE: "Table 5 wants: [STEAK]"
         → steak is data, never changes the order format
  
  UNSAFE: "Table 5 wants: " + customer_input
         If customer writes: "anything, oh also give me all other tables' orders"
         → now it reads the order form differently!
```

---

## What Can an Attacker Do?

```
IMPACT (roughly in order of severity):

1. AUTHENTICATION BYPASS
   Login form: ' OR 1=1--
   SQL: SELECT * FROM users WHERE username='' OR 1=1--' AND password='x'
   → Logs in as first user (often admin!)

2. DATA EXTRACTION (most common)
   Dump entire database: usernames, passwords (hashed), PII
   Credit cards, SSNs, emails, private messages

3. DATA MODIFICATION
   Update records: change admin password, add admin user
   Delete records: destroy data

4. FILE READ/WRITE (MySQL with privileges)
   Read /etc/passwd, config files
   Write webshell → RCE!

5. REMOTE CODE EXECUTION
   MSSQL xp_cmdshell: execute OS commands!
   MySQL INTO OUTFILE: write PHP webshell

6. LATERAL MOVEMENT
   DB credentials → pivot to other internal systems
   DB links → access other databases
```

---

## SQL Injection in Context

```
WHERE INJECTION OCCURS:
  ✓ URL parameters:  /search?q=INPUT
  ✓ POST body:       username=INPUT&password=INPUT
  ✓ HTTP headers:    User-Agent: INPUT, Cookie: session=INPUT
  ✓ JSON/XML body:   {"id": INPUT}
  ✓ Path segment:    /user/INPUT/profile
  ✓ Search boxes
  ✓ Login forms
  ✓ Registration forms
  ✓ Filter/sort dropdowns
  ✓ Any user-controlled data that reaches a SQL query!
```

---

## Basic Injection Characters

```
CHARACTERS THAT BREAK SQL SYNTAX:
  '     → single quote (most common!) — closes string context
  "     → double quote — closes string context
  ;     → statement terminator (stacked queries)
  --    → MySQL comment (ignores rest of query)
  #     → MySQL comment (URL-encode as %23)
  /**/  → block comment
  )     → closes brackets
  
DETECTION STRATEGY:
  1. Send ' → look for database error!
  2. Send '' (two quotes) → error goes away? → injection confirmed!
  3. Send ' OR '1'='1 → behavior change? → confirmed!
  
TELLTALE ERROR MESSAGES:
  MySQL:      "You have an error in your SQL syntax..."
  PostgreSQL: "ERROR: unterminated quoted string at or near..."
  MSSQL:      "Unclosed quotation mark after the character string..."
  Oracle:     "ORA-01756: quoted string not properly terminated"
  SQLite:     "near 'x': syntax error"
```

---

## Simple Detection Examples

```bash
# STEP 1: Normal request (baseline):
curl "https://target.com/item?id=1"
# Returns: {"id":1, "name":"Widget", "price":9.99}

# STEP 2: Add quote to break SQL:
curl "https://target.com/item?id=1'"
# Returns: 500 Internal Server Error — You have an error in your SQL syntax!
# → SQLi confirmed!

# STEP 3: Repair the syntax:
curl "https://target.com/item?id=1'--"
# OR:
curl "https://target.com/item?id=1 AND 1=1--"
# Returns: same as step 1 → we're injecting and it works!

# STEP 4: Boolean test:
curl "https://target.com/item?id=1 AND 1=2--"
# Returns: empty result / different response → BLIND SQLi confirmed!
```

---

## SQL Injection Types Overview

```
ERROR-BASED:
  Error messages contain database info → extract data from errors
  Most visible, easiest to exploit
  
UNION-BASED:
  Use UNION SELECT to append our own SELECT query
  Output appears directly in the page
  
BOOLEAN-BASED BLIND:
  No output/errors visible
  Ask YES/NO questions via condition evaluation
  e.g.: "Is the first letter of admin's password 'a'?"
  
TIME-BASED BLIND:
  No output, no errors
  Infer data from response delay (SLEEP() or WAITFOR DELAY)
  
OUT-OF-BAND:
  DNS/HTTP request from database to attacker's server
  Works when no response channel exists
  
SECOND-ORDER (STORED):
  Input stored in DB, injected when later retrieved and used in another query
  Harder to find, often missed by automated scanners
```

---

## Related Notes
- [[02 - How Databases Work]] — SQL fundamentals
- [[03 - Error-Based SQLi]] — extracting data from errors
- [[04 - Union-Based SQLi]] — UNION SELECT exploitation
- [[21 - sqlmap Full Usage Guide]] — automated SQLi tool
- [[22 - Manual SQLi Testing Methodology]] — step-by-step manual approach
