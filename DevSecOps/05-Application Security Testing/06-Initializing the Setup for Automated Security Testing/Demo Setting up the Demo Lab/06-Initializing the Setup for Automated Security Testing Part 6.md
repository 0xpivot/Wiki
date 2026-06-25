---
course: DevSecOps
topic: Initializing the Setup for Automated Security Testing
tags: [devsecops]
---

## Initializing the Setup for Automated Security Testing

### Introduction to Jenkins and GitLab Integration

Jenkins is an open-source automation server that provides continuous integration and continuous delivery (CI/CD) services. It is widely used in DevSecOps environments to automate the building, testing, and deployment of applications. GitLab, on the other hand, is a web-based Git repository manager that provides a wide range of features for project management, issue tracking, code review, and more. Integrating Jenkins with GitLab allows for seamless automation of the entire software development lifecycle.

### Installing the GitLab Branch Source Plugin

To integrate Jenkins with GitLab, we first need to install the GitLab Branch Source Plugin. This plugin enables Jenkins to interact with GitLab repositories and branches, allowing for automated builds and deployments based on changes in the repository.

#### Step-by-Step Installation

1. **Access Jenkins Plugin Management**:
    - Navigate to `Manage Jenkins` in the Jenkins dashboard.
    - Click on `Manage Plugins`.

2. **Search for GitLab Branch Source Plugin**:
    - In the `Available` tab, use the search field to enter "GitLab branch".
    - This will filter the list to show plugins related to GitLab branches.

3. **Select and Install the Plugin**:
    - Locate the `GitLab Branch Source Plugin` in the filtered list.
    - Click on `Download now and install after restart`.
    - Jenkins will prompt you to restart after the installation is complete.

#### Potential Issues and Solutions

- **Finicky Installation**: Sometimes, the installation process may be finicky due to network issues or plugin dependencies. If the installation fails, try reloading Jenkins and retrying the installation.
- **Restart Required**: Ensure that Jenkins is restarted after the installation to apply the changes.

### Installing the Docker Plugin

Next, we need to install the Docker plugin to enable Jenkins to interact with Docker containers. This is essential for building and deploying applications in a containerized environment.

#### Step-by-Step Installation

1. **Access Jenkins Plugin Management**:
    - Navigate to `Manage Jenkins` in the Jenkins dashboard.
    - Click on `Manage Plugins`.

2. **Search for Docker Plugin**:
    - In the `Available` tab, use the search field to enter "Docker".
    - This will filter the list to show plugins related to Docker.

3. **Select and Install the Plugin**:
    - Locate the `Docker Plugin` in the filtered list.
    - Click on `Download now and install after restart`.
    - Jenkins will prompt you to restart after the installation is complete.

#### Potential Issues and Solutions

- **Multiple Docker Plugins**: There are several Docker-related plugins available. Ensure you select the correct one (`Docker Plugin`) to avoid conflicts.
- **Restart Required**: Ensure that Jenkins is restarted after the installation to apply the changes.

### Configuring Jenkins for GitLab Integration

After installing the necessary plugins, we need to configure Jenkins to work with our GitLab instance.

#### Step-by-Step Configuration

1. **Access Jenkins Configuration**:
    - Navigate to `Manage Jenkins` in the Jenkins dashboard.
    - Click on `Configure System`.

2. **Add GitLab Server**:
    - Scroll down to the `GitLab` section.
    - Click on `Add GitLab server`.
    - Enter a display name for the GitLab server.
    - Enter the server URL (e.g., `http://gitlab.demo.local`).

3. **Add Credentials**:
    - Click on `Add credentials`.
    - Select `GitLab Personal Access Token`.
    - Enter the personal access token generated from the GitLab web interface.
    - Optionally, add a description for the token.
    - Leave the `ID` field blank; Jenkins will generate a random ID.

4. **Manage Webhooks and System Hooks**:
    - Click on `Manage webhooks` to configure webhooks for triggering Jenkins jobs.
    - Click on `Manage system hooks` to configure system hooks for monitoring GitLab events.

#### Potential Issues and Solutions

- **Usage Statistics**: For security purposes, it is recommended to unselect the usage statistics option in the `Configure System` page.
- **Webhook Configuration**: Ensure that the webhook URLs are correctly configured in both Jenkins and GitLab to avoid miscommunication.

### Real-World Examples and Recent Breaches

#### Example: Docker Security Vulnerability (CVE-2019-14271)

In 2019, a critical vulnerability was discovered in Docker, allowing attackers to execute arbitrary commands on the host system. This vulnerability highlights the importance of securing Docker configurations and ensuring that only trusted images are used.

```mermaid
sequenceDiagram
    participant User as User
    participant Jenkins as Jenkins
    participant Docker as Docker
    participant GitLab as GitLab
    User->>Jenkins: Trigger Build
    Jenkins->>Docker: Pull Image
    Docker-->>Jenkins: Return Image
    Jenkins->>GitLab: Update Status
```

#### Secure Coding Practices

To prevent such vulnerabilities, ensure that Docker images are scanned for known vulnerabilities using tools like Trivy or Clair. Additionally, use Docker security features such as AppArmor or SELinux to restrict container privileges.

```mermaid
graph LR
    A[User] --> B[Jenkins]
    B --> C[Docker]
    C --> D[GitLab]
    D --> E[Webhook]
    E --> F[Build]
    F --> G[Deployment]
```

### How to Prevent / Defend

#### Detection

- **Regular Scans**: Use tools like Trivy or Clair to regularly scan Docker images for known vulnerabilities.
- **Monitoring**: Implement monitoring solutions to detect unauthorized access or suspicious activities.

#### Prevention

- **Secure Configurations**: Ensure that Docker configurations are secure and only trusted images are used.
- **Least Privilege Principle**: Apply the least privilege principle to limit container privileges.

#### Secure-Coding Fixes

Compare the vulnerable and secure versions of Docker configurations:

**Vulnerable Version**

```yaml
version: '3'
services:
  web:
    image: my-vulnerable-image:latest
    ports:
      - "8080:80"
```

**Secure Version**

```yaml
version: '3'
services:
  web:
    image: my-secure-image:latest
    ports:
      - "8080:80"
    security_opt:
      - "apparmor:unconfined"
```

### Complete Example

#### Full HTTP Request and Response

Here is a complete example of an HTTP request and response for configuring a webhook in Jenkins:

**HTTP Request**

```http
POST /jenkins/job/my-job/configure HTTP/1.1
Host: jenkins.example.com
Content-Type: application/x-www-form-urlencoded
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=

json={
  "property": [
    {
      "name": "org.jenkinsci.plugins.ghprb.GhprbTrigger",
      "configuration": {
        "triggerPhrase": "",
        "onlyTriggerPhrase": false,
        "skipBuildPhrase": "",
        "autoCloseFailedPullRequests": false,
        "autoMerge": false,
        "commitStatusContext": "jenkins",
        "pollInterval": "5",
        "useGitHubHooks": true,
        "useGitHubStatus": true,
        "statusPrefix": "",
        "overrideStatus": false,
        "overrideMessage": "",
        "overrideUrl": "",
        "overrideState": "",
        "overrideTargetUrl": ""
      }
    }
  ]
}
```

**HTTP Response**

```http
HTTP/1.1 200 OK
Date: Tue, 14 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Length: 0
Content-Type: text/html;charset=UTF-8
```

### Hands-On Labs

For practical experience, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive training on web security concepts and techniques.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application for learning about web security.

These labs provide a controlled environment to practice and reinforce the concepts learned in this chapter.

### Conclusion

Integrating Jenkins with GitLab and Docker is a crucial step in setting up automated security testing in a DevSecOps environment. By following the steps outlined in this chapter, you can ensure that your Jenkins setup is properly configured to work seamlessly with GitLab and Docker. Additionally, by implementing secure coding practices and regular monitoring, you can prevent and detect potential security vulnerabilities in your CI/CD pipeline.

---
<!-- nav -->
[[05-Initializing the Setup for Automated Security Testing Part 5|Initializing the Setup for Automated Security Testing Part 5]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/06-Initializing the Setup for Automated Security Testing/Demo Setting up the Demo Lab/00-Overview|Overview]] | [[07-Initializing the Setup for Automated Security Testing Part 7|Initializing the Setup for Automated Security Testing Part 7]]
