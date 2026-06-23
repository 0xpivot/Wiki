---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Identifying Input Parameters

The first step in exploiting an XSS vulnerability is to identify input parameters that reflect user input back to the page. In this lab, the search field is a prime candidate for injection.

### Example of a Search Field

Consider the following HTML snippet:

```html
<form action="/search" method="GET">
    <input type="text" name="query" placeholder="Search...">
    <button type="submit">Search</button>
</form>
```

When a user submits a search query, the server reflects the input back to the page. For example, if a user searches for "example", the URL might look like this:

```
http://example.com/search?query=example
```

### Analyzing the Response

To analyze the response, use Burp Suite to intercept and inspect the HTTP request and response. Here is an example of a GET request and its corresponding response:

#### HTTP Request

```http
GET /search?query=example HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Language: en-US,en;q=0.9
Connection: close
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 10 Jan 2022 12:00:00 GMT
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
    <h1>Search Results for "example"</h1>
    <p>Your search query was: example</p>
</body>
</html>
```

### Identifying Vulnerable Parameters

In the above example, the `query` parameter is reflected back to the user in the response. This makes it a potential target for an XSS attack.

---
<!-- nav -->
[[07-How to Prevent  Defend Against XSS|How to Prevent  Defend Against XSS]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/08-Lab 7 Reflected XSS into attribute with angle brackets HTML encoded/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/08-Lab 7 Reflected XSS into attribute with angle brackets HTML encoded/09-Practice Labs|Practice Labs]]
