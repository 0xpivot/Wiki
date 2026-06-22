---
course: DevSecOps
topic: Policy as Code
tags: [devsecops]
---

## Introduction to Policy as Code

Policy as Code is a practice where organizational policies are defined in machine-readable formats and enforced through automated systems. In the context of Kubernetes and cloud-native applications, Open Policy Agent (OPA) Gatekeeper is a popular tool that enables organizations to define, enforce, and audit compliance policies across their clusters. This chapter will delve into the installation and setup of OPA Gatekeeper within a Kubernetes cluster, providing a comprehensive understanding of the underlying concepts, practical steps, and security considerations.

### Background Theory

Before diving into the installation process, it's essential to understand the core principles behind Policy as Code and OPA Gatekeeper.

#### What is Policy as Code?

Policy as Code refers to the practice of defining organizational policies using code rather than relying on manual processes. These policies can cover a wide range of areas, including security, compliance, resource management, and more. By codifying policies, organizations can ensure consistency, automate enforcement, and maintain a clear audit trail.

#### What is Open Policy Agent (OPA)?

Open Policy Agent (OPA) is an open-source project that provides a general-purpose policy engine. OPA allows organizations to define, enforce, and audit policies across various systems and services. It supports a declarative policy language called Rego, which makes it easy to express complex policy logic.

#### What is OPA Gatekeeper?

OPA Gatekeeper is a Kubernetes admission controller that integrates OPA with Kubernetes. It enables organizations to define and enforce custom policies on Kubernetes resources. Gatekeeper uses Custom Resource Definitions (CRDs) to define policies and enforces them at the admission control level, ensuring that only compliant resources are admitted into the cluster.

### Prerequisites

Before installing OPA Gatekeeper, ensure that your environment meets the following prerequisites:

- A Kubernetes cluster (in this case, an Amazon EKS cluster).
- Access to the cluster with sufficient privileges to install and manage resources.
- Basic knowledge of Kubernetes concepts such as namespaces, pods, deployments, and CRDs.

### Setting Up the Environment

To begin, we need to set up our environment and prepare the cluster for Gatekeeper installation.

#### Creating a New Branch

First, we'll create a new branch in our Git repository to manage the changes related to Gatekeeper installation.

```bash
git checkout -b gatekeeper-install
```

Next, we'll add and commit our changes.

```bash
git add .
git commit -m "Add OPA Gatekeeper installation"
```

Finally, we'll push our local branch to the remote repository.

```bash
git push origin gatekeeper-install
```

This creates a new branch named `gatekeeper-install` and pushes the changes to the remote repository.

### Connecting to the EKS Cluster

To interact with the EKS cluster, we need to assume the appropriate IAM role and configure `kubectl`.

#### Assumptions and Role Configuration

Assuming we have an AWS account with the necessary permissions, we'll use the AWS CLI to assume the IAM role.

```bash
aws sts assume-role --role-arn arn:aws:iam::123456789012:role/community-admin --role-session-name kubectl-session
```

This command assumes the `community-admin` role and returns temporary credentials. We'll use these credentials to configure `kubectl`.

```bash
export AWS_ACCESS_KEY_ID=<access_key>
export AWS_SECRET_ACCESS_KEY=<secret_key>
export AWS_SESSION_TOKEN=<session_token>
```

Now, we can configure `kubectl` to connect to the EKS cluster.

```bash
aws eks update-kubeconfig --name <cluster_name> --region <region>
```

This command updates the `kubeconfig` file to include the necessary information to connect to the EKS cluster.

### Verifying the Cluster Setup

Once connected, we can verify the cluster setup by checking the available namespaces.

```bash
kubectl get namespaces
```

This command lists all the namespaces in the cluster. We should see the `open-policy-agent` namespace, which is where Gatekeeper will be installed.

### Installing OPA Gatekeeper

With the environment set up, we can proceed to install OPA Gatekeeper.

#### Deploying Gatekeeper

Gatekeeper can be installed using the Helm chart provided by the Gatekeeper project. First, we need to add the Gatekeeper Helm repository.

```bash
helm repo add open-policy-agent https://open-policy-agent.github.io/gatekeeper/charts
helm repo update
```

Next, we'll install Gatekeeper using the Helm chart.

```bash
helm install gatekeeper open-policy-agent/gatekeeper \
  --namespace open-policy-agent \
  --set gatekeeperManager.image.tag=v3.8.0 \
  --set webhookConfig.patchPolicy=true
```

This command installs Gatekeeper in the `open-policy-agent` namespace with the specified image tag and webhook configuration.

### Verifying the Installation

After installation, we can verify that Gatekeeper is running correctly by checking the deployed resources.

```bash
kubectl get all -n open-policy-agent
```

This command lists all the resources in the `open-policy-agent` namespace. We should see the Gatekeeper controller pods, the audit pod, and the webhook service.

### Understanding the Components

Let's break down the components of the Gatekeeper installation:

#### Gatekeeper Controller Pods

The Gatekeeper controller pods are responsible for enforcing the policies defined in the cluster. They run as a deployment with multiple replicas to ensure high availability.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gatekeeper-controller-manager
  namespace: open-policy-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gatekeeper-controller-manager
  template:
    metadata:
      labels:
        app: gatekeeper-controller-manager
    spec:
      containers:
      - name: manager
        image: gcr.io/open-policy-agent/gatekeeper:latest
        args:
        - --policy-dir=/etc/gatekeeper/policies
        - --webhook-port=9443
        volumeMounts:
        - name: policies
          mountPath: /etc/gatekeeper/policies
      volumes:
      - name: policies
        configMap:
          name: gatekeeper-policies
```

This deployment defines three replicas of the Gatekeeper controller pods, which run the `gatekeeper-manager` container. The container mounts the policies from a ConfigMap.

#### Gatekeeper Audit Pod

The Gatekeeper audit pod runs periodically to check the current state of the cluster against the defined policies. It helps in identifying any non-compliant resources.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: gatekeeper-audit
  namespace: open-policy-agent
spec:
  template:
    spec:
      containers:
      - name: audit
        image: gcr.io/open-policy-agent/gatekeeper:latest
        args:
        - --audit
        - --policy-dir=/etc/gatekeeper/policies
        volumeMounts:
        - name: policies
          mountPath: /etc/gatekeeper/policies
      restartPolicy: OnFailure
      volumes:
      - name: policies
        configMap:
          name: gatekeeper-policies
```

This job runs the `gatekeeper-audit` container, which checks the cluster against the policies.

#### Webhook Service

The webhook service is responsible for intercepting requests to the Kubernetes API server and validating them against the defined policies.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: gatekeeper-webhook-service
  namespace: open-policy-agent
spec:
  ports:
  - port: 443
    targetPort: 9443
  selector:
    app: gatekeeper-controller-manager
```

This service exposes the webhook endpoint on port 443, which is used by the Kubernetes API server to validate requests.

### Defining Policies

Now that Gatekeeper is installed, we can define and enforce policies in the cluster.

#### Example Policy Definition

Let's define a simple policy that restricts the creation of pods with privileged access.

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sPodSecurityStandard
metadata:
  name: deny-privileged-pods
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Pod"]
  parameters:
    privileged: false
```

This policy ensures that no pods with privileged access are created in the cluster.

#### Applying the Policy

We can apply the policy using `kubectl`.

```bash
kubectl apply -f deny-privileged-pods.yaml
```

This command applies the policy to the cluster.

### Testing the Policy

To test the policy, we can try to create a pod with privileged access and observe the result.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: privileged-pod
spec:
  containers:
  - name: privileged-container
    image: nginx
    securityContext:
      privileged: true
```

Applying this pod definition should result in a validation error due to the policy.

```bash
kubectl apply -f privileged-pod.yaml
```

The output should indicate that the pod creation is denied due to the policy violation.

### How to Prevent / Defend

#### Detection

To detect policy violations, we can use the Gatekeeper audit pod. The audit pod runs periodically and checks the current state of the cluster against the defined policies.

```bash
kubectl logs -l app=gatekeeper-audit -n open-policy-agent
```

This command shows the audit results, indicating any non-compliant resources.

#### Prevention

To prevent policy violations, we can enforce the policies using the webhook service. The webhook service intercepts requests to the Kubernetes API server and validates them against the defined policies.

#### Secure Coding Fixes

To ensure secure coding practices, we can define policies that enforce best practices and security standards. For example, we can define a policy that restricts the use of root users in pods.

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sPodSecurityStandard
metadata:
  name: deny-root-users
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Pod"]
  parameters:
    allowPrivilegeEscalation: false
    readOnlyRootFilesystem: true
```

This policy ensures that no pods with root users are created in the cluster.

#### Configuration Hardening

To harden the configuration, we can enable additional security features in the Gatekeeper controller pods. For example, we can enable the `readOnlyRootFilesystem` parameter to ensure that the root filesystem is read-only.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gatekeeper-controller-manager
  namespace: open-policy-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gatekeeper-controller-manager
  template:
    metadata:
      labels:
        app: gatekeeper-controller-manager
    spec:
      containers:
      - name: manager
        image: gcr.io/open-policy-agent/gatekeeper:latest
        args:
        - --policy-dir=/etc/gatekeeper/policies
        - --webhook-port=9443
        securityContext:
          readOnlyRootFilesystem: true
        volumeMounts:
        - name: policies
          mountPath: /etc/gatekeeper/policies
      volumes:
      - name: policies
        configMap:
          name: gatekeeper-policies
```

This configuration ensures that the root filesystem is read-only in the Gatekeeper controller pods.

### Real-World Examples

#### Recent CVEs and Breaches

Recent CVEs and breaches have highlighted the importance of enforcing security policies in Kubernetes clusters. For example, CVE-2021-25741 affected Kubernetes clusters that did not enforce proper RBAC policies, leading to unauthorized access.

By using OPA Gatekeeper, organizations can define and enforce strict RBAC policies to prevent such vulnerabilities.

### Hands-On Labs

To gain hands-on experience with OPA Gatekeeper, consider the following labs:

- **PortSwigger Web Security Academy**: Provides interactive labs for learning web application security.
- **OWASP Juice Shop**: An intentionally insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.
- **WebGoat**: An interactive training application designed to teach web application security.

These labs provide practical experience in applying security policies and best practices in real-world scenarios.

### Conclusion

In conclusion, Policy as Code and OPA Gatekeeper provide powerful tools for enforcing security policies in Kubernetes clusters. By following the steps outlined in this chapter, organizations can effectively define, enforce, and audit policies to ensure compliance and security.

### Further Reading

For further reading, consider the following resources:

- **Open Policy Agent Documentation**: Official documentation for OPA and Gatekeeper.
- **Kubernetes Documentation**: Official documentation for Kubernetes.
- **AWS EKS Documentation**: Official documentation for Amazon EKS.

These resources provide detailed information and best practices for implementing Policy as Code in Kubernetes clusters.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Install OPA Gatekeeper in Cluster/01-Introduction to Policy as Code Part 1|Introduction to Policy as Code Part 1]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/04-Policy as Code/Install OPA Gatekeeper in Cluster/00-Overview|Overview]] | [[03-Introduction to Policy as Code Part 3|Introduction to Policy as Code Part 3]]
