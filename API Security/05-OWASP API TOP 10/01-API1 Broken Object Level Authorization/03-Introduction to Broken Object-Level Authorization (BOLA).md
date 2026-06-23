---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## Introduction to Broken Object-Level Authorization (BOLA)

Broken Object-Level Authorization (BOLA) is a critical vulnerability within the realm of API security. This vulnerability occurs when an API fails to properly enforce access controls at the object level, allowing unauthorized users to access sensitive data or perform actions they should not be permitted to do. In essence, BOLA arises when an attacker can manipulate identifiers in API requests to gain access to resources they are not authorized to view or modify.

### What is Object-Level Authorization?

Object-Level Authorization refers to the practice of ensuring that a user has the appropriate permissions to interact with specific objects or resources within an application. This means that even if a user is authenticated and has certain privileges, they should only be allowed to access or modify the objects they are explicitly authorized to handle.

#### Why Does Object-Level Authorization Matter?

Proper object-level authorization is crucial because it helps prevent unauthorized access to sensitive data and ensures that users can only interact with the resources they are supposed to. Without this, an attacker could potentially manipulate identifiers in API requests to gain access to unauthorized resources, leading to data breaches, privilege escalation, and other serious security issues.

### How Does Broken Object-Level Authorization Work?

In a typical scenario, an API might expose endpoints that allow users to retrieve or modify their own data. However, if the API does not properly validate the user's authorization to access specific objects, an attacker could manipulate the identifiers in the API requests to gain access to other users' data.

For example, consider an API endpoint `/api/users/{userId}` that allows users to retrieve their own profile information. If the API does not verify that the requesting user is authorized to access the specified `userId`, an attacker could simply change the `userId` in the request to access another user's profile.

#### Example Scenario

Let's walk through a detailed example to illustrate how BOLA can occur:

1. **API Endpoint**: `/api/users/{userId}`
2. **Authenticated User**: Alice (with `userId = 1`)
3. **Normal Request**: Alice makes a request to `/api/users/1` to retrieve her own profile information.
4. **Malicious Request**: An attacker (Bob) changes the `userId` in the request to `/api/users/2` to attempt to retrieve another user's profile information.

If the API does not properly validate Alice's authorization to access `userId = 2`, Bob could successfully retrieve the profile information of another user, leading to a BOLA vulnerability.

### Real-World Examples of BOLA

Several high-profile breaches and vulnerabilities have been attributed to BOLA. Here are a few recent examples:

1. **CVE-2021-30116**: A vulnerability in the Microsoft Exchange Server allowed attackers to bypass authentication and gain unauthorized access to email accounts. This was due to improper validation of user permissions, allowing attackers to manipulate identifiers and access other users' emails.

2. **CVE-2020-1472**: Also known as "Zerologon," this vulnerability in the Netlogon Remote Protocol (MS-NRPC) allowed attackers to reset the password of any user, including the domain administrator. This was possible because the protocol did not properly validate the user's authorization to perform such actions.

### Detailed Example: Exploiting BOLA

To better understand how BOLA can be exploited, let's consider a more detailed example involving an API that manages user profiles.

#### Vulnerable API Code

```python
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify(user.profile)
    else:
        return jsonify({"error": "User not found"}), 404
```

In this example, the API endpoint `/api/users/<int:user_id>` retrieves the profile information of a user based on the provided `user_id`. However, the code does not check whether the authenticated user is authorized to access the specified `user_id`.

#### Exploitation Steps

1. **Identify the Vulnerability**: An attacker identifies that the API does not properly validate the user's authorization to access specific `user_id`s.
2. **Craft the Malicious Request**: The attacker crafts a request to `/api/users/<another_user_id>` to retrieve another user's profile information.
3. **Send the Request**: The attacker sends the malicious request to the API.
4. **Receive Unauthorized Data**: If the API does not properly validate the user's authorization, the attacker receives the profile information of another user.

#### Full HTTP Request and Response

**HTTP Request**

```http
GET /api/users/2 HTTP/1.1
Host: example.com
Authorization: Bearer <valid_token>
```

**HTTP Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "profile": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "123-456-7890"
  }
}
```

### How to Prevent / Defend Against BOLA

Preventing BOLA requires implementing robust access control mechanisms at the object level. Here are several strategies to ensure proper object-level authorization:

#### Secure Coding Practices

1. **Validate User Permissions**: Always validate the authenticated user's permissions to access specific objects. Ensure that the user is authorized to perform the requested action on the specified object.

2. **Use Role-Based Access Control (RBAC)**: Implement RBAC to define roles and permissions for different types of users. Ensure that users can only access objects that correspond to their assigned roles.

3. **Least Privilege Principle**: Follow the principle of least privilege by granting users only the minimum permissions necessary to perform their tasks.

#### Example of Secure Code

Here is an example of how to implement proper object-level authorization in Python using Flask:

```python
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    role = db.Column(db.String(80), nullable=False)

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    current_user = get_current_user()  # Function to get the currently authenticated user
    target_user = User.query.get(user_id)
    
    if target_user and current_user.role == 'admin':
        return jsonify(target_user.profile)
    elif target_user and current_user.id == user_id:
        return jsonify(target_user.profile)
    else:
        return jsonify({"error": "Unauthorized access"}), 403

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, the API checks whether the authenticated user is an admin or the owner of the specified `user_id` before returning the profile information.

#### Detection and Prevention Tools

1. **Static Application Security Testing (SAST)**: Use SAST tools to identify potential BOLA vulnerabilities in your codebase. These tools can analyze your code to find instances where object-level authorization is not properly enforced.

2. **Dynamic Application Security Testing (DAST)**: Use DAST tools to simulate attacks and test your API for BOLA vulnerabilities. These tools can help you identify and mitigate real-world attack scenarios.

3. **Penetration Testing**: Conduct regular penetration testing to identify and address BOLA vulnerabilities. Pen testers can simulate various attack scenarios to ensure that your API is properly securing object-level access.

### Conclusion

Broken Object-Level Authorization (BOLA) is a critical vulnerability that can lead to serious security issues if not properly addressed. By understanding the concepts, identifying real-world examples, and implementing robust access control mechanisms, you can effectively prevent and defend against BOLA vulnerabilities in your APIs.

### Practice Labs

To further solidify your understanding of BOLA and API security, consider the following practice labs:

1. **PortSwigger Web Security Academy**: Offers interactive labs that cover various aspects of API security, including BOLA.
2. **OWASP Juice Shop**: A deliberately insecure web application that includes numerous security vulnerabilities, including BOLA.
3. **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains numerous security vulnerabilities, including BOLA.

By working through these labs, you can gain hands-on experience in identifying and mitigating BOLA vulnerabilities in real-world scenarios.

---
<!-- nav -->
[[02-Introduction to Broken Object Level Authorization|Introduction to Broken Object Level Authorization]] | [[API Security/05-OWASP API TOP 10/01-API1 Broken Object Level Authorization/00-Overview|Overview]] | [[04-Introduction to Broken Object-Level Authorization|Introduction to Broken Object-Level Authorization]]
