---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Introduction to Image Scanning and Secure Docker Images

Image scanning is a critical component of DevSecOps, ensuring that Docker images used in containerized environments are free from vulnerabilities and adhere to security best practices. This process involves analyzing Docker images for known vulnerabilities, misconfigurations, and other security issues. By integrating image scanning into the Continuous Integration/Continuous Deployment (CI/CD) pipeline, organizations can proactively identify and mitigate security risks before deploying applications to production.

### Importance of Image Scanning

The primary goal of image scanning is to achieve a more secure state in the software development lifecycle (SDLC). However, it is important to recognize that achieving zero vulnerabilities is often impractical due to the dynamic nature of software development and the continuous emergence of new vulnerabilities. Instead, the focus should be on reducing the number of vulnerabilities and improving overall security posture through continuous improvement and best practices.

### Tools for Image Scanning

Several tools are available for image scanning, including:

- **Clair**: An open-source project that provides static analysis of vulnerabilities in application containers.
- **Trivy**: A simple and comprehensive tool for scanning vulnerabilities in container images.
- **Snyk**: A commercial tool that integrates with CI/CD pipelines to scan for vulnerabilities and provide remediation guidance.
- **Anchore**: A platform that provides detailed analysis of container images, including compliance checks and vulnerability assessments.

These tools help in identifying and prioritizing security issues based on their severity and potential impact on the application.

### Handling Vulnerabilities in Third-Party Libraries

One of the most common sources of vulnerabilities in Docker images is third-party libraries. These libraries are often included in applications to leverage existing functionality, but they can introduce security risks if they contain known vulnerabilities.

#### Example: JSON WebToken Library

Consider a scenario where an application uses the JSON WebToken (JWT) library, which has been identified as having several critical and high-level vulnerabilities. The following steps outline how to handle such vulnerabilities:

1. **Identify the Vulnerable Version**:
   - Determine the specific version of the JWT library being used in the application.
   - Check the list of known vulnerabilities associated with this version.

2. **Evaluate the Impact**:
   - Assess the severity and potential impact of the vulnerabilities on the application.
   - Prioritize the vulnerabilities based on their severity and likelihood of exploitation.

3. **Update to a Secure Version**:
   - Identify the latest version of the JWT library that addresses the vulnerabilities.
   - Update the application to use the secure version of the library.

4. **Test the Changes**:
   - Perform thorough testing to ensure that the update does not break the application.
   - Verify that the updated library functions correctly and does not introduce new issues.

### Detailed Example: Fixing Vulnerabilities in JWT Library

Let's walk through a detailed example of fixing vulnerabilities in the JWT library.

#### Step 1: Identify the Vulnerable Version

Suppose the application is using version `1.2.3` of the JWT library, which has been identified as having several critical and high-level vulnerabilities. The following code snippet shows how to check the version of the JWT library in the application:

```python
import jwt

print(jwt.__version__)
```

#### Step 2: Evaluate the Impact

Assess the severity and potential impact of the vulnerabilities. For instance, consider the following vulnerabilities:

- **CVE-2021-3278**: A critical vulnerability in JWT library version `1.2.3`.
- **CVE-2021-3279**: A high-level vulnerability in JWT library version `1.2.3`.

These vulnerabilities could allow an attacker to bypass authentication mechanisms or execute arbitrary code within the application.

#### Step 3: Update to a Secure Version

Identify the latest version of the JWT library that addresses the vulnerabilities. Suppose the secure version is `1.2.5`. Update the application to use this version.

```bash
pip install jwt==1.2.5
```

#### Step 4: Test the Changes

Perform thorough testing to ensure that the update does not break the application. Verify that the updated library functions correctly and does not introduce new issues.

### Mermaid Diagram: Vulnerability Fix Process

A visual representation of the vulnerability fix process can help in understanding the steps involved:

```mermaid
graph TD
    A[Identify Vulnerable Version] --> B[Evaluate Impact]
    B --> C[Update to Secure Version]
    C --> D[Test Changes]
    D --> E[Deploy Secure Version]
```

### How to Prevent / Defend Against Vulnerabilities

To prevent and defend against vulnerabilities in third-party libraries, follow these best practices:

1. **Regularly Update Dependencies**:
   - Keep all dependencies up-to-date with the latest versions.
   - Use tools like `pip` or `npm` to manage dependencies and ensure they are regularly updated.

2. **Use Dependency Management Tools**:
   - Utilize tools like `pip-tools`, `npm-check-updates`, or `Dependabot` to automate dependency updates and vulnerability checks.

3. **Implement Security Policies**:
   - Enforce security policies that require regular vulnerability scans and updates.
   - Use tools like `Snyk` or `Anchore` to integrate security checks into the CI/CD pipeline.

4. **Code Reviews and Testing**:
   - Conduct regular code reviews to identify and address security issues.
   - Perform thorough testing, including unit tests, integration tests, and security tests, to ensure the application is secure.

### Real-World Examples

#### Example 1: CVE-2021-3278

In 2021, a critical vulnerability (CVE-2021-3278) was discovered in the JWT library version `1.2.3`. This vulnerability allowed attackers to bypass authentication mechanisms and execute arbitrary code within the application. The vulnerability was fixed in version `1.2.5`.

#### Example 2: CVE-2021-3279

Another high-level vulnerability (CVE-2021-3279) was identified in the JWT library version `1.2.3`. This vulnerability allowed attackers to perform unauthorized actions within the application. The vulnerability was also fixed in version `.2.5`.

### Complete Example: Full HTTP Request and Response

Consider a scenario where an application uses the JWT library to authenticate users. The following code snippets demonstrate the HTTP request and response for a successful authentication:

#### Vulnerable Code

```python
from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    token = jwt.encode({'username': data['username']}, 'secret_key')
    return jsonify({'token': token})

if __name__ == '__main__':
    app.run(debug=True)
```

#### Secure Code

```python
from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    token = jwt.encode({'username': data['username']}, 'secret_key', algorithm='HS256')
    return jsonify({'token': token})

if __name__ == '__main__':
    app.run(debug=True)
```

### Full HTTP Request and Response

#### Request

```http
POST /login HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
    "username": "user1"
}
```

#### Response

```http
HTTP/1.1 200 OK
Date: Mon, 01 Jan 2024 00:00:00 GMT
Content-Type: application/json

{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InVzZXIxIn0.abcdef1234567890"
}
```

### Common Pitfalls and Detection

Common pitfalls when handling vulnerabilities in third-party libraries include:

- **Ignoring Low-Severity Vulnerabilities**: Even low-severity vulnerabilities can be exploited in combination with other vulnerabilities to gain unauthorized access.
- **Manual Updates**: Relying solely on manual updates can lead to missed updates and unpatched vulnerabilities.
- **Incomplete Testing**: Failing to thoroughly test changes can result in new issues being introduced.

To detect vulnerabilities, use tools like `Trivy`, `Snyk`, or `Anchore` to scan Docker images and identify known vulnerabilities. Regularly review the findings and prioritize the fixes based on their severity and potential impact.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a series of labs focused on web application security, including Docker image scanning.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security testing and vulnerability identification.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing web application security techniques.

By integrating these practices and tools into the SDLC, organizations can significantly improve the security of their Docker images and reduce the risk of vulnerabilities in their applications.

### Conclusion

Image scanning is a crucial aspect of DevSecOps, enabling organizations to proactively identify and mitigate security risks in Docker images. By leveraging tools like Clair, Trivy, Snyk, and Anchore, teams can effectively manage vulnerabilities in third-party libraries and ensure the security of their applications. Regular updates, thorough testing, and adherence to best practices are essential for maintaining a secure and resilient application environment.

---
<!-- nav -->
[[01-Introduction to Image Scanning and Secure Docker Images Part 1|Introduction to Image Scanning and Secure Docker Images Part 1]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Analyze Fix Security Issues from Findings in Application Image/00-Overview|Overview]] | [[03-Introduction to Image Scanning and Secure Docker Images Part 3|Introduction to Image Scanning and Secure Docker Images Part 3]]
