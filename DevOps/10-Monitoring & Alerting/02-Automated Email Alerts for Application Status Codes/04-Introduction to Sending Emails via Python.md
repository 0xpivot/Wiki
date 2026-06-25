---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Sending Emails via Python

Sending automated email alerts is a crucial aspect of monitoring application status codes and ensuring timely notifications for critical events. In this section, we will delve into how to send emails using Python, focusing on the built-in `smtplib` library. This library allows us to interact with Simple Mail Transfer Protocol (SMTP) servers, which are responsible for sending emails across the internet.

### What is SMTP?

SMTP stands for Simple Mail Transfer Protocol. It is a protocol used for sending email messages between servers. It defines the rules for how email should be composed and transmitted over the internet. SMTP operates on port 25 by default, although many email providers use port 587 for submission.

### Why Use `smtplib`?

The `smtplib` library in Python provides a straightforward way to send emails programmatically. It abstracts away much of the complexity involved in interacting with SMTP servers, making it easier to integrate email functionality into your applications.

### Prerequisites

Before diving into the implementation, ensure you have the following:

1. **Python Environment**: Ensure Python is installed on your system.
2. **Email Account**: You need an email account (e.g., Gmail, Outlook) to send emails from.
3. **SMTP Server Details**: Know the SMTP server details for your email provider.

### Step-by-Step Guide to Sending Emails

#### Step 1: Import the Required Libraries

First, import the necessary libraries:

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
```

- **`smtplib`**: Provides the necessary functions to interact with SMTP servers.
- **`MIMEText` and `MIMEMultipart`**: These classes help create the structure of the email message.

#### Step 2: Set Up the Email Credentials

To send an email, you need to provide the credentials of the sender's email account. For example, if you are using a Gmail account:

```python
sender_email = "your-email@gmail.com"
receiver_email = "receiver-email@example.com"
password = "your-password"
```

**Important Note**: Storing passwords directly in your code is insecure. Consider using environment variables or a secure vault service to manage sensitive information.

#### Step 3: Create the Email Message

Construct the email message using `MIMEMultipart` and `MIMEText`:

```python
message = MIMEMultipart("alternative")
message["Subject"] = "Automated Email Alert"
message["From"] = sender_email
message["To"] = receiver_email

# Create the body of the message (a plain-text and an HTML version).
text = """\
Hi,
This is an automated email alert.
"""
html = """\
<html>
  <body>
    <p>Hi,<br>
       This is an automated email alert.</p>
  </body>
</html>
"""

# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
message.attach(part1)
message.attach(part2)
```

#### Step 4: Connect to the SMTP Server

Establish a connection to the SMTP server and log in using the provided credentials:

```python
smtp_server = "smtp.gmail.com"
port = 587  # For starttls

# Create a secure SSL context
context = smtplib.SMTP_SSL(smtp_server, port)

try:
    context.login(sender_email, password)
except Exception as e:
    print(f"Failed to login: {e}")
```

#### Step 5: Send the Email

Finally, send the email using the `sendmail` method:

```python
try:
    context.sendmail(sender_email, receiver_email, message.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
finally:
    context.quit()
```

### Full Example Code

Here is the complete code to send an email using Python and `smtplib`:

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email credentials
sender_email = "your-email@gmail.com"
receiver_email = "receiver-email@example.com"
password = "your-password"

# Create the email message
message = MIMEMultipart("alternative")
message["Subject"] = "Automated Email Alert"
message["From"] = sender_email
message["To"] = receiver_email

# Create the body of the message (a plain-text and an HTML version).
text = """\
Hi,
This is an automated email alert.
"""
html = """\
<html>
  <body>
    <p>Hi,<br>
       This is an automated email alert.</p>
  </body>
</html>
"""

# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")

# Attach parts into message container.
message.attach(part1)
message.attach(part2)

# SMTP server details
smtp_server = "smtp.gmail.com"
port = 587  # For starttls

# Create a secure SSL context
context = smtplib.SMTP_SSL(smtp_server, port)

try:
    context.login(sender_email, password)
    context.sendmail(sender_email, receiver_email, message.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
finally:
    context.quit()
```

### Common Pitfalls and How to Avoid Them

1. **Security Risks**: Storing passwords in plain text within your code is highly insecure. Use environment variables or a secure vault service to manage sensitive information.
   
2. **Authentication Issues**: Ensure that the email account you are using has the necessary permissions to send emails. For Gmail, you might need to enable "Less secure app access" or use an App Password if two-factor authentication is enabled.

3. **Rate Limiting**: Some email providers impose rate limits on the number of emails that can be sent per hour. Be mindful of these limits to avoid being flagged as spam.

### Real-World Examples and Recent Breaches

One notable breach involving email services was the **Yahoo Data Breach** in 2013, where hackers accessed user data including email addresses and passwords. This highlights the importance of securing email credentials and using strong authentication mechanisms.

### How to Prevent / Defend

#### Detection

- **Monitor Logs**: Regularly review logs for unusual activity, such as unexpected email sends.
- **Use Security Tools**: Implement tools like intrusion detection systems (IDS) to monitor network traffic for suspicious patterns.

#### Prevention

- **Secure Credentials**: Use environment variables or a secure vault service to store sensitive information.
- **Enable Two-Factor Authentication (2FA)**: Require 2FA for accessing email accounts to add an extra layer of security.
- **Limit Permissions**: Restrict the permissions of the email account used for automated alerts to minimize potential damage in case of a breach.

#### Secure Coding Fixes

**Vulnerable Code**:

```python
password = "your-password"
```

**Secure Code**:

```python
import os

password = os.getenv("EMAIL_PASSWORD")
```

By using environment variables, you can securely manage sensitive information without hardcoding it into your scripts.

### Conclusion

Sending automated email alerts is a powerful tool for monitoring application status codes and ensuring timely notifications. By leveraging Python's `smtplib` library, you can easily integrate email functionality into your applications. However, it is crucial to follow best practices for security to protect against potential risks.

### Practice Labs

For hands-on practice with sending emails via Python, consider the following resources:

- **PortSwigger Web Security Academy**: Offers interactive labs on web security, including sections on email security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including email-related vulnerabilities.

These resources will help you gain practical experience and deepen your understanding of the concepts covered in this chapter.

---
<!-- nav -->
[[03-Introduction to Error Handling and Automated Email Alerts|Introduction to Error Handling and Automated Email Alerts]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/02-Automated Email Alerts for Application Status Codes/00-Overview|Overview]] | [[05-Accessing Environment Variables in Python|Accessing Environment Variables in Python]]
