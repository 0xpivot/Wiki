---
course: API Security
topic: Mass Assignment Attack
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what a mass assignment vulnerability is and why it poses a security risk.**

Mass assignment vulnerabilities occur when an application allows unfiltered input to update multiple attributes of an object, including sensitive ones such as roles or permissions. This poses a significant security risk because attackers can manipulate the input to set values for attributes they should not have access to, potentially escalating their privileges within the system.

**Q2. How would you exploit a mass assignment vulnerability in an API to escalate your privileges?**

To exploit a mass assignment vulnerability, an attacker would craft a request that includes parameters corresponding to sensitive fields, such as role IDs. For example, if the API allows updating user details via a PUT request, the attacker could send a payload like:

```json
{
  "role_id": 1,
  "email": "attacker@example.com"
}
```

Here, `role_id` is set to 1, which might correspond to an administrative role. By sending this request to the appropriate endpoint, the attacker could elevate their privileges to those of an administrator.

**Q3. Why is it important to validate and sanitize inputs in APIs to prevent mass assignment vulnerabilities?**

Validating and sanitizing inputs is crucial because it ensures that only expected and safe data is processed by the application. Without proper validation, an attacker can inject malicious data that manipulates the state of the application in unintended ways. For instance, in the context of mass assignment vulnerabilities, an attacker could set arbitrary values for sensitive attributes like role IDs, leading to privilege escalation.

**Q4. How would you configure an API to mitigate mass assignment vulnerabilities?**

To mitigate mass assignment vulnerabilities, you should:

1. **Whitelist Attributes**: Only allow specific, non-sensitive attributes to be updated through mass assignment operations. For example, in a user update operation, only allow changes to `name`, `email`, etc., but not `role_id`.

2. **Use Strong Input Validation**: Ensure that all input parameters are validated against expected formats and ranges. This helps prevent injection of unexpected values.

3. **Role-Based Access Control (RBAC)**: Implement RBAC to ensure that only users with appropriate permissions can modify certain attributes. For example, only administrators should be able to change role IDs.

4. **Automated Testing**: Use automated testing tools to detect potential mass assignment vulnerabilities in your API.

**Q5. Reference a recent real-world example of a mass assignment vulnerability and explain how it was exploited.**

A notable example is the CVE-2021-21972, which affected the popular Ruby on Rails framework. In this case, the vulnerability allowed attackers to manipulate the `id` attribute during a mass assignment operation, leading to unauthorized privilege escalation. The exploit involved crafting a POST request to update a user’s profile, where the attacker included a parameter to set the `id` attribute to a value corresponding to an administrative user. This effectively granted the attacker administrative privileges, demonstrating the severe consequences of mass assignment vulnerabilities.

---
<!-- nav -->
[[02-Understanding Mass Assignment Vulnerabilities|Understanding Mass Assignment Vulnerabilities]] | [[API Security/10-Mass Assignment Attack/02-Mass Assignment Demonstration 3/00-Overview|Overview]]
