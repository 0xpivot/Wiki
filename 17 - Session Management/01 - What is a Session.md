---
tags: [vapt, session-management, beginner]
difficulty: beginner
module: "17 - Session Management"
topic: "17.01 What is a Session?"
---

# 17.01 — What Is a Session?

## The Stateless Problem

```
HTTP IS STATELESS:
  Each request is independent — server forgets you between requests!
  
  Request 1: GET /login    → server has no idea who you are
  Request 2: POST /login   → you send username+password → server knows
  Request 3: GET /account  → server forgets! Who are you again??
  
THE SESSION SOLUTION:
  After authentication, server creates a SESSION:
  - Assigns a unique session ID (a token)
  - Stores the session ID + user data server-side
  - Sends the session ID to the browser (via cookie)
  - Browser sends session ID on every subsequent request
  - Server looks up session ID → finds your data → knows who you are!
```

---

## Session Flow

```
HOW IT WORKS:

1. USER LOGS IN:
   POST /login (username, password)
   Server verifies → creates session in database:
   sessions table: { id: "abc123xyz", user_id: 42, created_at: now }
   
2. SERVER SENDS SESSION ID IN COOKIE:
   HTTP/1.1 302 Found
   Set-Cookie: session_id=abc123xyz; HttpOnly; Secure; SameSite=Lax
   
3. BROWSER STORES COOKIE, SENDS ON EVERY REQUEST:
   GET /account HTTP/1.1
   Cookie: session_id=abc123xyz
   
4. SERVER LOOKS UP SESSION:
   SELECT user_id FROM sessions WHERE id = 'abc123xyz'
   → Returns user_id = 42
   → Loads user data for ID 42
   → Serves the account page for that user

5. LOGOUT:
   Server deletes session from database
   Browser clears the cookie
```

---

## Session ID Properties

```
A GOOD SESSION ID MUST BE:
  
  RANDOM:
    Must be generated using a cryptographically secure random number generator
    Attacker must NOT be able to guess or predict the next token
    Entropy: 128 bits minimum (32 hex characters)
    
  UNIQUE:
    No two users should have the same session ID
    
  UNPREDICTABLE:
    Sequential: session1, session2 → TERRIBLE!
    Timestamp: 1640000000 → TERRIBLE!
    Random: a3f8b2e1c9d4... → GOOD!
    
  LONG ENOUGH:
    4-digit token (10,000 combos) → brute forceable in seconds!
    128-bit random (2^128 combos) → brute force essentially impossible

GENERATION EXAMPLES:
  Python: import secrets; token = secrets.token_hex(32)  → 64-char hex
  PHP:    session_id() returns PHP's random session ID (auto-generated)
  Java:   new SecureRandom().nextBytes(32) + base64 encoding
  Node:   crypto.randomBytes(32).toString('hex')
```

---

## Where Session IDs Live

```
COOKIE (most common):
  Set-Cookie: session=TOKEN; HttpOnly; Secure; SameSite=Lax
  ✓ Automatic — browser sends with every request
  ✓ HttpOnly prevents JavaScript access (XSS protection)
  ✓ Secure ensures HTTPS-only
  
URL PARAMETER (bad):
  GET /account?session=TOKEN
  ✗ Token in URL → logs, history, Referer header → exposed!
  ✗ Someone bookmarks the URL → session persists
  
HIDDEN FORM FIELD (legacy):
  <input type="hidden" name="session" value="TOKEN">
  ✗ Same risks as URL parameter
  ✗ Lost on page refresh unless embedded in every form
  
CUSTOM HEADER (APIs):
  Authorization: Bearer JWT_TOKEN
  X-Session-Token: TOKEN
  ✓ Not automatic → must be set in JavaScript
  ✓ Not sent on cross-origin requests by default (CORS protection)
  ✗ Can't use HttpOnly → accessible to JavaScript → XSS risk
```

---

## Server-Side vs Client-Side Sessions

```
SERVER-SIDE SESSION:
  Session data stored on server (database, Redis, memory)
  Only session ID sent to client
  
  ADVANTAGES:
  ✓ Can revoke immediately (delete from DB → user is logged out)
  ✓ Client can't tamper with session data
  ✓ Can store large amounts of data
  
  DISADVANTAGES:
  ✗ Database lookup on every request (performance)
  ✗ Must share session store across multiple servers (distributed systems)
  
CLIENT-SIDE SESSION:
  All session data encoded in the token itself (JWT, signed cookie)
  Server validates signature but doesn't look up a database
  
  ADVANTAGES:
  ✓ Stateless → no database lookup → scalable!
  ✓ Easy in distributed/microservice architectures
  
  DISADVANTAGES:
  ✗ Can't revoke without a blocklist (defeats the purpose)
  ✗ Client has access to (and can see) the payload
  ✗ Token size grows with more data
  → See note 17.14 for JWT-specific attacks
```

---

## Related Notes
- [[02 - Session Token Entropy and Predictability]] — token randomness
- [[03 - Session Fixation]] — exploiting session creation
- [[11 - Cookie Flags Attack Scenarios]] — cookie security attributes
- [[14 - Client-Side Session Tokens JWT Signed Cookies]] — JWT sessions
- [[15 - Defense Secure Session Configuration]] — full defense
