---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Identifying Input Fields

The first step in exploiting a Reflected XSS vulnerability is to identify input fields that are reflected back in the application. Common input fields include:

- Search fields
- Comment sections
- User profile forms
- Query parameters in URLs

In our lab, we have a search field where the input is reflected back in the response. We can confirm this by entering a simple string and observing the response.

### Example Request and Response

Let's send a request to the search endpoint and observe the response:

```http
GET /search?query=test HTTP/1.1
Host: vulnerable-website.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Language: en-US,en;q=0.9
Cookie: session_id=abc123
Connection: close
```

```http
HTTP/1.1 200 OK
Date: Mon, 01 Aug 2022 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: close

<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
</head>
<body>
    <h1>Search Results</h1>
    <div id="results">
        test
    </div>
</body>
</html>
```

From the response, we can see that the input `test` is reflected back in the `results` div.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/20-Lab 19 Reflected XSS with some SVG markup allowed/04-How to Prevent  Defend Against XSS|How to Prevent  Defend Against XSS]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/20-Lab 19 Reflected XSS with some SVG markup allowed/00-Overview|Overview]] | [[06-Lab Exercise Reflected XSS with SVG Markup Allowed|Lab Exercise Reflected XSS with SVG Markup Allowed]]
