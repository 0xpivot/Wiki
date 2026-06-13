---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.60 Expect-CT — Certificate Transparency"
---

# 03.60 — Expect-CT

## What is it?

`Expect-CT` (deprecated since 2021) told browsers to require Certificate Transparency (CT) logs for TLS certificates. CT ensures that all issued certificates are publicly logged, making unauthorized certificates detectable. This header is now deprecated because browsers enforce CT natively.

---

## What Certificate Transparency Does

```
WITHOUT CT:
  Rogue CA issues fraudulent certificate for "bank.com"
  → MITM with valid-looking cert!
  → Users see green lock → trust it!
  
WITH CT:
  Every cert must be logged in public CT logs.
  Browser checks: "Is this cert in CT logs?"
  If not → browser rejects cert!
  
  Even if rogue cert issued:
  → It appears in public logs → company notices → emergency response!
  → Much smaller attack window!
```

---

## Expect-CT Header (Deprecated)

```
Expect-CT: max-age=86400, enforce, report-uri="https://example.com/report"

max-age    → how long to require CT (in seconds)
enforce    → reject certificates not in CT logs (without = report only)
report-uri → where to report violations

DEPRECATED (June 2021):
  Chrome 107+ ignores Expect-CT
  Browsers now enforce CT natively
  Header no longer needed
  
  Seeing Expect-CT in the wild → old/unmaintained server config!
```

---

## CT for Reconnaissance (crt.sh)

```
CT LOGS ARE PUBLIC → great for OSINT!

Find all certificates issued for a domain:
  https://crt.sh/?q=%.target.com
  
  Returns:
  - All subdomains that ever had a certificate!
  - Staging environments: staging.target.com
  - Internal tools: jenkins.target.com, jira.target.com
  - Old apps: legacy.target.com, old-api.target.com
  - Development: dev.target.com, test.target.com

COMMAND LINE:
  curl -s "https://crt.sh/?q=%.target.com&output=json" | \
    python3 -m json.tool | grep "name_value" | sort -u
    
  OR:
  subfinder -d target.com   (uses CT logs internally)
  amass enum -d target.com  (uses CT logs)
  
  → Discover attack surface via certificate transparency!
```

---

## Attack: Unauthorized Certificate Detection

```
CT MONITORING FOR DEFENDERS:
  Tools to alert when new cert is issued for your domain:
  - certspotter.com
  - Facebook CT Monitor
  - Spyse CT monitoring
  
  Alert: "New cert issued for *.target.com!"
  → If you didn't authorize it → rogue CA attack! → immediate action!
  
ATTACKER USE:
  Monitor target's CT logs → know when new subdomains are launched!
  cert.sh shows: new subdomain beta.target.com just got a cert!
  → New target to probe!
```

---

## Testing

```bash
# Check Expect-CT (informational only now):
curl -sI https://target.com | grep -i "expect-ct"

# Find subdomains via CT logs:
curl -s "https://crt.sh/?q=%.target.com&output=json" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); [print(x['name_value']) for x in d]" | \
  sort -u

# Check certificate in CT logs:
# https://crt.sh/?q=target.com
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Expect-CT header (deprecated) | Remove it; CT is enforced natively |
| Unauthorized cert issuance | Monitor CT logs for unexpected certs |
| CAA records not set | Set DNS CAA records to restrict which CAs can issue certs |

**CAA record example:**
```dns
target.com. IN CAA 0 issue "letsencrypt.org"
target.com. IN CAA 0 issuewild ";"     ← block all wildcard certs
```

---

## Related Notes
- [[01.18 - Certificates and Certificate Authorities]] — cert trust chain
- [[01.17 - TLS SSL How HTTPS Works]] — TLS and certificates
- [[Module 17 - Recon]] — subdomain discovery via CT logs
