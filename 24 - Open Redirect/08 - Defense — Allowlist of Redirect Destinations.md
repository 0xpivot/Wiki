---
tags: [vapt, open-redirect, defense, advanced]
difficulty: advanced
module: "24 - Open Redirect"
topic: "24.08 Defense — Allowlist of Redirect Destinations"
---

# 24.08 — Defense: Allowlist of Redirect Destinations

## What is it?
Defending against Open Redirects is conceptually simple but practically difficult because modern applications have extremely complex navigation flows. 

Relying on blocklists (e.g., blocking `http://`) or naive regex matching is highly prone to bypasses via URL parsing quirks (`/\`, `//`, `@`). 

The only mathematically secure way to prevent Open Redirects is to implement strict **Allowlisting**. This can take two forms:
1. **Indirect References (Tokenization):** The client never passes a URL. It passes an ID or token that the server maps to a URL.
2. **Strict Relative Pathing / Domain Whitelisting:** The server mathematically parses the URL and ensures the hostname exactly matches an allowed list, or ensures the path is strictly relative.

Think of it like a train switch operator. You don't let passengers pull levers to tell the train where to go. You give the passengers a menu of approved stations. When they pick "Station 3", you internally route the train to the pre-approved coordinates for Station 3.

## Core Defense 1: Indirect References (The Gold Standard)
Instead of passing `?next=/dashboard`, pass `?next=dashboard`. On the backend, use a dictionary map. If an attacker passes `?next=http://evil.com`, it won't exist in the dictionary, and the server defaults to the homepage.

**Python (Flask) Example:**
```python
@app.route('/login')
def login():
    target = request.args.get('next')
    
    # Secure Map
    allowed_routes = {
        'dashboard': '/user/dashboard',
        'settings': '/user/settings',
        'cart': '/checkout/cart'
    }
    
    # If the key exists, redirect there. Otherwise, default to home.
    safe_url = allowed_routes.get(target, '/home')
    return redirect(safe_url)
```

## Core Defense 2: Strict URL Parsing (If dynamic URLs are mandatory)
If your application *must* support dynamic relative redirects, you must use your language's built-in URL parsing library to guarantee the input is safe. 

**Rules for safe dynamic redirects:**
1. Parse the URL into its components (Scheme, Host, Path).
2. If it is intended to be a local relative path, ensure the Scheme and Host are completely empty.
3. Explicitly reject protocol-relative URLs (`//`).

**Java Example:**
```java
import java.net.URI;
import java.net.URISyntaxException;

public class RedirectValidator {
    public boolean isSafeLocalRedirect(String url) {
        if (url == null || url.trim().isEmpty()) {
            return false;
        }

        try {
            URI uri = new URI(url);
            
            // 1. Must not have a scheme (http/https)
            // 2. Must not have a host (domain name)
            // 3. Must start with a single slash (relative path)
            // 4. Must not start with double slashes (protocol-relative //evil.com)
            if (uri.getScheme() == null && 
                uri.getHost() == null && 
                url.startsWith("/") && 
                !url.startsWith("//")) {
                return true;
            }
        } catch (URISyntaxException e) {
            return false; // Malformed URLs are unsafe
        }
        
        return false;
    }
}
```

## Summary Checklist for Open Redirect Defense
- [ ] Are redirect parameters mapped to indirect references (IDs) rather than raw URLs?
- [ ] If raw URLs are used, is the URL parsed using a robust backend library (not just Regex)?
- [ ] Are Protocol-Relative URLs (`//evil.com`) explicitly caught and blocked?
- [ ] In OAuth flows, is the `redirect_uri` strictly checked against a pre-registered, exact-match whitelist on the Authorization Server?
- [ ] If making outbound HTTP requests (SSRF defense), has automatic redirect following been disabled in the HTTP client?

## Related Notes
- [[24.01 What is Open Redirect?]]
- [[24.03 Bypass Techniques]]
- [[24.06 Open Redirect + OAuth (token stealing)]]
