---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.01 HTTP Parameter Pollution HPP"
---

# HTTP Parameter Pollution (HPP)

## 1. Executive Summary

HTTP Parameter Pollution (HPP) is a sophisticated web application vulnerability that emerges when a web application, its underlying framework, or the intermediary infrastructure (such as Web Application Firewalls, Load Balancers, or Proxies) improperly handles multiple HTTP parameters bearing the same name. 

Because the HTTP specification (RFC 3986 and RFC 7230) does not explicitly dictate how web servers should parse or prioritize duplicate parameters in a URL query string or URL-encoded body payload, different technologies have implemented wildly disparate parsing behaviors. Attackers exploit these discrepancies to manipulate application logic, bypass input validation mechanisms, evade Web Application Firewalls (WAFs), or achieve secondary exploits such as Cross-Site Scripting (XSS), Server-Side Request Forgery (SSRF), and Broken Object Level Authorization (BOLA).

## 2. Conceptual Foundation and the Parsing Discrepancy

At its core, HPP is an impedance mismatch vulnerability. It relies on the assumption that Security Controls (like a WAF) and Application Logic (like a backend PHP script) will interpret the exact same HTTP request in the exact same way. When this assumption breaks down, vulnerabilities arise.

When a client transmits a request containing duplicate parameters:
`GET /api/v1/profile?user_id=1001&user_id=9999 HTTP/1.1`

The infrastructure must decide how to handle the `user_id` parameter. The lack of standardization results in the following behaviors:

| Web Server / Framework / Language | Behavior with Duplicate Parameters (`?p=1&p=2`) | Processed Value |
|-----------------------------------|------------------------------------------------|-----------------|
| **PHP / Apache**                  | Prioritizes the **last** occurrence.           | `2`             |
| **ASP.NET / IIS**                 | **Concatenates** values with a comma.          | `1,2`           |
| **Node.js / Express**             | Converts into an **Array** of strings.         | `[1, 2]`        |
| **Java / Tomcat / JSP**           | Prioritizes the **first** occurrence.          | `1`             |
| **Python / Django**               | Prioritizes the **last** occurrence.           | `2`             |
| **Python / Flask**                | Prioritizes the **first** occurrence.          | `1`             |
| **Go / `net/http`**               | Prioritizes the **first** occurrence.          | `1`             |
| **Ruby on Rails**                 | Converts into an **Array** (historically last).| `[1, 2]`        |

Understanding this table is the absolute foundation of exploiting HPP. If an attacker knows the technology stack, they can craft payloads that are ignored by the WAF but executed by the backend.

## 3. In-Depth Architectural Mechanics

### Server-Side HPP
Server-Side HPP occurs entirely on the backend. The vulnerability manifests when the application uses the duplicated parameter to interact with internal systems, databases, or APIs. The attacker cannot directly see the result in the client browser (unless reflected), but the backend logic executes maliciously.

### Client-Side HPP
Client-Side HPP occurs when the application takes a polluted parameter and reflects it back into the Document Object Model (DOM) or uses it to construct subsequent URLs, scripts, or links. This often leads to DOM-based XSS, Open Redirects, or hijacking of JSONP callbacks.

## 4. ASCII Diagram: HPP Architecture Flow

```text
       [ Attacker Workstation ]
                 |
                 | Payload: ?action=view&action=delete
                 v
   +------------------------------------+
   |       Web Application Firewall     |
   |           (e.g., ModSecurity)      |
   |                                    |
   |  * Parses FIRST parameter          |
   |  * Sees: action = "view"           |
   |  * Result: VALIDATED (Allowed)     |
   +------------------------------------+
                 |
                 | Forwarded Request (Unmodified)
                 | ?action=view&action=delete
                 v
   +------------------------------------+
   |         Backend Application        |
   |             (e.g., PHP)            |
   |                                    |
   |  * Parses LAST parameter           |
   |  * Sees: action = "delete"         |
   |  * Result: INITIATES DELETION!     |
   +------------------------------------+
                 |
                 v
        [ Database / Storage ]
      (Record permanently destroyed)
```

## 5. Vulnerability Discovery and Reconnaissance

To discover HPP, penetration testers must systematically inject duplicate parameters and observe the application's response.

**Methodology:**
1. **Identify Target Parameters:** Locate endpoints that accept parameters (GET query strings, POST body parameters, headers).
2. **Inject Duplicates:** Append a duplicate parameter with a distinctly different value.
   - Original: `?page=about`
   - Test: `?page=about&page=contact`
3. **Analyze the Response:** 
   - Does the page load `about`? (First occurrence parsed).
   - Does the page load `contact`? (Last occurrence parsed).
   - Does the application crash or throw a 500 Error? (Likely array conversion or concatenation failing type checks).
   - Does it load `about,contact`? (ASP.NET comma concatenation).
4. **Tooling:** Use tools like **Burp Suite's Param Miner** extension, which can automatically attempt parameter pollution attacks by injecting duplicate keys and analyzing differences in HTTP response codes, content length, or timing.

## 6. Exploitation Scenarios (Basic to Advanced)

### A. WAF Evasion (The Classic Use Case)
Many Web Application Firewalls optimize performance by only inspecting the first occurrence of a parameter. If an attacker wants to deliver a SQL Injection payload but the WAF blocks it:
- Blocked Request: `GET /product?id=1' UNION SELECT NULL,@@version--`
- HPP Evasion Request: `GET /product?id=1&id=1' UNION SELECT NULL,@@version--`
If the WAF checks the first `id=1`, it passes. The PHP backend processes the second `id` and executes the SQLi.

### B. Bypassing Business Logic and Authorization (BOLA/IDOR)
Consider an API endpoint that updates a user's email address. It relies on a `user_id` parameter to determine which account to update, but the authorization middleware checks the permissions differently than the controller.
- Attack Payload: `POST /api/update_email?user_id=1337&user_id=1`
- **Middleware (Java/Tomcat):** Checks `user_id=1337` (Attacker's ID). The attacker is authorized to update their own profile.
- **Controller (PHP Microservice):** Processes `user_id=1` (Victim's ID, Admin). The backend updates the Admin's email to the attacker's email, resulting in account takeover.

### C. Client-Side HPP: JSONP Callback Hijacking
Applications utilizing JSONP for cross-domain data exchange often accept a `callback` parameter.
- Normal: `GET /api/data?callback=processData` -> Responds with: `processData({"status":"ok"})`
- Attack: `GET /api/data?callback=processData&callback=alert(1)`
If the server reflects the last parameter, the response becomes: `alert(1)({"status":"ok"})`, leading to immediate Cross-Site Scripting (XSS).

### D. ASP.NET Command Concatenation
Because ASP.NET concatenates duplicate parameters with a comma, attackers can construct payloads that exploit comma-delimited parsers downstream.
- Attack: `GET /download?file=C:\Windows\System32&file=cmd.exe`
- Processed as: `file=C:\Windows\System32,cmd.exe`
If this string is passed to a vulnerable command execution function, it may traverse directories or execute arbitrary binaries.

## 7. Deep Dive: JSON Parameter Pollution

HPP is not restricted to URL query strings. It actively affects JSON payloads. The JSON specification (RFC 8259) states that object keys *should* be unique, but does not strictly forbid duplicate keys, nor does it specify how parsers should handle them.
```json
{
  "username": "attacker",
  "role": "user",
  "role": "admin"
}
```
Depending on the JSON parsing library (e.g., Python's standard `json` module vs. `ujson`, or Node's `JSON.parse`):
- Most standard parsers will quietly overwrite earlier keys with later ones, making the parsed object `{"username": "attacker", "role": "admin"}`.
- If a security filter uses a parser that takes the *first* key, but the application uses a parser that takes the *last* key, an attacker bypasses the filter entirely.

## 8. Real-World Case Studies

**Case Study: Twitter / HackerOne BOLA via HPP**
In a famous public vulnerability, an attacker discovered they could bypass authorization checks on a social media platform by supplying duplicate parameters. The platform verified the authenticity and ownership of the first parameter ID, but the backend microservice that executed the action processed the last parameter ID. This allowed attackers to delete other users' posts or unsubscribe users from services by simply appending `&target_id=VICTIM_ID` to their legitimate requests.

## 9. Source Code Analysis: Vulnerable vs Patched

### Vulnerable Code (PHP + Custom WAF Logic)
```php
<?php
// Naive WAF logic - Only checks the first parameter in the query string
$query_parts = explode('&', $_SERVER['QUERY_STRING']);
$first_param = explode('=', $query_parts[0]);

if ($first_param[0] === 'id' && preg_match('/UNION|SELECT|DROP/', $first_param[1])) {
    die("WAF: Malicious payload blocked.");
}

// Application Logic - PHP uses the LAST occurrence of 'id' natively
$id = $_GET['id'];
$result = $db->query("SELECT * FROM users WHERE id = " . $id);
// Attack: ?id=1&id=1 UNION SELECT password FROM admin
?>
```

### Patched Code (Strict Parameter Handling)
```php
<?php
// Defense 1: Reject requests with duplicate parameters entirely
$query_string = $_SERVER['QUERY_STRING'];
$params = explode('&', $query_string);
$keys = [];

foreach ($params as $param) {
    $key = explode('=', $param)[0];
    if (in_array($key, $keys)) {
        http_response_code(400);
        die("Error: Duplicate parameters are not permitted.");
    }
    $keys[] = $key;
}

// Defense 2: Type casting and parameterized queries
$id = filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT);
if ($id === false) { die("Invalid ID"); }

$stmt = $db->prepare("SELECT * FROM users WHERE id = ?");
$stmt->bind_param("i", $id);
$stmt->execute();
?>
```

## 10. Defensive Posture and Remediation

1. **Strict Input Validation & Schema Enforcement:** Applications should define an explicit schema for incoming requests. If a parameter is expected to be an integer, arrays or concatenated strings should result in an immediate 400 Bad Request.
2. **Reject Duplicate Keys:** Implement middleware at the application layer that actively scans the raw HTTP request and rejects any requests containing duplicate parameter names.
3. **Architecture Alignment:** Ensure that all layers of the technology stack (WAF, Load Balancer, API Gateway, Application) utilize the exact same parsing logic.
4. **Use Standardized Formats:** Transitioning from URL-encoded forms and query parameters to strict JSON payloads can mitigate traditional HPP, provided the JSON parser is configured to reject duplicate keys.
5. **WAF Configuration:** Modern WAFs should be configured to inspect *all* occurrences of a parameter, not just the first or last, and should flag duplicate keys as anomalous behavior.

## 11. Chaining Opportunities

- **HPP + SQL Injection (SQLi):** Masking SQLi payloads from WAF inspection.
- **HPP + Cross-Site Scripting (XSS):** Injecting secondary payloads that bypass initial sanitization filters.
- **HPP + Server-Side Request Forgery (SSRF):** Overriding `url` or `host` parameters to force the server to fetch internal resources.
- **HPP + Mass Assignment:** Using polluted parameters to overwrite object properties during binding.

## 12. Related Notes

- [[02 - Mass Assignment]]
- [[01 - API1 — Broken Object Level Authorization (BOLA)]]
- [[04 - Server-Side Request Forgery (SSRF)]]
- [[07 - Cross-Site Scripting (XSS)]]
- [[11 - Web Application Firewalls (WAF) Evasion]]
