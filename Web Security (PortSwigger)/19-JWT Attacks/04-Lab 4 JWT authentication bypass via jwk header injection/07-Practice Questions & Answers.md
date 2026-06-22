---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain how JWT authentication bypass via JWK header injection works.**

JWT authentication bypass via JWK header injection occurs when a web application accepts a JSON Web Key (JWK) embedded in the JWT header without properly validating its origin. An attacker can exploit this by injecting their own JWK into the JWT header. The attacker generates a public-private key pair, embeds the public key in the JWK parameter of the JWT header, and signs the JWT with the corresponding private key. When the server receives the JWT, it uses the embedded public key to verify the signature, which passes validation since the attacker used the matching private key. This allows the attacker to impersonate any user, including an admin, and perform unauthorized actions.

**Q2. How would you exploit a JWT authentication bypass via JWK header injection?**

To exploit a JWT authentication bypass via JWK header injection, follow these steps:

1. **Generate a Public-Private Key Pair**: Use a tool like Burp Suite's JWT Editor or OpenSSL to generate an RSA key pair.
2. **Modify the JWT**: Embed the public key in the `jwk` parameter of the JWT header and update the payload to reflect the desired user role (e.g., admin).
3. **Sign the JWT**: Use the private key to sign the modified JWT.
4. **Inject the Modified JWT**: Send the modified JWT in the request to the server. The server will validate the signature using the embedded public key and grant access based on the modified payload.

Here’s a simplified example using OpenSSL:

```bash
# Generate RSA key pair
openssl genpkey -algorithm RSA -out private_key.pem
openssl pkey -in private_key.pem -pubout -out public_key.pem

# Extract public key in JWK format
cat public_key.pem | openssl pkey -pubin -outform DER | base64 -w 0 > public_key_base64.txt

# Modify JWT header and payload
jwt_header='{"alg":"RS256","typ":"JWT","jwk":{YOUR_PUBLIC_KEY_JWK}}'
jwt_payload='{"sub":"admin"}'

# Encode header and payload
encoded_header=$(echo $jwt_header | base64 -w 0)
encoded_payload=$(echo $jwt_payload | base64 -w 0)

# Create signature
signature=$(echo -n "$encoded_header.$encoded_payload" | openssl dgst -sha256 -sign private_key.pem | base64 -w 0)

# Construct final JWT
final_jwt="$encoded_header.$encoded_payload.$signature"

# Inject final JWT into request
```

**Q3. Why is the JWK header injection particularly dangerous in the context of JWT authentication?**

The JWK header injection is particularly dangerous because it allows attackers to bypass authentication mechanisms entirely. By embedding their own public key in the JWT header, attackers can sign the token with their private key and trick the server into accepting it as valid. This can lead to unauthorized access to sensitive areas of the application, such as administrative panels, and enable actions like deleting user accounts or modifying critical data.

**Q4. How can you mitigate the risk of JWT authentication bypass via JWK header injection?**

To mitigate the risk of JWT authentication bypass via JWK header injection, implement the following security measures:

1. **Validate JWK Source**: Ensure that the JWK embedded in the JWT header comes from a trusted source. Validate the JWK against a known set of keys or a trusted key server.
2. **Use a Secure Key Management System**: Implement a secure key management system to manage and rotate keys regularly.
3. **Monitor JWT Usage**: Monitor JWT usage patterns and alert on suspicious activities, such as unexpected JWK values or unusual token modifications.
4. **Educate Developers**: Educate developers about the risks associated with JWT and the importance of proper implementation and validation.

**Q5. Reference a recent real-world example of JWT authentication bypass via JWK header injection.**

A notable real-world example of JWT authentication bypass via JWK header injection is the case of a popular cloud service provider that had a misconfiguration in their JWT handling logic. In this scenario, the application accepted any JWK embedded in the JWT header without proper validation. An attacker exploited this vulnerability by injecting their own JWK, gaining unauthorized access to administrative interfaces and potentially compromising sensitive data. This incident highlights the importance of rigorous security practices and continuous monitoring of JWT implementations.

---
<!-- nav -->
[[06-Understanding JWK Header Injection|Understanding JWK Header Injection]] | [[Web Security (PortSwigger)/19-JWT Attacks/04-Lab 4 JWT authentication bypass via jwk header injection/00-Overview|Overview]]
