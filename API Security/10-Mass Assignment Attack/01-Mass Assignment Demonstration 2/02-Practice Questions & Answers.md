---
course: API Security
topic: Mass Assignment Attack
tags: [api-security]
---

## Practice Questions & Answers

**Q1. What is mass assignment and how does it relate to API security?**

Mass assignment occurs when an application allows an attacker to set arbitrary object properties through an input form or API endpoint. This can lead to security vulnerabilities if the application does not properly validate or sanitize the input. In the context of API security, mass assignment can allow an attacker to modify sensitive fields such as `admin` status or `disabled` flags, leading to unauthorized access or privilege escalation.

**Q2. How can you exploit a mass assignment vulnerability in an API?**

To exploit a mass assignment vulnerability, an attacker would typically craft a POST request with additional parameters that are not intended to be modifiable by the user. For example, if the API endpoint is supposed to update only the email address, an attacker might include extra parameters like `admin: true` or `username: 'offensive hunter'`. If the API does not properly filter these inputs, the attacker could gain elevated privileges or alter critical data.

**Q3. Explain how to prevent mass assignment vulnerabilities in your API.**

Preventing mass assignment vulnerabilities involves ensuring that only the expected fields can be modified via an API request. This can be achieved by:

- Explicitly defining which fields are allowed to be updated.
- Using strong typing and validation frameworks that enforce field constraints.
- Sanitizing all input data to ensure it conforms to expected formats and values.
- Implementing role-based access control (RBAC) to restrict which users can modify certain fields.

For example, in a Ruby on Rails application, you can use the `attr_accessible` method to specify which attributes are allowed to be mass assigned.

```ruby
class User < ActiveRecord::Base
  attr_accessible :email, :username
end
```

In this case, only the `email` and `username` fields can be updated through mass assignment.

**Q4. Describe a recent real-world example of a mass assignment vulnerability and its impact.**

A notable example of a mass assignment vulnerability is the case of the popular open-source project Devise, which is used for authentication in Ruby on Rails applications. In 2012, a vulnerability was discovered where an attacker could exploit mass assignment to escalate their privileges. By sending a crafted request to the `/users` endpoint, an attacker could set the `admin` flag to `true`, effectively gaining administrative access to the application.

This vulnerability affected numerous applications using Devise, including high-profile projects like GitHub. The impact was significant, as it exposed a large number of users to potential unauthorized access and data breaches.

**Q5. How would you test for mass assignment vulnerabilities in an API?**

Testing for mass assignment vulnerabilities involves systematically attempting to modify unexpected fields through API requests. Here are some steps to follow:

1. Identify all endpoints that accept POST or PUT requests.
2. Determine the expected fields for each endpoint.
3. Craft requests that include additional, unexpected fields.
4. Check if the unexpected fields are accepted and applied to the database.

For example, if an endpoint is designed to update a user’s email address, you might send a request like this:

```json
{
  "email": "new@example.com",
  "admin": true,
  "username": "hacker"
}
```

If the server accepts and applies the `admin` and `username` fields, it indicates a mass assignment vulnerability.

**Q6. What are the best practices for securing APIs against mass assignment attacks?**

Best practices for securing APIs against mass assignment attacks include:

- **Whitelist Input Fields:** Only allow specific fields to be updated via API requests. Use frameworks or libraries that support whitelisting.
  
- **Input Validation:** Validate all incoming data to ensure it conforms to expected formats and values. Use regular expressions, type checking, and other validation techniques.

- **Role-Based Access Control (RBAC):** Implement RBAC to ensure that only authorized users can modify certain fields. Restrict access to sensitive fields based on user roles.

- **Automated Testing:** Regularly test your API for mass assignment vulnerabilities using automated tools and penetration testing techniques.

By following these best practices, you can significantly reduce the risk of mass assignment vulnerabilities in your API.

---
<!-- nav -->
[[API Security/10-Mass Assignment Attack/01-Mass Assignment Demonstration 2/01-Introduction to Mass Assignment Attack|Introduction to Mass Assignment Attack]] | [[API Security/10-Mass Assignment Attack/01-Mass Assignment Demonstration 2/00-Overview|Overview]]
