---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Jenkins and Its Role in DevOps

Jenkins is an open-source automation server that provides extensive support for continuous integration and continuous delivery (CI/CD) pipelines. It is widely used in DevOps environments to automate the building, testing, and deployment of applications. Jenkins supports a wide range of tools and technologies, making it a versatile choice for various development workflows.

### What is Jenkins?

Jenkins is a Java-based application that runs as a server and provides a web interface for managing and configuring jobs. A job in Jenkins is essentially a task or a series of tasks that are executed automatically based on certain triggers, such as changes in a code repository or scheduled times.

### Why Use Jenkins?

Jenkins offers several key benefits:

1. **Automation**: Jenkins automates repetitive tasks, reducing the likelihood of human error and freeing up developers to focus on more critical work.
2. **Integration**: Jenkins integrates seamlessly with a variety of tools and services, including version control systems like Git, build tools like Gradle, and testing frameworks.
3. **Scalability**: Jenkins can be scaled to handle large numbers of jobs and complex pipelines, making it suitable for both small and large organizations.
4. **Extensibility**: Jenkins has a vast ecosystem of plugins that extend its functionality, allowing users to customize their workflows according to their specific needs.

### How Jenkins Works

At a high level, Jenkins operates as follows:

1. **Job Configuration**: Users define jobs in Jenkins, specifying the steps to be executed and the conditions under which they should run.
2. **Build Triggers**: Jobs can be triggered manually or automatically based on events such as code commits or time-based schedules.
3. **Execution**: Jenkins executes the steps defined in the job, typically involving building the code, running tests, and deploying the application.
4. **Reporting**: Jenkins provides detailed reports on the status of each job, including logs, test results, and deployment artifacts.

### Jenkins Installation Using Docker on DigitalOcean

In this section, we will walk through the process of installing Jenkins using Docker on DigitalOcean. This approach leverages the benefits of containerization to provide a lightweight and portable Jenkins installation.

#### Prerequisites

Before proceeding with the installation, ensure you have the following:

1. **DigitalOcean Account**: Sign up for a DigitalOcean account if you don't already have one.
2. **Docker Installed**: Ensure Docker is installed on your DigitalOcean droplet. You can follow the official DigitalOcean guide to install Docker.

#### Step-by-Step Installation

1. **Create a Droplet**:
   - Log in to your DigitalOcean account.
   - Navigate to the "Create" menu and select "Droplets".
   - Choose a region and select an image (e.g., Ubuntu 20.04 LTS).
   - Select a size for your droplet (e.g., $5/month plan).
   - Add SSH keys for secure access.
   - Create the droplet.

2. **Install Docker**:
   - SSH into your droplet.
   - Follow the official DigitalOcean guide to install Docker.

3. **Run Jenkins Docker Container**:
   - Pull the Jenkins Docker image:
     ```bash
     docker pull jenkins/jenkins:lts
     ```
   - Run the Jenkins container:
     ```bash
     docker run -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home -d jenkins/jenkins:lts
     ```
   - The `-p` flags map ports 8080 and 50000 on the host to the container.
   - The `-v` flag mounts a volume named `jenkins_home` to `/var/jenkins_home` in the container, ensuring persistent storage for Jenkins data.

4. **Access Jenkins**:
   - Open a web browser and navigate to `http://<your-droplet-ip>:8080`.
   - Jenkins will prompt you to unlock the initial setup by providing an initial admin password. You can find this password in the container logs:
     ```bash
     docker logs <container-id>
     ```

5. **Initialize Jenkins**:
   - Enter the initial admin password and proceed with the setup wizard.
   - Install suggested plugins or select specific plugins based on your requirements.
   - Create an admin user and configure Jenkins as needed.

### Jenkins Plugins

Plugins are essential components that extend Jenkins' functionality. They can be installed during the initial setup or added later via the Jenkins web interface.

#### Commonly Used Plugins

1. **Git Plugin**: Integrates Jenkins with Git repositories for automated builds.
2. **Gradle Plugin**: Supports building projects using Gradle.
3. **Credentials Plugin**: Manages credentials securely within Jenkins.
4. **Pipeline Plugin**: Enables the creation and management of CI/CD pipelines.

#### Installing Plugins

During the initial setup, Jenkins prompts you to install plugins. You can choose to install suggested plugins or select specific ones. To install additional plugins later:

1. Navigate to `Manage Jenkins` > `Manage Plugins`.
2. In the `Available` tab, search for and select the desired plugins.
3. Click `Install without restart`.

### Creating Your First Admin User

After installing the necessary plugins, Jenkins will prompt you to create an admin user. This user will have administrative privileges and can manage Jenkins configurations.

#### Steps to Create an Admin User

1. Provide a username and password for the admin user.
2. Optionally, enter email and full name details.
3. Save the user.

### Configuring Jenkins

Once Jenkins is set up and the admin user is created, you can start configuring Jenkins to suit your needs.

#### Example Configuration

1. **Create a New Job**:
   - Navigate to `New Item`.
   - Enter a name for the job and select `Freestyle project`.
   - Configure the job settings, such as source code management, build triggers, and build steps.

2. **Source Code Management**:
   - Specify the Git repository URL and credentials if required.
   - Set branch specifications to define which branches to build.

3. **Build Triggers**:
   - Configure triggers such as polling SCM or triggering on commit.

4. **Build Steps**:
   - Define the steps to be executed during the build, such as running Gradle commands.

5. **Post-build Actions**:
   - Configure actions to be performed after the build, such as archiving artifacts or sending notifications.

### Real-World Examples and Recent CVEs

Jenkins, like any software, is susceptible to vulnerabilities. Here are some recent CVEs and breaches involving Jenkins:

1. **CVE-2021-21630**: This vulnerability allows remote code execution due to improper validation of plugin updates. Ensure you keep Jenkins and plugins updated to the latest versions.
2. **CVE-2021-25282**: This vulnerability affects the Jenkins CLI and can lead to unauthorized access. Secure the Jenkins CLI by limiting access and using strong authentication mechanisms.

### How to Prevent / Defend

To secure your Jenkins installation, follow these best practices:

1. **Keep Jenkins Updated**: Regularly update Jenkins and plugins to the latest versions to patch known vulnerabilities.
2. **Use Strong Authentication**: Enable and enforce strong authentication mechanisms, such as two-factor authentication (2FA).
3. **Limit Access**: Restrict access to Jenkins to only authorized users and limit administrative privileges.
4. **Secure Credentials**: Use the Credentials Plugin to securely store and manage sensitive information.
5. **Monitor and Audit**: Regularly monitor Jenkins logs and audit configurations to detect and respond to suspicious activities.

### Full Example: Jenkins Job Configuration

Here is a complete example of a Jenkins job configuration using a Freestyle project:

```yaml
# Jenkins Job Configuration
name: MyFirstJob
projectType: freestyle

sourceCodeManagement:
  scmType: git
  repositoryURL: https://github.com/myusername/myrepo.git
  credentialsId: mygitcredentials
  branchSpec: */main

buildTriggers:
  pollSCM: H/15 * * * *

buildSteps:
  - gradleCommand: clean build

postBuildActions:
  - archiveArtifacts: target/*.jar
```

### Raw HTTP Request and Response

When interacting with Jenkins via HTTP, you might send requests to trigger builds or retrieve job statuses. Here is an example of a raw HTTP request and response:

#### HTTP Request

```http
POST /job/MyFirstJob/buildWithParameters HTTP/1.1
Host: jenkins.example.com
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
Content-Type: application/x-www-form-urlencoded

PARAM1=value1&PARAM2=value2
```

#### HTTP Response

```http
HTTP/1.1 201 Created
Date: Tue, 01 Aug 2023 12:00:00 GMT
Location: http://jenkins.example.com/job/MyFirstJob/1/
Content-Length: 0
```

### Mermaid Diagrams

#### Jenkins Architecture Diagram

```mermaid
graph TD
    A[User] --> B[Jenkins Web Interface]
    B --> C[Jenkins Master]
    C --> D[Jenkins Slave]
    C --> E[Version Control System]
    C --> F[Build Tools]
    C --> G[Test Frameworks]
    C --> H[Deployment Targets]
```

#### Jenkins Pipeline Flow

```mermaid
graph TD
    A[Trigger] --> B[Checkout Code]
    B --> C[Build Project]
    C --> D[Run Tests]
    D --> E[Archive Artifacts]
    E --> F[Deploy Application]
```

### Hands-On Labs

For hands-on practice with Jenkins, consider the following labs:

1. **PortSwigger Web Security Academy**: Offers a comprehensive course on web security, including sections on CI/CD pipelines.
2. **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills, including CI/CD pipeline security.
3. **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning web security, including CI/CD pipeline security.

By following these steps and best practices, you can successfully install and configure Jenkins using Docker on DigitalOcean, and secure your environment against potential vulnerabilities.

---
<!-- nav -->
[[01-Introduction to Jenkins Installation Using Docker on DigitalOcean|Introduction to Jenkins Installation Using Docker on DigitalOcean]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/27-Jenkins Installation Using Docker On DigitalOcean/00-Overview|Overview]] | [[03-Jenkins Installation Using Docker on DigitalOcean|Jenkins Installation Using Docker on DigitalOcean]]
