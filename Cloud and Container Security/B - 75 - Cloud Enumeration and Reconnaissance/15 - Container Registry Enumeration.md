---
tags: [cloud, basics, enumeration, vapt]
difficulty: beginner
module: "75 - Cloud Enumeration and Reconnaissance"
topic: "75.15 Container Registry Enumeration"
---

# 75.15 Container Registry Enumeration

## Introduction to Container Registries

As organizations rapidly transition from monolithic architectures to microservices, the adoption of containerization technologies like Docker and Kubernetes has become ubiquitous. Containers package application code, dependencies, runtimes, and system tools into a single, immutable artifact known as a container image. 

These container images are stored, managed, and distributed via **Container Registries**. A registry acts as a centralized repository system. Major cloud providers offer native, fully managed registry services such as Amazon Elastic Container Registry (ECR), Google Artifact Registry (GAR), and Azure Container Registry (ACR). Additionally, organizations frequently self-host registries using Docker Hub, Harbor, or GitLab Container Registry.

From a penetration testing and cloud enumeration perspective, container registries are high-value targets. If an attacker can enumerate and access a private registry, they can download proprietary application images. These images often contain hardcoded secrets, database credentials, API keys, intellectual property, or vulnerable software libraries. Furthermore, registry compromise can lead to devastating supply chain attacks, where an attacker pushes a malicious image to the registry, which is then automatically deployed to production clusters by CI/CD pipelines.

## The Registry API and Enumeration Mechanics

Most modern container registries implement the Open Container Initiative (OCI) Distribution Specification or the legacy Docker Registry HTTP API V2. This standardization means that enumeration techniques remain largely consistent regardless of the underlying hosting platform.

The core of registry enumeration involves interacting with the HTTP API to list available repositories (image names) and their associated tags (versions).

### Standard API Endpoints

1. **Version Check:**
   `GET /v2/`
   A simple check to verify if the endpoint is a V2 Docker Registry. It usually returns a `200 OK` or requests authentication.
   
2. **Catalog Enumeration:**
   `GET /v2/_catalog`
   This is the most critical endpoint for reconnaissance. If successful, it returns a JSON list of all repositories (images) hosted in the registry.

3. **Tag Enumeration:**
   `GET /v2/<repository_name>/tags/list`
   Once a repository is identified, this endpoint lists all available tags (e.g., `latest`, `v1.0.4`, `dev-build`).

4. **Manifest Retrieval:**
   `GET /v2/<repository_name>/manifests/<tag>`
   Returns the image manifest, detailing the individual filesystem layers that make up the image.

### Authentication Flaws

Registries are intended to be secure, but misconfigurations are common:
- **Anonymous Access:** Administrators may accidentally configure the registry to allow anonymous pulling (reading) of images, intending to simplify internal CI/CD workflows but exposing the registry to the internet.
- **Weak Credentials:** Self-hosted registries often suffer from default credentials (e.g., `admin:admin`) or highly predictable passwords.
- **Leaked Tokens:** CI/CD pipelines require tokens to authenticate with the registry. These tokens are frequently leaked in GitHub repositories or CI/CD logs.

## Enumeration Methodologies and Tools

When an exposed or authenticated registry endpoint is identified, testers utilize specialized tools to extract data efficiently.

### Manual API Interaction with cURL

Testing a self-hosted registry at `registry.example.com` for anonymous catalog access:

```bash
curl -s -X GET https://registry.example.com/v2/_catalog
```

If the response is:
```json
{
  "repositories": [
    "frontend-app",
    "payment-gateway",
    "backend-api-dev"
  ]
}
```
The registry is vulnerable to anonymous enumeration. The tester would then enumerate tags for a specific target:

```bash
curl -s -X GET https://registry.example.com/v2/payment-gateway/tags/list
```

### Automated Tooling: Crane and Dive

While `curl` is excellent for verification, pulling and analyzing multi-gigabyte images requires robust tooling.

**Crane:** 
Developed by Google, `crane` is a tool for interacting with remote images and registries without requiring a local Docker daemon. It is incredibly fast for enumeration and extraction.

Listing repositories:
```bash
crane catalog registry.example.com
```

Exporting the entire filesystem of a remote image to a local tarball for offline analysis:
```bash
crane export registry.example.com/payment-gateway:latest payment-gateway.tar
```

**Dive:**
Once an image is downloaded, `dive` is an exceptional tool for exploring the image's filesystem layers. It allows testers to see exactly what files were added, modified, or removed in each step of the `Dockerfile`. This is critical for finding secrets that were added in one layer and deleted in a subsequent layer; the secret still exists in the image history!

## Visualizing Registry Compromise

```text
+-------------------------------------------------------------------------------------------------+
|                              Container Registry Attack Architecture                             |
+-------------------------------------------------------------------------------------------------+
|                                                                                                 |
|   [ CI/CD Pipeline ]                       [ Cloud Provider IAM ]                               |
|          | (Builds Image)                            | (Misconfigured Policy)                   |
|          v                                           v                                          |
|  +----------------------+                 +-------------------------+                           |
|  | Container Registry   | <== Pull ==     | Attacker Recon Node     |                           |
|  | (ECR / ACR / Harbor) |                 |                         |                           |
|  |                      |                 | 1. Enumerates /_catalog |                           |
|  | - payment-gateway:v1 |                 | 2. Identifies Tags      |                           |
|  | - auth-service:dev   |                 | 3. Uses 'crane' to pull |                           |
|  | - internal-tools:v2  |                 |    filesystem tarball   |                           |
|  +----------------------+                 +-------------------------+                           |
|          |                                           |                                          |
|          | (Deploys Image)                           | 4. Local Deep Dive Analysis              |
|          v                                           v                                          |
|  +----------------------+                 +-------------------------+                           |
|  | Kubernetes Cluster   |                 | Secret Extraction Phase |                           |
|  | (Production Env)     |                 |                         |                           |
|  |                      |                 | - Extracts .env files   |                           |
|  | Running Pods         |                 | - Finds DB Passwords    |                           |
|  |                      |                 | - Finds AWS IAM Keys    |                           |
|  +----------------------+                 +-------------------------+                           |
|                                                      |                                          |
|                                                      | 5. Exploitation                          |
|                                                      v                                          |
|                                           Attacker uses extracted keys                          |
|                                           to compromise production DB                           |
+-------------------------------------------------------------------------------------------------+
```

## Post-Enumeration: Image Analysis and Secret Hunting

Extracting the image is only half the battle. The core objective is finding vulnerabilities or secrets within the static image.

### Static Analysis and Vulnerability Scanning
Tools like **Trivy** or **Clair** are used to scan the pulled image for known CVEs in installed OS packages (like an outdated version of OpenSSL) or application dependencies (like a vulnerable Log4j library).

```bash
trivy image registry.example.com/payment-gateway:latest
```

### Secret Extraction
Images are notorious for housing secrets. Developers often build images using commands like `COPY . .`, inadvertently copying local `.env`, `.git` directories, or `~/.aws/credentials` into the final container.

Testers use tools like **TruffleHog** or custom regex scripts against the extracted filesystem tarball to hunt for these high-value artifacts. If a database password or a cloud API key is discovered within the container image, the attacker can pivot from simple registry enumeration to total infrastructure compromise, bypassing external firewalls entirely.

## Defensive Strategies and Best Practices

Securing container registries requires strict access control and integration into the CI/CD pipeline.

1. **Authentication and RBAC:** Never allow anonymous access to a registry. Implement robust Role-Based Access Control (RBAC) where CI/CD pipelines only have `Push` access, and deployment nodes (like Kubernetes worker nodes) only have `Pull` access.
2. **Network Scoping:** Private registries should not be exposed to the internet. They should be restricted to internal VPC endpoints or require VPN access for developers.
3. **Automated Scanning:** Integrate tools like Trivy into the CI/CD pipeline. Images must be scanned for secrets and severe vulnerabilities *before* they are allowed to be pushed to the registry.
4. **Multi-Stage Builds:** Developers must utilize multi-stage Docker builds. This ensures that build tools, temporary credentials, and source code are left behind in the build stage, and only the compiled binary is moved to the final production image layer.

## Chaining Opportunities
- Authentication tokens required to access secure registries are frequently discovered via reconnaissance techniques in [[11 - GitHub Recon for Leaked Cloud Keys]].
- The network location of internal registries might be mapped out during the firewall analysis discussed in [[14 - Identifying Misconfigured Cloud Networking Security Groups]].
- Exploiting a vulnerability found inside a container image naturally leads to the post-exploitation tactics of container breakout and cluster compromise covered in Module 76.

## Related Notes
- [[09 - Kubernetes Architecture and Security Boundaries]]
- [[22 - Source Code Analysis and Static Application Security Testing]]
- [[76 - Container Escape Methodologies]]
