---
course: API Security
topic: Broken Object Level Authorization issues
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain how BOLA user enumeration works through object IDs.**

BOLA (Brute-force Over Low Authentication) user enumeration through object IDs involves systematically querying an API with different object IDs to determine which IDs correspond to valid users or resources. By iterating through a range of possible IDs and analyzing the responses, an attacker can identify active user accounts or other resources. For example, if an API endpoint `/users/{id}` returns detailed user information when a valid ID is provided and an error message when an invalid ID is used, an attacker can enumerate all valid user IDs by testing a sequence of numbers until they receive an error response.

**Q2. How can you exploit BOLA user enumeration to gather sensitive information about users?**

To exploit BOLA user enumeration, an attacker would first identify an API endpoint that accepts object IDs and returns specific information about those objects. The attacker would then systematically query the endpoint with a range of IDs, analyzing the responses to determine which IDs correspond to valid entries. Once valid IDs are identified, the attacker can extract sensitive information such as usernames, roles, or other details associated with those IDs. For instance, if the API endpoint `/users/{id}` returns a user’s name, role, and email address, an attacker could compile a list of all users and their roles by enumerating through the valid IDs.

**Q3. What are some practical steps to mitigate BOLA user enumeration vulnerabilities in an API?**

To mitigate BOLA user enumeration vulnerabilities, consider the following steps:

1. **Consistent Error Responses**: Ensure that the API returns consistent error messages for both valid and invalid requests. This prevents attackers from distinguishing between valid and invalid IDs based on the response content.
   
2. **Rate Limiting**: Implement rate limiting on API endpoints to prevent rapid enumeration attempts. This can slow down or stop automated attacks.

3. **Authentication Requirements**: Require authentication for accessing sensitive endpoints. This ensures that only authenticated users can access user information, reducing the risk of unauthorized enumeration.

4. **Logging and Monitoring**: Monitor API logs for unusual patterns of requests that might indicate enumeration attempts. Set up alerts to notify administrators of suspicious activity.

5. **Input Validation**: Validate input parameters to ensure they conform to expected formats and ranges. This can help prevent enumeration by rejecting invalid inputs.

**Q4. How would you configure an API to return consistent error messages for both valid and invalid user IDs?**

To configure an API to return consistent error messages for both valid and invalid user IDs, you can implement the following approach:

```python
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Check if the user exists
    user = User.query.get(user_id)
    
    if user:
        # Return user data
        return jsonify({
            'id': user.id,
            'name': user.name,
            'role': user.role
        })
    else:
        # Return a consistent error message
        return jsonify({'error': 'User not found'}), 404
```

In this example, the API checks if the user exists. If the user does not exist, it returns a consistent error message without revealing whether the ID was valid or not. This makes it harder for an attacker to distinguish between valid and invalid IDs.

**Q5. Can you provide a recent real-world example of a BOLA user enumeration vulnerability and explain how it was exploited?**

A recent real-world example of a BOLA user enumeration vulnerability is the case of the Capital One breach in 2019 (CVE-2019-11510). In this incident, an attacker exploited a misconfigured server that allowed unauthorized access to sensitive data. The attacker was able to enumerate through a range of IDs to access customer records, leading to the exposure of over 100 million customers' personal information.

The vulnerability was exploited by sending requests to the server with different IDs and analyzing the responses to determine which IDs corresponded to valid records. Once valid IDs were identified, the attacker could access and download sensitive customer data. This highlights the importance of securing APIs against enumeration attacks and implementing proper access controls and monitoring mechanisms.

---
<!-- nav -->
[[02-Understanding Broken Object-Level Authorization (BOLA)|Understanding Broken Object-Level Authorization (BOLA)]] | [[API Security/06-Broken Object Level Authorization issues/05-BOLA User Enumeration Through Object IDs Part 2/00-Overview|Overview]]
