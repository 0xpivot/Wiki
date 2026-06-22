---
course: Web Security
topic: Information Disclosure
tags: [web-security]
---

## Introduction to Information Disclosure

Information disclosure is a type of vulnerability that occurs when sensitive data is unintentionally exposed to unauthorized users. This can happen through various means, such as debug pages, error messages, or misconfigured server settings. In this chapter, we will focus on a specific scenario involving an information disclosure vulnerability on a debug page. We will cover the background theory, the mechanics of the vulnerability, recent real-world examples, and how to prevent and defend against such vulnerabilities.

### Background Theory

#### What is Information Disclosure?

Information disclosure occurs when a system or application inadvertently reveals sensitive information to unauthorized parties. This can include:

- **Sensitive Data:** Such as passwords, API keys, or other confidential information.
- **System Details:** Including internal IP addresses, server configurations, or database schemas.
- **Error Messages:** That reveal internal system states or code snippets.

#### Why Does Information Disclosure Matter?

Information disclosure can lead to serious security risks, including:

- **Data Breaches:** Unauthorized access to sensitive data can result in data breaches.
- **Exploitation:** Attackers can use disclosed information to craft more sophisticated attacks.
- **Reputation Damage:** Public exposure of sensitive data can damage an organization's reputation.

### Mechanics of Information Disclosure on Debug Pages

#### What is a Debug Page?

A debug page is a special page within an application that provides detailed information about the application's internal state. These pages are typically used by developers during the development and debugging phases but should not be accessible in production environments.

#### How Does Information Disclosure Occur on Debug Pages?

Debug pages often contain sensitive information such as:

- **Environment Variables:** Such as API keys, database connection strings, or secret keys.
- **Internal Server Details:** Including IP addresses, server configurations, or database schemas.
- **Error Logs:** That may reveal internal system states or code snippets.

If these pages are not properly secured, attackers can access them and extract sensitive information.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example of information disclosure through debug pages is the breach of a major financial institution in 2021. The institution had a debug page that was accessible via a simple URL. This page contained sensitive information, including API keys and database connection strings. An attacker discovered this page and used the disclosed information to gain unauthorized access to the institution's systems.

Another example is a breach of a popular e-commerce platform in 2022. The platform had a debug page that was accessible via a specific URL. This page contained sensitive information, including internal server details and error logs. An attacker discovered this page and used the disclosed information to craft more sophisticated attacks.

### Lab Setup and Walkthrough

#### Accessing the Lab

To access the lab, follow these steps:

1. Visit the URL `https://portswigger.net/web-security`.
2. Click on the sign-up button to create an account.
3. Log in to your account.
4. Click on the "Academy" tab.
5. Select "All Labs".
6. Search for "information disclosure" and select lab number two titled "Information Disclosure on Debug Page".

#### Lab Goal

The goal of this lab is to find the debug page and obtain the secret key environment variable from the debug page.

### Step-by-Step Walkthrough

#### Accessing the Application

Once you have accessed the lab, you will see the built-in browser in Burp Suite. All your requests are already being passed through the Burp Suite proxy.

1. Click on a few pages to familiarize yourself with the application.
2. Look at the URL of the application. For example, the URL might be `http://0a.be`.

#### Finding the Debug Page

To find the debug page, you can use various techniques such as:

- **Manual Exploration:** Try appending different paths to the base URL to see if any debug pages are accessible.
- **Automated Tools:** Use tools like Burp Suite Intruder to automate the process of finding debug pages.

For example, you can try appending `/debug` to the base URL:

```plaintext
http://0a.be/debug
```

If the debug page is accessible, you will see sensitive information such as environment variables.

#### Extracting the Secret Key

Once you have found the debug page, you can extract the secret key environment variable. For example, the debug page might contain the following information:

```plaintext
SECRET_KEY=abc123
```

### Full HTTP Request and Response

Here is an example of the full HTTP request and response:

```http
GET /debug HTTP/1.1
Host: 0a.be
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Language: en-US,en;q=0.9
Connection: close

HTTP/1.1 200 OK
Date: Mon, 01 Aug 2022 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: close

<!DOCTYPE html>
<html>
<head>
    <title>Debug Page</title>
</head>
<body>
    <h1>Debug Information</h1>
    <pre>
        SECRET_KEY=abc123
        DATABASE_URL=jdbc:mysql://localhost:3306/mydb?useSSL=false&amp;serverTimezone=UTC
    </pre>
</body>
</html>
```

### Pitfalls and Common Mistakes

#### Common Mistakes

- **Not Securing Debug Pages:** Debug pages should be secured and not accessible in production environments.
- **Hardcoding Sensitive Information:** Sensitive information should not be hardcoded in the application. Instead, use environment variables or configuration files.
- **Improper Error Handling:** Error messages should not reveal internal system states or code snippets.

### How to Prevent / Defend Against Information Disclosure

#### Detection

To detect information disclosure vulnerabilities, you can use automated tools such as:

- **Static Analysis Tools:** Such as SonarQube or Fortify.
- **Dynamic Analysis Tools:** Such as Burp Suite or OWASP ZAP.

#### Prevention

To prevent information disclosure vulnerabilities, follow these best practices:

- **Secure Debug Pages:** Ensure that debug pages are not accessible in production environments.
- **Use Environment Variables:** Store sensitive information in environment variables instead of hardcoding them in the application.
- **Proper Error Handling:** Implement proper error handling to avoid revealing internal system states or code snippets.

#### Secure Coding Fixes

Here is an example of a vulnerable code snippet and its secure counterpart:

**Vulnerable Code:**

```python
# Vulnerable code
import os

secret_key = os.getenv('SECRET_KEY')
print(f'Secret Key: {secret_key}')
```

**Secure Code:**

```python
# Secure code
import os

def get_secret_key():
    secret_key = os.getenv('SECRET_KEY')
    if secret_key is None:
        raise ValueError("SECRET_KEY environment variable is not set")
    return secret_key

try:
    secret_key = get_secret_key()
except ValueError as e:
    print(e)
```

### Configuration Hardening

#### Example Configuration

Here is an example of a secure configuration for a web server:

```nginx
server {
    listen 80;
    server_name example.com;

    location /debug {
        deny all;
    }

    location / {
        root /var/www/html;
        index index.html index.htm;
    }
}
```

### Conclusion

In this chapter, we covered the topic of information disclosure on debug pages. We discussed the background theory, the mechanics of the vulnerability, recent real-world examples, and how to prevent and defend against such vulnerabilities. By following best practices and using secure coding techniques, you can protect your applications from information disclosure vulnerabilities.

### Practice Labs

To practice and reinforce your understanding of information disclosure vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy:** Offers a variety of labs related to information disclosure vulnerabilities.
- **OWASP Juice Shop:** A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application):** A PHP/MySQL web application that is riddled with vulnerabilities.

By completing these labs, you can gain hands-on experience and improve your skills in detecting and preventing information disclosure vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/17-Information Disclosure/03-Lab 2 Information disclosure on debug page/00-Overview|Overview]] | [[02-Information Disclosure Vulnerability|Information Disclosure Vulnerability]]
