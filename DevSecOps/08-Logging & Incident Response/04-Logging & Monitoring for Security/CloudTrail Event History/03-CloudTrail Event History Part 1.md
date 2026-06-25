---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## CloudTrail Event History

### Introduction to CloudTrail

Amazon CloudTrail is a service that enables AWS customers to log, continuously monitor, and retain account activity related to actions across their AWS infrastructure. These actions include API calls, changes to resources, and other activities within an AWS account. CloudTrail captures this information and delivers it to Amazon S3 buckets, where it can be stored, queried, and analyzed.

CloudTrail logs are essential for security and compliance purposes. They provide visibility into who is doing what, when, and from where within your AWS environment. This information is crucial for detecting unauthorized access, identifying potential security threats, and ensuring compliance with regulatory requirements.

### Regional Segregation of CloudTrail Events

One of the key features of CloudTrail is its ability to segregate event history based on AWS regions. Each region maintains its own set of CloudTrail logs, which means that events occurring in one region are not mixed with events from another region. This segregation is beneficial for several reasons:

- **Isolation**: By keeping events isolated by region, you can more easily manage and analyze logs for specific geographic areas.
- **Performance**: Processing and querying logs for a specific region can be faster and more efficient than handling a large, combined dataset.
- **Compliance**: Some regulatory requirements may mandate that certain types of data remain within specific geographic boundaries. Regional segregation helps meet these requirements.

#### Example: No Activity in Tokyo Region

Let’s consider an example where there is no activity in the Tokyo region. In this case, the CloudTrail event history for the Tokyo region would be empty. This scenario might occur if no AWS services are being used in that region or if there has been no recent activity.

```mermaid
graph TD
    A[No Activity] --> B[Tokyo Region]
    B --> C[Empty Event History]
```

### Default Region for Authentication Events

The North Virginia (us-east-1) region is designated as the default region for logging authentication events, such as console logins. This means that all sign-in events, regardless of the region where the actual resource resides, are recorded in the us-east-1 region.

#### Sign-In Events in North Virginia

Whenever a user attempts to log in to the AWS Management Console, an event is generated and recorded in the us-east-1 region. This includes both successful and unsuccessful login attempts. The event details include:

- **User Identity Data**: Information about the user attempting to log in, including the username.
- **User Agent**: The browser or application used to initiate the login attempt.
- **Login Status**: Whether the login attempt was successful or failed.
- **MFA Usage**: Whether multi-factor authentication (MFA) was used during the login attempt.
- **Source IP Address**: The IP address from which the login attempt originated.

#### Example: Admin User Login

Consider an example where an admin user logs in to the AWS Management Console. The following is a sample CloudTrail event for this login attempt:

```http
{
  "eventVersion": "1.08",
  "userIdentity": {
    "type": "IAMUser",
    "principalId": "AIDAJDOQEXAMPLE",
    "arn": "arn:aws:iam::123456789012:user/admin-user",
    "accountId": "123456789012",
    "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
    "userName": "admin-user"
  },
  "eventTime": "2023-10-01T12:34:56Z",
  "eventSource": "signin.amazonaws.com",
  "eventName": "ConsoleLogin",
  "awsRegion": "us-east-1",
  "sourceIPAddress": "192.0.2.1",
  "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
  "requestParameters": null,
  "responseElements": {
    "ConsoleLogin": "Success"
  },
  "additionalEventData": {
    "MFAUsed": "No"
  }
}
```

### Failed Authentication Attempts

In addition to successful login attempts, CloudTrail also records failed authentication attempts. This is crucial for detecting potential security threats, such as brute-force attacks or unauthorized access attempts.

#### Example: Failed Login Attempt

Consider an example where a user attempts to log in but fails due to incorrect credentials. The following is a sample CloudTrail event for this failed login attempt:

```http
{
  "eventVersion": "1.08",
  "userIdentity": {
    "type": "IAMUser",
    "principalId": "AIDAJDOQEXAMPLE",
    "arn": "arn:aws:iam::123456789012:user/admin-user",
    "accountId": "123456789012",
    "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
    "userName": "admin-user"
  },
  "eventTime": "2023-10-01T12:35:00Z",
  "eventSource": "signin.amazonaws.com",
  "eventName": "ConsoleLogin",
  "awsRegion": "us-east-1",
  "sourceIPAddress": "192.0.2.1",
  "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
  "requestParameters": null,
  "responseElements": {
    "ConsoleLogin": "Failure"
  },
  "additionalEventData": {
    "MFAUsed": "No"
  }
}
```

### Importance of Monitoring Authentication Events

Monitoring authentication events is critical for maintaining the security of your AWS environment. By analyzing these events, you can identify patterns of suspicious behavior, such as repeated failed login attempts from the same IP address, which could indicate a brute-force attack.

#### Real-World Example: Brute-Force Attack Detection

In a real-world scenario, a company detected a series of failed login attempts from a single IP address over a short period. Upon investigation, it was determined that this was a brute-force attack attempt. The company was able to take immediate action to block the IP address and enhance security measures.

### How to Prevent / Defend Against Unauthorized Access

To prevent unauthorized access and ensure the security of your AWS environment, follow these best practices:

1. **Enable Multi-Factor Authentication (MFA)**: Require MFA for all users, especially those with administrative privileges. This adds an additional layer of security by requiring a second form of verification, such as a time-based one-time password (TOTP).

2. **Monitor CloudTrail Logs**: Regularly review CloudTrail logs to detect any suspicious activity. Set up alerts for failed login attempts and other security-relevant events.

3. **Use IAM Policies**: Implement least privilege access policies to restrict user permissions. Ensure that users have only the minimum permissions necessary to perform their job functions.

4. **Block Suspicious IPs**: Use AWS WAF (Web Application Firewall) or security groups to block IP addresses associated with suspicious activity.

5. **Implement Network Security Groups**: Use network security groups to control inbound and outbound traffic to your instances. Limit access to only necessary ports and protocols.

6. **Regularly Rotate Credentials**: Enforce regular rotation of access keys and passwords to minimize the risk of compromised credentials.

#### Secure Coding Practices

Here is an example of how to implement MFA in IAM policies:

**Vulnerable Code:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```

**Secure Code:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```

### Conclusion

Understanding and effectively utilizing CloudTrail event history is crucial for maintaining the security and compliance of your AWS environment. By leveraging regional segregation, monitoring authentication events, and implementing robust security measures, you can significantly reduce the risk of unauthorized access and ensure the integrity of your AWS resources.

### Hands-On Labs

For practical experience with CloudTrail and logging, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on logging and monitoring for security.
- **OWASP Juice Shop**: Provides a hands-on environment to practice security monitoring techniques.
- **AWS Well-Architected Labs**: Includes labs focused on setting up and monitoring CloudTrail.

By engaging in these labs, you can gain hands-on experience with the concepts discussed in this chapter.

---
<!-- nav -->
[[02-Introduction to CloudTrail Event History|Introduction to CloudTrail Event History]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/CloudTrail Event History/00-Overview|Overview]] | [[04-CloudTrail Event History Part 2|CloudTrail Event History Part 2]]
