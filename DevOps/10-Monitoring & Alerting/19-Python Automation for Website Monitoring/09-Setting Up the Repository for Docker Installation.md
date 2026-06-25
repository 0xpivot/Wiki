---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Setting Up the Repository for Docker Installation

When setting up a new server environment, one of the critical tasks is ensuring that the necessary software packages are available and up-to-date. In this case, we are focusing on installing Docker, a powerful platform for developing, shipping, and running applications inside lightweight containers. Before diving into the installation process, let's understand the underlying concepts and the importance of setting up the repository correctly.

### Understanding Repositories

A repository is a collection of software packages that can be installed on your system. These repositories are maintained by various organizations and are typically categorized based on the Linux distribution or operating system you are using. For instance, Ubuntu, Debian, CentOS, and Fedora each have their own set of repositories.

#### Why Repositories Matter

Repositories are crucial because they ensure that you are installing the latest and most secure versions of software. They also provide a consistent way to manage software updates and dependencies across different systems. By setting up the correct repository, you can easily install and update Docker and other related tools.

### Connecting as Root User

In the context of our setup, we are connecting to the server as a root user. The root user is the superuser in Unix-based systems, having full administrative privileges. This means that any command executed by the root user does not require additional permissions or the use of `sudo`.

#### Why Not Use `sudo`?

Using `sudo` is generally recommended in non-root environments to avoid accidentally executing harmful commands. However, since we are already logged in as the root user, there is no need to prepend commands with `sudo`. This simplifies the command execution process and reduces the risk of permission-related errors.

### Updating the Package Manager

Before installing Docker, it is essential to update the package manager's repository information. This ensures that you are working with the latest package lists and dependencies.

```bash
apt-get update
```

This command updates the list of available packages and their versions, but it does not install or upgrade any packages. It is a crucial step to ensure that you are installing the most recent and secure versions of the software.

### Adding Docker's Official Repository

To install Docker, we need to add Docker's official repository to our system. This repository contains the latest versions of Docker and its related tools.

#### Steps to Add the Repository

1. **Add Docker's GPG Key**: Docker uses GPG keys to sign its packages, ensuring their authenticity and integrity. We need to add Docker's official GPG key to our system.

    ```bash
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
    ```

    This command downloads the GPG key from Docker's official repository and adds it to the system's keyring.

2. **Verify the Key**: After adding the key, it is good practice to verify its fingerprint to ensure that it matches the expected value.

    ```bash
    apt-key fingerprint 0EBFCD88
    ```

    This command verifies the fingerprint of the added key. The output should match the expected fingerprint provided by Docker.

3. **Add the Docker Repository**: Once the key is verified, we can add the Docker repository to our system.

    ```bash
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    ```

    This command adds the Docker repository to the list of repositories managed by `apt-get`. The `$(lsb_release -cs)` part dynamically inserts the codename of the current Ubuntu release.

### Installing Docker

With the repository set up, we can now proceed to install Docker and its related tools.

```bash
apt-get update
apt-get install docker-ce docker-ce-cli containerd.io
```

These commands perform the following actions:

1. **Update the Package List**: `apt-get update` ensures that we have the latest package information.
2. **Install Docker**: `apt-get install docker-ce docker-ce-cli containerd.io` installs the Docker engine (`docker-ce`), the Docker CLI (`docker-ce-cli`), and the container runtime (`containerd.io`).

### Verifying the Installation

After installation, it is important to verify that Docker is correctly installed and functioning.

```bash
docker --version
```

This command prints the version of Docker installed on the system, confirming that the installation was successful.

### Common Pitfalls and How to Prevent Them

#### Incorrect Repository Setup

**Problem**: If the wrong repository is added, you might end up installing outdated or insecure versions of Docker.

**Prevention**:
- Always use the official Docker repository.
- Verify the GPG key fingerprint to ensure authenticity.

#### Missing Updates

**Problem**: Failing to update the package list before installation can result in installing outdated packages.

**Prevention**:
- Always run `apt-get update` before installing any new packages.

#### Insufficient Permissions

**Problem**: Executing commands without proper permissions can lead to errors or incomplete installations.

**Prevention**:
- Ensure you are logged in as the root user or use `sudo` when required.

### Real-World Example: CVE-2021-29923

CVE-2021-29923 is a vulnerability in Docker that allows an attacker to escalate privileges and gain root access to the host system. This vulnerability highlights the importance of keeping Docker and its components up-to-date.

#### Impact

An attacker could exploit this vulnerability to execute arbitrary code with elevated privileges, potentially compromising the entire system.

#### Prevention

1. **Keep Docker Updated**: Regularly update Docker to the latest version.
2. **Use Secure Configuration**: Follow best practices for securing Docker configurations.

### Secure Coding Practices

#### Vulnerable Code Example

```yaml
# Dockerfile
FROM ubuntu:latest
RUN apt-get update && apt-get install -y curl
```

#### Secure Code Example

```yaml
# Dockerfile
FROM ubuntu:latest
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*
```

The secure version removes the package lists after installation, reducing the attack surface.

### Hands-On Lab Suggestions

For practical experience with Docker installation and management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on web security, including sections on Docker and container security.
- **OWASP Juice Shop**: A deliberately vulnerable web application for practicing web security skills, including Docker usage.
- **Docker Documentation Labs**: Official Docker documentation provides step-by-step guides and labs for learning Docker.

By following these steps and best practices, you can ensure a secure and efficient setup of Docker on your server.

---
<!-- nav -->
[[08-Running an EngineX Container|Running an EngineX Container]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/19-Python Automation for Website Monitoring/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/19-Python Automation for Website Monitoring/10-Conclusion|Conclusion]]
