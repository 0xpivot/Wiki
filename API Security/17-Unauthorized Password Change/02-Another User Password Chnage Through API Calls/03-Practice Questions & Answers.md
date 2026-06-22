---
course: API Security
topic: Unauthorized Password Change
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain why changing another user's password through an API call without proper authorization is considered a security vulnerability.**

The ability to change another user's password through an API call without proper authorization is a significant security vulnerability because it allows an attacker to gain unauthorized access to another user's account. This can lead to unauthorized actions being performed under the guise of the legitimate user, potentially compromising sensitive data or causing other forms of harm. For instance, if an attacker changes the password of a high-level administrator, they could take control of the system and perform malicious activities. This type of vulnerability was seen in several recent breaches where attackers exploited weak authentication mechanisms to escalate their privileges within a system.

**Q2. How can you ensure that an API endpoint for changing a user's password is properly secured against unauthorized access?**

To ensure that an API endpoint for changing a user's password is properly secured against unauthorized access, the following steps should be taken:

1. **Use Strong Authentication Mechanisms:** Ensure that the API requires a strong form of authentication such as JSON Web Tokens (JWT) with appropriate claims that identify the user making the request. The token should be validated on the server side to confirm the identity of the user.

2. **Validate Token Claims:** When a user attempts to change their password, the API should verify that the JWT contains the necessary claims to authorize the action. Specifically, the user ID in the token should match the user attempting to change the password.

3. **Restrict Access Based on Roles:** Implement role-based access control (RBAC) to restrict who can perform sensitive actions like changing passwords. Only users with specific roles should be allowed to execute such actions.

4. **Monitor and Log Access Attempts:** Keep detailed logs of all access attempts to the password change endpoint. Monitor these logs for any suspicious activity that might indicate an attempted breach.

Here is an example of how you might implement these steps in a Node.js application:

```javascript
const jwt = require('jsonwebtoken');
const secretKey = 'your_secret_key';

function changePassword(req, res) {
    const { userId, newPassword } = req.body;
    const token = req.headers['authorization'];
    
    // Validate the token
    try {
        const decoded = jwt.verify(token, secretKey);
        
        // Check if the user ID in the token matches the user ID in the request
        if (decoded.userId !== userId) {
            return res.status(403).json({ message: 'Unauthorized' });
        }
        
        // Proceed with changing the password
        // ...
        return res.status(200).json({ message: 'Password changed successfully' });
    } catch (err) {
        return res.status(401).json({ message: 'Invalid token' });
    }
}
```

**Q3. What is the difference between using a JWT token to validate user identity and relying solely on the request body for user information?**

Using a JWT token to validate user identity is more secure than relying solely on the request body for user information because:

1. **Token Validation:** A JWT token is signed by the server and contains claims that can be verified. This ensures that the token has not been tampered with and that the user identity is valid. If the token is invalid or tampered with, the server can reject the request.

2. **Prevent Tampering:** When user information is included in the request body, it can be easily tampered with by an attacker. An attacker could modify the request body to impersonate another user. However, if the user information is embedded in a JWT token, any attempt to modify the token will invalidate it due to the signature verification process.

3. **Centralized Authorization:** Using JWT tokens allows for centralized management of user permissions and roles. The server can check the token to determine if the user is authorized to perform certain actions, reducing the risk of unauthorized access.

For example, consider the recent CVE-2021-21972, which affected several web applications. Attackers were able to exploit a vulnerability where user information was not properly validated, leading to unauthorized access. By using JWT tokens, the applications could have ensured that the user identity was correctly validated before allowing sensitive actions.

**Q4. How would you exploit a vulnerable API endpoint that allows changing another user’s password without proper validation?**

To exploit a vulnerable API endpoint that allows changing another user’s password without proper validation, follow these steps:

1. **Identify the Vulnerable Endpoint:** Determine the API endpoint responsible for changing user passwords. This can often be found in the documentation or by analyzing network traffic.

2. **Craft the Exploit Request:** Construct a request to the endpoint that includes the target user’s ID and the new password. Since the endpoint does not properly validate the user identity, you can specify any user ID.

3. **Send the Request:** Send the crafted request to the API endpoint. If the endpoint is indeed vulnerable, the password for the specified user will be changed.

Here is an example of how you might craft such an exploit request using `curl`:

```bash
curl -X POST https://api.example.com/change-password \
-H "Authorization: Bearer <your_jwt_token>" \
-d '{"userId": "target_user_id", "newPassword": "hacked_password"}'
```

In this example, `<your_jwt_token>` is your own valid JWT token, and `target_user_id` is the ID of the user whose password you wish to change. If the API endpoint is vulnerable, the password for `target_user_id` will be changed to `hacked_password`.

**Q5. How would you configure an API to prevent unauthorized password changes by ensuring the user identity is validated through a JWT token?**

To configure an API to prevent unauthorized password changes by ensuring the user identity is validated through a JWT token, follow these steps:

1. **Generate JWT Tokens:** When a user logs in, generate a JWT token that includes the user’s ID and any other necessary claims. Sign the token with a secret key known only to the server.

2. **Protect the Endpoint:** Ensure that the API endpoint for changing passwords requires a valid JWT token. Use middleware to validate the token before processing the request.

3. **Verify User Identity:** In the middleware, extract the user ID from the JWT token and compare it with the user ID in the request body. If they do not match, reject the request.

4. **Log and Monitor:** Maintain detailed logs of all requests to the password change endpoint. Monitor these logs for any suspicious activity.

Here is an example of how you might implement this in a Node.js application using Express:

```javascript
const express = require('express');
const jwt = require('jsonwebtoken');
const app = express();
const secretKey = 'your_secret_key';

app.use(express.json());

// Middleware to validate JWT token
function authenticateToken(req, res, next) {
    const token = req.headers['authorization'];
    if (!token) return res.status(401).json({ message: 'No token provided' });

    jwt.verify(token, secretKey, (err, decoded) => {
        if (err) return res.status(403).json({ message: 'Invalid token' });
        req.user = decoded;
        next();
    });
}

// Change password endpoint
app.post('/change-password', authenticateToken, (req, res) => {
    const { userId, newPassword } = req.body;

    // Verify user identity
    if (req.user.userId !== userId) {
        return res.status(403).json({ message: 'Unauthorized' });
    }

    // Proceed with changing the password
    // ...

    return res.status(200).json({ message: 'Password changed successfully' });
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

By implementing these steps, you can ensure that only authenticated users can change their passwords, preventing unauthorized access and maintaining the security of your API.

---
<!-- nav -->
[[02-Understanding Unauthorized Password Change Through API Calls|Understanding Unauthorized Password Change Through API Calls]] | [[API Security/17-Unauthorized Password Change/02-Another User Password Chnage Through API Calls/00-Overview|Overview]]
