---
tags: [vapt, recon, osint, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.09 Certificate Transparency Logs (crt.sh)"
---

# 05.09 — Certificate Transparency Logs (crt.sh)

## What is it?

Certificate Transparency (CT) is a system where every SSL/TLS certificate issued must be logged in public CT logs. This was designed to detect rogue certificate issuance, but as a side effect, it creates a comprehensive public record of every subdomain that has ever had a certificate. This makes CT logs one of the most powerful passive subdomain discovery sources.

---

## What CT Logs Reveal

```
Every certificate contains:
  - Common Name (CN): primary domain it's issued for
  - Subject Alternative Names (SANs): all other domains covered
  - Issuer: which Certificate Authority issued it
  - Validity dates: when it was created
  - Organization: who it was issued to

EXAMPLE CERTIFICATE:
  CN: api.target.com
  SANs: 
    api.target.com
    api-v2.target.com       ← NEW SUBDOMAIN DISCOVERED!
    api-staging.target.com  ← STAGING ENVIRONMENT!
    internal-api.target.com ← INTERNAL API ENDPOINT!
  Issuer: Let's Encrypt
  Not Before: 2024-01-15
  Not After: 2024-04-15
```

---

## crt.sh

```bash
# WEB INTERFACE:
# https://crt.sh/?q=%.target.com
# %. prefix = wildcard match all subdomains

# Search options:
# %.target.com → all subdomains (most useful)
# target.com   → exact domain only
# %target.com  → anything ending in target.com (careful: evilrtarget.com matches!)

# CURL (API):
curl "https://crt.sh/?q=%.target.com&output=json" | python3 -m json.tool | less

# EXTRACT SUBDOMAINS:
curl -s "https://crt.sh/?q=%.target.com&output=json" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
names = set()
for cert in data:
    for name in cert['name_value'].split('\n'):
        name = name.strip()
        if name and not name.startswith('*'):
            names.add(name)
for name in sorted(names):
    print(name)
"

# INCLUDE WILDCARDS (for finding wildcard cert scopes):
curl -s "https://crt.sh/?q=%.target.com&output=json" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
names = set()
for cert in data:
    for name in cert['name_value'].split('\n'):
        names.add(name.strip())
for name in sorted(names):
    print(name)
"
```

---

## Automated Tools Using CT Logs

```bash
# SUBFINDER (uses crt.sh internally):
subfinder -d target.com -silent

# AMASS (uses multiple CT sources):
amass enum -passive -d target.com

# CERT-SPOTTER:
curl https://certspotter.com/api/v1/issuances?domain=target.com&include_subdomains=true&expand=dns_names | \
  python3 -c "import json,sys; [print(n) for cert in json.load(sys.stdin) for n in cert['dns_names']]" | sort -u

# FACEBOOK CT API:
curl "https://graph.facebook.com/v13.0/certificates" \
  -d "access_token=APP_ID|APP_SECRET" \
  -d "query=target.com" \
  -d "fields=domains" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); [print(n) for c in d.get('data',[]) for n in c.get('domains',[])]" | sort -u

# CERTSH (wrapper script):
curl -s "https://crt.sh/?q=%.target.com&output=json" | \
  jq -r '.[].name_value' | sed 's/\*\.//g' | sort -u
```

---

## What to Look For in CT Data

```
INTERESTING PATTERNS:
  dev.target.com          → Development server
  staging.target.com      → Staging with real data
  test.target.com         → Test environment
  old.target.com          → Forgotten old application
  beta.target.com         → Beta feature, may lack security
  internal.target.com     → Should be internal but cert is public!
  vpn.target.com          → VPN portal
  admin.target.com        → Admin panel
  jenkins.target.com      → CI/CD system
  git.target.com          → Git repository
  grafana.target.com      → Monitoring dashboard
  kibana.target.com       → Log dashboard
  
  NEW SUBDOMAINS (by cert date):
  Sort by "not_before" date → recently added subdomains
  → "What changed recently?" → often less hardened!

WILDCARD CERTS:
  *.target.com → all subdomains under one cert
  → Need to brute force to find actual subdomains
  → But confirms subdomains exist!
```

---

## CT Log Monitoring for Defense

```
DEFENDER USE:
  Monitor CT logs for certificates issued for your domain.
  Alert when unexpected certs appear.
  
  Tools:
  - certspotter.com (free monitoring)
  - Facebook CT Monitor
  - Google Certificate Transparency monitoring
  - Calidog/certstream (real-time CT log stream)

ATTACKER INTEL:
  "Target just got a new cert for payments.target.com"
  → New feature being deployed!
  → Test it before it's hardened!

CERTSTREAM (real-time monitoring):
  pip install certstream
  certstream | grep "target.com"
  → See every new certificate for your target as it's issued!
```

---

## Related Notes
- [[08 - Subdomain Enumeration]] — using CT data for subdomain discovery
- [[05.05 - Censys]] — Censys certificate search
- [[01.18 - Certificates and Certificate Authorities]] — CT system background
