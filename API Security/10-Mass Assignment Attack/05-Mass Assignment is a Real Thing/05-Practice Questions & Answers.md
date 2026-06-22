---
course: API Security
topic: Mass Assignment Attack
tags: [api-security]
---

## Practice Questions & Answers

**Q1. What is a mass assignment vulnerability, and why is it considered dangerous?**

A mass assignment vulnerability occurs when a user is able to initialize or override server-side variables that were not intended to be modified by the user. This can lead to significant security risks, such as unauthorized access, data tampering, and privilege escalation. For example, if a user can set their own `email_verified` flag to `true`, they might bypass necessary verification steps, leading to unauthorized account access.

**Q2. How can a malicious user exploit a mass assignment vulnerability during user registration?**

A malicious user can exploit a mass assignment vulnerability by including additional parameters in the registration request that are not intended to be set by the user. For instance, consider a registration endpoint that accepts `email` and `password`. If the endpoint does not properly sanitize inputs, a user could include an extra parameter like `email_verified=true` in the request body. This would allow the user to bypass the email verification process, leading to unauthorized account creation.

**Q3. Explain how nested objects can contribute to mass assignment vulnerabilities.**

Nested objects can contribute to mass assignment vulnerabilities when developers fail to properly validate and sanitize input data. For example, if an API endpoint accepts a JSON payload containing nested objects, a malicious user could inject additional properties within these nested objects. These properties might correspond to sensitive attributes, such as user roles or permissions. If the application does not enforce strict validation rules, the attacker could potentially escalate their privileges by setting these attributes to desired values.

**Q4. How can developers prevent mass assignment vulnerabilities in their applications?**

To prevent mass assignment vulnerabilities, developers should implement strict input validation and sanitization practices. Specifically:

1. **Whitelist Attributes**: Only allow specific attributes to be updated or created. For example, if a user profile update should only change the `name` and `bio`, explicitly whitelist these fields and ignore any others.

2. **Parameter Filtering**: Use frameworks or libraries that automatically filter out unexpected parameters. Many modern web frameworks provide mechanisms to whitelist or blacklist parameters.

3. **Manual Validation**: Manually validate each incoming parameter to ensure it matches expected types and values. For example, ensure that `email_verified` can only be set to `false` unless the proper verification steps have been completed.

4. **Use Strong Typing**: Employ strong typing in languages that support it to catch type mismatches early.

Here’s an example of how to whitelist attributes in Ruby on Rails:

```ruby
class User < ApplicationRecord
  attr_accessible :name, :bio # Only allow name and bio to be mass assigned
end
```

**Q5. Provide a recent real-world example of a mass assignment vulnerability and explain how it was exploited.**

One notable example is the CVE-2019-16760, which affected the popular Ruby on Rails framework. The vulnerability allowed attackers to manipulate certain attributes, such as `admin` status, through mass assignment. In this case, an attacker could send a crafted POST request to a user update endpoint, including an `admin` parameter set to `true`.

For instance, an attacker might send a request like:

```json
{
  "user": {
    "name": "attacker",
    "email": "attacker@example.com",
    "admin": true
  }
}
```

If the application did not properly restrict which attributes could be updated, the attacker could elevate their privileges to admin level, gaining full control over the application.

To mitigate such vulnerabilities, developers should follow best practices such as those outlined in the previous question.

---
<!-- nav -->
[[04-Understanding Mass Assignment Vulnerabilities|Understanding Mass Assignment Vulnerabilities]] | [[API Security/10-Mass Assignment Attack/05-Mass Assignment is a Real Thing/00-Overview|Overview]]
