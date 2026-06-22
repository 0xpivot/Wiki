---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what is meant by "excessive data exposure" in the context of APIs.**

Excessive data exposure refers to a situation where an API returns more data than necessary or required by the client. This often happens when the API relies on the client to filter out unnecessary data. If an attacker can directly access the API, they can retrieve all the data, leading to potential security risks such as exposure of sensitive information.

**Q2. How does excessive data exposure typically occur in API interactions?**

Excessive data exposure occurs when the API returns full data objects as they are stored in the backend database, rather than filtering the data based on the user's requirements. The client applications then filter the response and display only the necessary data to the user. However, if an attacker can bypass the client application and directly interact with the API, they can retrieve the full unfiltered data, leading to excessive data exposure.

**Q3. Provide an example of how excessive data exposure can lead to security vulnerabilities.**

In the Uber account takeover example, an attacker exploited an endpoint that returned a driver's UUID in the response. By using this UUID, the attacker could make further requests to the API and obtain sensitive information such as mobile application authentication tokens. This demonstrates how excessive data exposure can lead to serious security vulnerabilities, allowing attackers to gain unauthorized access to sensitive data.

**Q4. How can one check if an API is vulnerable to excessive data exposure?**

To check if an API is vulnerable to excessive data exposure, follow these steps:

1. **Check API Responses:** Verify if the API returns sensitive data by design or full data objects stored in the database.
2. **Compare Client-Side Filtering:** Compare the data presented to the user after client-side filtering with the raw API response. If the responses differ, it indicates a potential vulnerability.
3. **Direct API Access:** Directly access the API and observe the response. If the response contains more data than what is shown to the user, it suggests excessive data exposure.

**Q5. What are some recent real-world examples of excessive data exposure through APIs?**

One notable example is the Capital One data breach in 2019 (CVE-2019-11176). An attacker exploited a misconfigured server that exposed sensitive customer data through an API. The API returned more data than necessary, leading to the exposure of personal information of over 100 million customers. This incident highlights the importance of properly configuring and securing APIs to prevent excessive data exposure.

**Q6. How can developers mitigate the risk of excessive data exposure in APIs?**

Developers can mitigate the risk of excessive data exposure in APIs by following these best practices:

1. **Implement Server-Side Filtering:** Ensure that the API filters data based on the user's requirements before sending the response.
2. **Use Role-Based Access Control (RBAC):** Limit the amount of data returned based on the user's role and permissions.
3. **Regular Audits and Testing:** Conduct regular security audits and penetration testing to identify and fix vulnerabilities related to excessive data exposure.
4. **Use Security Tools:** Utilize automated security tools to detect and alert on potential excessive data exposure issues.

By implementing these measures, developers can significantly reduce the risk of excessive data exposure and protect sensitive information.

---
<!-- nav -->
[[API Security/05-OWASP API TOP 10/04-API3 Excessive Data Exposure/02-Excessive Data Exposure in APIs|Excessive Data Exposure in APIs]] | [[API Security/05-OWASP API TOP 10/04-API3 Excessive Data Exposure/00-Overview|Overview]]
