---
course: API Security
topic: Information Disclosure
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain how information disclosure vulnerabilities can occur through API endpoints.**

Information disclosure vulnerabilities can occur through API endpoints when sensitive data is inadvertently exposed due to improper handling of errors, unsecured access controls, or insufficient validation of input parameters. For instance, if an API endpoint returns detailed error messages containing internal database schema information or user data when an invalid request is made, an attacker could use this information to craft further attacks. Additionally, if the API does not properly validate input parameters, an attacker might be able to trigger specific error conditions that leak sensitive information.

**Q2. How would you exploit an API endpoint that reveals sensitive information through error messages?**

To exploit an API endpoint that reveals sensitive information through error messages, follow these steps:

1. **Identify the Endpoint**: Determine which API endpoint is leaking information. This can often be found by observing error responses when sending malformed requests.

2. **Craft Malformed Requests**: Send requests with intentionally incorrect parameters to trigger error messages. For example, if the endpoint expects a `roleID` parameter, send a request with an invalid `roleID` value.

3. **Analyze Error Responses**: Carefully examine the error messages returned by the server. These might include database schema details, such as column names (`ID`, `roleID`, `updated`, `createdAt`), or even partial data.

4. **Refine Attacks**: Use the information gathered to refine your attacks. For instance, if you discover that the `name` field does not have a default value, you can exploit this by crafting requests that trigger specific error conditions related to this field.

5. **Exploit Further**: With detailed knowledge of the backend structure, you can attempt to perform actions like unauthorized deletions, insertions, or modifications. For example, if you know the exact structure of the `users` table, you might be able to delete or modify records.

**Q3. Why is it important to handle errors gracefully in API endpoints?**

Handling errors gracefully in API endpoints is crucial for several reasons:

1. **Security**: Graceful error handling prevents sensitive information from being disclosed to unauthorized users. Detailed error messages can expose internal system structures, such as database schemas, which can be exploited by attackers.

2. **User Experience**: Providing clear, user-friendly error messages improves the overall user experience. Users should receive meaningful feedback that helps them understand what went wrong and how they can correct it.

3. **Maintainability**: Consistent error handling practices make it easier to maintain and debug applications. By standardizing how errors are reported, developers can quickly identify and resolve issues.

4. **Compliance**: Many regulatory frameworks require that sensitive information be protected. Improper error handling can lead to non-compliance and potential legal consequences.

**Q4. How would you configure an API to prevent information disclosure through error messages?**

To configure an API to prevent information disclosure through error messages, implement the following measures:

1. **Custom Error Handling**: Implement custom error handlers that return generic error messages instead of detailed technical information. For example, instead of returning a full stack trace, return a message like "An unexpected error occurred."

2. **Error Logging**: Log detailed error information internally, but do not expose it to the client. This allows you to diagnose issues without compromising security.

3. **Input Validation**: Ensure that all input parameters are validated before processing. Invalid inputs should result in consistent, non-descriptive error messages.

4. **Access Controls**: Enforce strict access controls to ensure that only authorized users can access sensitive endpoints. Use authentication and authorization mechanisms to restrict access.

5. **Rate Limiting**: Implement rate limiting to prevent attackers from making excessive requests that could lead to information disclosure.

Here is an example of a custom error handler in Python using Flask:

```python
from flask import jsonify

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request'}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource Not Found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500
```

**Q5. Reference recent real-world examples where information disclosure vulnerabilities led to breaches.**

One notable recent example of an information disclosure vulnerability leading to a breach is the case of the Capital One data breach in 2019. The breach involved an attacker exploiting a misconfigured web application firewall (WAF) that exposed sensitive customer data. The WAF was configured to allow access to certain log files, which contained personally identifiable information (PII) of approximately 100 million customers.

The attacker was able to access these log files by exploiting a misconfiguration that allowed unauthorized access to the WAF's logging mechanism. This information disclosure vulnerability allowed the attacker to download large amounts of sensitive data, including names, addresses, credit scores, and social security numbers.

This incident highlights the importance of proper configuration management and the need to carefully control access to sensitive data. It also underscores the risks associated with exposing internal system details through improperly configured APIs and web services.

---
<!-- nav -->
[[03-Information Disclosure via Error Messages|Information Disclosure via Error Messages]] | [[API Security/16-Information Disclosure/02-Information Disclosure Demonstration Part 2/00-Overview|Overview]]
