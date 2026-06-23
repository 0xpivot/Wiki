---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain why a weak signing key in JWT can be exploited and how it differs from an asymmetric algorithm like RS-256.**

The JSON Web Token (JWT) uses a signing key to ensure the integrity and authenticity of the token. When the signing key is weak, it can be brute-forced using tools like Hashcat, which can guess the key from a list of common passwords. This is particularly true for symmetric algorithms like HS-256, where the same key is used for both signing and verification. 

In contrast, asymmetric algorithms like RS-256 use a public-private key pair. The private key is used to sign the token, while the public key is used to verify it. Brute-forcing the private key in an asymmetric algorithm is computationally infeasible due to the large key size and the complexity of the cryptographic operations involved. Therefore, asymmetric algorithms are generally more secure against brute-force attacks compared to symmetric ones.

**Q2. How would you exploit a JWT with a weak signing key? Provide a step-by-step process.**

To exploit a JWT with a weak signing key, follow these steps:

1. **Identify the JWT**: Capture the JWT from the network traffic or cookies.
2. **Extract the Algorithm**: Determine the algorithm used (e.g., HS-256).
3. **Brute Force the Secret Key**: Use a tool like Hashcat to brute-force the secret key using a word list of common passwords.
4. **Modify the Payload**: Change the payload to grant elevated privileges (e.g., set the `sub` claim to "admin").
5. **Sign the Modified Token**: Use the discovered secret key to sign the modified token.
6. **Inject the Modified Token**: Replace the original token with the modified one in the network traffic or cookies.
7. **Access Restricted Resources**: Use the modified token to access restricted resources or perform unauthorized actions.

**Q3. Why is it important to use strong secret keys for JWTs? Provide recent real-world examples.**

Using strong secret keys for JWTs is crucial to prevent brute-force attacks that can lead to unauthorized access and data breaches. A weak secret key can be easily guessed or brute-forced, allowing attackers to forge valid tokens and impersonate legitimate users.

Recent real-world examples include:

- **CVE-2021-20199**: A vulnerability in the Auth0 platform allowed attackers to bypass authentication by exploiting a weak secret key used for JWT signatures. This led to unauthorized access to user accounts and sensitive data.
- **GitHub OAuth Token Exposure**: In 2019, GitHub exposed OAuth tokens due to a misconfiguration in their JWT implementation. Although not directly related to a weak secret key, it highlights the importance of proper security practices in JWT usage.

**Q4. How does the use of an asymmetric algorithm like RS-256 enhance security compared to a symmetric algorithm like HS-256?**

An asymmetric algorithm like RS-256 enhances security in several ways compared to a symmetric algorithm like HS-256:

1. **Key Management**: In RS-256, the private key is kept secret and used only for signing, while the public key is shared for verification. This ensures that even if the public key is compromised, the private key remains secure.
2. **Resistance to Brute-Force Attacks**: Asymmetric algorithms use much larger key sizes (typically 2048 bits or more), making brute-force attacks computationally infeasible. Symmetric algorithms, especially with weak keys, can be brute-forced relatively easily.
3. **Non-repudiation**: With RS-256, the signature can be verified without revealing the private key, providing a level of non-repudiation that is not possible with symmetric algorithms.

**Q5. What are the steps to verify if a JWT signature is being properly validated by the server?**

To verify if a JWT signature is being properly validated by the server, follow these steps:

1. **Capture the JWT**: Intercept the JWT from network traffic or cookies.
2. **Modify the Signature**: Change a few characters in the signature part of the JWT.
3. **Send the Modified JWT**: Send the modified JWT back to the server and observe the response.
4. **Check Server Response**: If the server still accepts the JWT despite the modified signature, it indicates that the signature is not being properly validated.

This test helps ensure that the server is correctly verifying the integrity of the JWT, preventing unauthorized modifications.

---
<!-- nav -->
[[09-Symmetric vs Asymmetric Algorithms|Symmetric vs Asymmetric Algorithms]] | [[Web Security (PortSwigger)/19-JWT Attacks/03-Lab 3 JWT authentication bypass via weak signing key/00-Overview|Overview]]
