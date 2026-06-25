---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Accessing Environment Variables in Python

In the context of DevOps and automated systems, environment variables play a crucial role in managing configurations and sensitive data such as passwords and API keys. This section will delve into how to access these environment variables within a Python application, focusing on the `os` module and best practices for handling sensitive information.

### What Are Environment Variables?

Environment variables are dynamic-named values that can affect the way running processes will behave on a computer. They are part of the environment in which a process runs. In the context of a Python application, environment variables can be used to store configuration settings, database connection strings, API keys, and other sensitive information.

#### Why Use Environment Variables?

Using environment variables for configuration and sensitive data has several advantages:

1. **Security**: Environment variables can be managed outside of your codebase, reducing the risk of accidentally committing sensitive information to version control.
2. **Flexibility**: Different environments (development, testing, production) can have different configurations without changing the code.
3. **Isolation**: Environment variables can be set independently of the code, allowing for easy changes without redeploying the application.

### Accessing Environment Variables in Python

To access environment variables in Python, we use the `os` module, which provides a portable way of using operating system-dependent functionality. Specifically, we use the `os.environ` dictionary to retrieve the values of environment variables.

#### Example: Retrieving Environment Variables

Let's consider an example where we need to retrieve the email password from an environment variable named `EMAIL_PASSWORD`.

```python
import os

# Retrieve the email password from the environment variable
email_password = os.environ.get('EMAIL_PASSWORD')

print(f"The email password is: {email_password}")
```

In this example, `os.environ.get('EMAIL_PASSWORD')` retrieves the value of the `EMAIL_PASSWORD` environment variable. The `get` method returns `None` if the environment variable does not exist, which can be useful for providing default values.

### Setting Environment Variables

Before we can retrieve environment variables, we need to set them. This can be done in various ways depending on the operating system and the deployment environment.

#### Setting Environment Variables in Unix/Linux

In Unix/Linux systems, you can set environment variables using the `export` command in the terminal:

```sh
export EMAIL_PASSWORD="your_password_here"
```

This sets the `EMAIL_PASSWORD` environment variable for the current session. To make it persistent across sessions, you can add the export command to your shell profile file (e.g., `.bashrc`, `.zshrc`).

#### Setting Environment Variables in Windows

In Windows, you can set environment variables through the System Properties dialog or via the command line:

```cmd
set EMAIL_PASSWORD=your_password_here
```

For persistent settings, you can use the `setx` command:

```cmd
setx EMAIL_PASSWORD "your_password_here"
```

### Handling Sensitive Data Securely

When dealing with sensitive data like passwords, it is crucial to handle them securely. Here are some best practices:

1. **Avoid Hardcoding**: Never hardcode sensitive information directly into your code.
2. **Use Environment Variables**: Store sensitive data in environment variables.
3. **Secure Configuration Management**: Use tools like Docker secrets, Kubernetes secrets, or HashiCorp Vault to manage sensitive data securely.
4. **Limit Exposure**: Ensure that sensitive data is only exposed to necessary components and users.

### Real-World Example: CVE-2021-44228 (Log4Shell)

The Log4Shell vulnerability (CVE-2021-44228) is a critical security flaw in the Apache Log4j library that allows attackers to execute arbitrary code on a server. This vulnerability highlights the importance of securing sensitive data and configurations.

#### How to Prevent / Defend

1. **Update Dependencies**: Keep all dependencies up to date, especially those related to logging frameworks.
2. **Environment Variable Best Practices**:
    - Use environment variables for sensitive data.
    - Avoid exposing sensitive data in logs or error messages.
    - Use secure configuration management tools.

### Complete Example: Automated Email Alerts

Let's create a complete example where we send automated email alerts based on application status codes. We will use environment variables to store the email credentials.

#### Step 1: Set Environment Variables

```sh
export EMAIL_USER="your_email_user"
export EMAIL_PASSWORD="your_email_password"
```

#### Step 2: Python Code to Send Email

```python
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body):
    # Retrieve email credentials from environment variables
    email_user = os.environ.get('EMAIL_USER')
    email_password = os.environ.get('EMAIL_PASSWORD')

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_user
    msg['Subject'] = subject

    # Attach the body of the email
    msg.attach(MIMEText(body, 'plain'))

    # Connect to the SMTP server and send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_password)
        text = msg.as_string()
        server.sendmail(email_user, email_user, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Example usage
send_email("Application Alert", "The application status code is 500.")
```

### Full HTTP Request and Response

Here is an example of the HTTP request and response when sending an email using SMTP:

#### HTTP Request

```http
POST /smtp.gmail.com:587/starttls HTTP/1.1
Host: smtp.gmail.com:587
Content-Type: text/plain
Authorization: Basic <base64_encoded_credentials>

EHLO example.com
AUTH LOGIN
<base64_encoded_username>
<base64_encoded_password>
MAIL FROM:<sender@example.com>
RCPT TO:<receiver@example.com>
DATA
Subject: Application Alert

The application status code is 500.
.
QUIT
```

#### HTTP Response

```http
HTTP/1.1 250 OK
250-smtp.gmail.com at your service, [client_ip]
250-SIZE 35882577
250-8BITMIME
250-STARTTLS
250-ENHANCEDSTATUSCODES
250-PIPELINING
250-CHUNKING
250 SMTPUTF8

235 2.7.0 Authentication successful

250 2.1.0 Ok

250 2.1.5 Ok

354 End data with <CR><LF>.<CR><LF>

250 2.0.0 Ok: queued as ABCDEF123456

221 2.0.0 Bye
```

### Common Pitfalls and Best Practices

1. **Error Handling**: Always include error handling when working with external services like SMTP servers.
2. **Logging**: Avoid logging sensitive data like passwords.
3. **Testing**: Test your application thoroughly in a staging environment before deploying to production.

### How to Prevent / Defend

1. **Secure Configuration Management**: Use tools like Docker secrets, Kubernetes secrets, or HashiCorp Vault.
2. **Regular Audits**: Regularly audit your environment variables and configurations.
3. **Least Privilege Principle**: Ensure that environment variables are accessible only to necessary components and users.

### Practice Labs

For hands-on practice with automated email alerts and environment variables, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on secure coding practices and environment variable management.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing secure coding and configuration management.

By following these best practices and using the provided examples, you can effectively manage environment variables and automate email alerts in your Python applications.

---
<!-- nav -->
[[04-Introduction to Sending Emails via Python|Introduction to Sending Emails via Python]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/02-Automated Email Alerts for Application Status Codes/00-Overview|Overview]] | [[06-Automated Email Alerts for Application Status Codes|Automated Email Alerts for Application Status Codes]]
