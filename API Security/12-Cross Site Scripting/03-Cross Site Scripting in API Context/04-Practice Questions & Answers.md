---
course: API Security
topic: Cross Site Scripting
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain the difference between reflected, stored, and blind XSS attacks in the context of APIs.**

Reflected XSS occurs when the malicious script is reflected off a web server, typically via a search query or URL parameter. For example, if an API endpoint reflects user input without proper sanitization, an attacker can craft a URL that includes a script tag, which gets executed when the victim visits the URL.

Stored XSS happens when the malicious script is permanently stored on the target servers, such as in a database. An example would be a comment system where user-submitted comments are stored and later displayed to other users. If the comments are not properly sanitized, an attacker can insert a script that executes every time someone views the comment.

Blind XSS occurs when the injected script does not directly affect the user viewing the page but instead sends data to another location, often the attacker’s server. In an API context, this might involve submitting feedback to an admin panel where the script executes when the admin views the feedback.

**Q2. How can you detect and mitigate XSS vulnerabilities in an API that handles user registration?**

To detect XSS vulnerabilities in a user registration API, you should test the API endpoints with various payloads that include script tags. For instance, you can use payloads like `<script>alert('XSS')</script>` in the `username` field during registration.

Mitigation strategies include:
1. Input validation: Ensure that all inputs are validated against expected formats.
2. Output encoding: Encode all user inputs before rendering them in the response.
3. Content Security Policy (CSP): Implement a strict CSP to limit the sources from which scripts can be loaded.
4. Use of security headers: Set appropriate HTTP headers like `X-XSS-Protection`.

Example of setting a CSP header:
```http
Content-Security-Policy: default-src 'self'
```

**Q3. Describe a recent real-world example of an XSS vulnerability in an API and explain how it was exploited.**

One notable example is the GitHub XSS vulnerability disclosed in 2020 (CVE-2020-28496). This vulnerability allowed attackers to inject malicious JavaScript into the user interface of GitHub repositories. The vulnerability was present in the way GitHub handled certain URLs and user input.

Attackers could craft a URL that included a script tag, which would execute when the victim visited the URL. For instance, a URL like `https://github.com/<script>alert('XSS')</script>` could be used to trigger the vulnerability.

The exploitation involved tricking users into visiting a crafted URL, which would then execute the injected script within the context of the GitHub domain. This could potentially lead to session hijacking or other malicious activities.

**Q4. How would you exploit a stored XSS vulnerability in an API that handles comments?**

To exploit a stored XSS vulnerability in an API that handles comments, follow these steps:

1. Identify the API endpoint responsible for storing comments, e.g., `/api/v2/comments`.
2. Craft a payload that includes a script tag, such as `<script>alert('XSS')</script>`.
3. Submit the payload to the API using a POST request to store the comment.
4. Ensure that the comment is rendered in the HTML response when other users view it.
5. When another user views the comment, the script will execute in their browser, leading to the XSS attack.

Example of a POST request to submit the comment:
```http
POST /api/v2/comments HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "comment": "<script>alert('XSS')</script>"
}
```

**Q5. How can you configure an API to prevent XSS attacks when handling user feedback submitted to an admin panel?**

To prevent XSS attacks when handling user feedback submitted to an admin panel, you should implement the following measures:

1. Sanitize user input: Ensure that all user-submitted feedback is properly sanitized to remove any potential script tags.
2. Use output encoding: Encode all user inputs before rendering them in the response.
3. Implement a Content Security Policy (CSP): Set a strict CSP to limit the sources from which scripts can be loaded.
4. Use security headers: Set appropriate HTTP headers like `X-XSS-Protection` to enhance security.

Example of setting a CSP header:
```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
```

By implementing these measures, you can significantly reduce the risk of XSS attacks in your API.

---
<!-- nav -->
[[03-Cross-Site Scripting (XSS) in API Context|Cross-Site Scripting (XSS) in API Context]] | [[API Security/12-Cross Site Scripting/03-Cross Site Scripting in API Context/00-Overview|Overview]]
