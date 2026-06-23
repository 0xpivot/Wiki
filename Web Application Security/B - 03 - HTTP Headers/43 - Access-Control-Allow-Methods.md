---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.43 Access-Control-Allow-Methods — CORS Method Control"
---

# 03.43 — Access-Control-Allow-Methods

## What is it?

`Access-Control-Allow-Methods` is an HTTP response header returned during a CORS preflight request (`OPTIONS`) indicating which HTTP methods (e.g., `GET`, `POST`, `PUT`, `DELETE`, `PATCH`) are permitted when making a cross-origin request.

If a web application wants to send a non-simple request (such as a request with a method other than `GET`, `HEAD`, or `POST`, or with custom content types/headers) to another domain, the browser first sends an `OPTIONS` request. The server responds with `Access-Control-Allow-Methods` to declare the HTTP methods it allows. If the method intended for the actual request is not in this list, the browser blocks the actual request.

### Beginner Explanation
Imagine you want to borrow a book from a library, but you also want to draw in it or return it to a different shelf. Before doing this, you ask the librarian: "Am I allowed to edit or delete pages in this book?" The librarian responds: "You can only read and borrow, but not delete." 
`Access-Control-Allow-Methods` is like that list of permitted actions. It tells the browser what actions (methods like `GET` for reading, `PUT` for editing, or `DELETE` for deleting) the website on the other domain is allowed to perform on the server.

---

## Format

```
Access-Control-Allow-Methods: <method>, <method>, ...
```

Examples:
- `Access-Control-Allow-Methods: GET, POST` (Only simple retrieving and posting are allowed)
- `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS` (Allows editing and deleting resources)
- `Access-Control-Allow-Methods: *` (Wildcard: allows any HTTP method, though credentials cannot be used with wildcards in some older browser implementations)

---

## Categories
- **Security Concept:** Cross-Origin Resource Sharing (CORS)
- **Header Type:** Response Header
- **Context:** Web Application Security / API Endpoint Protection

---

## Use Cases

1. **API Security Hardening:** Restricting third-party web applications to safe actions (e.g., only letting external apps fetch public data using `GET`, while preventing them from performing modifications via `PUT` or `DELETE`).
2. **Feature Control:** Allowing internal or specific trusted subdomains to update/delete data cross-origin, while restricting other origins.
3. **CORS Preflight Responses:** Responding to `OPTIONS` preflight requests so browsers know if they can proceed with the primary API call.

---

## Security Implication: Cross-Origin PUT/DELETE/PATCH

If state-changing methods (such as `PUT`, `PATCH`, `DELETE`) are allowed cross-origin and combined with a loose `Access-Control-Allow-Origin` (ACAO) policy and credentials enabled (`Access-Control-Allow-Credentials: true`), attackers can perform actions on behalf of authenticated users.

```
SCENARIO: An API allows DELETE requests cross-origin from any origin with credentials.

1. A victim is logged into target.com.
2. The victim visits evil.com.
3. evil.com executes JavaScript:
   fetch('https://target.com/api/user/settings', {
     method: 'DELETE',
     credentials: 'include'
   });
4. The browser sends a preflight OPTIONS request.
5. The server responds with:
   Access-Control-Allow-Origin: https://evil.com
   Access-Control-Allow-Methods: GET, POST, DELETE
   Access-Control-Allow-Credentials: true
6. The browser sends the actual DELETE request containing the victim's session cookies.
7. The victim's settings are deleted.
```

---

## Simple Methods (No Preflight Needed)

The methods `GET`, `POST`, and `HEAD` are classified as **simple methods**. They do not trigger a preflight `OPTIONS` request. 
- Even without the `Access-Control-Allow-Methods` header, a browser will send `GET` or `POST` requests cross-origin.
- The browser will block the JavaScript from *reading* the response if the server does not return the correct `Access-Control-Allow-Origin` header, but the server side actions (mutations) may still execute.
- **CSRF Risk:** Because simple methods bypass the preflight check, they can be targeted using standard Cross-Site Request Forgery (CSRF) via simple HTML forms or image requests.

---

## Commands

To check the allowed HTTP methods for a CORS-enabled endpoint, send an `OPTIONS` request mimicking a preflight call using `curl`. You must include the `Origin` and `Access-Control-Request-Method` headers.

```bash
curl -X OPTIONS -I -s "https://httpbin.org/status/200" \
  -H "Origin: https://example.com" \
  -H "Access-Control-Request-Method: DELETE"
```

---

## Sample Output

A secure server response to a preflight request will specify only the necessary allowed methods:

```http
HTTP/2 200 OK
Date: Tue, 16 Jun 2026 10:20:38 GMT
Content-Type: text/html; charset=utf-8
Connection: keep-alive
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST
Access-Control-Allow-Headers: Content-Type
Access-Control-Max-Age: 86400
Access-Control-Allow-Credentials: true
```

---

## How to Fix / Secure

| Risk / Issue | Mitigation / Action |
|--------------|---------------------|
| **Dangerous Methods Allowed** | Do not include `PUT`, `PATCH`, or `DELETE` in `Access-Control-Allow-Methods` unless strictly required for cross-origin partners. |
| **Wildcard Allowed Methods** | Avoid returning `*` for `Access-Control-Allow-Methods` in authenticated environments. Explicitly list allowed methods. |
| **CORS and CSRF Link** | Ensure that all state-changing endpoints (even those requiring preflight) are protected with anti-CSRF tokens or `SameSite` cookie policies. |

---

## Related Notes
- [[41 - Access-Control-Allow-Origin]] — ACAO header
- [[42 - Access-Control-Allow-Credentials]] — credential risk
- [[Module 08 - CORS]] — full CORS exploitation
