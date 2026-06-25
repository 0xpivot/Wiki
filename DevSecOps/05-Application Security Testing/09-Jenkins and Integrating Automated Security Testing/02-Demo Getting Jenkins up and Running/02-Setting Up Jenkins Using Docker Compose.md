---
course: DevSecOps
topic: Jenkins and Integrating Automated Security Testing
tags: [devsecops]
---

## Setting Up Jenkins Using Docker Compose

### Introduction to Jenkins and Docker Compose

Jenkins is an open-source automation server that provides continuous integration and continuous delivery (CI/CD) services. It is widely used in DevSecOps practices to automate the building, testing, and deployment of applications. Docker Compose is a tool for defining and running multi-container Docker applications. By combining Jenkins with Docker Compose, we can easily set up a Jenkins environment that can manage multiple Docker containers.

### Directory Listing and File Inspection

Before diving into setting up Jenkins, let's first inspect the files in our current directory. We'll use the `ll` command to list all files with detailed information:

```sh
ll
```

This command will display all files in the directory along with their permissions, sizes, and timestamps. We are particularly interested in the `docker-compose.yml` file, which defines the services we will start.

To view the contents of the `docker-compose.yml` file, we can use the `bat` command, which provides syntax highlighting for better readability:

```sh
bat docker-compose.yml
```

### Understanding the `docker-compose.yml` File

The `docker-compose.yml` file is written in YAML format and defines the services that will be started. Each service is defined with a unique name and a set of properties such as image, ports, volumes, and environment variables.

#### Example `docker-compose.yml` File

Here is an example of a `docker-compose.yml` file:

```yaml
version: '3.5'
services:
  jenkins:
    image: jenkins/jenkins:lts
    container_name: jenkins
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - ./jenkins_home:/var/jenkins_home
    user: "900:900"
```

In this example:
- `version: '3.5'` specifies the version of the Docker Compose file format.
- `services:` defines the services to be created.
- `jenkins:` is the name of the service.
- `image: jenkins/jenkins:lts` specifies the Docker image to use.
- `container_name: jenkins` sets the name of the container.
- `ports:` maps the host port to the container port.
- `volumes:` mounts a volume from the host to the container.
- `user: "900:900"` specifies the user and group IDs to run the container as.

### Checking the Docker Group ID

The `user: "900:900"` line in the `docker-compose.yml` file specifies the user and group IDs that Jenkins will run as inside the container. This is important because Jenkins needs to interact with Docker containers, and the user ID must match the Docker group ID on the host system.

To check the Docker group ID on your local system, you can use the following command:

```sh
getent group docker
```

On the system described in the transcript, the output might look like this:

```sh
docker:x:999:user1,user2
```

This indicates that the Docker group ID is 999.

### Overriding the User ID in Docker Compose

If the group ID in the `docker-compose.yml` file does not match the Docker group ID on your system, you need to create an override file to correct this. We will create a new file called `docker-compose.override.yml`.

#### Creating the Override File

We can use any text editor to create this file. In the transcript, the lecturer uses `emacs`, but you can use any editor you prefer.

Here is how to create the override file using `emacs`:

```sh
emacs docker-compose.override.yml
```

In the editor, we will start by specifying the version number and then redefine the Jenkins service to override the user ID:

```yaml
version: '3.5'
services:
  jenkins:
    user: "999:999"
```

This file overrides the `user` property in the original `docker-compose.yml` file.

### Full Example of `docker-compose.yml` and `docker-compose.override.yml`

Here is the full example of both files:

**docker-compose.yml:**

```yaml
version: '3.5'
services:
  jenkins:
    image: jenkins/jenkins:lts
    container_name: jenkins
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - ./jenkins_home:/var/jenkins_home
    user: "900:900"
```

**docker-compose.override.yml:**

```yaml
version: '3.5'
services:
  jenkins:
    user: "999:999"
```

### Starting Jenkins with Docker Compose

Once the files are correctly configured, you can start Jenkins using Docker Compose:

```sh
docker-compose up -d
```

This command starts the Jenkins service in detached mode (`-d`).

### Verifying Jenkins Setup

To verify that Jenkins is running correctly, you can access it via a web browser at `http://localhost:8080`. You should see the Jenkins setup wizard, indicating that Jenkins is running successfully.

### Integrating Automated Security Testing

Now that Jenkins is set up, we can integrate automated security testing into our CI/CD pipeline. This involves configuring Jenkins jobs to run security scans on the codebase.

#### Example Security Scan Configuration

Here is an example of how to configure a Jenkins job to run a security scan using a tool like SonarQube:

1. **Install SonarQube Scanner Plugin**: Ensure that the SonarQube Scanner plugin is installed in Jenkins.
2. **Configure Jenkins Job**: Create a new Jenkins job and configure it to run the security scan.

**Jenkinsfile Example:**

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Security Scan') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'mvn sonar:sonar'
                }
            }
        }
    }
}
```

In this example:
- The `Build` stage runs a Maven build.
- The `Security Scan` stage runs a SonarQube analysis.

### Common Pitfalls and How to Prevent Them

#### Incorrect User ID Configuration

**Problem:** If the user ID in the `docker-compose.yml` file does not match the Docker group ID on the host system, Jenkins may not be able to interact with Docker containers properly.

**Solution:** Always ensure that the user ID in the `docker-compose.yml` file matches the Docker group ID on the host system. Use an override file if necessary.

#### Missing Security Scans

**Problem:** Not integrating security scans into the CI/CD pipeline can lead to vulnerabilities being missed.

**Solution:** Always configure Jenkins jobs to run security scans as part of the pipeline. Use tools like SonarQube, OWASP ZAP, or other security scanners.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example is the Jenkins Credentials Manager vulnerability (CVE-2018-1000301), which allowed attackers to execute arbitrary code on Jenkins servers. This highlights the importance of keeping Jenkins and its plugins up to date and integrating security scans into the CI/CD pipeline.

### Hands-On Labs

For hands-on practice with Jenkins and Docker Compose, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web application security, including CI/CD pipelines.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training.

These labs provide practical experience in setting up Jenkins and integrating security testing into the CI/CD pipeline.

### Conclusion

Setting up Jenkins using Docker Compose and integrating automated security testing is crucial for maintaining a secure CI/CD pipeline. By following the steps outlined above and being aware of common pitfalls, you can ensure that your Jenkins environment is robust and secure.

---
<!-- nav -->
[[01-Getting Jenkins Up and Running|Getting Jenkins Up and Running]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/09-Jenkins and Integrating Automated Security Testing/03-Demo Getting Jenkins up and Running/00-Overview|Overview]] | [[03-Setting Up Jenkins for DevSecOps|Setting Up Jenkins for DevSecOps]]
