---
course: API Security
topic: Course Introduction
tags: [api-security]
---

## Practice Questions & Answers

**Q1. What are the prerequisites for this API Security course?**

The API Security course does not require any specific prerequisites. The course starts from scratch and covers all necessary concepts. However, having some familiarity with constructing API requests and understanding tools like Swagger or Postman could be beneficial.

**Q2. Why is Hunter 2.0 recommended alongside this course?**

Hunter 2.0 is recommended because it provides additional resources and detailed information on finding and exploiting vulnerabilities. While this course focuses on identifying vulnerabilities and basic API penetration testing techniques, Hunter 2.0 offers more in-depth knowledge on how to escalate these findings.

**Q3. How important is it to understand how to construct API requests for this course?**

Understanding how to construct API requests is crucial for this course. You should be able to create requests based on documentation such as Swagger, Postman, or JSON files. This skill is fundamental for performing API security testing effectively. For example, if you encounter an API endpoint `https://targetapi.com`, you should be able to craft a request body that interacts with this endpoint correctly.

**Q4. Can you provide an example of how to construct an API request using Swagger documentation?**

Certainly! Let's assume you have a Swagger documentation for an API endpoint `https://exampleapi.com/users`. Here’s how you might construct a GET request to retrieve user data:

```json
{
  "method": "GET",
  "url": "https://exampleapi.com/users",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_ACCESS_TOKEN"
  }
}
```

In this example, the `Content-Type` header specifies the format of the request, and the `Authorization` header includes an access token required for authentication.

**Q5. What are some recent real-world examples of API security breaches and what can we learn from them?**

One notable example is the Capital One breach in 2019 (CVE-2019-11171). In this case, an attacker exploited a misconfigured serverless function that exposed sensitive customer data. This highlights the importance of proper configuration and validation of API endpoints. Another example is the Zoom API leak in 2020, which exposed user data due to insufficient API security measures. These incidents underscore the need for robust API security practices, including input validation, proper authentication mechanisms, and regular security audits.

---
<!-- nav -->
[[02-Course Prerequisites|Course Prerequisites]] | [[API Security/01-Course Introduction/02-Course Prerequists/00-Overview|Overview]]
