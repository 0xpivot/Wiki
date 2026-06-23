---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Environment Variables and Automated Email Alerts for Application Status Codes

### Introduction to Environment Variables

Environment variables are dynamic-named values that can affect the way running processes will behave on a computer. They are part of the environment in which a process runs. Environment variables can be used to store sensitive information such as API keys, database credentials, and email credentials. This makes them a crucial component in the development and deployment of applications.

#### Why Use Environment Variables?

Using environment variables helps keep sensitive data out of your codebase, making it easier to manage different environments (development, testing, production) without hardcoding sensitive information. This is particularly important for security reasons, as hardcoding sensitive information can lead to data breaches.

#### How Environment Variables Work

When a process starts, it inherits a set of environment variables from its parent process. These variables can be accessed within the process using specific commands or functions depending on the programming language being used. For example, in Bash, you can access an environment variable using `$VARIABLE_NAME`.

### Setting Environment Variables in Bash Profile

On macOS, you can set environment variables in the `.bash_profile` file. This file is executed every time a new terminal session is started, ensuring that the environment variables are available throughout the session.

```bash
# .bash_profile
export EMAIL_ADDRESS="your-email@example.com"
export EMAIL_PASSWORD="your-password"
```

#### Pitfalls of Using Bash Profile

While setting environment variables in the `.bash_profile` is convenient, it has some drawbacks:

1. **Restart Requirement**: Changes made to the `.bash_profile` require restarting the terminal session or the entire system to take effect.
2. **Security Concerns**: Storing sensitive information like passwords in plain text in a file can be risky if the file is not properly secured.

### Using PyCharm to Set Environment Variables

PyCharm is a popular Integrated Development Environment (IDE) for Python developers. It provides a feature to set environment variables specifically for a project, which is more flexible and secure than using the `.bash_profile`.

#### Steps to Set Environment Variables in PyCharm

1. Open your project in PyCharm.
2. Navigate to `Run > Edit Configurations`.
3. Select the configuration you want to modify.
4. Click on the `Environment variables` section.
5. Add your environment variables as key-value pairs.

```plaintext
EMAIL_ADDRESS=your-email@example.com
EMAIL_PASSWORD=your-password
```

#### Benefits of Using PyCharm for Environment Variables

1. **No Restart Required**: Changes to environment variables in PyCharm take effect immediately without needing to restart the system.
2. **Project-Specific**: Environment variables set in PyCharm are only applicable to the current project, reducing the risk of conflicts with other projects.
3. **Secure Storage**: PyCharm does not store these variables in plain text files, making them less likely to be exposed.

### Example: Automated Email Alerts for Application Status Codes

Let's walk through an example of how to set up automated email alerts for application status codes using environment variables.

#### Step 1: Set Up Environment Variables in PyCharm

1. Open your project in PyCharm.
2. Go to `Run > Edit Configurations`.
3. Add the following environment variables:

```plaintext
EMAIL_ADDRESS=your-email@example.com
EMAIL_PASSWORD=your-password
```

#### Step 2: Write the Script to Send Email Alerts

Here’s a simple Python script that sends an email alert based on the status code of a website:

```python
import os
import smtplib
from email.mime.text import MIMEText

def send_email(subject, body):
    email_address = os.getenv('EMAIL_ADDRESS')
    email_password = os.getenv('EMAIL_PASSWORD')

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = email_address

    with smtplib.SMTP_SSL('smtp.example.com', 465) as server:
        server.login(email_address, email_password)
        server.sendmail(email_address, [email_address], msg.as_string())

def check_website_status(url):
    import requests
    response = requests.get(url)
    status_code = response.status_code

    if status_code != 200:
        send_email(f"Website {url} returned status code {status_code}", f"The website {url} returned status code {status_code}. Please check the site.")

check_website_status("https://example.com")
```

#### Full HTTP Request and Response

Here’s an example of the full HTTP request and response when checking the website status:

```http
GET / HTTP/1.1
Host: example.com
User-Agent: python-requests/2.25.1
Accept-Encoding: gzip, deflate
Accept: */*
Connection: keep-alive

HTTP/1.1 200 OK
Date: Tue, 14 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: close

<!DOCTYPE html>
<html>
<head>
    <title>Example Domain</title>
</head>
<body>
    <div>
        <h1>Example Domain</h1>
        <p>This domain is established to be used for illustrative examples in documents. You may use this domain in examples without prior coordination or asking for permission.</p>
    </div>
</body>
</html>
```

### Real-World Examples and Recent Breaches

#### Example: CVE-2021-44228 (Log4Shell)

The Log4Shell vulnerability (CVE-2021-44228) is a critical security flaw in the widely-used Apache Log4j logging library. This vulnerability allows attackers to execute arbitrary code on affected systems, leading to remote code execution (RCE).

**Impact**: Many organizations were affected, including Apple, Tesla, and Twitter.

**Mitigation**: Ensure that all instances of Log4j are updated to the latest version, and monitor for suspicious activity.

### How to Prevent / Defend

#### Secure Coding Practices

1. **Use Environment Variables**: Store sensitive information in environment variables rather than hardcoding them in your codebase.
2. **Validate Inputs**: Always validate inputs to ensure they meet expected criteria.
3. **Use Secure Libraries**: Keep all libraries and dependencies up to date to avoid known vulnerabilities.

#### Secure Configuration

1. **Limit Permissions**: Ensure that environment variables are only accessible to the necessary processes.
2. **Use Secure Communication Protocols**: Use HTTPS for all communication to encrypt data in transit.
3. **Monitor Logs**: Regularly review logs for suspicious activity.

#### Detection and Prevention

1. **Static Code Analysis**: Use tools like SonarQube or Bandit to scan your code for security vulnerabilities.
2. **Dynamic Analysis**: Use tools like Burp Suite or ZAP to test your application for runtime vulnerabilities.
3. **Penetration Testing**: Conduct regular penetration tests to identify and mitigate security weaknesses.

### Conclusion

Setting up automated email alerts for application status codes is a crucial step in maintaining the health and security of your applications. By using environment variables effectively, you can ensure that sensitive information is stored securely and that your applications can respond appropriately to changes in status codes.

### Practice Labs

For hands-on practice with automated email alerts and environment variables, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web security, including email alerts and environment management.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes, which includes features related to email alerts and environment configuration.

By following these steps and practicing with real-world examples, you can gain a deep understanding of how to effectively use environment variables and set up automated email alerts for application status codes.

---
<!-- nav -->
[[07-Constants and Environment Variables|Constants and Environment Variables]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/02-Automated Email Alerts for Application Status Codes/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/02-Automated Email Alerts for Application Status Codes/09-Practice Questions & Answers|Practice Questions & Answers]]
