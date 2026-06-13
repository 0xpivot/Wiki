---
tags: [vapt, ssrf, advanced]
difficulty: advanced
module: "13 - SSRF"
topic: "13.15 SSRF — DNS Rebinding"
---

# 13.15 — SSRF DNS Rebinding

## What Is DNS Rebinding?

```
THE PROBLEM TO SOLVE:
  Server validates URL → "Is the IP allowed?"
  
  1. URL: http://evil.com/
  2. DNS resolve: evil.com → 1.2.3.4 (real IP — safe to fetch from!)
  3. Filter: "1.2.3.4 is OK" → allowed
  4. Server makes connection to evil.com...
  
  But what if between step 2 and step 4, evil.com's DNS changes?
  
DNS REBINDING:
  1. evil.com resolves to 1.2.3.4 (first resolution — for the VALIDATION)
  2. Filter: 1.2.3.4 is safe → allowed
  3. Server makes the actual HTTP connection to evil.com
  4. evil.com's DNS changed to 127.0.0.1! (second resolution — for connection!)
  5. Server connects to 127.0.0.1 → SSRF!
  
  Bypasses IP-based SSRF filters!
  Race condition: validation uses first DNS answer, connection uses second!
```

---

## How DNS Rebinding Works

```
DNS TTL = Time To Live (how long to cache the DNS answer)

ATTACK SETUP:
  1. Attacker controls evil.com and its nameserver
  2. Set DNS TTL to 0 (or very low, like 1 second)
  3. Configure nameserver to alternate between:
     First query: 1.2.3.4 (legit IP)
     Second query: 127.0.0.1 (target)

DNS REBINDING FLOW:
  ┌─────────────────────────────────────────────────────┐
  │ TIME 1: URL submitted: http://evil.com/admin         │
  │ Server resolves evil.com → 1.2.3.4 (legit!)         │
  │ Validation: 1.2.3.4 is allowed → pass!              │
  │                                                       │
  │ TIME 2: Server makes connection                       │
  │ Re-resolves evil.com (TTL expired!) → 127.0.0.1!    │
  │ Connects to 127.0.0.1/admin → SSRF!                 │
  └─────────────────────────────────────────────────────┘

REQUIREMENTS:
  ✓ Validation and connection have separate DNS resolutions
  ✓ Short TTL (to force re-resolution)
  ✓ Control of the malicious domain's DNS
```

---

## DNS Rebinding Tools and Services

```bash
# OPTION 1: RBNDR.US (free DNS rebinding service):
# Your URL: http://A.B.rbndr.us
# Where A = first IP (legit), B = second IP (attack target)
# Alternates between the two IPs on each DNS request!

# EXAMPLE:
# 1.2.3.4 = legit external IP (use any public IP)
# 127.0.0.1 = target (decimal: 01.00.00.127 for rbndr format?)
# URL: http://01020304.7f000001.rbndr.us/

# OPTION 2: singularity.me (DNS rebinding framework):
git clone https://github.com/nccgroup/singularity
cd singularity
# Provides manager UI for configuring DNS rebinding attacks

# OPTION 3: rebind.it (online service):
# https://rebind.it → configure TTL 0 alternating IPs
# Get unique URL to use in SSRF

# OPTION 4: Own Domain (most reliable):
# Set up Bind9 or PowerDNS
# Configure with lua/python for dynamic responses
# Alternate between legit IP and 127.0.0.1

# FREE SERVICE: 1u.ms
# http://make-1.2.3.4-and-127.0.0.1-rebind-1234-rr.1u.ms
# Resolves to 1.2.3.4 first time, 127.0.0.1 second time!
```

---

## Practical DNS Rebinding Attack

```
STEP 1: SET UP REBINDING DOMAIN
  Using rbndr.us:
  URL = http://LEGITIP.7f000001.rbndr.us/admin
  
  First resolution: → LEGITIP (passes filter!)
  Second resolution: → 127.0.0.1 (actual connection target!)

STEP 2: SUBMIT TO SSRF ENDPOINT
  POST /fetch
  url=http://LEGITIP.7f000001.rbndr.us/admin
  
  Server:
  1. Validates DNS → gets LEGITIP → ALLOWED!
  2. Makes HTTP request → DNS re-resolved → gets 127.0.0.1!
  3. Connects to 127.0.0.1/admin → SSRF!

STEP 3: READ RESPONSE
  If in-band SSRF: admin panel content returned!
  If blind: use Burp Collaborator on LEGITIP to confirm bypass

TIMING:
  The attack depends on DNS TTL being 0 or very short.
  Some servers cache DNS internally — rebinding fails!
  Retry multiple times if first attempt fails.
```

---

## Why DNS Rebinding Bypasses Filters

```
COMMON FILTER APPROACHES:

APPROACH 1: Resolve hostname, check if IP is internal → BYPASS WITH REBINDING!
  (Resolution happens before connection, so rebinding beats this check)

APPROACH 2: Send request, check what IP was used → Partially protects
  (Still may be bypassable if check happens before connection)

APPROACH 3: Resolve hostname once, pin for the connection → Protects!
  (Resolution pinning prevents rebinding)

APPROACH 4: Block all non-public IPs in the HTTP library → Protects!
  (If library refuses to connect to internal IPs regardless of hostname)

TAKEAWAY:
  DNS rebinding bypasses filters that rely on DNS resolution for validation
  but then make a separate DNS resolution for the actual connection.
  It's a Time-Of-Check vs Time-Of-Use (TOCTOU) vulnerability!
```

---

## Detection

```
TESTING FOR DNS REBINDING SUSCEPTIBILITY:
  1. Find SSRF endpoint
  2. Test if 127.0.0.1 is blocked: url=http://127.0.0.1/
  3. If blocked → try DNS rebinding
  4. Use rbndr.us or similar:
     url=http://LEGIT.7f000001.rbndr.us/
  5. Submit multiple times (to win the race condition)
  6. Check if any response differs

TOOLS:
  Burp Suite: Record which DNS queries are made
  Wireshark: (if you can observe server traffic)
  Collaborator: Place Collaborator URL as both IPs to see resolution order
```

---

## Related Notes
- [[14 - SSRF Localhost Bypass]] — IP bypass without DNS rebinding
- [[16 - SSRF URL Parser Confusion]] — other parsing tricks
- [[17 - SSRF WAF Bypass]] — comprehensive bypass techniques
- [[01 - What is SSRF]] — fundamentals
