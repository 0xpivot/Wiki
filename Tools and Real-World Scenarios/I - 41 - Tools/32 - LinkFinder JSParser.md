---
tags: [tools, vapt, utility]
difficulty: intermediate
module: "41 - Tools"
topic: "41.32 LinkFinder JSParser"
---

# JavaScript Analysis & Endpoint Discovery: LinkFinder & JSParser

## 1. Introduction to JavaScript Reconnaissance

Modern web applications are heavily reliant on client-side JavaScript. Single Page Applications (SPAs) built on sophisticated frontend frameworks like React, Angular, Vue, and Svelte offload significant rendering, routing, and business logic directly to the browser. Consequently, JavaScript files contain a treasure trove of information for a penetration tester.

Embedded within these massive, minified `.js` files are API endpoints, hidden administrative routing paths, hardcoded secrets (API keys, JWT tokens), and the structural logic of the application itself. Analyzing JavaScript is no longer an optional step; it is a critical phase of web reconnaissance. Tools like LinkFinder and JSParser automate the tedious and complex process of extracting this hidden information.

## 2. JavaScript Analysis Workflow (ASCII Diagram)

```text
+-------------------+      1. Identify JS Files      +-------------------+
| Target Web Page   |      (e.g., app.min.js,        |                   |
| (HTML Source)     | ----  chunk-vendors.js) -----> |  Attacker System  |
+-------------------+                                |                   |
                                                     +-------------------+
                                                              |
                                                              v
                                                     +-------------------+
                                                     | Analysis Tool     |
                                                     | (LinkFinder /     |
                                                     |  JSParser)        |
                                                     +-------------------+
                                                              |
                 +--------------------------------------------+
                 |
                 v
+-----------------------------------+     +-----------------------------------+
| LinkFinder (Regex-Based)          |     | JSParser (AST-Based)              |
| - Scans raw text for patterns     |     | - Builds Abstract Syntax Tree     |
| - Extracts strings looking like   |     | - Analyzes execution flow         |
|   URLs, paths (/api/v1/user)      |     | - Extracts variables, AJAX calls  |
+-----------------------------------+     +-----------------------------------+
                 |                                            |
                 v                                            v
+-----------------------------------------------------------------------------+
| Aggregated Output:                                                          |
| - Hidden API Endpoints (e.g., https://api.target.com/v2/admin/delete)       |
| - Hardcoded API Keys (e.g., X-API-KEY: "AIzaSyB...")                        |
| - Unreferenced parameters mapping to backend functions                      |
+-----------------------------------------------------------------------------+
```

## 3. LinkFinder Deep Dive

### 3.1 Overview
LinkFinder, written by Gerben Javado, is a powerful Python script that discovers endpoints and parameters buried deep within JavaScript files. It is arguably the most famous and widely utilized tool in this category. Its primary mechanism of action is advanced regular expression (Regex) matching.

### 3.2 How It Works
LinkFinder downloads the target JavaScript file (or reads it from a local directory) and immediately processes it through `jsbeautifier` to un-minify the code. This is crucial because minified code on a single line breaks many regex engines. It then applies a comprehensive set of complex regular expressions designed specifically to identify strings that look like relative paths (e.g., `/user/profile/update`), absolute URLs (e.g., `https://api.example.com/v2`), and specific predictable parameters.

### 3.3 Key Features
*   **Regex Power:** The core strength of LinkFinder is its finely tuned regex, which is highly effective at minimizing false positives while aggressively catching obscure endpoint formats.
*   **Output Formats:** It can output results cleanly to the CLI, or generate a highly interactive HTML report that highlights the exact line in the beautified JS where the endpoint was found, allowing for quick manual verification.
*   **Burp Suite Integration:** It is available as a Burp Suite extension, allowing it to passively analyze all JS files passing through the proxy during normal browsing, finding endpoints without any active scanning.

### 3.4 Usage Examples

```bash
# Analyze an online JavaScript file and output directly to CLI
python3 linkfinder.py -i https://example.com/js/app.js -o cli

# Analyze a local folder containing downloaded JS files
python3 linkfinder.py -i 'downloads/*.js' -o cli

# Generate an interactive HTML report for an online file
python3 linkfinder.py -i https://example.com/js/app.js -o report.html

# Look specifically for Burp Collaborator payloads or specific target strings
python3 linkfinder.py -i https://example.com/js/app.js -o cli -r "collaborator"
```

## 4. JSParser Deep Dive

### 4.1 Overview
While LinkFinder treats JS entirely as raw text to be regexed, JSParser takes a significantly more sophisticated approach. Originally written as a Python script utilizing Tornado and JSBeautifier, and later adapted into various other Node.js forms, JSParser utilizes actual JavaScript parsing engines (like Esprima, Acorn, or similar AST builders) to understand the code's inherent structure.

### 4.2 How It Works (AST Analysis)
JSParser builds an Abstract Syntax Tree (AST) of the JavaScript code. An AST is a tree representation of the abstract syntactic structure of source code. By analyzing the AST, the tool isn't just looking for random strings; it's explicitly looking for *functions* that make web requests (like `fetch()`, `XMLHttpRequest()`, `$.ajax()`, or Axios calls). 

Once it identifies a network request function, it traverses the AST to analyze the arguments passed to that call. This allows it to extract the endpoint URL, the HTTP method (GET, POST, PUT), and crucially, any dynamic parameters or headers included in the request body.

### 4.3 Key Features
*   **Contextual Understanding:** Because it understands the code structure, it can often determine not just *what* the endpoint is, but *how* it is used (e.g., "This path `/api/update` is called with a `POST` method containing a JSON body").
*   **Parameter Extraction:** Excellent at pulling out variable names that are used to construct requests, providing highly accurate fodder for parameter fuzzing tools.
*   **Lower False Positives:** Regex tools sometimes flag random strings that happen to look like paths. AST-based tools only flag paths that are actively used in identified network request functions.

### 4.4 Usage and Pipeline Integration
While standalone JSParser scripts exist, the *concept* of AST parsing is increasingly integrated into larger modern toolsets or custom scripts using Node.js libraries like `acorn` or `babel-parser`. Modern equivalents or successors often include specialized static application security testing (SAST) tools or custom browser automation scripts.

### 4.5 Exploiting Source Maps
Modern developers write in TypeScript or modern JavaScript, which is then compiled and heavily minified by tools like Webpack. Debugging minified code is notoriously hard, so developers often generate "Source Maps" (files ending in `.js.map`). 
If these `.map` files are inadvertently uploaded to the production server (a very common misconfiguration), tools can use them to perfectly reconstruct the original, unminified source code, complete with original variable names, developer comments, and full directory structures.
When LinkFinder or manual analysis identifies a `sourceMappingURL` comment at the bottom of a JS file, the penetration tester can download the map file and use tools like `sourcemapper` to unpack the entire frontend codebase, drastically simplifying the discovery of hidden logic and unauthenticated endpoints.

## 5. Comparison: Regex vs. AST (LinkFinder vs. JSParser)

| Feature | LinkFinder (Regex-Based) | JSParser (AST-Based) |
| :--- | :--- | :--- |
| **Analysis Method** | Regular Expressions | Abstract Syntax Tree Parsing |
| **Speed** | Very Fast | Slower (requires full code parsing) |
| **Endpoint Discovery** | Excellent (finds almost all string paths) | Good (finds paths actively used in functions) |
| **Context Extraction**| Poor (just returns a string) | Excellent (knows HTTP method, params, headers) |
| **False Positives** | Higher (random strings match regex) | Lower (analyzes actual execution flow) |

## 6. Real-World Penetration Testing Methodology

Discovering an endpoint in a JS file is only step one. The real vulnerability discovery lies in testing it.

1.  **Extraction:** Use LinkFinder on `main.js` to extract paths.
    *Result:* `/api/v1/admin/deleteUser` is found.
2.  **Contextualization:** The tester manually reviews the beautified JS surrounding the path or uses an AST tool to determine it requires a POST request and an ID parameter.
3.  **Constructing the Request:** The tester crafts a request in Burp Repeater:
    ```http
    POST /api/v1/admin/deleteUser HTTP/1.1
    Host: target.com
    Content-Type: application/json

    {"id": 123}
    ```
4.  **Testing Authorization:** The tester sends the request using an unauthenticated or low-privileged user session to test for Broken Object Level Authorization (BOLA) or Broken Function Level Authorization (BFLA). Often, developers hide admin endpoints in the UI, but forget to properly secure the API endpoint itself.

## 7. Defending Against JS Analysis

As a defender, you absolutely cannot stop attackers from downloading your client-side JavaScript. However, you can mitigate the associated risks:
- **Never Hardcode Secrets:** API keys for backend services, passwords, or cryptographic keys must never be embedded in client-side code under any circumstances.
- **Implement Robust Backend Authorization:** Never rely on "security by obscurity." Just because the UI doesn't show the "Admin" button to a standard user doesn't mean they can't call the `/api/admin` endpoint. Ensure the backend verifies the user's role on *every single* request.
- **Code Splitting / Dynamic Loading:** Only load the JavaScript required for the user's current authenticated role. Don't serve the entire admin dashboard routing logic to unauthenticated, anonymous users.

## 8. Conclusion

JavaScript analysis is a mandatory, non-negotiable step in assessing modern web applications. Tools like LinkFinder provide rapid, regex-based discovery of hidden paths and secrets, while AST-based parsers provide deeper context into how those endpoints are used. Uncovering these hidden endpoints often leads to the most critical logic vulnerabilities, bypassing front-end UI restrictions entirely.

## 9. Chaining Opportunities
- Feed extracted endpoints directly into [[30 - XSStrike dalfox]] for rapid parameter fuzzing.
- Combine with [[12 - Subdomain Enumeration]] to find hidden APIs hosted on obscure subdomains.
- Test discovered hidden endpoints for [[01 - API1 — Broken Object Level Authorization (BOLA)]].

## 10. Related Notes
- [[16 - URL and Parameter Discovery]]
- [[42 - Burp Suite Pro Features]]
- [[11 - Web Application Architecture]]
- [[31 - API Security]]
