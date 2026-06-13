---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.24 Service Worker Attacks"
---

# Service Worker Attacks

## Introduction
Service Workers are specialized JavaScript assets that act as proxy servers sitting between web applications, the browser, and the network (when available). They are designed to create effective offline experiences, intercept network requests, and manage background syncing or push notifications. Because they operate at such a low level—effectively man-in-the-middle (MitM) for the web application—compromising a Service Worker grants an attacker persistent, high-impact control over a user's interaction with a site.

Service Workers run in an isolated worker context, meaning they have no access to the DOM, but they have complete control over fetch events and caching within their registered scope.

## Technical Deep Dive

### Service Worker Lifecycle and Scope
1. **Registration:** A web page calls `navigator.serviceWorker.register('sw.js', { scope: '/app/' })`.
2. **Installation:** The browser downloads `sw.js` and fires the `install` event.
3. **Activation:** The worker activates and can take control of clients.
4. **Interception:** It listens for `fetch` events, intercepting HTTP requests made by the scope.

**Crucial Security Constraint (Scope):** A Service Worker can only control pages within its scope. By default, the scope is the directory of the worker file. A worker at `https://example.com/js/sw.js` can only control URLs under `/js/`. It cannot control `/admin/` unless the `Service-Worker-Allowed` HTTP header explicitly permits it.

### Vulnerability Vectors

#### 1. DOM XSS to Service Worker Takeover
If an application is vulnerable to Cross-Site Scripting (XSS), an attacker can register their own malicious Service Worker.

```javascript
// Attacker payload injected via XSS
navigator.serviceWorker.register('https://example.com/upload/malicious_sw.js', {scope: '/'})
```
**Challenge:** Service Workers must be served from the same origin. The attacker cannot register `https://attacker.com/sw.js`. They must find an endpoint on `example.com` that serves attacker-controlled JavaScript (e.g., an insecure file upload, a JSONP endpoint, or an open redirect coupled with a caching anomaly).

#### 2. Service Worker File Upload Bypass
If the application allows users to upload files and serves them from the same domain (e.g., a profile picture or document upload), an attacker can upload a malicious JS file.

If the upload directory is `/uploads/`, the attacker can register:
`navigator.serviceWorker.register('/uploads/hacker.js', {scope: '/uploads/'})`

To expand the scope to the entire site (`'/'`), the server must return the `Service-Worker-Allowed: /` header when serving the file, which is rare for upload directories but a critical misconfiguration to look for.

#### 3. Path Traversal in Registration
Sometimes, developers dynamically generate the SW path. If this path is susceptible to traversal, an attacker might point it to an API endpoint that reflects input.
`navigator.serviceWorker.register('/assets/../api/echo?text=malicious_code')`

### The Malicious Service Worker Payload
Once registered, the malicious Service Worker acts as a persistent proxy.

**Intercepting and Modifying Responses:**
```javascript
self.addEventListener('fetch', function(event) {
    if (event.request.url.includes('/login')) {
        // Exfiltrate credentials or serve a fake login page
        event.respondWith(
            fetch(event.request).then(response => {
                // Clone response, extract data, send to attacker
                return response;
            })
        );
    } else if (event.request.url.includes('app.js')) {
        // Inject persistent XSS into the main application script
        event.respondWith(
            new Response("<script>alert('Persistent Pwnage')</script>", {
                headers: { 'Content-Type': 'text/html' }
            })
        );
    }
});
```

### ASCII Diagram: Service Worker Man-in-the-Middle

```text
+-------------------+                          +-------------------+
| Victim Browser    |                          | Web Server        |
| (example.com)     |                          | (example.com)     |
|                   |                          |                   |
| 1. HTTP GET /login|------ Intercepted ------>|                   |
+-------------------+         |                +-------------------+
                              |
                              v
                +---------------------------+
                | Malicious Service Worker  |
                | (Registered via XSS)      |
                |                           |
                | 2. Clone request, steal   |
                |    creds, send to C2      |
                |                           |
                | 3. Modify response,       |
                |    inject backdoors       |
                +---------------------------+
                              |
                              | 4. Return malicious response
                              v
+-------------------+
| Victim Browser    |
| executes backdoored
| login page        |
+-------------------+
```

### Persistence Mechanism
Service Workers are notoriously persistent. Even if the initial XSS vulnerability is patched, the malicious Service Worker remains installed in the victim's browser, continually intercepting requests. It acts as an incredibly stealthy browser-based rootkit. The only ways to remove it are:
1. The user manually clears site data/caches in browser settings.
2. The developer pushes a new, benign Service Worker to overwrite the malicious one.
3. The server sets a `Clear-Site-Data` header.

### Defense and Mitigation

#### Secure Contexts
Browsers mandate that Service Workers only operate over secure contexts (HTTPS or localhost). This prevents network-level attackers from injecting them.

#### Strict Scoping
Ensure Service Workers are placed in the correct directory. Never place a Service Worker at the web root (`/sw.js`) unless absolutely necessary, and never configure the `Service-Worker-Allowed` header to expand scope broadly without extreme caution.

#### Isolate User Uploads
Serve user-uploaded content from a completely different origin (e.g., a CDN or a dedicated sandbox domain like `exampleusercontent.com`). This prevents uploaded scripts from being registered as Service Workers for the main application.

#### Service Worker Updates
Implement robust logic to update Service Workers. Use `self.skipWaiting()` and `clients.claim()` carefully, and ensure that if a worker is compromised, pushing a clean worker will successfully deregister the bad one.

### VAPT Methodology
1. **Identify Usage:** Look for `navigator.serviceWorker.register` in the application's JavaScript.
2. **Analyze Scope:** Check the scope of the registered workers.
3. **Find the Upload Vector:** Look for any functionality that allows hosting user-controlled JavaScript on the same origin. JSONP endpoints are prime targets here.
4. **Check Headers:** Look for misconfigured `Service-Worker-Allowed` headers.
5. **Chain with XSS:** If XSS is found, elevate it to persistent MitM by attempting to register a SW.

## Chaining Opportunities
- **Stored/Reflected XSS:** The absolute prerequisite for installing a rogue Service Worker if an upload vector isn't directly available.
- **JSONP Injection / Open Redirects:** Used to bypass the same-origin restriction for the Service Worker file location.
- **Cache Poisoning:** Malicious SWs can poison the CacheStorage API, ensuring malicious files are served even when offline or bypassing network checks.

## Related Notes
- [[04 - Cross-Site Scripting (XSS)]]
- [[17 - Web Cache Poisoning]]
- [[25 - Abuse of Browser APIs]]
