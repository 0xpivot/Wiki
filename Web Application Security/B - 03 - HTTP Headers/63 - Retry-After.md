---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.63 Retry-After — Rate Limit Bypass Timing"
---

# 03.63 — Retry-After

## What is it?

`Retry-After` tells the client how long to wait before retrying a request. It's sent with:
- `429 Too Many Requests` — rate limiting
- `503 Service Unavailable` — server overloaded/maintenance
- `301/302` redirects — temporary resource unavailability

From a VAPT perspective, it reveals rate limiting implementation and can be abused to understand the window for bypass attempts.

---

## Format

```
Retry-After: 120                            → wait 120 seconds
Retry-After: Mon, 10 Jun 2024 12:00:00 GMT  → wait until this time

RESPONSE CONTEXT:
  HTTP/1.1 429 Too Many Requests
  Retry-After: 60
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1717070400
```

---

## Attack: Understanding Rate Limit for Bypass

```
WHAT RETRY-AFTER REVEALS:
  "Retry-After: 60" with 429 → rate limit window is 60 seconds!
  
  ATTACK TIMING:
  - Know the window → know when to retry!
  - Automate: wait 60 seconds → 100 more requests → wait → repeat!
  - Each 60-second window = 100 attempts!
  
  BRUTE FORCE MATH:
  100 attempts/minute = 6000 attempts/hour = 144,000/day!
  For 6-digit PIN: only 1 million combinations → cracked in 7 days!
```

---

## Attack: Rate Limit Bypass Techniques

```
COMBINE WITH IP HEADER BYPASS:
  After hitting rate limit → rotate IP:
  X-Forwarded-For: 1.2.3.4  (request 1-100)
  X-Forwarded-For: 1.2.3.5  (request 101-200)
  Each IP gets its own rate limit!
  
  Effective if rate limiting is by IP (via header).

DISTRIBUTE ACROSS ACCOUNTS:
  If rate limit is per-account → use multiple accounts!
  Credential stuffing: different email per batch.

GRAPHQL BATCHING:
  GraphQL rate limits by HTTP request (not by query):
  1 HTTP request with 100 queries inside = 1 request counted!
  → 100x effective rate per request!
```

---

## Rate Limit Header Information Disclosure

```
X-RateLimit-Limit: 100      → max requests per window
X-RateLimit-Remaining: 45   → requests left in current window
X-RateLimit-Reset: 1717070400  → Unix timestamp when window resets

ATTACKER USES:
  → Know exactly when to send next batch!
  → Calculate optimal attack cadence
  → Know max requests per window for planning
  
LESS COMMON BUT SEEN:
  X-RateLimit-Policy: 100;w=60  → compact: 100 reqs per 60 sec window
```

---

## Testing Rate Limits

```bash
# Trigger 429 to see Retry-After:
for i in $(seq 1 200); do
  curl -X POST https://target.com/login \
    -d "user=admin&pass=wrong" -s -o /dev/null \
    -w "Request $i: %{http_code}\n"
done
# When you see 429 → note when it started → that's the limit!

# Check all rate limit headers:
curl -sI https://target.com/api/endpoint | grep -iE "ratelimit|retry-after|x-rate"

# Time-based bypass (wait for reset):
RESET=$(curl -sI https://target.com/api | grep -i "ratelimit-reset" | awk '{print $2}')
WAIT=$((RESET - $(date +%s)))
sleep $WAIT  # wait for window reset → new 100 requests!
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Rate limit by IP header | Rate limit by authenticated user; session-based |
| Small window easily bypassed | Implement exponential backoff (longer wait per failure) |
| Revealing window in Retry-After | Jitter the Retry-After value to obscure exact window |
| No global rate limit | Add both per-endpoint AND global rate limits |

---

## Related Notes
- [[02 - X-Forwarded-For]] — IP header for rate limit bypass
- [[Module 05 - Authentication Bypass]] — brute force and rate limit bypass
- [[Module 07 - API Security]] — API rate limiting
