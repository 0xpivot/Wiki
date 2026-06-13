---
tags: [aws, ecs, eks, containers, kubernetes, privesc]
difficulty: intermediate
module: "37 - Cloud Infrastructure"
topic: "37.05 AWS ECS EKS"
---

# AWS ECS & EKS — Container Privilege Escalation

## 1. Introduction to AWS Container Services
AWS offers two primary container orchestration services:
- **Elastic Container Service (ECS)**: AWS's proprietary, highly integrated orchestration service.
- **Elastic Kubernetes Service (EKS)**: AWS's managed Kubernetes service.

Both services can run on underlying EC2 instances (where the customer manages the host nodes) or on AWS Fargate (serverless compute for containers, where AWS manages the underlying infrastructure).

The security of containerized environments relies on isolating the container from the host and correctly managing IAM privileges assigned to the container (Pods/Tasks) versus the host (EC2 Nodes).

## 2. ASCII Architecture Diagram: ECS/EKS Container Breakout

```text
    [ External Attacker ]
             |
             |  1. RCE via Web App Vulnerability
             v
   +---------------------------------------------------+
   |  [ Compromised Pod / ECS Task ]                   |
   |                                                   |
   |  2. Container is running in --privileged mode     |
   |     or has sensitive hostPath mounts.             |
   |                                                   |
   |  3. Attacker mounts host filesystem:              |
   |     mount /dev/xvda1 /mnt/host                    |
   |                                                   |
   +-------------------------+-------------------------+
                             |
                             |  4. Attacker breaks out to Host Node
                             v
   +---------------------------------------------------+
   |  [ Underlying EC2 Node (EKS Worker / ECS Host) ]  |
   |                                                   |
   |  5. Query Node's EC2 IMDS                         |
   |     curl http://169.254.169.254/...               |
   |                                                   |
   |  6. Steal Node IAM Role (NodeInstanceRole)        |
   +---------------------------------------------------+
                             |
                             |  7. Node Role has privileges to
                             |     read Secrets or modify cluster
                             v
              [ Cluster / AWS Account Compromise ]
```

## 3. Container Escapes & Host Compromise
The primary goal of an attacker who has achieved RCE inside a container is to escape the container and compromise the underlying host.

### 3.1. Privileged Containers
If a container is launched with the `--privileged` flag, it possesses almost all capabilities of the host machine.
- **Exploitation**: The attacker can list host devices (`ls /dev`) and mount the host's root filesystem.
  ```bash
  mkdir -p /mnt/host
  mount /dev/nvme0n1p1 /mnt/host
  chroot /mnt/host
  ```
- **Impact**: Full control over the EC2 node. The attacker can access other containers running on the same node, extract secrets from memory, or steal the host's IAM credentials.

### 3.2. Writable HostPath Mounts
In Kubernetes (EKS) or ECS, if a container mounts a sensitive host directory (like `/`, `/etc`, or `/var/run/docker.sock`) with write permissions, an escape is trivial.
- **Docker Socket Escape**: If `/var/run/docker.sock` is mounted, the attacker can install the Docker client and spawn a new, fully privileged container that mounts the host root.
  ```bash
  docker run -it -v /:/host/ ubuntu chroot /host/ bash
  ```

## 4. Identity & Access Management in Containers
The most critical cloud-specific vulnerability in ECS/EKS is the mismanagement of IAM roles.

### 4.1. The EKS / ECS Metadata SSRF Vector
By default, containers running on an EC2-backed EKS or ECS cluster can reach the EC2 Instance Metadata Service (IMDS) at `169.254.169.254`.
- **The Misconfiguration**: If IAM Roles for Service Accounts (IRSA) in EKS or Task Roles in ECS are not strictly enforced, a compromised container can query the IMDS and extract the IAM credentials of the **underlying EC2 host node**.
- **The Impact**: The EC2 Node Role (e.g., `eks-node-role`) often has broad permissions, including pulling images from ECR, modifying networking, or even joining the cluster as a node (which can lead to full Kubernetes cluster compromise via `kubelet` API manipulation).

### 4.2. Exploiting EKS IRSA (IAM Roles for Service Accounts)
IRSA allows assigning AWS IAM roles directly to Kubernetes Service Accounts.
- When IRSA is configured, the pod receives environment variables: `AWS_ROLE_ARN` and `AWS_WEB_IDENTITY_TOKEN_FILE`.
- An attacker with RCE in the pod can read the token (usually mounted at `/var/run/secrets/eks.amazonaws.com/serviceaccount/token`) and use it to assume the AWS IAM role via the STS `AssumeRoleWithWebIdentity` API.
  ```bash
  aws sts assume-role-with-web-identity \
      --role-arn $AWS_ROLE_ARN \
      --role-session-name attacker-session \
      --web-identity-token file://$AWS_WEB_IDENTITY_TOKEN_FILE
  ```
- If the assigned IAM role is overly permissive (e.g., allows modifying other AWS resources), the attacker pivots from Kubernetes back into the AWS API.

## 5. Exploiting EKS-Specific Mechanisms

### 5.1. Kubeconfig Extraction
If an attacker compromises an admin's local machine or an EC2 instance used as a jump box, they can steal the `~/.kube/config` file. In EKS, authentication to the cluster is managed by `aws-iam-authenticator`. As long as the attacker has the AWS credentials of the IAM entity mapped in the `aws-auth` ConfigMap, they can access the cluster.

### 5.2. aws-auth ConfigMap Manipulation
In EKS, the `aws-auth` ConfigMap located in the `kube-system` namespace maps AWS IAM users/roles to Kubernetes RBAC groups (like `system:masters`).
- If an attacker gains permissions to edit this ConfigMap (e.g., via a compromised pod with cluster-admin rights), they can add their own external AWS IAM user to the `system:masters` group, creating a persistent backdoor into the cluster.

## 6. Fargate Security Implications
AWS Fargate abstracts the underlying EC2 node.
- **Security Benefits**: You cannot escape to the host (there is no accessible host). The EC2 IMDS is not available; Fargate tasks use a specific endpoint for metadata that only returns the Task Role credentials.
- **Remaining Risks**: You still have to secure the Task IAM Role. If the Fargate task role has overly permissive AWS IAM permissions, the attacker can still pivot to the cloud environment.

## 7. Remediation and Best Practices
1. **Use Fargate**: Where possible, use Fargate to eliminate host-level container escapes and IMDS hijacking.
2. **Block IMDS Access**: If using EC2-backed clusters, use `iptables` or Network Policies (like Calico in EKS) to block pod access to `169.254.169.254`. Force the use of IRSA or ECS Task Roles.
3. **Pod Security Standards (PSS)**: In EKS, enforce the "Restricted" Pod Security Standard to prevent privileged containers, hostPath mounts, and host networking.
4. **Least Privilege for IRSA/Task Roles**: Ensure the IAM role assigned to a specific pod only has the exact permissions that application requires.
5. **Audit aws-auth**: Regularly monitor the `aws-auth` ConfigMap in EKS for unauthorized modifications.

## 8. Conclusion
Compromising a container in AWS is rarely the end goal; it is a stepping stone. The intersection of container orchestration mechanisms (Kubernetes/Docker) and cloud identity (AWS IAM) creates complex attack surfaces where a misconfiguration in one layer can lead to the complete compromise of the other.

---

## Chaining Opportunities
- **[[03 - AWS EC2 — Metadata Service (IMDS) Exploitation]]**: Container escapes often lead directly to querying the host's IMDS to escalate from Kubernetes/Docker context to AWS IAM context.
- **[[01 - AWS IAM — Roles, Policies, Misconfigurations]]**: Stolen IRSA web identity tokens are used to assume IAM roles, leading to standard IAM privesc techniques.
- **[[06 - AWS SecretsManager Parameter Store — Misconfigured Access]]**: Compromised container roles frequently have legitimate access to retrieve database strings or API keys from Secrets Manager.

## Related Notes
- [[04 - AWS Lambda — Privilege Escalation, Event Injection]]
- [[07 - AWS CloudTrail — Disabling Logging]]
