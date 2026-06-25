---
course: DevSecOps
topic: Differentiating the Pros and Cons of Automated Security Testing
tags: [devsecops]
---

## Hands-On Labs for Practice

### Recommended Labs

To gain practical experience with automated security testing, consider the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including automated security testing.
- **OWASP Juice Shop**: A deliberately insecure web application that can be used to practice security testing and penetration testing.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable, allowing users to practice security testing.

### Example Lab: OWASP Juice Shop

The OWASP Juice Shop is a popular hands-on lab for practicing web security. Here’s how to set it up and use it for automated security testing:

1. **Install Docker**: Ensure Docker is installed on your machine.
2. **Run OWASP Juice Shop**:
    ```bash
    docker run -p 3000:3000 bkimminich/juice-shop
    ```
3. **Access OWASP Juice Shop**: Open a web browser and navigate to `http://localhost:3000`.
4. **Perform Automated Security Testing**: Use tools like OWASP ZAP to perform automated security testing on the OWASP Juice Shop.

By following these steps, you can gain practical experience with automated security testing and improve your skills in identifying and addressing security vulnerabilities.

### Conclusion

Automated security testing offers significant advantages, including scalability, repeatability, build blocking, immediate feedback, and the ability to adapt to changing security threats. By understanding these concepts and implementing them effectively, organizations can significantly enhance their security posture and protect their systems from emerging threats.

---
<!-- nav -->
[[15-Differentiating the Pros and Cons of Automated Security Testing|Differentiating the Pros and Cons of Automated Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/05-Differentiating the Pros and Cons of Automated Security Testing/The Pros and Cons of Automated Security Testing/00-Overview|Overview]] | [[17-Immediate Feedback for Developers|Immediate Feedback for Developers]]
