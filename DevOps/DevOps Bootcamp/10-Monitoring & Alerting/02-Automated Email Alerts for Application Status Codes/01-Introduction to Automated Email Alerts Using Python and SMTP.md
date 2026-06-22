---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Automated Email Alerts Using Python and SMTP

Automated email alerts are a crucial component of monitoring and maintaining the health of applications and systems. In this section, we will delve into the process of setting up automated email alerts using Python and Simple Mail Transfer Protocol (SMTP). This setup will allow you to monitor application status codes and send alerts via email when certain conditions are met.

### Background Theory

#### What is SMTP?

SMTP stands for Simple Mail Transfer Protocol. It is a protocol used for sending emails between servers. SMTP operates on port 25 by default, although other ports such as 465 (for SSL/TLS encryption) and 587 (for STARTTLS encryption) are also commonly used.

#### Why Use SMTP for Automated Alerts?

SMTP is widely supported and can be easily integrated into various programming languages, including Python. By leveraging SMTP, you can create robust and reliable alerting mechanisms that notify you of critical events in real-time.

### Setting Up the Environment

To set up automated email alerts using Python and SMTP, you need to ensure that you have the necessary libraries installed. The `smtplib` library in Python provides the functionality to interact with SMTP servers.

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
```

### Connecting to the SMTP Server

The first step is to establish a connection to the SMTP server. In this example, we will use Gmail's SMTP server, which requires TLS encryption for secure communication.

```python
smtp_server = "smtp.gmail.com"
port = 587  # For starttls
```

### Establishing a Secure Connection

Before sending any data, it is essential to establish a secure connection using TLS (Transport Layer Security).

```python
# Create a secure connection with the server
server = smtplib.SMTP(smtp_server, port)
server.starttls()  # Secure the connection
```

#### Explanation of `starttls()`

The `starttls()` method upgrades the current insecure connection to a secure one using TLS. This ensures that all subsequent communications are encrypted, protecting sensitive information such as login credentials and email content.

### Identifying the Client

Once the connection is secure, you need to identify your Python application to the mail server using the `ehlo()` method.

```python
server.ehlo()  # Identify ourselves to the server
```

#### Explanation of `ehlo()`

The `ehlo()` method sends a greeting to the mail server, indicating that the client supports extended SMTP features. This is a standard step in establishing a connection and is required before proceeding with further operations.

### Logging In to the SMTP Server

Next, you need to authenticate with the SMTP server using your email credentials.

```python
email_address = "your-email@gmail.com"
password = "your-password"

server.login(email_address, password)
```

#### Handling Two-Factor Authentication (2FA)

Gmail supports two-factor authentication (2FA), which adds an extra layer of security to your account. If you have 2FA enabled, you will need to generate an app-specific password to use with your script.

```python
# If 2FA is enabled, use an app-specific password
app_password = "your-app-specific-password"
server.login(email_address, app_password)
```

### Composing the Email

Now that you are logged in, you can compose the email. This involves creating a `MIMEMultipart` object and adding the necessary components such as the sender, recipient, subject, and body.

```python
msg = MIMEMultipart()
msg['From'] = email_address
msg['To'] = "recipient-email@example.com"
msg['Subject'] = "Application Status Alert"

body = "This is an automated alert regarding the application status."
msg.attach(MIMEText(body, 'plain'))
```

### Sending the Email

Finally, you can send the email using the `sendmail()` method.

```python
server.sendmail(email_address, "recipient-email@example.com", msg.as_string())
```

### Closing the Connection

After sending the email, it is important to close the connection to the SMTP server.

```python
server.quit()
```

### Full Example Code

Here is the complete code for sending an automated email alert:

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP server details
smtp_server = "smtp.gmail.com"
port = 587  # For starttls

# Email credentials
email_address = "your-email@gmail.com"
password = "your-password"

# Recipient email
recipient_email = "recipient-email@example.com"

# Create a secure connection with the server
server = smtplib.SMTP(smtp_server, port)
server.starttls()  # Secure the connection
server.ehlo()  # Identify ourselves to the server

# Login to the SMTP server
server.login(email_address, password)

# Compose the email
msg = MIMEMultipart()
msg['From'] = email_address
msg['To'] = recipient_email
msg['Subject'] = "Application Status Alert"

body = "This is an automated alert regarding the application status."
msg.attach(MIMEText(body, 'plain'))

# Send the email
server.sendmail(email_address, recipient_email, msg.as_string())

# Close the connection
server.quit()
```

### Common Pitfalls and How to Avoid Them

#### Incorrect Credentials

Ensure that you are using the correct email address and password. If 2FA is enabled, use an app-specific password instead of your regular password.

#### Network Issues

Make sure that your network allows connections to the SMTP server on the specified port. Some networks may block outgoing connections on port 25.

#### Error Handling

Add error handling to manage potential issues such as network errors, authentication failures, and other exceptions.

```python
try:
    # SMTP server details
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls

    # Email credentials
    email_address = "your-email@gmail.com"
    password = "your-password"

    # Recipient email
    recipient_email = "recipient-email@example.com"

    # Create a secure connection with the server
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()  # Secure the connection
    server.ehlo()  # Identify ourselves to the server

    # Login to the SMTP server
    server.login(email_address, password)

    # Compose the email
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = recipient_email
    msg['Subject'] = "Application Status Alert"

    body = "This is an automated alert regarding the application status."
    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    server.sendmail(email_address, recipient_email, msg.as_string())

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the connection
    server.quit()
```

### Real-World Examples and Recent Breaches

#### Example: CVE-2021-21166

In 2021, a critical vulnerability was discovered in Microsoft Exchange Server, allowing attackers to gain unauthorized access to email accounts and send spam emails. This highlights the importance of securing email infrastructure and implementing robust monitoring and alerting mechanisms.

#### Example: SolarWinds Supply Chain Attack

In 2020, a sophisticated supply chain attack compromised SolarWinds Orion software, leading to widespread breaches across multiple organizations. Automated email alerts could have helped detect and respond to such attacks more quickly.

### How to Prevent / Defend

#### Detection

Implement monitoring tools to detect unusual activity, such as unexpected email traffic or failed login attempts. Use intrusion detection systems (IDS) and security information and event management (SIEM) solutions to correlate and analyze security events.

#### Prevention

1. **Use Strong Passwords**: Ensure that all email accounts use strong, unique passwords.
2. **Enable Two-Factor Authentication (2FA)**: Enable 2FA for all email accounts to add an extra layer of security.
3. **Secure Configuration**: Configure SMTP servers securely, ensuring that only authorized users can send emails.
4. **Regular Audits**: Conduct regular security audits to identify and mitigate vulnerabilities.

#### Secure Coding Fixes

Compare the vulnerable code with the secure code to understand the differences and improvements.

**Vulnerable Code:**

```python
server.login(email_address, password)
```

**Secure Code:**

```python
# If 2FA is enabled, use an app-specific password
app_password = "your-app-specific-password"
server.login(email_address, app_password)
```

### Conclusion

Automated email alerts using Python and SMTP provide a powerful mechanism for monitoring and maintaining the health of applications and systems. By following the steps outlined in this chapter, you can set up a robust alerting system that notifies you of critical events in real-time. Remember to handle credentials securely, implement strong authentication mechanisms, and regularly audit your systems to ensure maximum security.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive training on web security, including email-related attacks and defenses.
- **OWASP Juice Shop**: A deliberately vulnerable web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning web security.

These labs provide practical experience in setting up and securing automated email alerts, helping you master the concepts covered in this chapter.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/02-Automated Email Alerts for Application Status Codes/00-Overview|Overview]] | [[02-Introduction to Automated Email Alerts for Application Status Codes|Introduction to Automated Email Alerts for Application Status Codes]]
