---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of a broken access control vulnerability and how it can lead to data leakage.**

Broken access control vulnerabilities occur when a web application fails to enforce proper restrictions on what actions authenticated users are allowed to perform. This can result in unauthorized access to resources or information that should be restricted to specific users. In the context of the lab, the vulnerability arises because the application allows a user to specify another user's ID in the request parameters, leading to the potential exposure of sensitive data such as API keys. When the application attempts to load the specified user's account details but instead redirects due to authentication issues, the sensitive data may still be present in the redirect response, thus leaking the data.

**Q2. How would you exploit a broken access control vulnerability where the user ID is controlled by a request parameter? Provide a step-by-step explanation.**

To exploit a broken access control vulnerability where the user ID is controlled by a request parameter, follow these steps:

1. Identify the parameter that controls the user ID in the request.
2. Attempt to modify this parameter to specify a different user’s ID.
3. Monitor the response to see if the application loads the specified user’s data before redirecting.
4. Use a tool like Burp Suite to intercept the redirect response and check if it contains any sensitive data, such as an API key.
5. Extract the sensitive data from the redirect response.

For example, if the URL is `https://example.com/user?id=123`, change `id` to `id=Carlos` and observe the response.

**Q3. Why is it important to disable TLS certificate verification in the Python script used to exploit the vulnerability?**

Disabling TLS certificate verification is important in the Python script used to exploit the vulnerability because it allows the script to bypass SSL/TLS certificate validation. This is often necessary when working with internal or test environments where self-signed certificates are used, or when debugging purposes require ignoring certificate errors. By disabling TLS verification, the script can make HTTPS requests without encountering certificate-related errors, ensuring smooth operation during exploitation.

**Q4. How would you configure Burp Suite to convert 302 redirects to 200 OK responses to exploit the vulnerability described in the lab?**

To configure Burp Suite to convert 302 redirects to 200 OK responses, follow these steps:

1. Open Burp Suite and navigate to the Proxy tab.
2. Ensure that the Intercept feature is turned on to capture HTTP requests.
3. Send a request that triggers a 302 redirect.
4. In the Intercept pane, right-click the intercepted request and select "Send to Repeater."
5. Go to the Repeater tab.
6. In the Repeater tab, you can manually change the status code of the response from 302 to 200.
7. Click "Forward" to send the modified response back to the client.

This configuration allows you to view the content of the redirect response directly, revealing any sensitive data that might be present.

**Q5. What recent real-world examples or CVEs demonstrate the risks associated with broken access control vulnerabilities?**

One notable example is the CVE-2021-21972, which affected the Atlassian Confluence Server and Data Center products. This vulnerability allowed an attacker to read the contents of arbitrary files on the server, including sensitive configuration files and user data, due to improper access control checks. Another example is CVE-2020-14182, which impacted the Jenkins CI/CD platform, allowing unauthorized users to access sensitive information and perform administrative actions due to insufficient access control mechanisms.

These examples highlight the critical importance of implementing robust access control measures to prevent unauthorized access and data leakage.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/10-Lab 9 User ID controlled by request parameter with data leakage in redirect/08-Understanding Access Control Vulnerabilities|Understanding Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/10-Lab 9 User ID controlled by request parameter with data leakage in redirect/00-Overview|Overview]] | [[10-Summary|Summary]]
