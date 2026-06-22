---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## Introduction to Mass Assignment

Mass assignment, also known as overposting, is a critical security issue in web applications, particularly those involving APIs. This vulnerability occurs when an application allows an attacker to modify fields that should not be modifiable by the user. In essence, mass assignment happens when an API endpoint accepts a large number of input parameters and blindly maps these inputs to an object without proper validation or sanitization.

### What is Mass Assignment?

Mass assignment refers to the practice of allowing a client to submit a large number of fields in a single request, which are then automatically mapped to an object in the backend. This can lead to unintended consequences if certain fields are not properly validated or restricted. For instance, an attacker might be able to modify sensitive fields such as `isAdmin` or `role` by simply including these fields in the request payload.

### Why Does Mass Assignment Matter?

Mass assignment is significant because it can lead to unauthorized access, privilege escalation, and data corruption. If an attacker can manipulate fields that should remain immutable, they can potentially gain elevated privileges or alter critical data within the system. This can result in severe security breaches and loss of trust from users.

### How Does Mass Assignment Work Under the Hood?

To understand mass assignment, let's consider a typical scenario where an API endpoint handles user updates. Suppose we have an endpoint `/api/users/:id` that allows updating user details. The request body might look something like this:

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "real_name": "John Doe",
  "password": "secure_password",
  "comment": "This is a comment.",
  "isAdmin": true
}
```

In a poorly implemented system, the server might take this entire payload and directly map it to a user object in the database. If the `isAdmin` field is not properly validated, an attacker could set it to `true`, thereby elevating their privileges.

### Real-World Example: CVE-2018-1268

A notable real-world example of mass assignment is CVE-2018-1268, which affected the popular Ruby on Rails framework. In this case, an attacker could exploit a mass assignment vulnerability to escalate their privileges by modifying the `admin` attribute of a user object. This allowed attackers to gain administrative access to the application, leading to potential data breaches and unauthorized actions.

### Background Theory

To fully grasp the implications of mass assignment, it's essential to understand the underlying principles of object mapping and data validation in web applications.

#### Object Mapping

Object mapping is the process of converting data from one format to another, typically between a database record and an object in memory. In the context of web applications, this often involves mapping incoming request data to an object model used by the application.

#### Data Validation

Data validation is crucial in ensuring that the data received from clients is safe and appropriate for processing. This includes checking for the presence of required fields, verifying the format and type of data, and ensuring that sensitive fields are not being manipulated.

### Detailed Example: Vulnerable Code

Let's walk through a detailed example to illustrate how mass assignment can occur and how it can be exploited.

#### Vulnerable Code

Consider the following Node.js Express application that handles user updates:

```javascript
const express = require('express');
const app = express();
app.use(express.json());

// User model
class User {
  constructor(data) {
    this.username = data.username;
    this.email = data.email;
    this.realName = data.realName;
    this.password = data.password;
    this.isAdmin = data.isAdmin || false; // Default to false
  }
}

let users = [];

app.post('/api/users', (req, res) => {
  const newUser = new User(req.body);
  users.push(newUser);
  res.status(201).send(newUser);
});

app.listen(3000, () => console.log('Server started on port 3000'));
```

In this example, the `User` class constructor directly maps the incoming request data to the object properties. An attacker could exploit this by sending a request like the following:

```http
POST /api/users HTTP/1.1
Host: localhost:3000
Content-Type: application/json

{
  "username": "attacker",
  "email": "attacker@example.com",
  "realName": "Attacker",
  "password": "weak_password",
  "isAdmin": true
}
```

The server would create a new user with `isAdmin` set to `true`, granting the attacker administrative privileges.

### How to Prevent / Defend Against Mass Assignment

Preventing mass assignment requires a combination of proper validation, whitelisting, and secure coding practices. Let's explore these methods in detail.

#### Whitelisting Properties

One effective way to prevent mass assignment is to explicitly whitelist the properties that can be modified. This ensures that only the intended fields are updated, preventing unauthorized modifications.

##### Secure Code Example

Here’s how the previous example can be modified to include whitelisting:

```javascript
const express = require('express');
const app = express();
app.use(express.json());

class User {
  constructor(data) {
    this.username = data.username;
    this.email = data.email;
    this.realName = data.realName;
    this.password = data.password;
    this.isAdmin = false; // Default to false
  }

  update(data) {
    if (data.username) this.username = data.username;
    if (data.email) this.email = data.email;
    if (data.realName) this.realName = data.realName;
    if (data.password) this.password = data.password;
  }
}

let users = [];

app.post('/api/users', (req, res) => {
  const newUser = new User(req.body);
  users.push(newUser);
  res.status(201).send(newUser);
});

app.put('/api/users/:id', (req, res) => {
  const userId = parseInt(req.params.id);
  const userToUpdate = users.find(user => user.id === userId);

  if (!userToUpdate) {
    return res.status(404).send({ error: 'User not found' });
  }

  userToUpdate.update(req.body);
  res.send(userToUpdate);
});

app.listen(3000, () => console.log('Server started on port 3000'));
```

In this updated example, the `update` method explicitly checks for the presence of each field before updating it. This prevents unauthorized modification of sensitive fields like `isAdmin`.

#### Data Validation

Another important aspect of preventing mass assignment is thorough data validation. This includes checking for the presence of required fields, verifying the format and type of data, and ensuring that sensitive fields are not being manipulated.

##### Secure Code Example

Here’s how data validation can be added to the previous example:

```javascript
const express = require('express');
const app = express();
app.use(express.json());

function validateUserInput(data) {
  if (!data.username) return { error: 'Username is required' };
  if (!data.email) return { error: 'Email is required' };
  if (!data.realName) return { error: 'Real name is required' };
  if (!data.password) return { error: 'Password is required' };

  return null;
}

class User {
  constructor(data) {
    this.username = data.username;
    this.email = data.email;
    this.realName = data.realName;
    this.password = data.password;
    this.isAdmin = false; // Default to false
  }

  update(data) {
    if (data.username) this.username = data.username;
    if (data.email) this.email = data.email;
    if (data.realName) this.realName = data.realName;
    if (data.password) this.password = data.password;
  }
}

let users = [];

app.post('/api/users', (req, res) => {
  const validationError = validateUserInput(req.body);
  if (validationError) return res.status(400).send(validationError);

  const newUser = new User(req.body);
  users.push(newUser);
  res.status(201).send(newUser);
});

app.put('/api/users/:id', (req, res) => {
  const userId = parseInt(req.params.id);
  const userToUpdate = users.find(user => user.id === userId);

  if (!userToUpdate) {
    return res.status(404).send({ error: 'User not found' });
  }

  const validationError = validateUserInput(req.body);
  if (validationError) return res.status(400).send(validationError);

  userToUpdate.update(req.body);
  res.send(userToUpdate);
});

app.listen(3000, () => console.log('Server started on port 3000'));
```

In this updated example, the `validateUserInput` function ensures that all required fields are present and valid before creating or updating a user.

### Detection and Prevention

Detecting and preventing mass assignment vulnerabilities involves both static analysis and runtime monitoring.

#### Static Analysis

Static analysis tools can help identify potential mass assignment vulnerabilities by analyzing the codebase for patterns that allow unfiltered input to be mapped to objects. Tools like ESLint for JavaScript or SonarQube for various languages can be configured to flag suspicious code patterns.

#### Runtime Monitoring

Runtime monitoring tools can detect and alert on suspicious activities, such as unexpected modifications to sensitive fields. These tools can help catch mass assignment attacks in real-time and provide insights into the nature of the attack.

### Conclusion

Mass assignment is a serious security vulnerability that can lead to unauthorized access and data corruption. By understanding the principles behind object mapping and data validation, developers can implement robust defenses against this threat. Whitelisting properties, thorough data validation, and using static analysis and runtime monitoring tools are key strategies for preventing mass assignment vulnerabilities.

### Practice Labs

For hands-on experience with mass assignment vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on mass assignment and other API security issues.
- **OWASP Juice Shop**: A deliberately insecure web application that includes scenarios for practicing API security.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of web application vulnerabilities, including mass assignment.

By engaging with these labs, you can gain practical experience in identifying and mitigating mass assignment vulnerabilities in real-world scenarios.

---
<!-- nav -->
[[01-Introduction to Mass Assignment Vulnerability|Introduction to Mass Assignment Vulnerability]] | [[API Security/05-OWASP API TOP 10/07-API6 Mass Assignment/00-Overview|Overview]] | [[03-API6 Mass Assignment|API6 Mass Assignment]]
