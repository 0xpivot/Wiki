---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Conclusion

Selecting lightweight base images and excluding unnecessary content are essential best practices for building secure Docker images. By using Alpine Linux as the base image and leveraging `.dockerignore` files and multi-stage builds, you can significantly reduce the size and potential attack surface of your Docker images. Regularly scanning and reviewing your Dockerfiles and `.dockerignore` files can help ensure that your images remain secure and efficient.

### Practice Labs

For hands-on experience with Docker security best practices, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, including Docker security.
- **OWASP Juice Shop**: A deliberately insecure web application that can be used to practice various security techniques, including Docker security.
- **Kubernetes Goat**: A Kubernetes-based security training platform that includes exercises related to Docker security.

These labs provide practical experience in applying the concepts discussed in this chapter.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Docker Security Best Practices/08-Using Official and Verified Docker Images|Using Official and Verified Docker Images]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Docker Security Best Practices/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Docker Security Best Practices/10-Practice Questions & Answers|Practice Questions & Answers]]
