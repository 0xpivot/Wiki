---
course: API Security
topic: BFLA Issues
tags: [api-security]
---

## Introduction to Broken Function Level Authorization (BFLA)

Broken Function Level Authorization (BFLA) is a critical security issue that arises when an application fails to properly enforce access controls at the function level. This means that users might be able to perform actions they should not be allowed to, such as modifying or deleting data that does not belong to them. In the context of APIs, this can lead to severe vulnerabilities, especially when dealing with sensitive operations like editing grades in a student portal.

### What is BFLA?

BFLA occurs when an application allows unauthorized users to perform actions that they should not be permitted to do. This typically happens due to insufficient or incorrect implementation of authorization checks within the application logic. For instance, in a student portal, a user might be able to edit the grades of other students if proper authorization checks are not in place.

#### Why Does BFLA Matter?

BFLA is significant because it can lead to unauthorized access and manipulation of sensitive data. In the case of a student portal, this could result in students being able to alter their own or others' grades, leading to academic dishonesty and potential legal issues. Moreover, BFLA can be exploited by attackers to gain unauthorized access to critical systems and data, making it a serious security concern.

### How Does BFLA Work?

To understand BFLA, let's consider a practical example using a student portal API. Suppose we have an API endpoint that allows users to view, edit, and delete grades. The API uses HTTP methods such as GET, PUT, and DELETE to interact with the grades.

#### Example Scenario

Consider the following scenario:

- A student portal API has endpoints for viewing, editing, and deleting grades.
- Each grade is associated with a unique `grade_id` and a `user_id`.
- Users should only be able to view, edit, or delete grades that belong to them.

Let's break down the steps involved in this scenario:

1. **Viewing Grades**: Users can view their own grades using the GET method.
2. **Editing Grades**: Users can edit their own grades using the PUT method.
3. **Deleting Grades**: Users can delete their own grades using the DELETE method.

However, if proper authorization checks are not implemented, users might be able to perform these actions on grades that do not belong to them.

### Detailed Example

Let's walk through a detailed example to illustrate how BFLA can occur and how it can be exploited.

#### Step 1: Viewing Grades

First, let's consider the GET request to view grades.

```http
GET /grades?user_id=3 HTTP/1.1
Host: studentportal.example.com
Authorization: Bearer <access_token>
```

The server responds with the grades associated with `user_id=3`.

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "grades": [
    {
      "grade_id": 7,
      "user_id": 3,
      "grade": 71
    }
  ]
}
```

#### Step 2: Editing Grades

Next, let's consider the PUT request to edit a grade.

```http
PUT /grades/13 HTTP/1.1
Host: studentportal.example.com
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "grade": 100
}
```

If proper authorization checks are not in place, the server might update the grade without verifying if the user is authorized to modify it.

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Grade updated successfully"
}
```

#### Step 3: Deleting Grades

Finally, let's consider the DELETE request to delete a grade.

```http
DELETE /grades/13 HTTP/1.1
Host: studentportal.example.com
Authorization: Bearer <access_token>
```

Again, if proper authorization checks are not in place, the server might delete the grade without verifying if the user is authorized to do so.

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Grade deleted successfully"
}
```

### Real-World Examples and Recent Breaches

BFLA vulnerabilities have been observed in various real-world scenarios. One notable example is the breach of a healthcare provider's system, where unauthorized users were able to access and modify patient records due to insufficient authorization checks. Another example is the exploitation of a university's student portal, where students were able to alter their grades and those of their peers.

#### CVE Example

CVE-2021-3427 is a recent example where a vulnerability in a web application allowed unauthorized users to access and modify sensitive data due to improper authorization checks. This CVE highlights the importance of implementing robust authorization mechanisms to prevent such attacks.

### How to Prevent / Defend Against BFLA

Preventing BFLA requires a combination of proper authorization checks, secure coding practices, and regular security audits. Here are some key strategies to defend against BFLA:

#### 1. Implement Proper Authorization Checks

Ensure that every API endpoint performs thorough authorization checks before allowing any action. This includes verifying the user's identity and ensuring they have the necessary permissions to perform the requested action.

##### Secure Coding Fix

Here is an example of how to implement proper authorization checks in a Python Flask application:

```python
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

# Sample user data
users = {
    1: {'username': 'user1', 'password': 'pass1'},
    2: {'username': 'user2', 'password': 'pass2'}
}

# Sample grade data
grades = {
    1: {'grade_id': 1, 'user_id': 1, 'grade': 71},
    2: {'grade_id': 2, 'user_id': 2, 'grade': 85}
}

def authenticate(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return jsonify({'message': 'Authentication failed'}), 401
        return f(*args, **kwargs)
    return decorated

def check_auth(username, password):
    for user_id, user_data in users.items():
        if user_data['username'] == username and user_data['password'] == password:
            return True
    return False

@app.route('/grades/<int:grade_id>', methods=['PUT'])
@authenticate
def update_grade(grade_id):
    user_id = 1  # Replace with actual user ID retrieval logic
    if grade_id not in grades or grades[grade_id]['user_id'] != user_id:
        return jsonify({'message': 'Unauthorized access'}), 403
    new_grade = request.json.get('grade')
    grades[grade_id]['grade'] = new_grade
    return jsonify({'message': 'Grade updated successfully'})

if __name__ == '__main__':
    app.run(debug=True)
```

#### 2. Regular Security Audits

Perform regular security audits to identify and address any potential vulnerabilities. This includes both automated scans and manual reviews of the codebase.

#### 3. Use Secure Coding Practices

Adopt secure coding practices to minimize the risk of introducing vulnerabilities. This includes using parameterized queries, input validation, and avoiding hardcoded credentials.

#### 4. Implement Role-Based Access Control (RBAC)

Use RBAC to define and enforce access control policies based on user roles. This ensures that users can only perform actions that are appropriate for their role.

### Conclusion

Broken Function Level Authorization (BFLA) is a serious security issue that can lead to unauthorized access and manipulation of sensitive data. By implementing proper authorization checks, performing regular security audits, and adopting secure coding practices, organizations can effectively defend against BFLA vulnerabilities.

### Practice Labs

For hands-on practice with BFLA, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including BFLA.
- **OWASP Juice Shop**: A deliberately insecure web application that can be used to practice identifying and exploiting BFLA vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable, providing a platform to learn about and test BFLA.

By engaging with these labs, you can gain practical experience in identifying and mitigating BFLA vulnerabilities in real-world applications.

---
<!-- nav -->
[[01-Introduction to Broken Authentication|Introduction to Broken Authentication]] | [[API Security/07-BFLA Issues/02-Broken Authentication Demonstration/00-Overview|Overview]] | [[03-Introduction to Broken Functional Level Authorization (BFLA)|Introduction to Broken Functional Level Authorization (BFLA)]]
