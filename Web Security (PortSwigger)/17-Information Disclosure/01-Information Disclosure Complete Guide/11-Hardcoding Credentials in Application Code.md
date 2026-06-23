---
course: Web Security
topic: Information Disclosure
tags: [web-security]
---

## Hardcoding Credentials in Application Code

### What Is Hardcoding Credentials?

Hardcoding credentials refers to the practice of embedding sensitive information, such as passwords or cryptographic keys, directly into the source code of an application. This is a serious security risk because if the source code is compromised, the credentials can be easily extracted and used by attackers.

### Why Does This Matter?

Hardcoding credentials makes it easy for attackers to gain unauthorized access to systems and services. If an attacker gains access to the source code, they can extract the credentials and use them to authenticate to various systems, leading to potential data breaches and unauthorized access.

### How Does This Work Under the Hood?

When credentials are hardcoded in the application code, they are stored as plain text within the source files. This means that if an attacker gains access to the source code, they can simply read the credentials from the files. For example, consider the following Python code:

```python
import requests

API_KEY = "my_secret_api_key"
url = "https://api.example.com/data"

response = requests.get(url, headers={"Authorization": f"Bearer {API_KEY}"})
print(response.json())
```

In this example, the API key is hardcoded in the source code. If an attacker gains access to the source code, they can easily extract the API key and use it to make unauthorized requests to the API.

### Real-World Examples

One of the most notable examples of hardcoding credentials is the Equifax breach (CVE-2017-5638). In this breach, attackers exploited a vulnerability in Apache Struts to gain unauthorized access to the Equifax system. Once inside, they were able to extract hard-coded credentials from the source code, which allowed them to escalate their privileges and access sensitive data.

### How to Prevent / Defend

#### Detection

To detect hardcoding of credentials, you can use static code analysis tools like SonarQube or Fortify. These tools scan the source code for patterns that indicate hardcoding of credentials and flag them for review.

#### Prevention

To prevent hardcoding of credentials, you should use a secret management solution to store and manage credentials securely. Secret management solutions provide a centralized and secure way to store credentials, ensuring that they are not embedded in the source code.

Here is an example of using a secret management solution:

```python
import os
import requests

API_KEY = os.getenv("API_KEY")
url = "https://api.example.com/data"

response = requests.get(url, headers={"Authorization": f"Bearer {API_KEY}"})
print(response.json())
```

In this example, the API key is stored as an environment variable, which is accessed using `os.getenv`. This ensures that the API key is not hardcoded in the source code.

### Secure Coding Fixes

#### Vulnerable Code

```python
import requests

API_KEY = "my_secret_api_key"
url = "https://api.example.com/data"

response = requests.get(url, headers={"Authorization": f"Bearer {API_KEY}"})
print(response.json())
```

#### Fixed Code

```python
import os
import requests

API_KEY = os.getenv("API_KEY")
url = "https://api.example.com/data"

response = requests.get(url, headers={"Authorization": f"Bearer {API_KEY}"})
print(response.json())
```

In the fixed code, the API key is stored as an environment variable, which is accessed using `os.getenv`. This ensures that the API key is not hardcoded in the source code.

### Hands-On Labs

For hands-on practice with this topic, you can use the following labs:

- **PortSwigger Web Security Academy**: This lab provides exercises on detecting and preventing hardcoding of credentials.
- **OWASP Juice Shop**: This lab includes scenarios where credentials are hardcoded in the source code, and you can practice identifying and fixing these issues.

---
<!-- nav -->
[[Web Security (PortSwigger)/17-Information Disclosure/01-Information Disclosure Complete Guide/10-Hands-On Labs|Hands-On Labs]] | [[Web Security (PortSwigger)/17-Information Disclosure/01-Information Disclosure Complete Guide/00-Overview|Overview]] | [[12-How to Prevent  Defend Against Information Disclosure Vulnerabilities|How to Prevent  Defend Against Information Disclosure Vulnerabilities]]
