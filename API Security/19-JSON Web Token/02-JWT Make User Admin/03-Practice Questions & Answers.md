---
course: API Security
topic: JSON Web Token
tags: [api-security]
---

## Practice Questions & Answers

**Q1. What is JWT and how does it work in the context of API security?**

JWT stands for JSON Web Token, which is a compact, URL-safe means of representing claims to be transferred between two parties. In the context of API security, JWTs are used to securely transmit information between parties as a JSON object. This information can be verified and trusted because it is digitally signed using a secret key. The structure of a JWT consists of three parts: header, payload, and signature. The header typically contains the type of token and the signing algorithm. The payload contains the claims, which are statements about an entity (typically the user) and additional data. The signature is created by hashing the base64-encoded header and payload with a secret key.

**Q2. How can an attacker modify a JWT to gain admin privileges?**

An attacker can attempt to modify a JWT to gain admin privileges by altering the payload of the token. For example, if the original payload contains a claim such as `{"user": "regular"}`, the attacker might change it to `{"user": "admin"}`. However, this modification alone is insufficient; the attacker must also ensure that the modified token is properly signed with the secret key used by the server to validate the token. Without the correct signature, the server will reject the token as invalid.

To achieve this, the attacker needs to either know the secret key or use a brute-force approach to guess it. Tools like `jwtcat` can be used to perform brute-force attacks against the secret key. Once the secret key is obtained, the attacker can sign the modified payload with this key and present the new token to the server, potentially gaining unauthorized access.

**Q3. Explain how the `jwtcat` tool can be used to brute-force the secret key of a JWT.**

The `jwtcat` tool is designed to help in cracking JWT tokens by brute-forcing the secret key. Here’s how it can be used:

1. **Install the Tool**: Ensure `jwtcat` is installed. You can install it via pip or another package manager depending on your environment.

2. **Prepare the Token**: Obtain the JWT token that you want to crack. Copy the token string.

3. **Run the Brute-Force Attack**: Use `jwtcat` to perform a brute-force attack on the token. The command typically looks like this:
   ```bash
   python3 jwtcat.py -w wordlist.txt <token>
   ```
   Here, `wordlist.txt` is a file containing potential secret keys (e.g., common passwords), and `<token>` is the JWT token you want to crack.

4. **Interpret the Results**: If `jwtcat` finds the correct secret key, it will output the key. With the secret key, you can then modify the payload of the JWT and sign it correctly to create a valid token with elevated privileges.

For example, if the token is `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZGVmYXVsdCJ9.abc123`, you would run:
```bash
python3 jwtcat.py -w 10k_common_passwords.txt eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZGVmYXVsdCJ9.abc123
```

If the secret key is found, you can use it to sign a modified payload.

**Q4. What recent real-world examples or CVEs highlight the risks associated with insecure JWT implementations?**

One notable example is the case of the popular authentication library `auth0`. In 2017, a vulnerability was discovered where the library did not properly validate the issuer (`iss`) claim in JWTs. This allowed attackers to craft malicious tokens that could impersonate any user, leading to unauthorized access. This vulnerability was assigned the CVE identifier CVE-2017-14856.

Another example is the case of the `firebase-admin` SDK, where a misconfiguration allowed attackers to bypass authentication checks. This occurred due to improper validation of JWTs, allowing attackers to forge tokens and gain unauthorized access to Firebase services. This vulnerability was widely publicized and led to updates in the SDK to enforce stricter validation rules.

These examples underscore the importance of proper implementation and validation of JWTs to prevent unauthorized access and maintain the security of APIs.

**Q5. How can developers mitigate the risk of JWT-based attacks in their applications?**

Developers can mitigate the risk of JWT-based attacks by implementing several best practices:

1. **Use Strong Secret Keys**: Ensure that the secret key used to sign JWTs is strong and kept secure. Avoid using common or easily guessable keys.

2. **Validate All Claims**: Always validate all claims within the JWT, including the issuer (`iss`), subject (`sub`), audience (`aud`), and expiration (`exp`). This helps prevent attacks where an attacker modifies these claims.

3. **Use HTTPS**: Ensure that JWTs are transmitted over HTTPS to prevent interception and tampering.

4. **Implement Short Expiration Times**: Set short expiration times for JWTs to minimize the window of opportunity for an attacker to use a stolen token.

5. **Monitor and Audit**: Regularly monitor and audit JWT usage patterns to detect any unusual activity that may indicate an attack.

6. **Use Secure Storage**: Store JWTs securely on the client side, such as in HTTP-only cookies or in a secure storage mechanism like `localStorage`.

By following these guidelines, developers can significantly reduce the risk of JWT-based attacks and enhance the security of their applications.

---
<!-- nav -->
[[02-Making a User Admin via JWT Manipulation|Making a User Admin via JWT Manipulation]] | [[API Security/19-JSON Web Token/02-JWT Make User Admin/00-Overview|Overview]]
