---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Introduction to Image Scanning and Secure Docker Images

In the realm of DevSecOps, ensuring the security of Docker images is paramount. One critical aspect of this process is image scanning, which involves analyzing Docker images for vulnerabilities, misconfigurations, and other security issues. This chapter delves into the process of analyzing and fixing security issues found in an application image, specifically focusing on upgrading outdated packages and dependencies.

### Background Theory

Docker images are built from Dockerfiles, which contain instructions to create a container environment. These images often include various packages and dependencies required by the application. Over time, these packages may become outdated, introducing security vulnerabilities. Image scanning tools help identify such vulnerabilities by comparing the versions of packages in the image against known vulnerabilities in databases like the National Vulnerability Database (NVD).

### Real-World Examples

Recent real-world examples highlight the importance of keeping packages up-to-date:

- **CVE-2021-21315**: A vulnerability in the `jsonwebtoken` package allowed attackers to bypass authentication mechanisms. This CVE affected versions prior to 8.5.1.
- **CVE-2021-23222**: Another vulnerability in the `jsonwebtoken` package allowed attackers to perform signature forgery attacks. This CVE affected versions prior to 8.5.1.

These examples underscore the necessity of regularly updating packages and dependencies to mitigate such risks.

### Example Scenario

Consider an application that uses the `jsonwebtoken` package. The current version in the `package.json` file is `0.4.0`, which is known to be vulnerable. To address this issue, we need to update the package to a secure version.

#### Step-by-Step Process

1. **Identify Vulnerable Packages**:
    - Use a tool like `RetireJS` to scan the application for known vulnerabilities.
    - `RetireJS` will identify the `jsonwebtoken` package as vulnerable due to its outdated version.

2. **Update Direct Dependencies**:
    - Open the `package.json` file and locate the `jsonwebtoken` entry.
    - Update the version number to a secure version, e.g., `8.5.1`.

3. **Handle Sub-Dependencies**:
    - Some vulnerabilities might exist in sub-dependencies, which are not directly listed in `package.json`.
    - Use `npm ls` to identify where the `jsonwebtoken` package is being used across all dependencies.

### Detailed Steps

#### Step 1: Identify Vulnerable Packages

First, we need to identify the vulnerable packages in our application. We can use `RetireJS` for this purpose.

```bash
npm install -g retire
retire --path ./node_modules
```

This command scans the `node_modules` directory and identifies any known vulnerabilities.

#### Step 2: Update Direct Dependencies

Next, we update the direct dependencies in the `package.json` file.

1. **Open `package.json`**:
    - Locate the `jsonwebtoken` entry.
    - Update the version number to a secure version.

```json
{
  "name": "my-app",
  "version": "1.0.0",
  "dependencies": {
    "jsonwebtoken": "^8.5.1"
  }
}
```

2. **Install Updated Dependencies**:
    - Run `npm install` to update the `node_modules` directory.

```bash
npm install
```

#### Step 3: Handle Sub-Dependencies

Some vulnerabilities might exist in sub-dependencies. We need to identify and update these as well.

1. **List All Dependencies**:
    - Use `npm ls` to list all dependencies and their versions.

```bash
npm ls jsonwebtoken
```

This command will show the version of `jsonwebtoken` used by all dependencies.

### Mermaid Diagrams

To visualize the dependency tree, we can use a mermaid diagram.

```mermaid
graph TD
  A[my-app] --> B(jsonwebtoken@0.4.0)
  C[dependency1] --> D(jsonwebtoken@0.4.0)
  E[dependency2] --> F(jsonwebtoken@0.4.0)
```

### How to Prevent / Defend

#### Detection

Regularly scan your Docker images for vulnerabilities using tools like `Trivy`, `Clair`, or `Snyk`.

```bash
trivy image my-docker-image:latest
```

#### Prevention

1. **Keep Dependencies Up-to-Date**:
    - Regularly check for updates to your dependencies.
    - Use tools like `npm-check-updates` to automate this process.

```bash
npm install -g npm-check-updates
ncu -u
npm install
```

2. **Use Dependency Management Tools**:
    - Tools like `Renovate` or `Dependabot` can automatically open pull requests to update dependencies.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of the `package.json` file.

**Vulnerable Version**:

```json
{
  "name": "my-app",
  "version": "1.0.0",
  "dependencies": {
    "jsonwebtoken": "^0.4.0"
  }
}
```

**Secure Version**:

```json
{
  "name": "my-app",
  "version": "1.0.0",
  "dependencies": {
    "jsonwebtoken": "^8.5.1"
  }
}
```

### Complete Example

#### Full HTTP Request and Response

When updating dependencies, the full HTTP request and response can be useful to understand the process.

**HTTP Request**:

```http
POST /api/npm/install HTTP/1.1
Host: localhost:3000
Content-Type: application/json

{
  "dependencies": {
    "jsonwebtoken": "^8.5.1"
  }
}
```

**HTTP Response**:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "message": "Dependencies updated successfully",
  "updated": [
    "jsonwebtoken@8.5.1"
  ]
}
```

### Common Pitfalls

1. **Ignoring Sub-Dependencies**:
    - Not all vulnerabilities are in direct dependencies. Ensure you check sub-dependencies as well.

2. **Manual Updates**:
    - Manual updates can be error-prone. Use automation tools to manage dependencies.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing web applications.
- **OWASP Juice Shop**: A deliberately insecure web app for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.

### Conclusion

Ensuring the security of Docker images is crucial in DevSecOps. By regularly scanning images for vulnerabilities and updating dependencies, you can significantly reduce the risk of security breaches. Tools like `RetireJS`, `Trivy`, and `npm-check-updates` can help automate this process, making it easier to maintain secure applications.

---
<!-- nav -->
[[02-Introduction to Image Scanning and Secure Docker Images Part 2|Introduction to Image Scanning and Secure Docker Images Part 2]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Analyze Fix Security Issues from Findings in Application Image/00-Overview|Overview]] | [[04-Introduction to Image Scanning and Secure Docker Images Part 4|Introduction to Image Scanning and Secure Docker Images Part 4]]
