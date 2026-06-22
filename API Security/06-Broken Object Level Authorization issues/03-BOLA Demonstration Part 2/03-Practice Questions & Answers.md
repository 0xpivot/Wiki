---
course: API Security
topic: Broken Object Level Authorization issues
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain how the lack of proper identification in API endpoints can lead to BOLA vulnerabilities.**

The lack of proper identification in API endpoints can lead to BOLA (Broken Object Level Authorization) vulnerabilities when an attacker can manipulate object identifiers to access or modify resources they should not have permission to access. For instance, if an endpoint allows reading or updating an order by specifying an order ID without verifying that the user has the appropriate permissions, an attacker could potentially specify another user's order ID and gain unauthorized access to sensitive data or make unauthorized changes. This is particularly dangerous in APIs that handle financial transactions or personal information.

**Q2. How would you exploit a BOLA vulnerability in an API that allows updating order details by specifying an order ID?**

To exploit a BOLA vulnerability in an API that allows updating order details by specifying an order ID, an attacker would follow these steps:

1. Identify the endpoint responsible for updating order details, typically something like `PUT /orders/{orderId}`.
2. Determine if the API properly checks whether the user making the request has the right to modify the specified order ID.
3. Craft a request to update an order detail using a different user’s order ID. For example, using `curl`:
   ```bash
   curl -X PUT https://api.example.com/orders/12345 \
        -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
        -d '{"notes": "This order was modified by an attacker"}'
   ```
4. If the API does not properly validate the user's permissions, the attacker's request will succeed, allowing them to modify another user's order details.

**Q3. Describe a recent real-world example of a BOLA vulnerability and explain how it was exploited.**

A notable example of a BOLA vulnerability is the breach at Capital One in 2019 (CVE-2019-11165). The attacker exploited a misconfigured web application firewall (WAF) rule that allowed unauthorized access to customer data. Specifically, the WAF rule did not properly restrict access to certain API endpoints, enabling the attacker to access sensitive customer information by manipulating object identifiers.

In this case, the attacker was able to access more than 100 million records of customer data by exploiting the misconfiguration. The lack of proper validation and authorization controls on the API endpoints led to the exposure of sensitive data, highlighting the importance of robust security practices in API design and implementation.

**Q4. How would you configure an API endpoint to prevent BOLA vulnerabilities when handling user-specific data such as account settings?**

To prevent BOLA vulnerabilities when handling user-specific data such as account settings, the following configuration steps should be taken:

1. **Implement Proper Authentication**: Ensure that every request to the API includes a valid authentication token that identifies the user making the request.
2. **Validate User Permissions**: Before processing any request, verify that the authenticated user has the necessary permissions to access or modify the specific resource being requested.
3. **Use Unique Identifiers**: Utilize unique identifiers that are tied to the authenticated user, ensuring that only the intended user can access their own data.
4. **Audit Logs**: Implement logging mechanisms to track who accessed or modified which resources, providing a trail for auditing purposes.

For example, consider an API endpoint for updating account settings:

```python
@app.route('/account/settings/<username>', methods=['PUT'])
@auth_required
def update_account_settings(username):
    # Verify that the authenticated user matches the username in the URL
    if current_user.username != username:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Proceed with updating the account settings
    # ...
```

By enforcing these measures, the API ensures that only authorized users can access and modify their own data, thereby preventing BOLA vulnerabilities.

**Q5. Explain how you would test for BOLA vulnerabilities in an API that handles user-specific data such as order details or product IDs.**

To test for BOLA vulnerabilities in an API that handles user-specific data such as order details or product IDs, follow these steps:

1. **Identify Endpoints**: List all API endpoints that allow operations on user-specific data, such as `GET /orders/{orderID}`, `PUT /products/{productID}`, etc.
2. **Authenticate as Different Users**: Obtain access tokens for multiple users to simulate different user contexts.
3. **Manipulate Object Identifiers**: For each endpoint, attempt to access or modify data using object identifiers associated with other users. For example, if authenticated as User A, try accessing User B's order details.
4. **Check Responses**: Analyze the responses to determine if the API properly restricts access based on user permissions. Unauthorized access indicates a potential BOLA vulnerability.
5. **Automate Testing**: Use tools like Burp Suite, OWASP ZAP, or custom scripts to automate the testing process, systematically checking each endpoint for vulnerabilities.

By thoroughly testing each endpoint with different user contexts, you can identify and mitigate BOLA vulnerabilities, ensuring that the API securely handles user-specific data.

---
<!-- nav -->
[[02-Broken Object Level Authorization (BOLA)|Broken Object Level Authorization (BOLA)]] | [[API Security/06-Broken Object Level Authorization issues/03-BOLA Demonstration Part 2/00-Overview|Overview]]
