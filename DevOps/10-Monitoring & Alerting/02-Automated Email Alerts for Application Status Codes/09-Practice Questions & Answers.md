---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain why automated email alerts are necessary for monitoring application status codes.**

Automated email alerts are crucial for monitoring application status codes because they ensure immediate notification when an application encounters issues. Without such alerts, teams might not be aware of problems until users report them, leading to potential downtime and user dissatisfaction. By automating alerts, teams can proactively address issues, ensuring the application remains operational and reliable.

**Q2. How would you implement an automated email alert system using Python's SMTP library to notify a team when an application returns a non-200 status code?**

To implement an automated email alert system using Python's SMTP library, follow these steps:

1. **Setup SMTP Client**: Use `smtplib.SMTP()` to connect to the SMTP server.
2. **Secure Connection**: Use `starttls()` to establish a secure connection.
3. **Login**: Use `login()` to authenticate with the SMTP server.
4. **Send Email**: Use `sendmail()` to send the email.

Here’s a sample implementation:

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body):
    # Set up the SMTP client
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'your-email@gmail.com'
    receiver_email = 'receiver-email@gmail.com'
    
    # Create SMTP session
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    
    # Login with credentials
    server.login(sender_email, 'your-password')
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    # Attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))
    
    # Send the email
    server.send_message(msg)
    
    # Close the server connection
    server.quit()

# Example usage
if __name__ == "__main__":
    status_code = 500  # Assume this is the status code received from the application
    if status_code != 200:
        subject = "Application Down"
        body = f"The application returned status code {status_code}. Please fix the issue."
        send_email(subject, body)
```

**Q3. What are the security considerations when allowing a Python script to send emails from a Gmail account?**

When allowing a Python script to send emails from a Gmail account, several security considerations must be addressed:

1. **Two-Factor Authentication (2FA)**: If 2FA is enabled, you need to generate an application-specific password rather than using your regular Gmail password.
2. **Less Secure Apps**: If 2FA is not enabled, you can enable "Allow less secure apps" in your Google account settings. However, this is less secure and not recommended for accounts with sensitive data.
3. **Environment Variables**: Store sensitive information like email addresses and passwords in environment variables rather than hardcoding them in the script.
4. **Secure Communication**: Ensure that the communication between the Python script and the SMTP server is encrypted using `starttls()`.

**Q4. How can you handle exceptions in the Python script to ensure that an email is sent even if the server does not respond?**

To handle exceptions and ensure that an email is sent even if the server does not respond, use a `try-except` block around the code that makes the HTTP request. If an exception occurs, catch it and send an email with the details of the error.

Here’s an example:

```python
import requests

def check_application_status(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            send_email("Application Down", f"The application returned status code {response.status_code}.")
    except requests.exceptions.RequestException as e:
        send_email("Connection Error", f"Failed to connect to the application: {str(e)}")

# Example usage
if __name__ == "__main__":
    url = "http://example.com"
    check_application_status(url)
```

**Q5. Why is it important to abstract the email-sending logic into a function?**

Abstracting the email-sending logic into a function is important for several reasons:

1. **Code Reusability**: Functions can be reused throughout the codebase, reducing redundancy.
2. **Maintainability**: If the email-sending logic changes, you only need to update the function, not every place where the logic is used.
3. **Readability**: Functions improve code readability by encapsulating complex operations into named blocks.

Here’s an example of abstracting the email-sending logic:

```python
def send_notification(subject, body):
    # Email sending logic here
    pass

# Usage
if status_code != 2[END_OF_TEXT]

---
<!-- nav -->
[[08-Environment Variables and Automated Email Alerts for Application Status Codes|Environment Variables and Automated Email Alerts for Application Status Codes]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/02-Automated Email Alerts for Application Status Codes/00-Overview|Overview]]
