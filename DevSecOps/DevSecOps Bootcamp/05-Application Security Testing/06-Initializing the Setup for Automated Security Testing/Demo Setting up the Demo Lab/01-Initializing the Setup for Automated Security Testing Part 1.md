---
course: DevSecOps
topic: Initializing the Setup for Automated Security Testing
tags: [devsecops]
---

## Initializing the Setup for Automated Security Testing

### Checking Out the Tag and Creating a New Branch

In the context of setting up an automated security testing environment, the first step involves checking out a specific tag and creating a new branch. This ensures that the environment is consistent and reproducible, which is crucial for reliable testing.

#### Checking Out the Tag

The command to check out a specific tag is:

```bash
git checkout tags/demo_1
```

This command checks out the `demo_1` tag, which represents a specific snapshot of the repository. Tags are typically used to mark important points in the development history, such as releases or milestones.

#### Creating a New Branch

After checking out the tag, it is often useful to create a new branch for the current session. This allows you to make changes without affecting the original tag. The command to create a new branch is:

```bash
git checkout -b demo_1
```

This creates a new branch named `demo_1` based on the current commit (which is the `demo_1` tag).

### Viewing the Docker Compose File

To understand the setup, we need to view the Docker Compose file. Docker Compose is a tool for defining and running multi-container Docker applications. The file defines services, networks, and volumes.

#### Using Utility `bet` for Syntax Highlighting

The utility `bet` is used to view the Docker Compose file with syntax highlighting. This makes it easier to read and understand the file. The command to use `bet` is:

```bash
bet docker-compose.yml
```

This command opens the `docker-compose.yml` file with syntax highlighting.

### Understanding Docker Compose Syntax

Docker Compose files are written in YAML format. They define services, networks, and volumes. Each service is a container that runs a specific application or process.

#### Defining the Network

The first section of the Docker Compose file defines the network:

```yaml
networks:
  lab:
    driver: bridge
```

This defines a network named `lab` using the bridge driver. The bridge driver creates a virtual network that connects the containers.

#### Defining Services

The Docker Compose file defines three services: GitLab, Jenkins, and a registry.

##### GitLab Service

The GitLab service is defined as follows:

```yaml
services:
  gitlab:
    image: gitlab/gitlab-ce:latest
    hostname: gitlab.demo.local
    ports:
      - "80:80"
      - "7722:22"
```

- **Image**: The `image` field specifies the Docker image to use. Here, it uses the latest version of the `gitlab/gitlab-ce` image.
- **Hostname**: The `hostname` field sets the hostname for the GitLab service.
- **Ports**: The `ports` field maps the container's ports to the host's ports. Port 80 is mapped to the web interface, and port 7722 is mapped to SSH/Git access.

##### Jenkins Service

The Jenkins service is defined as follows:

```yaml
  jenkins:
    image: jenkinsci/blueocean:latest
    ports:
      - "8080:8080"
    hostname: jenkins.demo.local
```

- **Image**: The `image` field specifies the Docker image to use. Here, it uses the latest version of the `jenkinsci/blueocean` image.
- **Ports**: The `ports` field maps the container's port 8080 to the host's port 8080.
- **Hostname**: The `hostname` field sets the hostname for the Jenkins service.

##### Registry Service

The registry service is defined as follows:

```yaml
  registry:
    image: registry:2
    ports:
      - "5000:5000"
```

- **Image**: The `image` field specifies the Docker image to use. Here, it uses the `registry:2` image.
- **Ports**: The `ports` field maps the container's port 5000 to the host's port 5000.

### Full Docker Compose File

Here is the full Docker Compose file:

```yaml
version: '3'
services:
  gitlab:
    image: gitlab/gitlab-ce:latest
    hostname: gitlab.demo.local
    ports:
      - "80:80"
      - "7722:22"
  jenkins:
    image: jenkinsci/blueocean:latest
    ports:
      - "8080:8080"
    hostname: jenkins.demo.local
  registry:
    image: registry:2
    ports:
      - "5000:5000"
networks:
  lab:
    driver: bridge
```

### Running the Docker Compose File

To run the Docker Compose file, use the following command:

```bash
docker-compose up -d
```

This command starts the services in detached mode (`-d`).

### Network Topology

The network topology can be visualized using a Mermaid diagram:

```mermaid
graph LR
  A[Host] -->|80| B[GitLab]
  A -->|7722| B
  A -->|8080| C[Jenkins]
  A -->|5000| D[Registry]
  B --|Network| C
  B --|Network| D
  C --|Network| D
```

### Common Pitfalls and How to Prevent Them

#### Exposing Sensitive Ports

Exposing sensitive ports like SSH (port 22) can lead to unauthorized access. To prevent this, ensure that only necessary ports are exposed and use secure authentication methods.

**Vulnerable Configuration:**

```yaml
services:
  gitlab:
    image: gitlab/gitlab-ce:latest
    hostname: gitlab.demo.local
    ports:
      - "80:80"
      - "22:22"
```

**Secure Configuration:**

```yaml
services:
  gitlab:
    image: gitlab/gitlab-ce:latest
    hostname: gitlab.demo.local
    ports:
      - "80:80"
      - "7722:22"
```

#### Using Latest Tags

Using the `latest` tag for images can lead to unexpected behavior due to changes in the image. To prevent this, use specific tags.

**Vulnerable Configuration:**

```yaml
services:
  gitlab:
    image: gitlab/gitlab-ce:latest
```

**Secure Configuration:**

```yaml
services:
  gitlab:
    image: gitlab/gitlab-ce:14.10.0
```

### Real-World Examples

#### CVE-2021-22205

CVE-2021-22205 is a vulnerability in Jenkins that allows remote code execution. This vulnerability can be exploited if Jenkins is exposed to the internet without proper authentication.

**Detection:**

Use tools like `nmap` to scan for open ports and `curl` to check for Jenkins versions.

```bash
nmap -p 8080 <IP>
curl http://<IP>:8080/ci/
```

**Prevention:**

- Ensure Jenkins is not exposed to the internet.
- Use strong authentication methods.
- Regularly update Jenkins to the latest version.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs for web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

These labs provide practical experience in setting up and securing environments similar to the one described in this chapter.

### Conclusion

Setting up an automated security testing environment involves careful planning and configuration. By understanding the Docker Compose syntax and the importance of network definitions, you can create a robust and secure environment. Always be aware of common pitfalls and take steps to prevent them. Real-world examples and hands-on labs provide valuable practice and reinforce the concepts learned.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/06-Initializing the Setup for Automated Security Testing/Demo Setting up the Demo Lab/00-Overview|Overview]] | [[02-Initializing the Setup for Automated Security Testing Part 2|Initializing the Setup for Automated Security Testing Part 2]]
