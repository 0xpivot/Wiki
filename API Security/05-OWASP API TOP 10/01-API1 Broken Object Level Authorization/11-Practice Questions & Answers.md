---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what is meant by "broken object level authorization" in the context of API security.**

Broken object level authorization refers to a situation where an API does not properly enforce authorization rules for accessing specific objects or resources. Typically, an authenticated user should only be able to access resources that they are explicitly authorized to access. However, if the API fails to correctly validate the user's permissions before granting access, an attacker could manipulate the request to gain unauthorized access to other users' data or perform actions they should not be allowed to do. This can lead to serious security issues such as data breaches or unauthorized modifications to resources.

**Q2. How can an attacker exploit a broken object level authorization vulnerability? Provide a practical example.**

An attacker can exploit a broken object level authorization vulnerability by manipulating the unique identifiers (IDs) in API requests to access resources that they are not supposed to. For instance, consider an API endpoint `/api/accounts/{id}` that retrieves account details based on the `id` parameter. If the API does not properly check whether the authenticated user is authorized to view the account associated with the given `id`, an attacker could simply change the `id` to that of another user and retrieve their account details. Here’s a practical example:

```plaintext
GET /api/accounts/123 HTTP/1.1
Authorization: Bearer <valid_token>
```

If the API does not check the authorization for `id=123`, an attacker could change the `id` to `456` and retrieve another user's account details:

```plaintext
GET /api/accounts/456 HTTP/1.1
Authorization: Bearer <valid_token>
```

**Q3. Why is it difficult to detect broken object level authorization vulnerabilities using automated tools?**

Automated tools often struggle to detect broken object level authorization vulnerabilities because these vulnerabilities depend heavily on the specific business logic and authorization rules of the application. Automated scanners typically rely on predefined patterns and signatures to identify vulnerabilities, but they may not fully understand the complex relationships between users, roles, and resources within an application. Additionally, these tools may not have the necessary context to determine whether a user is authorized to access a particular resource based on the application's business logic. As a result, manual testing and understanding of the application's authorization mechanisms are crucial for identifying such vulnerabilities.

**Q4. Describe a recent real-world example of a broken object level authorization vulnerability and its impact.**

A notable example of a broken object level authorization vulnerability occurred with the Capital One data breach in 2019 (CVE-2019-11253). In this incident, an attacker exploited a misconfigured web application firewall (WAF) that did not properly restrict access to sensitive data. The WAF was configured to allow access to certain API endpoints without enforcing proper authorization checks. As a result, the attacker was able to access the personal information of approximately 100 million customers and small business clients. This breach highlighted the importance of implementing robust authorization controls and regularly reviewing configurations to ensure that sensitive data is protected.

**Q5. How can developers prevent broken object level authorization vulnerabilities in their APIs?**

Developers can prevent broken object level authorization vulnerabilities by implementing strict authorization checks for every API endpoint that accesses sensitive resources. Here are some best practices:

1. **Implement Role-Based Access Control (RBAC):** Ensure that each user has a defined set of roles and permissions that dictate what actions they can perform and what resources they can access.
   
2. **Validate User Permissions:** Before allowing access to a resource, validate that the authenticated user has the appropriate permissions to perform the requested action.
   
3. **Use Unique Identifiers:** Avoid using sequential or easily guessable identifiers for resources. Instead, use GUIDs or other unique identifiers that are harder to predict.
   
4. **Review and Test Authorization Logic:** Regularly review and test the authorization logic to ensure that it correctly enforces access controls and prevents unauthorized access.
   
5. **Educate Developers:** Train developers on the importance of proper authorization and the risks associated with broken object level authorization vulnerabilities.

By following these practices, developers can significantly reduce the risk of broken object level authorization vulnerabilities in their APIs.

---
<!-- nav -->
[[API Security/05-OWASP API TOP 10/01-API1 Broken Object Level Authorization/10-Conclusion|Conclusion]] | [[API Security/05-OWASP API TOP 10/01-API1 Broken Object Level Authorization/00-Overview|Overview]]
