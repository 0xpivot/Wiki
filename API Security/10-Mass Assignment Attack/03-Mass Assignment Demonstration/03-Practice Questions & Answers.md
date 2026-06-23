---
course: API Security
topic: Mass Assignment Attack
tags: [api-security]
---

## Practice Questions & Answers

**Q1. What is mass assignment vulnerability and how does it affect API security?**

Mass assignment vulnerability occurs when an application allows external input to set values for object properties that should not be modifiable by the user. In the context of APIs, this can lead to unauthorized access or privilege escalation if sensitive fields such as `admin` status can be manipulated through user input. For example, in the demonstration, the attacker was able to set the `admin` field to `true` during user registration, thereby gaining administrative privileges.

**Q2. How can you identify potential mass assignment vulnerabilities in an API?**

To identify potential mass assignment vulnerabilities, one should review the API endpoints that handle object creation or updates. Look for endpoints that accept JSON payloads containing multiple attributes and check whether all these attributes are properly validated and sanitized before being assigned to the corresponding object properties. Additionally, ensure that sensitive fields like `admin` status are protected and cannot be modified via user input.

**Q3. Explain how the mass assignment vulnerability was exploited in the demonstration.**

In the demonstration, the attacker exploited the mass assignment vulnerability by sending a POST request to the user registration endpoint with a JSON payload that included the `admin` field set to `true`. The API did not validate or restrict this field, allowing the attacker to create a new user account with administrative privileges. This was evident when the newly created user with ID `12` had its `admin` property set to `true`.

**Q4. What measures can be taken to prevent mass assignment vulnerabilities in APIs?**

To prevent mass assignment vulnerabilities, developers can take several measures:

1. **Whitelist Attributes**: Only allow specific attributes to be updated or created. This means explicitly defining which fields can be modified via user input.
   
   ```python
   class User:
       def __init__(self, data):
           self.username = data.get('username')
           self.password = data.get('password')
           # Do not allow 'admin' to be set via user input
   ```

2. **Strong Input Validation**: Ensure that all incoming data is validated against expected formats and constraints. Use frameworks or libraries that provide built-in protection mechanisms against mass assignment.

3. **Use ORM Safeguards**: If using an ORM (Object-Relational Mapping) tool, configure it to prevent mass assignment. Many ORMs have settings or methods to whitelist or blacklist certain attributes.

4. **Role-Based Access Control (RBAC)**: Implement RBAC to ensure that only authorized users can perform actions that modify sensitive fields.

**Q5. Can you provide a recent real-world example of a mass assignment vulnerability?**

A notable example of a mass assignment vulnerability occurred in the Ruby on Rails framework. In 2012, a vulnerability was discovered that allowed attackers to escalate their privileges by manipulating the `role` attribute during user creation or update operations. This vulnerability was fixed in later versions of Ruby on Rails, but it highlighted the importance of properly securing sensitive fields in web applications.

**Q6. How would you exploit a mass assignment vulnerability in an API to gain unauthorized access?**

To exploit a mass assignment vulnerability, an attacker would follow these steps:

1. Identify an API endpoint that handles user creation or updates.
2. Craft a JSON payload that includes sensitive fields like `admin` or `role`.
3. Send a POST or PUT request to the endpoint with the crafted payload.
4. Verify that the sensitive fields were successfully set by querying the API or logging into the system with the newly created or updated user credentials.

For example, if the vulnerable API endpoint is `/users`, the attacker might send a POST request with the following payload:

```json
{
  "username": "attacker",
  "password": "password123",
  "admin": true
}
```

If successful, the attacker would have created a user with administrative privileges.

**Q7. What is the difference between mass assignment and SQL injection attacks?**

Mass assignment and SQL injection are both types of security vulnerabilities, but they differ in their nature and exploitation methods:

- **Mass Assignment**: This vulnerability occurs when an application allows external input to set values for object properties that should not be modifiable by the user. It typically affects object-oriented programming languages and frameworks that use ORM tools. Exploitation involves manipulating the input to set sensitive fields like `admin` status.

- **SQL Injection**: This vulnerability occurs when an application constructs SQL queries using untrusted input without proper sanitization. An attacker can inject malicious SQL code to manipulate database queries, potentially leading to unauthorized data access, modification, or deletion. Exploitation involves crafting input that alters the intended SQL query structure.

Both vulnerabilities require careful input validation and proper handling of user-provided data to prevent exploitation.

---
<!-- nav -->
[[02-Mass Assignment Attack|Mass Assignment Attack]] | [[API Security/10-Mass Assignment Attack/03-Mass Assignment Demonstration/00-Overview|Overview]]
