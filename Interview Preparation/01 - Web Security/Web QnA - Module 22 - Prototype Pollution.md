---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 22"
---

# Web QnA - Module 22 - Prototype Pollution

```text
  [ Attacker Payload ]
  {"__proto__": {"isAdmin": true}}
           |
           | (1) JSON parsing / Recursive Merge
           v
  +-----------------------------------+
  | Target JavaScript Application     |
  | Object.prototype.isAdmin = true   | <=== (2) The global prototype is polluted!
  +-----------------------------------+
           |
           | (3) Application logic execution
           v
  [ User Object ]  (Created without isAdmin property)
  if (user.isAdmin) {
      // (4) Property not found on user object.
      // JS engine checks user.__proto__ (Object.prototype)
      // Returns true!
      GrantAdminAccess(); <=== (5) Privilege Escalation bypass!
  }
```

## Formal Technical Questions

**Q1: Explain the underlying mechanism of Prototype Pollution in JavaScript. Why does it affect all objects across the application?**
**Answer:**
JavaScript is a prototype-based language. When you attempt to access a property on an object (e.g., `obj.prop`), the JavaScript engine first checks if the property exists directly on the object. If it doesn't, the engine traverses up the prototype chain to the object's prototype (`obj.__proto__`), and then its prototype's prototype, until it reaches `Object.prototype` (and finally `null`). 
Prototype Pollution occurs when an attacker can control the keys and values being assigned to an object, typically during operations like recursive merging, deep cloning, or parsing query strings. By injecting the key `__proto__` (or `constructor.prototype`), the attacker modifies `Object.prototype` itself. Since nearly all objects in JavaScript inherit from `Object.prototype`, injecting a property here means that *every* object in the application that doesn't explicitly define that property will now inherit the attacker-injected value. This global mutation leads to logic bypasses, denial of service, or remote code execution.

**Q2: Differentiate between Client-Side and Server-Side Prototype Pollution. What are the typical impacts of each?**
**Answer:**
*Client-Side Prototype Pollution:* Occurs in the browser (frontend JS). The typical vectors are URL query strings or URL fragments being parsed insecurely by libraries like jQuery, Lodash, or custom parsers. The impact usually revolves around Cross-Site Scripting (XSS) via "gadgets" (polluting a configuration property that is later used in an `innerHTML` sink), client-side logic bypass, or Denial of Service (crashing the UI).
*Server-Side Prototype Pollution:* Occurs in a Node.js backend. Vectors are usually JSON body payloads or query parameters being processed by recursive merge functions. The impact is significantly more critical. It can lead to Authentication/Authorization bypass (polluting `isAdmin` or `role`), Denial of Service (polluting `toString` to break application logic or crash the event loop), and Remote Code Execution (RCE) by polluting environment variables or arguments passed to `child_process.exec()` or `fork()`.

**Q3: Explain what a "Gadget" is in the context of Prototype Pollution.**
**Answer:**
A prototype pollution gadget is a specific piece of legitimate application or library code that behaves insecurely when a globally inherited property is modified via prototype pollution. 
For example, if an application has a function that checks for a configuration option:
```javascript
let config = {};
if (config.transport_url) {
    let script = document.createElement('script');
    script.src = config.transport_url;
    document.body.appendChild(script);
}
```
If an attacker pollutes `Object.prototype.transport_url = "https://evil.com/xss.js"`, the `config` object (which is empty) will inherit `transport_url`. The `if` condition evaluates to true, and the script is injected. The code snippet above is the "gadget" that turns the prototype pollution vulnerability into an XSS execution.

## Scenario-Based Questions

**Q4: You are performing a white-box assessment of a Node.js application. You identify a vulnerable deep-merge function that allows Prototype Pollution. However, the application only uses a single database connection and has no child processes executing. How would you attempt to achieve a Denial of Service (DoS)?**
**Answer:**
If RCE via `child_process` gadgets isn't possible, I would pivot to Application-Level DoS using Prototype Pollution. There are several ways to crash a Node.js process:
1. **Polluting Built-in Object Methods:** Polluting `Object.prototype.toString = "boom"` or `Object.prototype.valueOf = 1`. Many libraries implicitly call these methods (e.g., when coercing objects to strings for logging). If they are replaced with non-functions or garbage strings, the application will throw a `TypeError` and crash.
2. **Polluting Express.js internals:** If the app uses Express, I can pollute `Object.prototype.status = 500`. Since Express response objects inherit this, it might cause all requests to fail or break internal middleware logic.
3. **Polluting Array prototype:** Modifying `Array.prototype.push` or `map` would instantly break all internal loops and logic, bringing down the event loop.
4. **JSON.stringify DoS:** Polluting `toJSON` to return a circular reference or an infinite loop mechanism, causing the process to exhaust memory when returning JSON responses.

**Q5: During a Red Team engagement, you find a client-side prototype pollution vulnerability via the URL query string: `?__proto__[test]=1`. You have verified `Object.prototype.test` is `1`. However, you cannot find any obvious gadgets in the custom application code. The site imports React, Vue, and a large analytics library. What is your strategy?**
**Answer:**
Finding manual gadgets in heavily minified, modern SPA code is difficult. My strategy would be:
1. **Automated Gadget Scanning:** I would use tools like DOM Invader (built into Burp Suite) or the BlackFan Prototype Pollution tool. These tools automatically inject test payloads and scan the application's DOM and JavaScript execution for known gadgets in popular libraries.
2. **Targeting Third-Party Libraries:** Even if the custom code is secure, third-party libraries often contain gadgets. For example:
   - *Vue.js:* Polluting `template` or `v-html` related internal properties.
   - *Analytics libraries (Google Analytics, Segment):* They often create script tags dynamically based on configuration objects. Polluting `src` or `url` properties might result in script injection.
   - *Webpack:* If Webpack's public path is loaded dynamically, polluting `__webpack_public_path__` can redirect chunk loading to an attacker-controlled server.
3. **Fuzzing Common Keys:** I would fuzz standard gadget keys like `src`, `href`, `url`, `template`, `innerHTML`, `content`, `action`, and `data` to observe if they trigger network requests or DOM changes.

## Deep-Dive Defensive Questions

**Q6: You are a Lead AppSec Engineer reviewing a pull request that fixes a Prototype Pollution vulnerability. The developer has added the following mitigation to the deep merge function: `if (key === '__proto__') continue;`. Is this mitigation sufficient? Why or why not?**
**Answer:**
This mitigation is **insufficient and can be bypassed.** While it blocks the direct use of `__proto__`, JavaScript provides another pathway to the prototype object: the `constructor` property. 
Every object has a `constructor` property pointing to the function that created it (e.g., `Object`). The `constructor` function itself has a `prototype` property pointing to the prototype object. 
Therefore, an attacker can bypass the filter by using the payload: `{"constructor": {"prototype": {"isAdmin": true}}}`.
To properly fix this, the developer must block BOTH `__proto__` and `constructor` (and ideally `prototype`).
A robust mitigation would look like:
```javascript
if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
    continue;
}
```

**Q7: Explain the concept of `Object.create(null)` and how it acts as a structural defense against Prototype Pollution.**
**Answer:**
When you create a standard JavaScript object using `{}` or `new Object()`, it automatically inherits from `Object.prototype`. 
`Object.create(null)` is a method that creates a completely blank object that does *not* inherit from `Object.prototype`. It has no prototype chain (its `__proto__` is `null`).
Because it doesn't inherit from `Object.prototype`, even if an attacker successfully pollutes `Object.prototype.isAdmin = true`, the object created with `Object.create(null)` will **not** inherit the `isAdmin` property. 
As a structural defense, if an application uses `Object.create(null)` for data structures that store state, configuration, or user privileges, those objects are immune to the effects of prototype pollution occurring elsewhere in the application. Another strong defense is using `Object.freeze(Object.prototype)` at the very beginning of the application's execution to prevent any modifications to the global prototype.

## Defensive Coding Examples

**Insecure Implementation (Custom Deep Merge):**
```javascript
function merge(target, source) {
    for (let key in source) {
        if (typeof source[key] === 'object' && typeof target[key] === 'object') {
            merge(target[key], source[key]);
        } else {
            // VULNERABLE: No check for __proto__ or constructor
            target[key] = source[key];
        }
    }
    return target;
}
```

**Secure Implementation (Custom Deep Merge):**
```javascript
function mergeSecure(target, source) {
    for (let key in source) {
        // SAFE: Strict sanitization of prototype traversal keys
        if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
            continue; 
        }
        if (typeof source[key] === 'object' && typeof target[key] === 'object') {
            mergeSecure(target[key], source[key]);
        } else {
            target[key] = source[key];
        }
    }
    return target;
}
```

**Using Maps for Data Storage (Secure Alternative):**
```javascript
// Instead of using objects as hash maps which are vulnerable to inheritance:
const userRoles = {}; // Vulnerable

// Use ES6 Maps which do not inherit from Object.prototype keys in a dangerous way for .get()
const userRolesMap = new Map();
userRolesMap.set('sanchit', 'admin');
if (userRolesMap.get(username) === 'admin') { ... } // Immune to global object pollution
```

## Bonus Practical Exercises

1. **Node.js DoS Lab:**
   - Create a simple Express server with a vulnerable JSON body parser or a custom merge function.
   - Send payloads trying to overwrite `Object.prototype.toString` to break the server.
   - Observe the stack trace when the application crashes.
2. **Gadget Hunting:**
   - Review the source code of older versions of jQuery (e.g., `< 3.4.0`) and find the `$.extend` prototype pollution vulnerability.
   - Set up an HTML page, load the vulnerable jQuery.
   - Craft a URL query payload that pollutes an internal jQuery configuration setting to pop an alert box.

## Tooling & Automation

- **DOM Invader:** Integrated into Burp Suite's built-in Chromium browser. It injects a unique string into various sources and monitors the DOM and JavaScript execution to detect if that string makes its way onto the prototype.
- **NodeJsScan:** A static analysis tool for Node.js code that flags insecure imports of known vulnerable libraries (like old versions of `lodash`).
- **Snyk / Dependabot:** Keep dependencies updated, as prototype pollution often originates from transitive dependencies rather than direct application code.

## Real-World Attack Scenario

**Scenario:** RCE in a Node.js microservice handling image processing.
1. The attacker interacts with an API endpoint `/api/convert` that accepts a JSON payload to define image cropping parameters.
2. The backend uses an outdated version of the `lodash` library's `merge` function to combine the user's JSON with default system configurations.
3. The attacker sends a malicious JSON payload:
```json
{
    "image_id": "12345",
    "crop": {"x": 10, "y": 10},
    "__proto__": {
        "env": {
            "NODE_OPTIONS": "--require /proc/self/environ"
        },
        "shell": "/bin/sh"
    }
}
```
4. The vulnerable `merge` function processes the payload, and `Object.prototype.env` and `Object.prototype.shell` are globally polluted.
5. In another part of the application, the service uses `child_process.fork()` or `child_process.spawn()` to execute an external image processing binary (like ImageMagick).
6. When `spawn()` is called, Node.js checks an options object for configurations. Because the options object is uninitialized for `env` and `shell`, it traverses the prototype chain and inherits the attacker's polluted values.
7. Node.js executes the child process using `/bin/sh` as the shell, and passes the injected `NODE_OPTIONS`. This allows the attacker to manipulate the Node environment, executing arbitrary commands via the injected environment variables, resulting in full Remote Code Execution (RCE) on the server.

## Chaining Opportunities

- **Prototype Pollution -> DOM XSS:** The most common client-side chain. Polluting configuration properties that dictate where scripts are loaded from or what HTML is rendered.
- **Prototype Pollution -> RCE (Node.js):** Exploiting `child_process.spawn/exec/fork` by polluting `env`, `shell`, `NODE_OPTIONS`, or `LD_PRELOAD`.
- **Prototype Pollution -> Authentication Bypass:** Polluting token validation objects, role arrays, or session configuration objects.
- **Prototype Pollution -> SQL Injection:** If an ORM relies on object properties to construct queries without strict typing (e.g., polluting `Object.prototype.where = "1=1; DROP TABLE users"`).
- **Prototype Pollution -> CSRF Bypass:** Polluting the configuration objects of HTTP clients (like Axios) to manipulate request headers, stripping CSRF tokens or changing target origins.

## Related Notes

- [[02 - Cross-Site Scripting (XSS)]]
- [[17 - Advanced Node.js Security]]
- [[19 - JavaScript Deserialization and AST Injection]]
- [[20 - Client-Side Security and DOM Clobbering]]
