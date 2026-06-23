---
course: Web Security
topic: Cross-Site Request Forgery (CSRF)
tags: [web-security]
---

## Conclusion

In this lab, we explored a scenario where the web application attempted to block CSRF attacks but only applied defenses to certain types of requests. By crafting a malicious request that exploited the incomplete token validation mechanism, we were able to change the email address of the user. To prevent such attacks, it is crucial to implement robust defenses, such as using anti-CSRF tokens, validating request methods, and configuring web applications securely.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs to practice web security techniques, including CSRF.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains numerous security vulnerabilities.

By mastering the concepts and techniques covered in this chapter, you will be well-equipped to defend against CSRF attacks and protect web applications from similar vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/13-Understanding the Vulnerability|Understanding the Vulnerability]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/00-Overview|Overview]] | [[Web Security (PortSwigger)/04-Cross-Site Request Forgery (CSRF)/03-Lab 2 CSRF where token validation depends on request method/15-Practice Questions & Answers|Practice Questions & Answers]]
