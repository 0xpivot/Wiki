---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Understanding Root User Privileges and Risks

In the context of deploying applications, particularly in a DevOps environment, understanding the risks associated with using the root user is crucial. The root user, also known as the superuser, has unrestricted access to all files, directories, and commands on a Unix-based system. This level of privilege is necessary for certain administrative tasks but poses significant security risks when used for application deployments.

### Why Root User Is Dangerous

When an application runs as the root user, it inherits all the privileges of the root account. If an attacker gains control of the application through a vulnerability such as a buffer overflow or SQL injection, they can leverage these elevated privileges to perform malicious actions. These actions could include:

- Modifying system files and configurations.
- Installing additional malware.
- Accessing sensitive data stored on the system.
- Escalating attacks to other systems within the network.

### Real-World Example: CVE-2021-44228 (Log4Shell)

One of the most notable recent vulnerabilities is CVE-2021-44228, commonly known as Log4Shell. This vulnerability affected the Apache Log4j library, which is widely used in Java applications. An attacker could exploit this vulnerability to execute arbitrary code on the target system. If the application running Log4j was deployed as the root user, the attacker would gain full control of the system, leading to severe consequences.

### How to Prevent / Defend Against Root User Risks

To mitigate the risks associated with running applications as the root user, it is essential to follow best practices for securing deployments. Here are some key steps:

#### Create Non-Root Users for Applications

Creating dedicated users for each application ensures that the application runs with the minimum necessary privileges. This approach limits the potential damage an attacker can cause if they compromise the application.

```bash
# Creating a non-root user for a Node.js application
sudo useradd --no-create-home --shell /usr/sbin/nologin nodeapp
```

#### Secure Configuration Files

Ensure that configuration files and sensitive data are owned by the non-root user and have appropriate permissions set.

```bash
# Setting ownership and permissions for a Node.js application
sudo chown -R nodeapp:nodeapp /path/to/nodeapp
sudo chmod -R 755 /path/to/nodeapp
```

#### Use Application-Specific Permissions

Grant the non-root user only the permissions required to run the application. Avoid granting unnecessary privileges that could be exploited.

```bash
# Granting specific permissions to the non-root user
sudo setcap cap_net_bind_service=+ep /path/to/nodeapp
```

### Full Example: Securing a Node.js Deployment

Let's walk through a complete example of securing a Node.js deployment using a non-root user.

#### Step 1: Create a Non-Root User

First, create a non-root user specifically for the Node.js application.

```bash
# Creating a non-root user for the Node.js application
sudo useradd --no-create-home --shell /usr/sbin/nologin nodeapp
```

#### Step 2: Set Up the Application Directory

Set up the directory structure for the Node.js application and ensure it is owned by the non-root user.

```bash
# Creating the application directory and setting ownership
mkdir -p /opt/nodeapp
sudo chown -R nodeapp:nodeapp /opt/nodeapp
```

#### Step 3: Configure the Application

Place the Node.js application files in the `/opt/nodeapp` directory and ensure they are owned by the non-root user.

```bash
# Copying the application files and setting ownership
cp -r /path/to/nodejs/app/* /opt/nodeapp/
sudo chown -R nodeapp:nodeapp /opt/nodeapp
```

#### Step 4: Run the Application as the Non-Root User

Use a process manager like `pm2` to run the Node.js application as the non-root user.

```bash
# Running the Node.js application with pm2
sudo -u nodeapp pm2 start /opt/nodeapp/app.js
```

#### Full HTTP Request and Response Example

Here is an example of a full HTTP request and response when accessing the Node.js application.

```http
GET /api/data HTTP/1.1
Host: example.com
User-Agent: curl/7.64.1
Accept: */*

HTTP/1.1 200 OK
Date: Mon, 01 Jan 2024 00:00:00 GMT
Server: nginx/1.18.0
Content-Type: application/json
Content-Length: 24
Connection: keep-alive

{"data": "Hello, World!"}
```

### Mermaid Diagram: Application Deployment Architecture

A visual representation of the deployment architecture can help understand how the components interact.

```mermaid
graph TD
    A[Web Server] --> B[Node.js Application]
    B --> C[Database]
    D[Non-Root User] --> B
    E[Root User] --> A
    F[Process Manager (pm2)] --> B
```

### Common Pitfalls and Detection

#### Pitfall: Inadequate Permission Settings

Failing to set appropriate permissions for the application directory and files can lead to security vulnerabilities.

#### Detection: Monitoring for Elevated Privilege Usage

Monitor system logs and audit trails to detect any unauthorized usage of elevated privileges.

### Secure Coding Practices

Always validate and sanitize inputs to prevent common vulnerabilities such as SQL injection and cross-site scripting (XSS).

```javascript
// Vulnerable code
const query = `SELECT * FROM users WHERE username = '${username}'`;

// Secure code
const query = `SELECT * FROM users WHERE username = ?`;
db.query(query, [username]);
```

### Conclusion

Deploying applications as non-root users is a fundamental security practice that significantly reduces the risk of system compromise. By following the steps outlined above and adhering to secure coding practices, you can ensure that your Node.js applications are deployed securely and are resilient against potential attacks.

### Practice Labs

For hands-on experience with securing Node.js deployments, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice securing web applications.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing and penetration testing.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning web security.

By engaging with these labs, you can reinforce your understanding and practical skills in securing Node.js deployments.

---
<!-- nav -->
[[02-Securing Node.js Deployments with Non-Root Users|Securing Node.js Deployments with Non-Root Users]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/18-Securing Node.js Deployments with Non-Root Users/00-Overview|Overview]] | [[04-Understanding User Management in Node.js Deployments|Understanding User Management in Node.js Deployments]]
