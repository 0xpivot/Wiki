---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Introduction to Continuous Delivery Pipelines

Continuous Delivery (CD) pipelines are a critical component of modern DevSecOps practices. They automate the process of building, testing, and deploying applications, ensuring that code changes can be safely and efficiently released to production. One key aspect of CD pipelines is the ability to build application images, which are often done using Docker. In this section, we will explore how to build Docker images on a self-managed GitLab runner, leveraging Docker caching to optimize the build process.

### Why Use a Self-Managed Runner?

Using a self-managed GitLab runner allows for greater control over the environment where your builds run. This is particularly useful when dealing with sensitive data or proprietary software that cannot be hosted on shared infrastructure. Additionally, self-managed runners can be configured to meet specific performance requirements, ensuring that builds are executed quickly and reliably.

### Setting Up the Environment

To build Docker images on a self-managed GitLab runner, we need to ensure that the necessary tools are installed on the runner. Specifically, we need Docker and AWS CLI (Amazon Web Services Command Line Interface).

#### Installing Docker on Ubuntu

Let's start by installing Docker on an Ubuntu-based system. The following steps outline the process:

```bash
# Update package index
sudo apt-get update

# Install required packages
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

# Add Docker’s official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Set up the stable repository
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

# Update package index again
sudo apt-get update

# Install Docker CE
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
```

#### Installing AWS CLI

Next, we need to install the AWS CLI. This can be done using pip, Python's package manager:

```bash
# Install pip if not already installed
sudo apt-get install python3-pip

# Install AWS CLI
pip3 install awscli --upgrade --user
```

### Configuring User Permissions

Once Docker is installed, we need to ensure that the user running the build jobs has the necessary permissions to execute Docker commands. By default, Docker requires root privileges to run. To avoid using `sudo` every time, we can add the user to the `docker` group.

```bash
# Add the current user to the docker group
sudo usermod -aG docker $USER

# Log out and log back in for the group membership to take effect
```

### Understanding Docker Caching

Docker caching is a mechanism that speeds up the build process by reusing previously built layers. Each line in a Dockerfile corresponds to a layer. If a layer has not changed since the last build, Docker can reuse the cached version of that layer, significantly reducing the build time.

#### Dockerfile Example

Consider the following Dockerfile:

```Dockerfile
FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    curl \
    wget

COPY . /app

WORKDIR /app

RUN make

CMD ["./myapp"]
```

In this Dockerfile, the `RUN apt-get update && apt-get install -y curl wget` command creates a layer that installs `curl` and `wget`. If these dependencies do not change between builds, Docker can reuse the cached layer, saving time.

### Building Docker Images on the Self-Managed Runner

Now that we have set up the environment, we can proceed to build Docker images on the self-managed GitLab runner. Here is an example `.gitlab-ci.yml` file that defines the build job:

```yaml
stages:
  - build

build_image:
  stage: build
  script:
    - docker build -t myapp .
  only:
    - master
```

This configuration specifies that the `build_image` job should run during the `build` stage. The `script` section contains the command to build the Docker image.

### Full HTTP Request and Response Example

When interacting with Docker via the API, we might send HTTP requests to manage images and containers. Here is an example of a full HTTP request and response:

```http
POST /v1.41/images/create?fromImage=myapp&tag=latest HTTP/1.1
Host: localhost:2375
Content-Type: application/json

HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "Downloaded newer image for myapp:latest",
  "stream": "..."
}
```

### Common Pitfalls and How to Prevent Them

#### Pitfall: Missing Dependencies

One common issue is missing dependencies. Ensure that all required tools (Docker, AWS CLI) are installed and configured correctly on the runner.

**Prevention:**
- Verify the installation of Docker and AWS CLI by running simple commands (`docker --version`, `aws --version`).
- Check that the user has been added to the `docker` group and has the necessary permissions.

#### Pitfall: Incorrect User Permissions

Another pitfall is incorrect user permissions. If the user does not have the necessary permissions to execute Docker commands, the build will fail.

**Prevention:**
- Ensure that the user is added to the `docker` group.
- Log out and log back in for the group membership to take effect.

### Secure Coding Practices

#### Vulnerable Code Example

Consider a scenario where the Dockerfile includes a command that installs unnecessary packages, potentially introducing vulnerabilities:

```Dockerfile
FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    vim

COPY . /app

WORKDIR /app

RUN make

CMD ["./myapp"]
```

#### Secure Code Example

To mitigate this, we can remove unnecessary packages and ensure that only required dependencies are installed:

```Dockerfile
FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    curl \
    wget

COPY . /app

WORKDIR /app

RUN make

CMD ["./myapp"]
```

### Real-World Examples and Recent Breaches

#### Example: Docker Hub Breach

In 2021, Docker Hub experienced a breach where unauthorized access was gained to some repositories. This highlights the importance of securing your Docker images and ensuring that only trusted sources are used.

**Prevention:**
- Use Docker Content Trust to verify the integrity of images.
- Regularly audit and update your Docker images to patch known vulnerabilities.

### Conclusion

Building Docker images on a self-managed GitLab runner is a powerful way to control the build environment and leverage Docker caching for faster builds. By ensuring that the necessary tools are installed and configured correctly, and by following secure coding practices, you can create robust and efficient CD pipelines.

### Practice Labs

For hands-on practice, consider the following labs:
- **PortSwigger Web Security Academy**: Focuses on web application security but also covers Docker and CI/CD pipelines.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **GitLab CI/CD Documentation**: Official GitLab documentation provides detailed guides and examples for setting up CI/CD pipelines.

By combining theoretical knowledge with practical experience, you can master the art of building and managing CD pipelines effectively.

---
<!-- nav -->
[[05-Introduction to Continuous Delivery Pipelines Part 4|Introduction to Continuous Delivery Pipelines Part 4]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Build Application Images on Self Managed Runner Leverage Docker Caching/00-Overview|Overview]] | [[07-Build Application Images on Self-Managed Runner Leveraging Docker Caching|Build Application Images on Self-Managed Runner Leveraging Docker Caching]]
