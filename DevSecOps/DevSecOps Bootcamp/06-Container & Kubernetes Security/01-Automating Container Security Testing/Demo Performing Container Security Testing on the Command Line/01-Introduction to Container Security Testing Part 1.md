---
course: DevSecOps
topic: Automating Container Security Testing
tags: [devsecops]
---

## Introduction to Container Security Testing

Container security testing is a critical component of DevSecOps practices, ensuring that applications deployed within containers are secure against various vulnerabilities and threats. Containers provide a lightweight, portable environment for applications, but they also introduce unique security challenges. In this chapter, we will delve into automating container security testing using the command line, focusing on the Anchor Engine and Docker Compose.

### Background Theory

Containers are isolated environments that run applications with their dependencies. They are based on images, which are essentially snapshots of the application and its dependencies. Docker is one of the most popular containerization platforms, providing tools to build, ship, and run distributed applications.

#### Docker Compose

Docker Compose is a tool for defining and running multi-container Docker applications. With Compose, you use a `docker-compose.yml` file to configure your application’s services. Once configured, you can create and start all the services from your configuration with a single command.

```yaml
version: '3'
services:
  web:
    build: .
    ports:
      - "5000:5000"
  redis:
    image: "redis:alpine"
```

In this example, the `docker-compose.yml` file defines two services: `web` and `redis`. The `web` service is built from the current directory, and the `redis` service uses the `redis:alpine` image.

### Setting Up the Environment

To perform container security testing, we will use the Anchor Engine, a tool designed to help with container security analysis. The Anchor Engine runs in a Docker container and provides a command-line interface (CLI) for interacting with it.

#### Directory Structure

Docker Compose expects one directory to be used for one `docker-compose.yml` file. Therefore, we will create a new directory called `AnchorEngine` to house our setup.

```bash
mkdir AnchorEngine
cd AnchorEngine
```

### Downloading and Starting Services

We will download the necessary Docker images and start the services required for our container scan. This involves creating a `docker-compose.yml` file and running the `docker-compose up` command.

```yaml
version: '3'
services:
  anchor-engine:
    image: anchor/engine
    networks:
      - lab
  gitlab:
    image: gitlab/gitlab-ce:latest
    networks:
      - lab
  jenkins:
    image: jenkins/jenkins:lts
    networks:
      - lab
  registry:
    image: registry:2
    networks:
      - lab
networks:
  lab:
```

This `docker-compose.yml` file defines five services: `anchor-engine`, `gitlab`, `jenkins`, `registry`, and a custom network named `lab`.

```bash
docker-compose up -d
```

The `-d` flag runs the services in detached mode, meaning they will run in the background.

### Interacting with the Anchor Engine

Once the services are up and running, we can interact with the Anchor Engine using its command-line interface (CLI).

#### Using Docker Exec

One way to interact with the Anchor Engine is by using the `docker exec` command to run the CLI inside the running container.

```bash
docker exec -it <container_name> anchor-cli system status
```

Here, `<container_name>` should be replaced with the actual name of the container running the Anchor Engine. The `system status` command provides an overview of the running system.

#### Example Response

```plaintext
Service Status:
- Service 1: Running
- Service 2: Running
- Service 3: Running
- Service 4: Running
- Service 5: Running
- Service 6: Running
```

All six services are up and running, indicating that the system is ready for container scans.

#### Using Docker Run

Another method to interact with the Anchor Engine is by running the tools image that we built in an earlier demo. This involves using the `docker run` command with the `--rm` flag to automatically clean up the container once it exits.

```bash
docker run --rm <tools_image> anchor-cli system status
```

Here, `<tools_image>` should be replaced with the actual name of the tools image.

#### Troubleshooting

If the `docker run` command does not work, it could be due to network issues. All services defined in the `docker-compose.yml` file use the same named network (`lab`). Ensure that the network is correctly set up and that the services are communicating properly.

### Real-World Examples

Recent breaches and vulnerabilities have highlighted the importance of container security. For instance, the Log4j vulnerability (CVE-2021-44228) affected numerous applications, including those running in containers. Ensuring that containers are scanned regularly for such vulnerabilities is crucial.

### How to Prevent / Defend

#### Detection

Regularly scanning containers for vulnerabilities is essential. Tools like the Anchor Engine can help detect vulnerabilities in container images. Additionally, integrating security scans into the CI/CD pipeline ensures that vulnerabilities are caught early.

#### Prevention

1. **Secure Coding Practices**: Implement secure coding practices to avoid introducing vulnerabilities in the first place.
2. **Image Scanning**: Use tools like the Anchor Engine to scan container images for known vulnerabilities.
3. **Network Isolation**: Ensure that containers are isolated from each other and from the host system.
4. **Least Privilege Principle**: Run containers with the least privileges necessary to perform their tasks.

#### Secure Code Fix

Here is an example of a vulnerable code snippet and its secure counterpart:

**Vulnerable Code:**

```python
import os
import subprocess

def execute_command(command):
    subprocess.run(command, shell=True)
```

**Secure Code:**

```python
import os
import subprocess

def execute_command(command):
    subprocess.run(command.split(), check=True)
```

In the secure version, the `shell=True` parameter is removed, and the command is split into a list of arguments to avoid shell injection attacks.

### Complete Example

Let's walk through a complete example of setting up and running a container security test using the Anchor Engine.

#### Step 1: Create the `docker-compose.yml` File

```yaml
version: '3'
services:
  anchor-engine:
    image: anchor/engine
    networks:
      - lab
  gitlab:
    image: gitlab/gitlab-ce:latest
    networks:
      - lab
  jenkins:
    image: jenkins/jenkins:lts
    networks:
      - lab
  registry:
    image: registry:2
    networks:
      - lab
networks:
  lab:
```

#### Step 2: Start the Services

```bash
docker-compose up -d
```

#### Step 3: Check the System Status

Using `docker exec`:

```bash
docker exec -it anchor-engine anchor-cli system status
```

Using `docker run`:

```bash
docker run --rm tools-image anchor-cli system status
```

#### Step 4: Perform a Security Scan

```bash
docker exec -it anchor-engine anchor-cli scan --image my-image:latest
```

### Pitfalls and Common Mistakes

1. **Incorrect Network Configuration**: Ensure that all services are connected to the correct network.
2. **Missing Dependencies**: Make sure that all necessary dependencies are included in the container images.
3. **Security Misconfigurations**: Regularly review and update security configurations to mitigate known vulnerabilities.

### Conclusion

Automating container security testing is a vital part of DevSecOps practices. By using tools like the Anchor Engine and Docker Compose, you can ensure that your containers are secure and free from vulnerabilities. Regularly scanning and securing your containers helps protect your applications from potential threats.

### Practice Labs

For hands-on practice, consider the following labs:

- **Kubernetes Goat**: A Kubernetes-based security training platform.
- **OWASP WrongSecrets**: A series of challenges to learn about web security.
- **kube-hunter**: A tool for finding security misconfigurations in Kubernetes clusters.

These labs provide practical experience in container security and help reinforce the concepts covered in this chapter.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/01-Automating Container Security Testing/Demo Performing Container Security Testing on the Command Line/00-Overview|Overview]] | [[02-Introduction to Container Security Testing|Introduction to Container Security Testing]]
