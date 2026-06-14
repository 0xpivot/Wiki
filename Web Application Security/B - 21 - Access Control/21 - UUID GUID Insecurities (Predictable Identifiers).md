---
tags: [vapt, access-control, idor, uuid, predictable-id, intermediate]
difficulty: intermediate
module: "21 - Access Control"
topic: "21.21 UUID/GUID Insecurities (Predictable Identifiers)"
---

# 21.21 — UUID/GUID Insecurities (Predictable Identifiers)

## What is it?
A **UUID** (Universally Unique Identifier, a.k.a. GUID) is a 128-bit value written as 32 hex digits in five groups:
```text
12345678 - abcd - 1a56 - a539 - 103755193864
xxxxxxxx - xxxx - Mxxx - Nxxx - xxxxxxxxxxxx
                   |      |
                   |      +-- N position = variant
                   +--------- M position = version
```
Developers reach for UUIDs assuming they are "random and unguessable," so they often use them as **access-control tokens** — password-reset links, object IDs, invite codes — *without an authorization check*. The danger: **not all UUID versions are random.** If the version is predictable, the "unguessable token" becomes guessable, turning into an IDOR/account-takeover primitive.

Think of it like a hotel that gives every guest a room key with a "random" number — but actually the numbers are just the check-in time. Watch two guests check in and you can predict everyone else's key.

## UUID versions — which are safe?
| Version | How it's generated | Predictable? |
|---|---|---|
| **v1** | timestamp + clock sequence + node **MAC address** | **YES** — time-based, leaks MAC |
| v2 | like v1 + local domain (rare) | YES |
| **v3** | MD5 hash of namespace + name | YES if inputs known |
| **v4** | (almost) fully random | **NO** (safe if good RNG) |
| **v5** | SHA-1 hash of namespace + name | YES if inputs known |

**Rule of thumb:** only **v4** is safe as a secret. v1/v2 leak time + MAC and are sequential; v3/v5 are deterministic from their inputs.

> Identify the version by the **M** nibble (13th hex digit). `...-1xxx-...` = v1, `...-4xxx-...` = v4.

## Sandwich Attack (exploiting UUID v1)
The flagship attack: abuse the **time-ordered** nature of UUID v1 to brute-force a victim's token by bracketing it between two attacker-generated tokens.

**Scenario:** app issues UUID **v1** password-reset links.

1. **Setup** — attacker controls `attacker1@acme.com` and `attacker2@acme.com`; target is `victim@acme.com`.
2. **Execution (do these back-to-back, fast):**
   - Trigger reset for `attacker1` → receive UUID `99874128-7592-11e9-8201-bb2f15014a14`.
   - Immediately trigger reset for `victim`.
   - Immediately trigger reset for `attacker2` → receive UUID `998796b4-7592-11e9-8201-bb2f15014a14`.
3. **Analysis** — the victim's UUID was generated *between* the two attacker UUIDs in time, so its value falls **between** `99874128...` and `998796b4...`.
4. **Brute force** — generate every UUID v1 in that narrow range and try each reset link:
   ```text
   https://www.acme.com/reset/<generated-UUID>
   ```
5. **Takeover** — when one works, reset the victim's password.

The attack succeeds when (a) tokens are UUID v1 and (b) there's no rate-limiting / one-time-use / expiry on the reset endpoint.

## ASCII Diagram
```text
================================================================================
                       SANDWICH ATTACK ON UUID v1
================================================================================

  time --->

  [attacker1 reset]      [VICTIM reset]        [attacker2 reset]
  99874128-7592-...       ??? (unknown)         998796b4-7592-...
        |                      |                       |
        +----- known low ------+------ known high ------+
                               |
                   victim UUID is somewhere IN HERE
                               |
                               v
            brute force every UUID v1 in [low .. high]
            try each at /reset/<uuid>  => account takeover
================================================================================
```

## Hands-on testing
1. **Capture a UUID** the app treats as a secret (reset link, object ID, invite).
2. **Check the version** — look at the 13th hex digit (the M position). `1` = v1 (vulnerable), `4` = v4 (likely safe).
3. If **v1**: generate two of your own tokens with a fast request burst around a third action and confirm they're time-ordered (monotonically increasing).
4. Run the **Sandwich Attack** to bracket and brute force.
5. Even for **v4**: test for weak RNG (repeating bytes, sequential values) and for **IDOR** — a perfectly random UUID is still broken if the endpoint never checks *who* owns the object.

## Tools
- **`sandwich`** — automates the bracket-and-bruteforce flow.
- **Burp "UUID Detector"** extension — flags UUIDs in traffic and identifies their version.

## Defense
- **Use UUID v4** (or a CSPRNG-backed random token) for anything secret. Never use v1/v2/v3/v5 as an unguessable identifier.
- **Always pair the ID with an authorization check** — confirm the requesting user owns the object. A random ID is *not* an access-control mechanism on its own (that's the IDOR lesson).
- For reset tokens: make them **single-use**, **short-lived**, **rate-limited**, and tied to the account server-side.

## Related
- [[18 - Account Takeover via IDOR on Password Reset]] — the IDOR sibling of this attack
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — the real fix for both
