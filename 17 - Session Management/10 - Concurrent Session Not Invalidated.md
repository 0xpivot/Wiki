---
tags: [vapt, session-management, beginner]
difficulty: beginner
module: "17 - Session Management"
topic: "17.10 Concurrent Session Not Invalidated"
---

# 17.10 — Concurrent Session Not Invalidated

## What Is a Concurrent Session Attack?

```
SCENARIO:
  Attacker steals victim's session token
  Victim continues using the app (their cookie still works)
  Attacker also uses the stolen token simultaneously
  
  → Two people using the same session!
  → App should detect this and invalidate (but usually doesn't)
  
OTHER SCENARIOS:
  User logs in on multiple devices (laptop + phone + work PC)
  If app has no concurrent session limit:
  → Unlimited simultaneous sessions possible
  → After compromise, attacker's session persists alongside victim's
  → Victim never notices!
```

---

## Testing for Concurrent Sessions

```
TEST 1: MULTIPLE SIMULTANEOUS SESSIONS
  1. Login on Browser A → note session token A
  2. Login on Browser B → note session token B
  3. Both A and B should work if app allows concurrent sessions
  4. Does the app tell user "new login detected, other sessions terminated"?
  5. Can you see active sessions in account settings?

TEST 2: SESSION A STILL WORKS AFTER SESSION B CREATED
  1. Login → session A
  2. Login again (different tab/browser) → session B
  3. Use session A → still works?
     → If app terminates all old sessions on new login → session A fails!
     → If not → concurrent sessions allowed without notification

TEST 3: ACTIVE SESSION COUNT
  1. Login 5 times from "different devices" (same IP, different session IDs)
  2. Check account security page → does it show 5 active sessions?
  3. Each legitimate — but attack would add a 6th silently!

TEST 4: SESSION PERSISTENCE THROUGH PASSWORD CHANGE
  1. Login on Device A → session A (attacker's "device")
  2. Victim changes password → session B created on Device B
  3. Try session A → still works?
     → Should be invalidated! If not → attacker persists after password change!
```

---

## "Logout Everywhere" Feature Testing

```
TEST: SESSION REVOCATION
  1. Login on multiple "devices" (multiple sessions)
  2. On "Device 1": use "Log out all other devices" or "Logout everywhere" feature
  3. Try sessions from "Devices 2, 3, 4"
  → They should all be invalidated!
  → If any still work → revocation is incomplete!

TEST: CHANGE PASSWORD REVOKES ALL SESSIONS
  1. Login on Browser A → session A (simulate attacker session)
  2. Login on Browser B → session B (simulate victim's current session)
  3. In Browser B: change password
  4. In Browser A: try to access protected page
  → Session A should be invalidated! If not → compromised attacker session persists!

EXPECTED SECURE BEHAVIOR:
  Login → all previous sessions for this user TERMINATED
  OR: User explicitly sees list of sessions and can terminate any
  Password change → all sessions terminated
  Email change → all sessions terminated
```

---

## Implementation Approaches

```
APPROACH 1: SINGLE SESSION POLICY
  Allow only one active session per user
  Each new login → invalidate ALL previous sessions
  
  PROS: Simple, maximum security
  CONS: User logs in on phone → logged out of laptop!
  Suitable for: banking, high-security admin panels
  
APPROACH 2: SESSION LISTING + MANUAL REVOCATION
  Allow unlimited concurrent sessions
  Show user list: "Signed in on iPhone (2 hours ago), Laptop (yesterday)"
  User can revoke specific sessions
  Auto-revoke after X days of inactivity
  
  Suitable for: Gmail, GitHub model
  
APPROACH 3: INTELLIGENT ANOMALY DETECTION
  Allow concurrent sessions
  Detect suspicious patterns:
  - Two sessions from completely different countries simultaneously
  - Rapid switching between IPs
  - Unusual access patterns
  → Alert user, require re-auth

DATABASE MODEL:
  sessions table:
    id: unique session token (hashed)
    user_id: FK to users
    created_at: when session started
    last_active: updated on each request
    device_info: user agent, IP (for display)
    is_active: boolean
  
  On login: INSERT new session (optionally DELETE old ones)
  On logout: UPDATE is_active = false (or DELETE)
  "Logout all": UPDATE is_active = false WHERE user_id = ?
```

---

## Related Notes
- [[08 - Session Not Invalidated on Logout]] — basic session invalidation
- [[09 - Long-Lived Sessions]] — session lifetime
- [[15 - Defense Secure Session Configuration]] — full hardening
