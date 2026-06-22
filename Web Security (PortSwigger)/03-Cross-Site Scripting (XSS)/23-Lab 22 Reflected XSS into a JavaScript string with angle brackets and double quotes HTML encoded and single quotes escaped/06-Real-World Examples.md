---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Real-World Examples

### Recent CVEs and Breaches

#### CVE-2021-21972: WordPress REST API Reflected XSS

In 2021, a reflected XSS vulnerability was discovered in the WordPress REST API. Attackers could inject malicious scripts through the `wp-json` endpoint, leading to potential session hijacking and data theft.

#### CVE-2022-22965: Drupal Core Reflected XSS

Another example is the reflected XSS vulnerability in Drupal Core, where attackers could inject scripts through the `q` parameter in the URL, leading to unauthorized access and data exfiltration.

### Detailed Example: Reflected XSS in a Search Function

Consider a web application with a search function that reflects the input back in the JavaScript context:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
</head>
<body>
    <h1>Search Results</h1>
    <script>
        var searchTerm = "<%= request.getParameter('search') %>";
        document.write("You searched for: " + searchTerm);
    </script>
</body>
</html>
```

If the input is not properly encoded or escaped, an attacker can inject a script:

```
http://example.com/search?search='</script><script>alert(1)</script>
```

This would result in the following output:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
</head>
<body>
    <h1>Search Results</h1>
    <script>
        var searchTerm = '&lt;script&gt;alert(1)&lt;/script&gt;';
        document.write("You searched for: " + searchTerm);
    </script>
</body>
</html>
```

The single quote is escaped, but the rest of the input is not properly encoded, leading to the execution of the `alert(1)` script.

---
<!-- nav -->
[[05-How to Prevent  Defend Against XSS|How to Prevent  Defend Against XSS]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/23-Lab 22 Reflected XSS into a JavaScript string with angle brackets and double quotes HTML encoded and single quotes escaped/00-Overview|Overview]] | [[07-Understanding the Vulnerability|Understanding the Vulnerability]]
