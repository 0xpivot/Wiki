---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Understanding Algorithm Confusion

Algorithm confusion occurs when the server does not enforce a strict validation of the signing algorithm used in the JWT. This allows an attacker to craft a token using a different algorithm, potentially bypassing the intended security measures.

### Example Scenario

Consider a scenario where the server expects a token signed with the `RS256` algorithm but fails to validate this requirement strictly. An attacker could craft a token signed with the `HS256` algorithm instead, which is much easier to forge.

#### Real-World Example: CVE-2019-16759

CVE-2019-16759 is a real-world example of an algorithm confusion vulnerability. In this case, a web application failed to properly validate the signing algorithm, allowing attackers to bypass authentication by using a weaker algorithm.

### Steps to Exploit Algorithm Confusion

1. **Obtain the Public Key**: The server exposes its public key via a standard endpoint. You need to retrieve this key to understand the expected signing algorithm.
2. **Craft a Modified Token**: Using the obtained public key, craft a token with a different signing algorithm that the server might accept.
3. **Submit the Token**: Send the crafted token to the server to gain unauthorized access.

---
<!-- nav -->
[[Web Security (PortSwigger)/19-JWT Attacks/07-Lab 7 JWT authentication bypass via algorithm confusion/11-Practice Labs|Practice Labs]] | [[Web Security (PortSwigger)/19-JWT Attacks/07-Lab 7 JWT authentication bypass via algorithm confusion/00-Overview|Overview]] | [[13-Understanding JWT Algorithms|Understanding JWT Algorithms]]
