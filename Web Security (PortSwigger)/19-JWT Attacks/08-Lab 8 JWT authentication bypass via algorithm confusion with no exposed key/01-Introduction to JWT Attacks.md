---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Introduction to JWT Attacks

Welcome to the Web Security Academy series, where we delve deep into various security vulnerabilities and attacks. Today, we will focus on a specific type of attack involving JSON Web Tokens (JWTs): the JWT authentication bypass via algorithm confusion with no exposed key. This attack exploits a flaw in the way JWTs are implemented, leading to unauthorized access to sensitive resources.

### Background on JWTs

JSON Web Tokens (JWTs) are a compact, URL-safe means of representing claims to be transferred between two parties. They are commonly used in web applications for authentication and information exchange. A JWT consists of three parts separated by dots (`.`):

1. **Header**: Contains metadata about the token, such as the type of token and the signing algorithm used.
2. **Payload**: Contains the claims, which are statements about an entity (typically the user) and additional data.
3. **Signature**: Ensures the integrity of the token, preventing tampering and verifying the authenticity of the sender.

The structure of a JWT looks like this:

```
<base64UrlEncode(header)>.<base64UrlEncode(payload)>.<signature>
```

### Lab Setup

To follow along with this lab, you need an account on the Web Security Academy. You can create one by visiting [PortSwigger.net/Web Security](https://portswigger.net/web-security) and clicking on the sign-up button. Once you have an account and are logged in, navigate to the Academy section, select all content, and then all labs. Search for the "JOT module" and find lab number eight titled "JOT authentication bypass via algorithm confusion with no exposed key."

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/00-Overview|Overview]] | [[Web Security (PortSwigger)/19-JWT Attacks/08-Lab 8 JWT authentication bypass via algorithm confusion with no exposed key/02-Introduction to JWT and Algorithm Confusion Attacks|Introduction to JWT and Algorithm Confusion Attacks]]
