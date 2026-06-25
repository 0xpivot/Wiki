---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Automated Email Alerts for Application Status Codes

In modern software development and operations, ensuring the availability and reliability of applications is paramount. One critical aspect of maintaining application health is monitoring its status codes and promptly notifying relevant personnel when issues arise. This chapter delves into the concept of automated email alerts for application status codes, explaining the underlying principles, implementation details, and best practices for securing such systems.

### What Are Status Codes?

Status codes are numerical values returned by servers in response to client requests. They indicate the outcome of the request and provide information about the current state of the application. The most commonly used status codes are:

- **200 OK**: The request was successful.
- **400 Bad Request**: The server could not understand the request due to invalid syntax.
- **404 Not Found**: The requested resource could not be found on the server.
- **500 Internal Server Error**: The server encountered an unexpected condition that prevented it from fulfilling the request.

When an application returns a status code other than 200, it typically signifies that there is a problem with the application. This could range from minor issues like a misconfigured endpoint to major failures like a crashed service.

### Why Monitor Status Codes?

Monitoring status codes is essential for several reasons:

1. **User Experience**: When an application returns a non-200 status code, it often means that users are unable to access certain features or are encountering errors. This can lead to frustration and loss of trust.
   
2. **Operational Efficiency**: By automating the process of detecting and alerting on non-200 status codes, teams can respond more quickly to issues, reducing downtime and improving overall system reliability.

3. **Proactive Maintenance**: Monitoring status codes allows teams to identify patterns and trends, enabling them to proactively address potential issues before they become critical.

### How to Implement Automated Email Alerts

To implement automated email alerts for application status codes, we will use Python as our programming language. We will create a script that periodically checks the status of the application and sends an email notification if the status code is not 200.

#### Step-by-Step Implementation

1. **Set Up the Environment**:
   - Ensure Python is installed on your system.
   - Install necessary libraries using pip:
     ```bash
     pip install requests smtplib
     ```

2. **Create the Script**:
   - Write a Python script that makes HTTP requests to the application and checks the status code.
   - If the status code is not 200, send an email notification.

Here is a complete example of the script:

```python
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def check_status_code(url):
    try:
        response = requests.get(url)
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None

def send_email(subject, body, to_email):
    from_email = "your-email@example.com"
    password = "your-email-password"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.example.com', 587)
    server.starttls()
    server.login(from_email, password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

def main():
    url = "http://your-application-url.com"
    to_email = "devops@example.com"

    status_code = check_status_code(url)
    if status_code != 200:
        subject = "Application Down"
        body = f"The application is down. Status code: {status_code}"
        send_email(subject, body, to_email)

if __name__ == "__main__":
    main()
```

### Explanation of the Code

1. **Import Libraries**:
   - `requests`: Used to make HTTP requests.
   - `smtplib`: Used to send emails.
   - `email.mime.text.MIMEText` and `email.mime.multipart.MIMEMultipart`: Used to construct the email message.

2. **Check Status Code Function**:
   - `check_status_code(url)`: Makes an HTTP GET request to the specified URL and returns the status code.
   - Handles exceptions to catch any errors that occur during the request.

3. **Send Email Function**:
   - `send_email(subject, body, to_email)`: Constructs and sends an email using SMTP.
   - Sets up the email message with the specified subject and body.
   - Logs in to the SMTP server and sends the email.

4. **Main Function**:
   - Defines the URL of the application and the recipient email address.
   - Checks the status code of the application.
   - If the status code is not 200, constructs and sends an email notification.

### Real-World Examples

#### Example 1: Recent Breach Due to Unmonitored Status Codes

In 2022, a major e-commerce platform experienced a significant outage due to unmonitored status codes. The application returned a 500 Internal Server Error, but no alerts were triggered. As a result, users were unable to access the site for several hours, leading to financial losses and reputational damage.

#### Example 2: CVE-2021-44228 (Log4j Vulnerability)

The Log4j vulnerability (CVE-2021-44228) affected numerous applications, causing them to return unexpected status codes. By monitoring these status codes and triggering alerts, organizations could have detected and mitigated the issue more quickly.

### Common Pitfalls and Best Practices

#### Pitfall 1: Overloading Email Notifications

Sending too many email notifications can lead to alert fatigue, where important alerts are ignored. To avoid this, ensure that the threshold for triggering an alert is set appropriately.

#### Pitfall 2: Hardcoding Credentials

Hardcoding email credentials in the script is insecure. Instead, use environment variables or a secure vault to store sensitive information.

#### Best Practice 1: Use Environment Variables

Store sensitive information like email credentials in environment variables. This keeps the script secure and allows for easy configuration changes.

```python
import os

from_email = os.getenv("FROM_EMAIL")
password = os.getenv("EMAIL_PASSWORD")
```

#### Best Practice 2: Use Secure Communication Protocols

Ensure that the SMTP server uses secure communication protocols like TLS to encrypt the email transmission.

### How to Prevent / Defend

#### Detection

- **Logging**: Implement comprehensive logging to capture all HTTP requests and their corresponding status codes.
- **Monitoring Tools**: Use monitoring tools like Prometheus, Grafana, or Datadog to visualize and analyze status codes in real-time.

#### Prevention

- **Automated Testing**: Regularly run automated tests to ensure that the application returns the correct status codes under various conditions.
- **Code Reviews**: Conduct regular code reviews to identify and fix potential issues that could cause incorrect status codes.

#### Secure Coding Fixes

##### Vulnerable Code

```python
response = requests.get(url)
if response.status_code != 200:
    send_email("Application Down", f"Status code: {response.status_code}", to_email)
```

##### Secure Code

```python
response = requests.get(url)
if response.status_code != 200:
    subject = "Application Down"
    body = f"Status code: {response.status_code}"
    send_email(subject, body, to_email)
```

#### Configuration Hardening

- **Email Credentials**: Store email credentials securely using environment variables or a secure vault.
- **SMTP Configuration**: Configure the SMTP server to use secure communication protocols like TLS.

### Conclusion

Automated email alerts for application status codes are a crucial component of modern DevOps practices. By monitoring status codes and promptly notifying relevant personnel, teams can improve the reliability and availability of their applications. This chapter provided a comprehensive guide to implementing and securing such systems, including real-world examples, common pitfalls, and best practices.

### Practice Labs

For hands-on practice with automated email alerts for application status codes, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web application security, including monitoring and alerting.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security testing and monitoring.
- **DVWA (Damn Vulnerable Web Application)**: Another vulnerable web application for learning and practicing web security.

These labs will help you gain practical experience in implementing and securing automated email alerts for application status codes.

---
<!-- nav -->
[[01-Introduction to Automated Email Alerts Using Python and SMTP|Introduction to Automated Email Alerts Using Python and SMTP]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/02-Automated Email Alerts for Application Status Codes/00-Overview|Overview]] | [[03-Introduction to Error Handling and Automated Email Alerts|Introduction to Error Handling and Automated Email Alerts]]
