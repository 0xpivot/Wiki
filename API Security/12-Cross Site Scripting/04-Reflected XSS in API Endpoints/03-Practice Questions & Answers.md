---
course: API Security
topic: Cross Site Scripting
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what is meant by "reflected cross-site scripting (XSS)" in the context of API endpoints.**

Reflected Cross-Site Scripting (XSS) occurs when an attacker injects malicious scripts into a web page viewed by other users. In the context of API endpoints, this happens when an API endpoint reflects user input directly in its response without proper sanitization. For instance, if a GET request to an API endpoint includes a parameter that is echoed back in the response, an attacker might inject a script into this parameter, which gets executed in the user's browser when they view the response.

**Q2. How can you identify potential reflected XSS vulnerabilities in API endpoints?**

To identify potential reflected XSS vulnerabilities in API endpoints, you should:

1. **Inspect Input Handling**: Check how the API handles inputs from requests. Look for any parameters that are directly included in the response without being sanitized or encoded.
   
2. **Test with Malicious Inputs**: Inject various types of potentially harmful content into the API parameters, such as `<script>alert('XSS')</script>` or encoded versions like `%3Cscript%3Ealert('XSS')%3C/script%3E`. Observe if the injected content appears in the response and executes in the browser.

3. **Analyze Response Content-Type**: Ensure that the API response has appropriate `Content-Type` headers. Responses containing script tags should be served with `text/html` or similar content types, while JSON responses should be served with `application/json`.

4. **Use Tools**: Utilize tools like Burp Suite, OWASP ZAP, or Postman to automate testing and detect reflected XSS vulnerabilities.

**Q3. How would you exploit a reflected XSS vulnerability in an API endpoint?**

To exploit a reflected XSS vulnerability in an API endpoint, follow these steps:

1. **Identify Vulnerable Parameters**: Find parameters in the API request that reflect user input in the response.

2. **Inject Malicious Code**: Insert a script tag into the vulnerable parameter. For example, if the API endpoint is `/api/users?name=<script>alert('XSS')</script>`, the response should include this script tag.

3. **Trigger Execution**: Ensure the response is rendered in a context where the script will execute, such as within an HTML document. This often involves tricking a user into clicking a link or visiting a crafted URL.

Here’s an example payload:

```html
<script>alert('XSS');</script>
```

Encoded version:

```html
%3Cscript%3Ealert('XSS')%3C/script%3E
```

**Q4. How would you configure an API endpoint to prevent reflected XSS attacks?**

To prevent reflected XSS attacks in an API endpoint, implement the following measures:

1. **Input Validation**: Validate and sanitize all user inputs before using them in responses. Use libraries or functions that properly escape special characters.

2. **Output Encoding**: Encode output data to ensure that it cannot be interpreted as executable code. For example, use `htmlspecialchars()` in PHP or equivalent functions in other languages.

3. **Content Security Policy (CSP)**: Implement a Content Security Policy (CSP) to restrict the sources from which scripts can be loaded. This helps mitigate the impact of XSS attacks.

4. **HTTP Headers**: Set appropriate HTTP headers like `Content-Type` to ensure the response is treated correctly by the client. For example, set `Content-Type: application/json` for JSON responses.

Example of setting CSP header:

```http
Content-Security-Policy: default-src 'self'
```

**Q5. Explain a recent real-world example of a reflected XSS vulnerability in an API endpoint.**

A notable recent example is the reflected XSS vulnerability found in GitHub's API. In 2021, researchers discovered that certain API endpoints were reflecting user input without proper sanitization. Specifically, the `/repos/{owner}/{repo}/issues` endpoint was vulnerable to reflected XSS if an attacker could inject malicious JavaScript into issue titles or comments.

The vulnerability allowed attackers to craft URLs that, when clicked by a user, could execute arbitrary JavaScript in the context of the GitHub domain. This could lead to session hijacking or other malicious actions.

GitHub quickly patched the vulnerability by ensuring proper sanitization of user inputs in their API responses. This example highlights the importance of thorough input validation and output encoding in API security.

**Q6. How can you use Burp Suite to test for reflected XSS vulnerabilities in API endpoints?**

To test for reflected XSS vulnerabilities in API endpoints using Burp Suite, follow these steps:

1. **Intercept Requests**: Use Burp Suite's proxy to intercept HTTP requests made by your browser or API client.

2. **Modify Requests**: Inject malicious payloads into the request parameters. For example, replace a parameter value with `<script>alert('XSS')</script>`.

3. **Send Modified Requests**: Forward the modified requests to the server and observe the response. Check if the injected script appears in the response.

4. **Repeater Tool**: Use Burp Suite's Repeater tool to manually modify and resend requests. This allows you to fine-tune the payloads and easily test different scenarios.

5. **Intruder Tool**: Use the Intruder tool to automate the process of injecting multiple payloads into the request parameters. This can help identify vulnerabilities more efficiently.

Example of using Burp Suite Repeater:

1. Capture a request to the API endpoint.
2. Modify the request body or query parameters to include a script tag.
3. Send the request and check the response for the presence of the script tag.

By systematically testing with Burp Suite, you can effectively identify and exploit reflected XSS vulnerabilities in API endpoints.

---
<!-- nav -->
[[02-Introduction to Reflected Cross-Site Scripting (XSS) in API Endpoints|Introduction to Reflected Cross-Site Scripting (XSS) in API Endpoints]] | [[API Security/12-Cross Site Scripting/04-Reflected XSS in API Endpoints/00-Overview|Overview]]
