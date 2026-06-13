---
tags: [docker, secrets, forensics, container-security, layers]
difficulty: intermediate
module: "38 - Container and Kubernetes Security"
topic: "38.09 Docker Secrets"
---

# Secrets in Docker Images

## Introduction
One of the most pervasive and dangerous vulnerabilities in containerized infrastructure is the inadvertent inclusion of sensitive data—API keys, database credentials, private SSH keys, and TLS certificates—directly within Docker images. 

Because Docker images are designed to be immutable and easily distributable, a secret baked into an image is inherently compromised. If the image is pushed to a public registry (like Docker Hub), the secret is exposed to the world. If pushed to an internal registry, it becomes accessible to anyone within the organization who can pull the image, violating the principle of least privilege. Understanding how Docker manages filesystems is crucial to understanding why secrets persist and how to extract them.

## The Architecture of Docker Layers

To comprehend secret leakage, one must understand the Union File System (UnionFS), specifically the OverlayFS implementation used heavily by Docker. 

A Docker image is not a single monolithic file. It is composed of a series of read-only "layers." Each instruction in a Dockerfile that modifies the filesystem (like `RUN`, `COPY`, or `ADD`) creates a brand new layer that sits on top of the previous ones.

```text
+-------------------------------------------------------------------+
|                     Container Runtime (R/W)                       |
|   (The ephemeral layer created when `docker run` is executed)     |
+-------------------------------------------------------------------+
|   Layer 4 (Read-Only): RUN rm /app/config/database.yml            | <--- DELETION LAYER
+-------------------------------------------------------------------+
|   Layer 3 (Read-Only): COPY . /app                                | <--- SECRET ADDED HERE
+-------------------------------------------------------------------+
|   Layer 2 (Read-Only): RUN apt-get install python3                |
+-------------------------------------------------------------------+
|   Layer 1 (Read-Only): FROM ubuntu:20.04                          |
+-------------------------------------------------------------------+
```

### The "Deletion" Myth
A common, fatal misconception among developers is that deleting a file in a subsequent Dockerfile step removes it from the image. 

Consider this vulnerable Dockerfile snippet:
```dockerfile
COPY id_rsa /root/.ssh/id_rsa
RUN ssh -T git@github.com && \
    git clone git@github.com:company/private-repo.git
RUN rm /root/.ssh/id_rsa  # <--- THIS DOES NOT FIX THE VULNERABILITY
```

**Why this fails:**
1.  The `COPY` instruction creates Layer A, which contains the `id_rsa` file.
2.  The `RUN rm ...` instruction creates Layer B on top of Layer A. 
3.  OverlayFS handles the deletion by creating a "whiteout" file in Layer B. The whiteout file tells the final unioned filesystem *not* to display `id_rsa`.
4.  However, Layer A is immutable and permanently embedded in the image history. Anyone who downloads the image downloads all layers, including Layer A. The secret is simply hidden from the final view, not erased from the storage block.

## Extraction Techniques: How Attackers Find Secrets

Attackers leverage the layered architecture to meticulously dissect container images and extract hidden data.

### 1. `docker history` and `docker inspect`
The first step in reconnaissance is analyzing the image metadata.
*   `docker inspect <image>`: Reveals environment variables (`ENV`), entrypoints, and labels. Hardcoded secrets in the `ENV` instruction are immediately visible in cleartext.
*   `docker history --no-trunc <image>`: Displays the exact command used to create every single layer. This often reveals secrets passed inline via command line arguments during the build process (e.g., `RUN curl -u user:SuperSecretPassword http://api.com/data`).

### 2. Exporting and Dissecting the Tarball
The most reliable method for extracting secrets hidden in lower layers is to export the image to an archive and analyze its contents.

```bash
# 1. Save the image as a tar archive
docker save vulnerable-image:latest -o image.tar

# 2. Extract the archive
mkdir image-data && tar -xf image.tar -C image-data/
cd image-data
```

Inside the extracted directory, there are multiple subdirectories, each named with a SHA256 hash. These represent the individual layers. Each directory contains a `layer.tar` file. 
An attacker will simply iterate through every `layer.tar`, unpack them, and run tools like `grep`, `trufflehog`, or `gitleaks` to scan the raw file contents across the entire history of the image.

```bash
# Example: Searching all layers for an AWS Access Key
for layer in */layer.tar; do
    tar -xf "$layer" -C /tmp/layer-content/
    grep -R "AKIA[0-9A-Z]{16}" /tmp/layer-content/
    rm -rf /tmp/layer-content/*
done
```

### 3. Using Specialized Tools (`dive`)
`dive` is an exceptional open-source tool for exploring a Docker image, layer contents, and discovering ways to shrink the size of your Docker/OCI image. Attackers use it defensively. It provides a visual UI in the terminal, allowing the user to navigate through each layer and see exactly which files were added, modified, or deleted (whiteouts). Finding a whiteouted `.env` file in `dive` is a massive indicator of compromise.

## Forensic Indicators and Detection

Security operations must proactively scan images before they are pushed to production registries.
1.  **Secret Scanners**: Integrate tools like **TruffleHog**, **Gitleaks**, or **Checkov** into the CI/CD pipeline. These tools use regular expressions and entropy analysis to identify high-probability secrets (AWS keys, Slack tokens, SSH private keys) within the source code and the generated image layers.
2.  **Registry Scanning**: Modern container registries (like AWS ECR, Harbor, Docker Hub Pro) offer built-in image scanning. Ensure these features are enabled and configured to block deployments if critical secrets are detected.

## Secure Secret Management Strategies

To prevent secret leakage, developers must adopt secure build practices.

### 1. Multi-Stage Builds (The Clean Slate)
If a secret is required *only* during the build process (e.g., an SSH key to clone a private repo, or a token to download a proprietary package), use multi-stage builds. 
The secret is copied into the `builder` stage, used, and then discarded. The final production image is built FROM a clean base, and only the compiled artifacts are copied over. The intermediate builder layer (containing the secret) is not distributed with the final image.

### 2. Docker BuildKit Secrets
Modern Docker (using BuildKit) introduces a dedicated mechanism for handling build-time secrets securely without ever leaving a trace in the image layers.

```dockerfile
# syntax=docker/dockerfile:1.2
FROM ubuntu
# The secret is mounted ephemerally and is NEVER written to a layer
RUN --mount=type=secret,id=mysecret,dst=/run/secrets/mysecret \
    cat /run/secrets/mysecret > /tmp/proof && \
    curl -H "Authorization: Bearer $(cat /run/secrets/mysecret)" ...
```
Build command: `docker build --secret id=mysecret,src=secret.txt .`

### 3. Runtime Secret Injection
If the application requires the secret to operate (e.g., a database connection string), it must **never** be in the image. It must be provided at runtime.
*   **Environment Variables**: Pass them during deployment (`docker run -e DB_PASS=...`).
*   **Orchestrator Secrets**: Use Kubernetes Secrets, Docker Swarm Secrets, or HashiCorp Vault to securely inject credentials into the running container's environment or filesystem (via tmpfs memory mounts) at startup.

## Chaining Opportunities
*   [[08 - Dockerfile Security Misconfigurations]]: Improper use of the `COPY` command or failure to utilize `.dockerignore` files is the primary vector for introducing secrets into the build context.
*   [[13 - Bypassing Kubernetes Pod Security Policies]]: Extracted secrets often include cloud provider credentials or Kubernetes ServiceAccount tokens, allowing the attacker to pivot from local container analysis to cluster-wide compromise.
*   [[06 - Application RCE in Containers]]: If an attacker achieves RCE, they can read environment variables natively, bypassing the need to perform layer forensics.

## Related Notes
*   [[05 - Multi-Stage Builds and Distroless Images]]
*   [[02 - Image Registries and Supply Chain Security]]
*   [[14 - HashiCorp Vault for K8s Secret Management]]
