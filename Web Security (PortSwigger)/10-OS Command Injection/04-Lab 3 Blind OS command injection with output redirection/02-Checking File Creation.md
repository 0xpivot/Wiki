---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Checking File Creation

### Verifying File Creation

After redirecting the output, you need to verify if the file was successfully created. This can be done by accessing the file directly or checking the file listing in the directory.

#### Example: Accessing the File

You can access the file directly via the browser:

```http
GET /public/images/output.txt HTTP/1.1
Host: vulnerable-app.com
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Content-Type: text/plain
Content-Length: 10

root
```

### Detection and Prevention

**Detection**:
- **File Integrity Monitoring**: Use tools like Tripwire or AIDE to monitor file integrity.
- **Regular Audits**: Conduct regular audits to check for unauthorized file creations.

**Prevention**:
- **File Permissions**: Set strict file permissions to prevent unauthorized access.
- **Use Immutable Files**: Mark important files as immutable to prevent modification.

---
<!-- nav -->
[[Web Security (PortSwigger)/10-OS Command Injection/04-Lab 3 Blind OS command injection with output redirection/01-Introduction to OS Command Injection|Introduction to OS Command Injection]] | [[Web Security (PortSwigger)/10-OS Command Injection/04-Lab 3 Blind OS command injection with output redirection/00-Overview|Overview]] | [[03-Confirming the Vulnerability|Confirming the Vulnerability]]
