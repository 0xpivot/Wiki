---
tags: [vapt, recon, intermediate]
difficulty: intermediate
module: "05 - Recon"
topic: "05.20 Cloud Storage Enumeration (S3, Azure Blob, GCP)"
---

# 05.20 — Cloud Storage Enumeration

## What is it?

Cloud storage buckets (AWS S3, Azure Blob Storage, Google Cloud Storage) are often misconfigured to be publicly accessible. Exposed buckets can contain source code, database backups, customer PII, internal documentation, API keys, and more. Finding and enumerating cloud storage is a high-priority recon step.

---

## AWS S3 Bucket Enumeration

### Bucket Naming Patterns

```
COMMON BUCKET NAMING CONVENTIONS:
  target.com
  www.target.com
  target-assets
  target-backup
  target-uploads
  target-prod
  target-dev
  target-staging
  target-media
  target-logs
  target-static
  target-data
  target-api

URL FORMATS:
  https://BUCKET.s3.amazonaws.com
  https://s3.amazonaws.com/BUCKET
  https://BUCKET.s3.REGION.amazonaws.com
  https://s3.REGION.amazonaws.com/BUCKET
```

### Testing S3 Buckets

```bash
# CHECK IF BUCKET EXISTS AND IS PUBLIC:
curl -s https://target.s3.amazonaws.com/
# 200 → public! lists bucket contents (XML)
# 403 → exists but private
# 404 → bucket doesn't exist

# LIST BUCKET CONTENTS (if public):
curl -s "https://target.s3.amazonaws.com/?list-type=2" | \
  python3 -c "
import sys
from xml.etree import ElementTree
tree = ElementTree.parse(sys.stdin)
for key in tree.findall('.//{http://s3.amazonaws.com/doc/2006-03-01/}Key'):
    print(key.text)
"

# WITH AWS CLI (anonymous access):
aws s3 ls s3://target --no-sign-request
aws s3 ls s3://target/ --no-sign-request --recursive

# DOWNLOAD EVERYTHING (if public!):
aws s3 sync s3://target ./target-bucket --no-sign-request

# CHECK WRITE ACCESS (if authorized!):
echo "test" | aws s3 cp - s3://target/test.txt --no-sign-request
# Success → can write to bucket! (data injection, malware hosting)

# CHECK ACL:
aws s3api get-bucket-acl --bucket target --no-sign-request
```

### Automated S3 Discovery Tools

```bash
# LAZYS3 (bruteforce bucket names):
python3 lazys3.py target

# S3SCANNER:
pip3 install s3scanner
s3scanner scan --bucket target
s3scanner scan --bucket-file buckets.txt

# BUCKET FINDER (wordlist-based):
ruby bucket_finder.rb --download wordlist.txt

# CLOUD_ENUM (multi-cloud):
python3 cloud_enum.py -k target --quickscan

# AMASS with cloud option:
amass enum -d target.com -brute

# GENERATE PERMUTATIONS:
for prefix in "" "www." "dev." "staging." "prod." "api." "backup." "assets." "static." "media." "files."; do
  for suffix in "" "-assets" "-backup" "-data" "-files" "-media" "-static" "-uploads" "-logs"; do
    echo "${prefix}target${suffix}"
  done
done | while read bucket; do
  aws s3 ls "s3://$bucket" --no-sign-request 2>/dev/null && echo "FOUND: $bucket"
done
```

---

## Azure Blob Storage

```
URL FORMAT:
  https://ACCOUNT.blob.core.windows.net
  https://ACCOUNT.blob.core.windows.net/CONTAINER
  https://ACCOUNT.blob.core.windows.net/CONTAINER/BLOB

PUBLIC ACCESS LEVELS:
  Private: No anonymous access
  Container: Public read access to container + blobs (lists files!)
  Blob: Public read access to blobs only (no listing)
```

```bash
# CHECK ACCOUNT EXISTS:
curl -s https://target.blob.core.windows.net/
# 400 → account exists (request wrong, not 404)
# 404 → account doesn't exist

# LIST CONTAINERS (if public container access):
curl -s "https://target.blob.core.windows.net/?comp=list"

# LIST BLOBS IN CONTAINER:
curl -s "https://target.blob.core.windows.net/public?restype=container&comp=list"

# WITH AZURE CLI:
az storage blob list --account-name target --container-name public --auth-mode login

# COMMON CONTAINERS:
for container in public assets backup images files data logs media static; do
  url="https://target.blob.core.windows.net/$container?restype=container&comp=list"
  code=$(curl -s -o /tmp/az-resp -w "%{http_code}" "$url")
  [ "$code" = "200" ] && echo "PUBLIC CONTAINER: $container" && cat /tmp/az-resp
done

# BLOB URL PATTERNS:
# https://target.blob.core.windows.net/public/
# https://target.blob.core.windows.net/$web/  ← static website!
```

---

## Google Cloud Storage (GCS)

```
URL FORMAT:
  https://storage.googleapis.com/BUCKET
  https://BUCKET.storage.googleapis.com
  https://storage.cloud.google.com/BUCKET

PUBLIC ACCESS:
  allUsers → everyone can access
  allAuthenticatedUsers → any Google account can access
```

```bash
# CHECK IF BUCKET IS PUBLIC:
curl -s https://storage.googleapis.com/target

# LIST BUCKET CONTENTS:
curl -s https://storage.googleapis.com/storage/v1/b/target/o
# OR via browser: https://storage.googleapis.com/target?list

# WITH GSUTIL:
gsutil ls gs://target
gsutil ls -r gs://target  # recursive

# CHECK PERMISSIONS:
gsutil acl get gs://target

# WRITE CHECK (if authorized!):
echo "test" | gsutil cp - gs://target/test.txt
# Success → public write!

# COMMON GCS BUCKET NAMES:
for name in target www.target target-assets target-backup target-prod; do
  gsutil ls "gs://$name" 2>/dev/null && echo "FOUND: $name"
done
```

---

## Firebase Storage

```bash
# FIREBASE DATABASE (NoSQL, often misconfigured):
# Default rules allow public read!

# CHECK:
curl -s "https://target.firebaseio.com/.json"
# 200 with data → public read enabled!

# ENUMERATE:
curl -s "https://target.firebaseio.com/users.json"
curl -s "https://target.firebaseio.com/orders.json"
curl -s "https://target.firebaseio.com/admin.json"

# FIND FIREBASE APPS FROM JS:
# Look in JS files for: firebaseio.com, firebase.google.com
grep -r "firebaseio.com\|firebase.google.com\|firebaseapp.com" ./js-files/

# FIREBASE STORAGE:
curl -s "https://firebasestorage.googleapis.com/v0/b/target.appspot.com/o"

# CHECK FIREBASE CONFIG EXPOSED IN JS:
grep -r "apiKey\|authDomain\|databaseURL\|storageBucket" ./js-files/
# Firebase config in JS is expected → but check firebase.json rules!
```

---

## Multi-Cloud Enumeration

```bash
# CLOUD_ENUM (best tool — checks S3, Azure, GCS, Firebase simultaneously):
git clone https://github.com/initstring/cloud_enum.git
pip3 install -r requirements.txt

# BASIC SCAN:
python3 cloud_enum.py -k target

# WITH WORDLIST (common name mutations):
python3 cloud_enum.py -k target -kf wordlist.txt

# MANUAL WORDLIST GENERATION:
python3 -c "
name = 'target'
muts = [name, f'{name}-prod', f'{name}-dev', f'{name}-staging',
        f'{name}-backup', f'{name}-assets', f'{name}-data',
        f'{name}-static', f'{name}-media', f'{name}-files',
        f'prod-{name}', f'dev-{name}', f'backup-{name}']
print('\n'.join(muts))
" > mutations.txt
python3 cloud_enum.py -kf mutations.txt

# GREP FOR CLOUD URLS IN JS/HTML:
grep -rE "s3\.amazonaws\.com|blob\.core\.windows\.net|storage\.googleapis\.com|appspot\.com" ./
```

---

## What to Do When You Find Public Buckets

```
SEVERITY ASSESSMENT:
  Critical: customer PII, DB backups with plaintext passwords, private keys
  High: source code, internal documentation, API credentials, employee data
  Medium: internal photos, marketing materials, non-sensitive configs
  Low: public assets (already public images, CSS, JS)

DOCUMENT THE FINDING:
  URL: https://target.s3.amazonaws.com/
  Access Type: Public Read (list + download)
  Sample Contents:
    - database-backup-2024-01-15.sql.gz
    - api-keys.json
    - customer-emails.csv (10,000 records!)
  
  Do NOT download all the data — just enough to prove exposure!
  Screenshot the listing + one sample filename showing sensitivity.
  Do NOT read/use the actual PII — just note the file name.
  
CVSS: ~7.5 (High) for sensitive data exposure
REMEDIATION:
  - Remove public access from bucket
  - Enable bucket ACLs requiring authentication
  - Enable S3 Block Public Access at account level
  - Audit all buckets with AWS Config / Security Hub
```

---

## Related Notes
- [[27 - ASN and IP Range Discovery]] — finding cloud infrastructure IP ranges
- [[Module 09 - Cloud Security]] — full cloud security testing
- [[19 - Source Code Leakage]] — other data exposure vectors
- [[11 - GitHub Dorking for Secrets]] — finding bucket names in code
