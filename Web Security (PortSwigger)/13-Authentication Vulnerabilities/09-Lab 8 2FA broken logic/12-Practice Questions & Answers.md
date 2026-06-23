---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why the 2FA implementation in the lab is considered broken logic.**

The 2FA implementation in the lab is considered broken logic because it relies on client-side parameters to determine authentication decisions. Specifically, the `Verify` cookie, which contains the username, is used to send the 2FA token to the specified user. This allows an attacker to manipulate the `Verify` cookie to send the 2FA token to any user, including the victim Carlos. Additionally, the session management is flawed since removing the session token still allows access to the page, indicating that the session management is not properly enforcing authentication.

**Q2. How would you exploit the 2FA broken logic vulnerability to access Carlos' account?**

To exploit the 2FA broken logic vulnerability, follow these steps:

1. **Manipulate the `Verify` Cookie**: Change the `Verify` cookie to contain Carlos' username. This will cause the 2FA token to be sent to Carlos' email.
   
2. **Brute Force the MFA Code**: Use Burp Intruder to brute force the 4-digit MFA code. Set up the Intruder with the correct payload options (integers, length 4) and send the requests to the `/login_to` endpoint.

3. **Identify Successful Payload**: Monitor the responses for a 302 redirect to the `/my_account` page, which indicates a successful login attempt.

4. **Access Carlos' Account**: Once the correct MFA code is identified, use it to log in as Carlos. Replace the session token with the one received during the brute force attack.

Here is a sample setup for Burp Intruder:

```plaintext
Target: POST /login_to
Payloads: Integers, Length 4 (min=0000, max=9999)
```

**Q3. Why is it important to send the initial GET request to the `/login_to` endpoint with the `Verify` cookie set to Carlos' username before starting the brute force attack?**

It is crucial to send the initial GET request to the `/login_to` endpoint with the `Verify` cookie set to Carlos' username before starting the brute force attack because this ensures that Carlos receives the 4-digit security code. Without this step, Carlos would not receive the code, and even if the brute force attack correctly guesses the MFA code, it would not work because Carlos has not been sent the code.

**Q4. What are the main vulnerabilities identified in the lab's 2FA implementation?**

The main vulnerabilities identified in the lab's 2FA implementation are:

1. **Client-Side Parameter Dependency**: The system relies on the `Verify` cookie, which is a client-side parameter, to determine which user receives the 2FA token. This allows attackers to manipulate the cookie to send the token to any user.

2. **Broken Session Management**: The application does not enforce proper session management. Removing the session token still allows access to the page, indicating that the session management is flawed.

3. **No Brute Force Protection**: There is no mechanism to prevent brute force attacks on the MFA code, allowing attackers to systematically guess the code until they succeed.

4. **Username and Password Not Required**: The system does not require a valid username and password to log in; only the correct MFA code tied to the username is needed. This makes it possible to log in without knowing the password.

**Q5. How would you fix the vulnerabilities in the 2FA implementation described in the lab?**

To fix the vulnerabilities in the 2FA implementation, consider the following measures:

1. **Server-Side Validation**: Ensure that all authentication decisions are made based on server-side validation rather than client-side parameters. For example, the `Verify` cookie should not be used to determine the recipient of the 2FA token.

2. **Proper Session Management**: Implement robust session management to ensure that sessions are properly validated and enforced. This includes checking session tokens and ensuring that unauthorized access is prevented.

3. **Brute Force Protection**: Implement mechanisms to prevent brute force attacks, such as rate limiting, CAPTCHAs, or temporary account lockouts after multiple failed attempts.

4. **Require Username and Password**: Ensure that both the username and password are required for authentication, and that the MFA code is only used as an additional layer of security.

By addressing these issues, the 2FA implementation can be significantly strengthened against exploitation.

---
<!-- nav -->
[[Web Security (PortSwigger)/13-Authentication Vulnerabilities/09-Lab 8 2FA broken logic/11-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/09-Lab 8 2FA broken logic/00-Overview|Overview]]
