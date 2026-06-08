---
tags: [vapt, recon, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.15 robots.txt and sitemap.xml"
---

# 05.15 — robots.txt and sitemap.xml

## What is it?

`robots.txt` and `sitemap.xml` are standard web files that guide search engine crawlers. They're goldmines for VAPT because they explicitly list paths the site owner either wants indexed (sitemap) or doesn't want indexed (robots.txt) — and the ones they want to hide are often the most interesting.

---

## robots.txt

```
LOCATION: https://target.com/robots.txt (always check first!)

PURPOSE: Tell search engine crawlers which pages NOT to index.
IRONY: By listing "disallowed" pages, you advertise exactly what's sensitive!

EXAMPLE:
  User-agent: *
  Disallow: /admin/          ← admin panel!
  Disallow: /api/internal/   ← internal API!
  Disallow: /backup/         ← BACKUP FILES!
  Disallow: /config/         ← CONFIGURATION!
  Disallow: /private/
  Disallow: /dev/
  Disallow: /?debug=true     ← debug parameter!
  Disallow: /wp-admin/       ← WordPress admin
  Disallow: /phpmyadmin/     ← database admin!
  Disallow: /*.pdf$          ← PDF files
  Sitemap: https://target.com/sitemap.xml

KEY INSIGHT:
  "Disallow" in robots.txt = "interesting to test!"
  Bots obey robots.txt; attackers DO NOT HAVE TO.
  These paths are not hidden — they're just labeled "don't index."
```

---

## Testing robots.txt Findings

```bash
# Fetch and read:
curl -s https://target.com/robots.txt

# Extract all Disallow paths:
curl -s https://target.com/robots.txt | \
  grep "Disallow" | awk '{print $2}' > robots-paths.txt

# Test each path:
cat robots-paths.txt | while read path; do
  url="https://target.com${path}"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  echo "$code $url"
done

# Quick test with httpx:
cat robots-paths.txt | \
  sed 's|^|https://target.com|' | \
  httpx -status-code -title

# LOOK FOR:
# 200 → accessible!
# 401/403 → auth required → worth trying bypass!
# 200 with interesting title → admin/debug content
```

---

## sitemap.xml

```
LOCATION: https://target.com/sitemap.xml
OR: https://target.com/sitemap_index.xml

PURPOSE: List all important pages for search indexing.
VAPT VALUE: Complete map of intended pages → find hidden functionality!

EXAMPLE:
  <?xml version="1.0" encoding="UTF-8"?>
  <urlset>
    <url><loc>https://target.com/</loc></url>
    <url><loc>https://target.com/products/</loc></url>
    <url><loc>https://target.com/api/v1/docs</loc></url>  ← API docs!
    <url><loc>https://target.com/internal/report</loc></url>  ← internal?
    <url><loc>https://target.com/user/profile?id=1234</loc></url>  ← IDOR!
    <url><loc>https://target.com/download?file=report.pdf</loc></url>  ← path traversal?
  </urlset>

NESTED SITEMAPS:
  <sitemapindex>
    <sitemap><loc>https://target.com/sitemap-blog.xml</loc></sitemap>
    <sitemap><loc>https://target.com/sitemap-api.xml</loc></sitemap>
    <sitemap><loc>https://target.com/sitemap-admin.xml</loc></sitemap>  ← INTERESTING!
  </sitemapindex>
```

---

## Automated Processing

```bash
# Parse sitemap for all URLs:
curl -s https://target.com/sitemap.xml | \
  grep -oP '(?<=<loc>).*?(?=</loc>)' | sort -u > sitemap-urls.txt

# Handle sitemap index:
curl -s https://target.com/sitemap_index.xml | \
  grep -oP '(?<=<loc>).*?(?=</loc>)' | \
  while read smap; do
    curl -s "$smap" | grep -oP '(?<=<loc>).*?(?=</loc>)'
  done | sort -u > all-sitemap-urls.txt

# Extract parameters from sitemap URLs (IDOR targets):
cat sitemap-urls.txt | grep "?" | \
  python3 -c "
import sys
from urllib.parse import urlparse, parse_qs
for line in sys.stdin:
    url = line.strip()
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    if params:
        print(f'{url} → params: {list(params.keys())}')
"

# Check for integer IDs in URLs (IDOR!):
cat sitemap-urls.txt | grep -P '\?.*=\d+' | head -20
# /profile?id=1001 → try id=1002, id=1000, etc.
```

---

## Other Standard Web Files to Check

```bash
# Always check these on every target:
for path in \
  /robots.txt \
  /sitemap.xml \
  /sitemap_index.xml \
  /.well-known/security.txt \
  /security.txt \
  /.well-known/assetlinks.json \
  /.well-known/apple-app-site-association \
  /crossdomain.xml \
  /clientaccesspolicy.xml \
  /browserconfig.xml \
  /humans.txt \
  /README.md \
  /CHANGELOG.md \
  /version.txt \
  /build.txt \
  /package.json \
  /composer.json; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com$path")
    [ "$code" = "200" ] && echo "FOUND: https://target.com$path"
done
```

---

## security.txt (Defender Side)

```
/.well-known/security.txt — RFC 9116

WHO TO REPORT BUGS TO:
  Contact: mailto:security@target.com
  Contact: https://hackerone.com/target
  Encryption: https://target.com/pgp-key.txt
  Preferred-Languages: en
  Policy: https://target.com/security-policy
  
FOR VAPT:
  → Find who to contact for responsible disclosure!
  → Check their bug bounty program URL
  → Find the scope/policy document
```

---

## Related Notes
- [[16 - .well-known Directory]] — other standard paths
- [[29 - Directory and File Bruteforcing]] — finding additional paths
- [[10 - Web Archive Wayback Machine]] — historical versions of robots.txt
