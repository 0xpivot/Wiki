---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 15"
---

# Web QnA - Module 15 - Cross-Origin Resource Sharing CORS

## Custom ASCII Diagram

```text
    [Victim's Browser]                                [Vulnerable API Server]
          |                                                    |
          | 1. Visits https://attacker.com                     |
          |--------------------------------------------------->|
          |                                                    |
          | 2. Attacker JS executes:                           |
          |    fetch('https://api.bank.com/user/data', {       |
          |        credentials: 'include'                      |
          |    })                                              |
          |                                                    |
          | 3. Browser sends preflight OPTIONS request         |
          |    Origin: https://attacker.com                    |
          |--------------------------------------------------->|
          |                                                    |
          | 4. Server reflects Origin blindly                  |
          |<---------------------------------------------------|
          |    Access-Control-Allow-Origin: https://attacker.com
          |    Access-Control-Allow-Credentials: true          |
          |                                                    |
          | 5. Browser sends actual GET request + Cookies      |
          |--------------------------------------------------->|
          |                                                    |
          | 6. Server responds with sensitive JSON data        |
          |<---------------------------------------------------|
          |                                                    |
          | 7. Attacker JS reads JSON and exfiltrates data     |
          v                                                    v
```

## Real-World Attack Scenario

You are assessing a modern Single Page Application (SPA) that relies heavily on a backend microservice architecture. During traffic analysis, you intercept a request to the user profile endpoint: `https://api.corporate.local/v1/profile`. You modify the HTTP `Origin` header in your request to `Origin: https://evil.com`.

The API server responds with the sensitive JSON profile data, but crucially, it includes the following headers: 
`Access-Control-Allow-Origin: https://evil.com`
`Access-Control-Allow-Credentials: true`

You realize the backend developer implemented a flawed CORS policy that dynamically reflects whatever origin is supplied in the request header, likely to easily support multiple internal testing environments. 

To exploit this, you create a malicious webpage hosted on `https://evil.com`. The page contains JavaScript that uses the `fetch()` API to request `https://api.corporate.local/v1/profile` with `credentials: 'include'` set. You send the link to a corporate employee. When they browse to your site, their browser automatically appends their active authentication cookies for the API. Because the API reflects the malicious origin and allows credentials, the browser permits your JavaScript to read the resulting JSON response. Your script then exfiltrates the employee's PII and internal API tokens to your command-and-control server.

## Chaining Opportunities

1. **CORS Misconfiguration + Network Pivot:** Exploiting a permissive CORS policy on an internal corporate application to force an external victim's browser to map and exfiltrate data from internal, non-routable IP addresses (Internal SSRF via CORS).
2. **CORS + Cache Poisoning:** Forcing the server to cache a response containing malicious `Access-Control-Allow-Origin` headers, thereby globally poisoning the API endpoint for all users, opening it up to universal cross-origin attacks.
3. **CORS + CSRF:** While CORS primarily protects reading data, permissive CORS headers can sometimes bypass anti-CSRF token mechanisms if the attacker can use CORS to read the token first before submitting the state-changing request.
4. **CORS Null Origin + Local File Exfiltration:** Exploiting configurations that allow the `null` origin. An attacker can use an iframe with a `data:` URI or a local HTML file to generate a `null` origin request, bypassing poorly written regex filters and stealing data.

## Related Notes

- [[03 - Cross-Site Scripting XSS]]
- [[11 - Cross-Site Request Forgery CSRF]]
- [[22 - HTML5 Security Features]]
- [[24 - Browser Same Origin Policy SOP]]
- [[28 - WebSockets Security]]

---

## Formal Technical Questions

### Q1: Define the Same-Origin Policy (SOP). Why is CORS necessary if the SOP exists?

**Answer:**
The **Same-Origin Policy (SOP)** is a fundamental security mechanism implemented by web browsers. It restricts how a document or script loaded from one origin can interact with a resource from another origin. An "origin" is defined by the combination of the URI scheme, hostname, and port number (e.g., `https://example.com:443`). By default, SOP prevents a script on `site-a.com` from reading data returned by `site-b.com`.

**CORS (Cross-Origin Resource Sharing)** is necessary because modern web applications are rarely monolithic. An application hosted on `frontend.com` often needs to legitimately interact with an API hosted on `api.backend.com`. SOP would block this necessary interaction. 
CORS provides a controlled, secure mechanism to *relax* the Same-Origin Policy. It uses specific HTTP headers to allow servers to declare which external origins are permitted to read their data, bridging the gap between strict security and functional application architecture.

### Q2: What is a CORS "Preflight" request? When and why does the browser send it?

**Answer:**
A CORS preflight request is an HTTP `OPTIONS` request sent by the browser *before* the actual intended request. Its purpose is to check with the server if the upcoming cross-origin request is safe and permitted.

The browser automatically sends a preflight request when the actual request is considered "complex" or "non-simple". A request triggers a preflight if it meets conditions such as:
- Using HTTP methods other than `GET`, `HEAD`, or `POST`. (e.g., `PUT`, `DELETE`).
- Using a `POST` request with a `Content-Type` other than `application/x-www-form-urlencoded`, `multipart/form-data`, or `text/plain` (e.g., using `application/json` triggers a preflight).
- Including custom HTTP headers (e.g., `Authorization`, `X-Custom-Header`).

The server responds to the `OPTIONS` request with `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers`. If the server approves, the browser proceeds to send the actual request. This protects legacy servers that do not understand CORS from receiving unexpected and potentially destructive cross-origin requests.

---

## Scenario-Based Questions

### Q3: You notice a server responds with `Access-Control-Allow-Origin: *`. However, when you try to perform a cross-origin `fetch()` that includes cookies to steal user data, the browser blocks it. Why does this fail, and what server configuration is required for it to succeed?

**Answer:**
This fails due to a built-in security restriction in the CORS specification. 

When a server uses the wildcard `*` for the `Access-Control-Allow-Origin` header, it is declaring that the resource is completely public. To prevent mass data exposure of authenticated sessions, the specification dictates that browsers **will not** attach credentials (cookies, HTTP auth, client TLS certs) to a request if the ACAO header is a wildcard `*`.

Furthermore, if the JavaScript `fetch()` call explicitly sets `credentials: 'include'`, the browser expects the server to explicitly return:
`Access-Control-Allow-Credentials: true`

For an attacker to successfully steal authenticated data via CORS, the server must be misconfigured to return **both**:
1. `Access-Control-Allow-Origin: https://attacker.com` (It must explicitly name the attacker's origin, not a wildcard).
2. `Access-Control-Allow-Credentials: true`.

### Q4: During code review, you find the following logic for setting CORS headers:
```javascript
let origin = req.headers.origin;
if (origin.endsWith('trustedcompany.com')) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Access-Control-Allow-Credentials', 'true');
}
```
### How would you exploit this flawed validation?

**Answer:**
This is a classic regex/string-matching bypass vulnerability. The developer intended to only allow subdomains of `trustedcompany.com` (e.g., `api.trustedcompany.com`).

However, the `endsWith()` function only checks the tail end of the string. As an attacker, I can bypass this by registering a completely different domain that happens to end with the required string. 

I would register the domain:
`nottrustedcompany.com` or `eviltriustedcompany.com`

When I send a request from `https://nottrustedcompany.com`, the validation `origin.endsWith('trustedcompany.com')` evaluates to `true`. The server will dynamically reflect my malicious origin and allow credentials, leading to a full CORS bypass and data exfiltration.

---

## Deep-Dive Defensive Questions

### Q5: How do you properly configure CORS for an API that needs to be accessed by multiple, specific subdomains, but must remain secure against unauthorized cross-origin access?

**Answer:**
To securely configure CORS for multiple origins without falling victim to reflection attacks, the server must implement strict whitelisting.

1. **Maintain a Hardcoded Array:** Define an explicit array of fully qualified, trusted origins in the backend configuration.
   ```javascript
   const allowedOrigins = [
       'https://app.trusted.com',
       'https://dashboard.trusted.com'
   ];
   ```
2. **Exact String Matching:** When an incoming request arrives, extract the `Origin` header and perform an exact string match (or use a highly restrictive, well-tested Regex that anchors both the beginning `^` and end `$`) against the whitelist.
3. **Conditional Header Setting:**
   ```javascript
   const requestOrigin = req.headers.origin;
   if (allowedOrigins.includes(requestOrigin)) {
       res.setHeader('Access-Control-Allow-Origin', requestOrigin);
       res.setHeader('Access-Control-Allow-Credentials', 'true');
   } else {
       // Do not set CORS headers at all, letting the browser block it
   }
   ```
This approach avoids dynamic reflection and prevents bypasses associated with weak string methods like `endsWith()` or `includes()`.

### Q6: Can a permissive CORS policy (`Access-Control-Allow-Origin: *`) be dangerous on a public API that does not require authentication or cookies?

**Answer:**
While a wildcard CORS policy on a truly public, unauthenticated API (like a public weather API) is generally considered safe and standard practice, it can become dangerous depending on the internal network context and application architecture.

1. **Intranet Port Scanning and SSRF via Client:** If the public API is accessible internally by corporate employees, a permissive CORS policy can be abused. An attacker can trick an employee into visiting a malicious site. The malicious site can use CORS to instruct the employee's browser to scan internal network ranges or interact with internal APIs that share the same permissive CORS policy, effectively using the employee's browser as an internal pivot point.
2. **Denial of Service (DoS):** If the API is computationally expensive, attackers can easily host JavaScript on thousands of distributed websites, forcing visitors' browsers to silently bombard the public API with cross-origin requests, leading to a distributed application-layer DoS. 
Therefore, even for public APIs, it is often best practice to restrict CORS to known consumers if possible, or implement strict rate limiting to mitigate client-side abuse.
