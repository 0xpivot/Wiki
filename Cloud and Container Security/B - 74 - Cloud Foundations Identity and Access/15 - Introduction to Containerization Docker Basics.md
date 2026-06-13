---
tags: [cloud, basics, foundations, vapt]
difficulty: beginner
module: "74 - Cloud Foundations Identity and Access"
topic: "74.15 Introduction to Containerization Docker Basics"
---

# Introduction to Containerization: Docker Basics

## 1. Introduction and Core Concepts

Containerization has fundamentally altered the landscape of software development, deployment, and cloud security. Before the advent of containers, applications were typically deployed on bare-metal servers or Virtual Machines (VMs). VMs, while offering strong isolation, require a full, heavy operating system (Guest OS) for each application, leading to significant performance overhead, wasted resources, and slow boot times.

Containerization solves this by virtualizing at the operating system level, rather than the hardware level. Containers share the host system's kernel but encapsulate the application, its specific dependencies, libraries, and configuration files into a single, lightweight, executable package. This ensures the application runs consistently across entirely different environments, from a developer's local laptop to a massive production Kubernetes cluster in the cloud.

Docker is the prominent platform that popularized and standardized containerization. Understanding Docker is absolutely foundational for modern cloud security and VAPT, as almost all modern microservices and cloud-native applications are heavily containerized. The overall security posture of a modern cloud environment is directly reliant on the security posture of the containers running within it.

### 1.1 The Container Paradigm vs. Virtual Machines

The critical architectural difference lies in the treatment of the kernel.
*   **Virtual Machines:** A hypervisor runs on the host machine and creates virtual hardware. Each VM runs its own complete Guest OS on top of this virtual hardware. This provides strong isolation but is resource-intensive.
*   **Containers:** A container engine (like Docker Engine) runs directly on the host OS. Containers share the host OS kernel and use specific kernel features like **Namespaces** (for isolation of processes, networking, mounts) and **Control Groups (cgroups)** (for resource limiting). Containers are incredibly lightweight, start in milliseconds, and consume minimal background resources.

## 2. In-Depth Architecture: How Docker Works

Understanding the core components of Docker is essential for identifying misconfigurations and exploiting vulnerabilities during an assessment.

### 2.1 The Docker Daemon (dockerd)
The core component of the Docker architecture. It is a persistent background process that manages Docker images, containers, networks, and storage volumes. It listens for Docker API requests and processes them. By default, it runs as `root`, which is a massive security consideration. If compromised, the host is compromised.

### 2.2 Docker Client
The primary user interface (e.g., the `docker` CLI command). It communicates with the Docker Daemon via a REST API, typically over local UNIX sockets (`/var/run/docker.sock`) or occasionally over a network interface.

### 2.3 Images
A Docker image is a read-only template containing the exact instructions for creating a Docker container. It is built using a `Dockerfile`, which is a script containing a series of commands (e.g., `FROM ubuntu`, `RUN apt-get update`, `COPY . /app`). Images are composed of layers; each instruction in the Dockerfile creates a new, immutable layer. This layered architecture is highly efficient but can hide vulnerabilities if base layers are outdated.

### 2.4 Containers
A container is a runnable instance of an image. When you start a container, a read-write layer is added on top of the read-only image layers. Any changes made during the container's execution (creating files, modifying data) are written to this thin read-write layer. If the container is deleted, this layer—and all data within it—is permanently lost.

### 2.5 Registries
A Docker registry stores and distributes Docker images. Docker Hub is the default public registry, but organizations typically use private, authenticated registries (like AWS ECR, Azure ACR, or Harbor) to store proprietary images securely.

## 3. Visualizing Container Architecture vs. VM

```text
  +--------------------------------+       +--------------------------------+
  |       VIRTUAL MACHINES         |       |         CONTAINERS             |
  +--------------------------------+       +--------------------------------+
  | +---------+      +---------+   |       | +---------+      +---------+   |
  | |  App A  |      |  App B  |   |       | |  App A  |      |  App B  |   |
  | +---------+      +---------+   |       | +---------+      +---------+   |
  | | Bins/Libs|     | Bins/Libs|  |       | | Bins/Libs|     | Bins/Libs|  |
  | +---------+      +---------+   |       | +---------+      +---------+   |
  | | Guest OS|      | Guest OS|   |       | |         |      |         |   |
  | +---------+      +---------+   |       | +---------+      +---------+   |
  |                                |       |                                |
  | +----------------------------+ |       | +----------------------------+ |
  | |        HYPERVISOR          | |       | |       DOCKER ENGINE        | |
  | +----------------------------+ |       | +----------------------------+ |
  |                                |       |                                |
  | +----------------------------+ |       | +----------------------------+ |
  | |    HOST OPERATING SYSTEM   | |       | |    HOST OPERATING SYSTEM   | |
  | +----------------------------+ |       | +----------------------------+ |
  |                                |       |                                |
  | +----------------------------+ |       | +----------------------------+ |
  | |       INFRASTRUCTURE       | |       | |       INFRASTRUCTURE       | |
  | +----------------------------+ |       | +----------------------------+ |
  +--------------------------------+       +--------------------------------+
```

## 4. Threat Landscape and Vulnerabilities

Because containers share the host kernel, the isolation is logical, not physical. This creates highly unique security challenges.

### 4.1 Vulnerable Base Images
Developers frequently build containers `FROM` base images found on public registries without verifying their security posture. If a base image (like an outdated Ubuntu or Alpine Linux image) contains a known vulnerability (CVE), every single container built from it automatically inherits that vulnerability.

### 4.2 Hardcoded Secrets in Images
A common and critical mistake during development is copying sensitive files (API keys, SSH keys, database credentials) into the image during the build process using the `COPY` or `ADD` commands in the Dockerfile. Because images are built in layers, even if a secret is explicitly deleted in a subsequent layer, it remains accessible in the history of the image.

### 4.3 Privileged Containers
A container started with the `--privileged` flag bypasses almost all Docker security features. It grants the container access to all host devices, disables cgroups, and disables AppArmor/SELinux profiles. A compromised privileged container allows an attacker to trivially break out of the container and achieve full root access on the underlying host OS.

### 4.4 Exposed Docker Daemon Socket
The Docker daemon typically listens on a local UNIX socket (`/var/run/docker.sock`). Sometimes, administrators mistakenly expose this socket over a TCP port (e.g., 2375) to allow remote management, often without any authentication. If an attacker can access this socket, they have full control over the Docker daemon and, consequently, root access to the host. Furthermore, mounting the docker socket inside a container (`-v /var/run/docker.sock:/var/run/docker.sock`) allows the container itself to spawn new containers or manipulate existing ones, a massive security risk.

### 4.5 Container Breakouts
Container isolation relies heavily on kernel features (Namespaces, Capabilities, cgroups). If the kernel itself has a vulnerability, or if the container is misconfigured (e.g., granted excessive Linux capabilities like `CAP_SYS_ADMIN`), an attacker can exploit these flaws to "escape" the container boundaries and access the host file system or kernel.

## 5. Attack Vectors and VAPT Methodology

Testing containerized environments requires inspecting images, analyzing runtime configurations, and actively attempting to break isolation.

### 5.1 Image Analysis (Static Testing)
1.  **Vulnerability Scanning:** Use tools like Trivy, Clair, or Anchore to deeply scan Docker images for known CVEs in the base OS packages and application dependencies.
2.  **Secret Hunting:** Inspect the Docker image history (`docker history <image>`) and layers to uncover hardcoded secrets, certificates, or credentials. Tools like `trufflehog` or `git-secrets` can be adapted to scan image layers.
3.  **Dockerfile Review:** Manually analyze the `Dockerfile` for bad practices: running as root (`USER root`), using untrusted base images, or unnecessary installation of tools like `curl`, `netcat`, or `ssh`, which greatly aid attackers post-compromise.

### 5.2 Runtime Assessment (Dynamic Testing)
1.  **Daemon Security Check:** Check if the Docker daemon API is exposed externally without TLS authentication.
2.  **Configuration Auditing:** Use tools like `Docker Bench for Security` to automatically verify if the host and containers are configured according to CIS benchmarks.
3.  **Inspect Capabilities:** Examine running containers (`docker inspect <container_id>`) to see which Linux capabilities are granted. Look specifically for dangerous capabilities like `CAP_SYS_ADMIN`, `CAP_NET_ADMIN`, or `CAP_DAC_READ_SEARCH`. Check if the `--privileged` flag is in use.

### 5.3 Exploiting Container Breakouts
If an attacker gains code execution inside a container (e.g., via a web app vulnerability):
1.  **Reconnaissance:** Run tools like `linpeas` or `amicontained` inside the container to assess the environment. Check for mounted sensitive host directories or the presence of the Docker socket.
2.  **Socket Exploitation:** If `/var/run/docker.sock` is mounted, install the Docker CLI inside the container and use it to spawn a new, privileged container that mounts the host root file system (`/`). This provides immediate root access to the host.
3.  **Capability Exploitation:** If dangerous capabilities are present, attempt kernel exploits or manipulate host resources directly.

## 6. Defense and Mitigation Strategies

Securing Docker involves a multi-layered approach across the entire image build lifecycle and runtime environment.

### 6.1 Secure Image Building
*   **Use Minimal Base Images:** Use minimal images like Alpine Linux or Google's distroless images. A smaller image means a significantly smaller attack surface with fewer pre-installed utilities for attackers to leverage.
*   **Run as Non-Root:** Always create a dedicated, low-privileged user within the Dockerfile and use the `USER` directive to ensure the application process does not run as root inside the container.
*   **Image Scanning in CI/CD:** Integrate automated vulnerability scanning and secret scanning directly into the CI/CD pipeline. Fail the build automatically if critical vulnerabilities are detected.
*   **Do Not Hardcode Secrets:** Pass secrets to containers at runtime using environment variables or dedicated secret management tools (like Docker Secrets, HashiCorp Vault, or Kubernetes Secrets), rather than baking them into the immutable image.

### 6.2 Runtime Hardening
*   **Never Use --privileged:** Avoid privileged containers at all costs. If a container needs specific privileges, selectively grant them using the `--cap-add` flag, adding only what is absolutely necessary.
*   **Protect the Docker Socket:** Never expose the Docker daemon over an unauthenticated TCP port. Avoid mounting the Docker socket inside containers unless running a highly trusted administrative tool.
*   **Resource Limits:** Use cgroups to limit CPU and memory usage (`--cpus`, `--memory`). This prevents a single compromised container from launching a Denial of Service attack against the host by consuming all available resources.
*   **Seccomp and AppArmor/SELinux:** Enable default Docker security profiles (seccomp) to severely restrict the system calls a container can make. Use AppArmor or SELinux to enforce mandatory access control policies.

## 7. Chaining Opportunities

Container vulnerabilities are often the stepping stones to complete infrastructure compromise.

*   **RCE in Web App + Mounted Docker Socket = Host Takeover:** An attacker exploits a Remote Code Execution vulnerability in a Node.js application running inside a container. During reconnaissance, they discover that `/var/run/docker.sock` is mounted inside the container. They download the Docker client, connect to the socket, and launch a new container that mounts the host's `/etc` directory, allowing them to add a new root user to the host system.
*   **Exposed Docker API + Crypto Miner = Resource Hijacking:** An administrator mistakenly exposes the Docker daemon API on port 2375 to the internet without authentication. Automated scanners discover the open port. Attackers remotely instruct the daemon to pull a malicious image and launch hundreds of containers running cryptocurrency miners, consuming massive amounts of cloud compute resources.
*   **Hardcoded Cloud Keys in Image + Public Registry = Cloud Account Compromise:** A developer accidentally includes an AWS `credentials` file in a Docker image build context and pushes it to a public Docker Hub repository. Attackers continuously scrape public registries for secrets. They extract the AWS keys from the image layers and use them to compromise the entire AWS environment.

## 8. Related Notes
*   [[16 - Kubernetes Security Fundamentals]]
*   [[11 - Cloud Networking VPCs Subnets and Security Groups]]
*   [[02 - Identity and Access Management IAM Core Principles]]
*   [[05 - Cloud Configuration Auditing Tools]]
