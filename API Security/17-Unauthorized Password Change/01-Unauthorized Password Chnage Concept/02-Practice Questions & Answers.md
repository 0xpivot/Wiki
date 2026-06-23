---
course: API Security
topic: Unauthorized Password Change
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of unauthorized password change in the context of API security.**

Unauthorized password change occurs when an attacker can modify the password of another user due to a flaw in the application logic. Typically, this happens when the backend code incorrectly uses the username from the request body rather than the authenticated user information from the JWT token. This mistake allows an attacker to specify any username in their request and change that user's password without proper authorization.

**Q2. How can developers prevent unauthorized password changes in their applications?**

To prevent unauthorized password changes, developers should ensure that the username used for password updates comes from the authenticated user information in the JWT token, not from the request body. Additionally, the token should be validated to confirm its authenticity and integrity. Here’s a sample Python code snippet demonstrating secure password change logic:

```python
from flask import request
import jwt

def update_password():
    # Extract username from JWT token
    token = request.headers.get('Authorization').split()[1]
    decoded_token = jwt.decode(token, 'your_secret_key', algorithms=['HS256'])
    username = decoded_token['username']

    # Get new password from request body
    new_password = request.json['password']

    # Update password in database for the authenticated user
    # Example: db.update_password(username, new_password)
```

**Q3. What are the potential consequences of an unauthorized password change vulnerability?**

An unauthorized password change vulnerability can lead to significant security breaches. Attackers can gain access to user accounts, potentially leading to unauthorized transactions, data theft, or further exploitation of the system. For example, in the case of a recent breach at a financial institution, attackers exploited a similar vulnerability to change user passwords and perform fraudulent transactions. This highlights the importance of securing password change functionalities.

**Q4. How can an attacker exploit an unauthorized password change vulnerability?**

An attacker can exploit this vulnerability by crafting a malicious request that includes the target user's username and a new password. The attacker needs to send this request to the endpoint responsible for changing passwords. If the backend logic incorrectly uses the username from the request body instead of the authenticated user information, the attacker can successfully change the target user's password. Here’s an example payload:

```json
{
  "username": "target_user",
  "password": "new_password"
}
```

**Q5. Why is it important to validate the JWT token before using the username for password changes?**

Validating the JWT token ensures that the user is properly authenticated and authorized to perform actions such as changing passwords. If the token is not validated, an attacker might use a forged token or manipulate the request to impersonate another user. By validating the token, developers can ensure that only legitimate users can change their own passwords, thereby preventing unauthorized access and modifications.

---
<!-- nav -->
[[01-Unauthorized Password Change Vulnerability|Unauthorized Password Change Vulnerability]] | [[API Security/17-Unauthorized Password Change/01-Unauthorized Password Chnage Concept/00-Overview|Overview]]
