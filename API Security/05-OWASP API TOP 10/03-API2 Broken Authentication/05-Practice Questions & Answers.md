---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what is meant by "broken authentication" in the context of API security.**

Broken authentication refers to vulnerabilities in the authentication mechanisms used by APIs that allow attackers to bypass or manipulate authentication processes. This can result in unauthorized access to user accounts and sensitive data. For example, if an API does not properly validate tokens or allows weak passwords, an attacker could exploit these weaknesses to assume the identity of a legitimate user.

**Q2. How can an attacker exploit JWT vulnerabilities to assume the identity of another user?**

An attacker can exploit JWT vulnerabilities by manipulating the token structure. JWT tokens consist of three parts: header, payload, and signature. If the token uses the `none` algorithm, the attacker can modify the payload to include a different user ID and still present a valid-looking token. For instance, changing the `sub` (subject) field in the payload to a different user ID can allow the attacker to impersonate that user. Here’s an example payload:

```json
{
  "sub": "attacker_id",
  "exp": 9999999999
}
```

By changing the `sub` field from the original user ID to the attacker's desired ID, the attacker can bypass authentication checks.

**Q3. What are some common vulnerabilities associated with broken authentication in APIs?**

Common vulnerabilities associated with broken authentication in APIs include:
- Lack of brute force protection, allowing attackers to attempt multiple login attempts.
- Weak password policies, enabling the use of easily guessable passwords.
- Exposing sensitive data such as tokens or passwords in URLs.
- Failing to validate tokens properly.
- Accepting unsigned or weakly signed JWT tokens.
- Absence of token expiration dates.
- Using weak encryption keys or storing passwords in plain text.

**Q4. How can an API be configured to mitigate risks related to broken authentication?**

To mitigate risks related to broken authentication, an API should implement the following measures:
- Enforce strong password policies and multi-factor authentication.
- Implement rate limiting and account lockout mechanisms to prevent brute force attacks.
- Ensure proper validation and verification of authentication tokens.
- Use secure algorithms for token generation and avoid using the `none` algorithm.
- Set appropriate expiration times for tokens.
- Avoid exposing sensitive data in URLs.
- Store passwords securely using strong hashing algorithms.
- Regularly audit and test authentication mechanisms for vulnerabilities.

**Q5. Provide a recent real-world example of a breach caused by broken authentication and explain how it occurred.**

One notable example is the Capital One data breach in 2019. In this incident, an attacker exploited a misconfigured web application firewall (WAF) to access sensitive customer data. The WAF was improperly configured, allowing unauthorized access to the server logs. The attacker then used this access to enumerate and steal over 100 million customer records. This breach highlights the importance of securing authentication mechanisms and ensuring proper configuration of security controls to prevent unauthorized access.

**Q6. How can an attacker exploit weak encryption keys in an API to compromise authentication?**

Weak encryption keys can be exploited by an attacker to decrypt sensitive information such as authentication tokens or passwords. For example, if an API uses a weak encryption key for encrypting JWT tokens, an attacker could use brute force methods to guess the key and decrypt the token. Once decrypted, the attacker can modify the token payload and re-encrypt it with the same weak key to impersonate a legitimate user. To prevent this, APIs should use strong encryption keys and regularly rotate them to minimize the risk of exposure.

---
<!-- nav -->
[[04-Broken Authentication in APIs|Broken Authentication in APIs]] | [[API Security/05-OWASP API TOP 10/03-API2 Broken Authentication/00-Overview|Overview]]
