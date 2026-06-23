---
course: DevSecOps
topic: Initializing the Setup for Automated Security Testing
tags: [devsecops]
---

## Initializing the Setup for Automated Security Testing

### Prerequisites and Environment Setup

Before diving into the setup of the demo lab, it's essential to ensure that the necessary tools and environment are correctly configured. In this case, we'll be using Docker and Docker Compose, along with GitLab and Jenkins for automated security testing.

#### Docker Installation Verification

Docker is a platform that allows developers to package applications into containers, ensuring consistency across different environments. To verify that Docker is installed correctly, we can use the `which` command to locate the Docker binary:

```sh
which docker
```

If Docker is installed correctly, this command should return the path to the Docker binary, typically `/usr/bin/docker`. To further confirm that Docker is functioning correctly, we can run the `hello-world` image:

```sh
docker run hello-world
```

This command pulls the `hello-world` image from Docker Hub and runs it in a container. If the output indicates that Docker is correctly set up, you should see a message similar to:

```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

#### Docker Compose Installation Verification

Docker Compose is a tool for defining and running multi-container Docker applications. To verify that Docker Compose is installed correctly, we can use the `which` command again:

```sh
which docker-compose
```

If Docker Compose is installed correctly, this command should return the path to the `docker-compose` binary, typically `/usr/local/bin/docker-compose`.

### Setting Up the Demo Lab

The demo lab consists of a standard Debian Linux installation. We'll be using this environment to set up GitLab, Jenkins, and a Docker Registry.

#### Cloning the Repository

To begin, we need to clone the repository containing the necessary files for the demo lab. The repository can be found at:

```
https://github.com/PeterMosman/DevSecOps-Lab
```

We can clone the repository using the following command:

```sh
git clone https://github.com/PeterMosman/DevSecOps-Lab.git
```

After cloning the repository, we need to navigate to the directory:

```sh
cd DevSecOps-Lab
```

### Configuring GitLab

GitLab is a web-based Git repository manager that provides a wide range of features for project management, issue tracking, and continuous integration. To set up GitLab, we'll use Docker Compose.

#### Docker Compose Configuration

The `docker-compose.yml` file in the cloned repository defines the services required to run GitLab. Here is an example of what the `docker-compose.yml` file might look like:

```yaml
version: '3'
services:
  gitlab:
    image: 'gitlab/gitlab-ce:latest'
    container_name: 'gitlab'
    restart: unless-stopped
    hostname: 'gitlab.example.com'
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url 'http://gitlab.example.com/'
    ports:
      - '80:80'
      - '443:443'
      - '22:22'
    volumes:
      - './gitlab/config:/etc/gitlab'
      - './gitlab/logs:/var/log/gitlab'
      - './gitlab/data:/var/opt/gitlab'
```

This configuration sets up a GitLab instance with the following properties:
- Uses the latest version of the GitLab CE image.
- Restarts the container unless explicitly stopped.
- Sets the hostname to `gitlab.example.com`.
- Configures the external URL to `http://gitlab.example. com/`.
- Maps the necessary ports (HTTP, HTTPS, SSH).
- Mounts volumes for configuration, logs, and data.

#### Running GitLab

To start the GitLab service, we can use the following command:

```sh
docker-compose up -d
```

This command starts the services defined in the `docker-compose.yml` file in detached mode (`-d`). Once the services are up and running, you can access GitLab by navigating to `http://localhost` in your web browser.

### Configuring Jenkins

Jenkins is an open-source automation server that provides extensive support for continuous integration and continuous delivery. To set up Jenkins, we'll again use Docker Compose.

#### Docker Compose Configuration

The `docker-compose.yml` file in the cloned repository defines the services required to run Jenkins. Here is an example of what the `docker-compose.yml` file might look like:

```yaml
version: '3'
services:
  jenkins:
    image: 'jenkins/jenkins:lts'
    container_name: 'jenkins'
    restart: unless-stopped
    ports:
      - '8080:8080'
      - '50000:50000'
    volumes:
      - './jenkins_home:/var/jenkins_home'
```

This configuration sets up a Jenkins instance with the following properties:
- Uses the latest LTS version of the Jenkins image.
- Restarts the container unless explicitly stopped.
- Maps the necessary ports (HTTP, JNLP).
- Mounts a volume for the Jenkins home directory.

#### Running Jenkins

To start the Jenkins service, we can use the following command:

```sh
docker-compose up -d
```

Once the services are up and running, you can access Jenkins by navigating to `http://localhost:8080` in your web browser.

### Configuring the Docker Registry

A Docker Registry is a storage and distribution system for Docker images. To set up a Docker Registry, we'll use Docker Compose.

#### Docker Compose Configuration

The `docker-compose.yml` file in the cloned repository defines the services required to run the Docker Registry. Here is an example of what the `docker-compose.yml` file might look like:

```yaml
version: '3'
services:
  registry:
    image: 'registry:2'
    container_name: 'registry'
    restart: unless-stopped
    ports:
      - '5000:5000'
    volumes:
      - './registry:/var/lib/registry'
```

This configuration sets up a Docker Registry with the following properties:
- Uses the latest version 2 of the Docker Registry image.
- Restarts the container unless explicitly stopped.
- Maps the necessary port (HTTP).
- Mounts a volume for the registry data.

#### Running the Docker Registry

To start the Docker Registry service, we can use the following command:

```sh
docker-compose up -d
```

Once the services are up and running, you can access the Docker Registry by navigating to `http://localhost:5000` in your web browser.

### How to Prevent / Defend

#### Docker Hardening

To ensure the security of Docker, it's important to follow best practices for hardening the environment. Here are some key steps:

1. **Use Non-root Users**: Avoid running containers as the root user. Instead, create a non-root user within the container.
   
2. **Limit Capabilities**: Use the `--cap-drop` flag to limit the capabilities of the container. For example, to drop the `NET_ADMIN` capability, you can use:
   
   ```sh
   docker run --cap-drop=NET_ADMIN <image>
   ```

3. **Use Secure Socket Communication**: Ensure that communication between Docker components is secure. Use TLS for communication between the Docker daemon and clients.

4. **Regularly Update Images**: Keep Docker images up to date to ensure that they contain the latest security patches.

#### Jenkins Hardening

To ensure the security of Jenkins, it's important to follow best practices for hardening the environment. Here are some key steps:

1. **Secure Jenkins Credentials**: Use strong passwords and enable two-factor authentication for Jenkins users.

2. **Limit Jenkins Permissions**: Restrict the permissions of Jenkins users to only the necessary actions. Use role-based access control (RBAC) to manage permissions.

3. **Enable Security Plugins**: Enable security plugins such as the `Role Strategy Plugin` to manage user roles and permissions.

4. **Regularly Update Jenkins**: Keep Jenkins and its plugins up to date to ensure that they contain the latest security patches.

#### Docker Registry Hardening

To ensure the security of the Docker Registry, it's important to follow best practices for hardening the environment. Here are some key steps:

1. **Use TLS for Communication**: Ensure that communication between the Docker client and the registry is secure. Use TLS for communication.

2. **Limit Access to the Registry**: Restrict access to the registry to only authorized users. Use authentication mechanisms such as basic auth or OAuth.

3. **Regularly Update the Registry**: Keep the Docker Registry up to date to ensure that it contains the latest security patches.

### Conclusion

Setting up the demo lab for automated security testing involves configuring GitLab, Jenkins, and a Docker Registry using Docker and Docker Compose. By following the steps outlined above, you can ensure that the environment is correctly set up and hardened against potential security threats.

### Practice Labs

For hands-on practice with DevSecOps, consider the following labs:
- **PortSwigger Web Security Academy**: Offers interactive labs for web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

These labs provide practical experience in setting up and securing DevSecOps environments.

---
<!-- nav -->
[[07-Initializing the Setup for Automated Security Testing Part 7|Initializing the Setup for Automated Security Testing Part 7]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/06-Initializing the Setup for Automated Security Testing/Demo Setting up the Demo Lab/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/06-Initializing the Setup for Automated Security Testing/Demo Setting up the Demo Lab/09-Practice Questions & Answers|Practice Questions & Answers]]
