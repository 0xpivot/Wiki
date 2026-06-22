---
course: Web Security
topic: JWT Attacks
tags: [web-security]
---

## Lab Setup and Objective

In this lab, we will simulate a scenario where a web application uses JWTs for session management. The application has a vulnerability in the `kid` header, allowing an attacker to perform a path traversal attack.

### Lab Environment

The lab environment is set up on the PortSwigger Web Security Academy. To access the lab, follow these steps:

1. Visit the URL: https://portswigger.net/web-security
2. Click on the sign-up button to create an account.
3. Log in to your account.
4. Navigate to the Academy section.
5. Select all content and then all labs.
6. Search for the JWT topic and go to lab number six titled "JWT authentication bypass via KID header path traversal."

### Lab Objective

The objective of this lab is to bypass the JWT authentication mechanism by exploiting the `kid` header vulnerability. Specifically, you need to:

1. Craft a JWT with a manipulated `kid` value.
2. Use the crafted JWT to gain access to the admin panel.
3. Delete the user named "Carlos."

### Credentials Provided

You are provided with the following credentials for a regular user account:

- Username: `your_username`
- Password: `your_password`

---
<!-- nav -->
[[09-JWT Authentication Bypass via `kid` Header Path Traversal|JWT Authentication Bypass via `kid` Header Path Traversal]] | [[Web Security (PortSwigger)/19-JWT Attacks/06-Lab 6 JWT authentication bypass via kid header path traversal/00-Overview|Overview]] | [[11-Path Traversal Attack via `kid` Header|Path Traversal Attack via `kid` Header]]
