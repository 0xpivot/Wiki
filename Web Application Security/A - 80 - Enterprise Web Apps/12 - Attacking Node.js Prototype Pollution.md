---
tags: [web, advanced, enterprise, deserialization, vapt]
difficulty: advanced
module: "80 - Enterprise Web Apps: WebLogic, ColdFusion, Liferay"
topic: "80.12 Attacking Node.js Prototype Pollution"
---

# 12 - Attacking Node.js Prototype Pollution

## 1. Introduction to Prototype Pollution

Prototype Pollution is a critical vulnerability specific to JavaScript and Node.js environments. It occurs when an attacker can manipulate the properties of the base `Object.prototype`. Because JavaScript uses prototypal inheritance, almost all objects inherit from `Object.prototype`. If an attacker successfully injects a malicious property into the global prototype, that property will be inherited by all other objects in the application that do not explicitly override it.

This vulnerability typically arises in deep-merge, cloning, or object-extension operations where untrusted user input is not properly sanitized before being applied to a target object. The consequences of Prototype Pollution can range from unexpected application behavior and Denial of Service (DoS) to full Remote Code Execution (RCE) if the polluted property interacts with a vulnerable "gadget" in the application's code.

## 2. Understanding Prototypal Inheritance

In JavaScript, objects have an internal link to another object called their prototype. When you attempt to access a property on an object, JavaScript first checks the object itself. If the property is not found, it traverses up the prototype chain to the object's prototype, and then to the prototype's prototype, until it either finds the property or reaches `null`.

The global `Object.prototype` sits at the top of this chain for most objects.

### The `__proto__` and `constructor` Properties
- `__proto__`: A legacy getter/setter that exposes the internal `[[Prototype]]` of an object.
- `constructor`: A reference to the function that created the object. The `constructor.prototype` is effectively the same as `__proto__` for a newly instantiated object.

If an attacker can control a key during an assignment operation (e.g., `obj[key] = value`), and sets `key` to `"__proto__"`, they are no longer modifying the object `obj`, but rather modifying its prototype.

## 3. The Architecture of a Prototype Pollution Attack

Below is an ASCII representation of how Prototype Pollution corrupts the runtime environment:

```text
+-----------------------+      +-----------------------------------------+
| Attacker              |      | Node.js Application Environment         |
+-----------------------+      +-----------------------------------------+
|                       |      |                                         |
| 1. Send JSON payload  |      |   Object.prototype                      |
|    with __proto__     |      |   +---------------------------------+   |
| --------------------->|      |   | toString: function()            |   |
|                       |      |   | hasOwnProperty: function()      |   |
| 2. App uses vulnerable|      |   | *POLLUTED_PROP*: "malicious"    |<--+
|    merge() function   |      |   +---------------------------------+   |
|                       |      |            ^                            |
| 3. __proto__ is parsed|      |            | (Inherits from)            |
|    and merged into    |      |            |                            |
|    Object.prototype   |      |   Normal Object (e.g., config)          |
|                       |      |   +---------------------------------+   |
|                       |      |   | host: "localhost"               |   |
|                       |      |   | port: 8080                      |   |
|                       |      |   | // Accessing config.POLLUTED    |   |
|                       |      |   | // returns "malicious"!         |   |
+-----------------------+      +-----------------------------------------+
```

## 4. How the Vulnerability Occurs

The most common source of prototype pollution is recursive merge functions that do not validate the keys being merged.

### Vulnerable Code Example
Consider a simple, insecure deep merge function:

```javascript
function merge(target, source) {
    for (let key in source) {
        if (typeof source[key] === 'object' && typeof target[key] === 'object') {
            merge(target[key], source[key]);
        } else {
            target[key] = source[key];
        }
    }
    return target;
}
```

If an attacker sends the following JSON payload:
```json
{
    "__proto__": {
        "admin": true
    }
}
```
When this payload is parsed by `JSON.parse()` and passed into `merge(config, payload)`, the loop encounters the key `__proto__`. The target `config.__proto__` evaluates to `Object.prototype`. The function then effectively executes `Object.prototype["admin"] = true`.

From this point forward, ANY object in the Node.js process will evaluate `obj.admin` to `true` unless explicitly overridden.

## 5. Exploitation Strategies and Gadgets

Finding prototype pollution is only the first step. To achieve a meaningful impact (like RCE), the attacker must find a "gadget"—a piece of code that uses an undefined property of an object in a dangerous way.

### Denial of Service (DoS)
The easiest exploitation path. By polluting common properties like `toString` or `valueOf` with incompatible types (e.g., an object instead of a function), the application will crash when it implicitly tries to convert an object to a string.

```json
{"__proto__": {"toString": "crash"}}
```

### Privilege Escalation / Logic Bypass
If the application relies on an object property for authorization that is usually undefined:
```javascript
let userSession = {};
// ...
if (userSession.isAdmin) {
    grantSuperuserAccess();
}
```
Polluting `isAdmin` to `true` will instantly bypass the check.

### Remote Code Execution (RCE)
RCE in Node.js via Prototype Pollution generally requires the application to spawn child processes. The `child_process.spawn()` and `child_process.exec()` functions in Node.js accept an `options` object. If this object is not thoroughly defined, inherited properties from the polluted prototype can alter the execution environment.

**The `NODE_OPTIONS` Gadget**
If the application executes another Node.js script using `child_process.spawn('node', ['script.js'], options)`, an attacker can pollute the `env` property to inject environment variables.

```json
{
    "__proto__": {
        "env": {
            "NODE_OPTIONS": "--require /proc/self/environ"
        }
    }
}
```
By forcing Node.js to require `/proc/self/environ`, and injecting a malicious JavaScript payload into another environment variable (like an HTTP header that gets logged to the environment), the attacker can execute arbitrary JS in the context of the newly spawned process.

Another powerful gadget involves polluting properties read by template engines (like Pug, Handlebars, or EJS) to inject arbitrary JavaScript during template compilation.

## 6. Identification and Testing Methodology

### Static Analysis
Review code and third-party dependencies for unsafe use of:
- `merge()`, `deepMerge()`, `extend()`, `clone()`
- Recursive assignment loops without key validation.
Look for outdated versions of libraries like `lodash`, `jquery`, or `hoek` that had historic prototype pollution CVEs.

### Dynamic Black-Box Testing
1. Send benign pollution payloads that introduce a harmless, identifiable property.
   ```json
   {"__proto__": {"vapt_test_polluted": "yes"}}
   ```
   Or via query strings (if parsed securely by libraries like `qs`):
   ```
   ?__proto__[vapt_test_polluted]=yes
   ```
2. Trigger an endpoint that reflects the state or causes an error, and observe if the property `vapt_test_polluted` is accessible globally.
3. Use automated scanners and Burp Suite extensions (like "Server-Side Prototype Pollution") to systematically inject prototype payloads into JSON bodies and form data.

### Automated Tools for Detection
- **Server-Side Prototype Pollution (Burp Extension)**: Actively injects payloads during crawling and monitors for behavioral changes.
- **NodeJsScan**: A static analysis tool that flags insecure merge operations and dependency vulnerabilities.
- **Snyk / npm audit**: Continuously scans for outdated dependencies known to be vulnerable to prototype pollution.

## 7. Remediation and Defense

Fixing prototype pollution requires ensuring that user-controlled keys cannot modify the prototype chain.

### 1. Key Validation and Denylisting
In merge functions, explicitly reject dangerous keys:
```javascript
function safeMerge(target, source) {
    for (let key in source) {
        if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
            continue; // Skip dangerous keys
        }
        // ... continue merge
    }
}
```

### 2. Using Safe Object Creation
Create objects that do not inherit from `Object.prototype`. These objects are immune to prototype pollution.
```javascript
const safeObject = Object.create(null);
```
Since `safeObject` has no prototype, accessing `safeObject.__proto__` returns undefined, and it cannot be traversed to pollute the global scope.

### 3. Object Freezing
Freeze the global prototype early in the application lifecycle.
```javascript
Object.freeze(Object.prototype);
```
This prevents any subsequent modifications to the global prototype. While effective, this can break third-party libraries that legitimately rely on modifying the prototype.

### 4. Using Map instead of Object
When storing arbitrary key-value pairs where the keys are user-controlled, use the ES6 `Map` object instead of a plain JavaScript object. Maps are not susceptible to prototype pollution via key assignment.

## 8. Chaining Opportunities

- **[[15 - Server-Side Template Injection SSTI in Enterprise Apps]]**: Prototype pollution is frequently chained with template engines. By polluting options passed to Pug or EJS, an attacker can achieve SSTI and ultimately RCE.
- **[[08 - Privilege Escalation via Deserialization]]**: Similar concepts apply; manipulating object structures to bypass logic.
- **[[04 - SSRF Server-Side Request Forgery]]**: Polluting internal routing configuration objects or HTTP client options to redirect internal traffic to attacker-controlled servers.

## 9. Related Notes

- [[11 - .NET Deserialization ysoserial.net]]
- [[13 - GraphQL Introspection and Exploitation]]
- [[14 - Exploiting gRPC Endpoints]]
- [[09 - Insecure Direct Object References IDOR]]
- [[21 - Advanced WAF Bypassing Techniques]]
