---
course: API Security
topic: RCE Via Deserialization in API
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain how you would identify if an API is vulnerable to YAML deserialization attacks.**

To identify if an API is vulnerable to YAML deserialization attacks, you need to inspect how the API processes incoming files or data. Specifically, look for the use of `yaml.load()` in the backend code, which can lead to arbitrary code execution if exploited. You can test this by sending a crafted YAML payload through the API and observing if the server executes unintended commands. For example, you can use tools like Burp Suite to intercept and modify requests, changing the content type to `application/x-yaml` and inserting a payload that attempts to execute a command.

**Q2. How would you exploit a YAML deserialization vulnerability in a Python-based API?**

To exploit a YAML deserialization vulnerability in a Python-based API, you can craft a payload that uses the `!!python/object/apply:` tag to invoke Python functions. For instance, you could create a payload that executes a system command using the `subprocess.call` function. Here’s an example payload:

```yaml
!!python/object/apply:subprocess.call
- ['id']
```

This payload would attempt to execute the `id` command on the server. By sending this payload to the API, you can determine if the server is vulnerable and potentially gain unauthorized access or information.

**Q3. What recent real-world examples demonstrate the risks of YAML deserialization vulnerabilities?**

One notable example is the CVE-2017-17468, which affected several Python libraries including PyYAML. This vulnerability allowed attackers to execute arbitrary code by crafting malicious YAML input. Another example is the CVE-2019-10149, which affected the Kubernetes API server. Attackers could exploit this vulnerability to gain elevated privileges within a Kubernetes cluster. Both of these cases highlight the critical importance of securing against YAML deserialization vulnerabilities.

**Q4. How would you configure an API to prevent YAML deserialization attacks?**

To prevent YAML deserialization attacks, you should avoid using `yaml.load()` and instead use `yaml.safe_load()`, which does not allow for object instantiation and thus mitigates the risk of arbitrary code execution. Additionally, ensure that all input data is validated and sanitized before being processed. Implementing strict input validation and using secure coding practices can help prevent such vulnerabilities. Regularly updating dependencies and conducting security audits can also help mitigate risks.

**Q5. Explain why it is important to validate and sanitize input data in APIs to prevent YAML deserialization attacks.**

Validating and sanitizing input data is crucial in preventing YAML deserialization attacks because it ensures that only safe and expected data formats are processed. By validating input, you can detect and reject malformed or malicious data, reducing the risk of exploitation. Sanitization involves cleaning input data to remove any potentially harmful elements, such as unexpected tags or characters. This helps prevent attackers from injecting malicious payloads that could lead to arbitrary code execution or other security breaches.

---
<!-- nav -->
[[02-Remote Code Execution via Deserialization in APIs|Remote Code Execution via Deserialization in APIs]] | [[API Security/23-RCE Via Deserialization in API/02-RCE Demonstration/00-Overview|Overview]]
