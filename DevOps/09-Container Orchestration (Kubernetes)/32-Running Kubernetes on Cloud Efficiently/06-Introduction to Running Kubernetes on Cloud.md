---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Running Kubernetes on Cloud

In this section, we will delve into the intricacies of running Kubernetes on a cloud platform, specifically focusing on the benefits of using a managed Kubernetes service. We will explore a scenario where a team is developing a microservice application with a database that will be deployed in a Kubernetes cluster. The goal is to ensure that the application is accessible via a secure HTTP connection and that the entire setup meets stringent security and data persistence requirements. Additionally, we will discuss the importance of maintaining consistent development and production environments to facilitate thorough testing before deployment.

### Scenario Overview

Imagine you and your team are developing a microservice application that includes a database. This application will be deployed in a Kubernetes cluster, and you want it to be accessible from a browser via a secure HTTP connection. Furthermore, you have specific requirements such as ensuring the security of the entire cluster setup and maintaining data persistence for the database. To achieve these goals efficiently, you aim to avoid spending excessive time setting up and managing the infrastructure manually.

### Kubernetes Cluster Deployment Options

When deploying a Kubernetes cluster on a cloud platform, there are several options available. One popular choice is Linode, which offers both managed and unmanaged Kubernetes services. Let's explore the two primary options for setting up a Kubernetes cluster on Linode:

1. **Unmanaged Kubernetes Cluster**: In this approach, you manually spin up Linode server instances and create your own Kubernetes cluster from scratch. This involves installing the master processes on designated nodes and configuring them as master nodes.
2. **Managed Kubernetes Service**: This option leverages a managed Kubernetes service provided by Linode, which abstracts away much of the complexity involved in setting up and maintaining a Kubernetes cluster.

#### Unmanaged Kubernetes Cluster Setup

To set up an unmanaged Kubernetes cluster on Linode, you would typically follow these steps:

1. **Spin Up Linode Instances**: Create six Linode server instances. These instances will serve as the nodes in your Kubernetes cluster.
2. **Install Master Processes**: On three of these instances, install the master processes (kube-apiserver, kube-scheduler, and kube-controller-manager) to designate them as master nodes.
3. **Configure Worker Nodes**: The remaining three instances will act as worker nodes, where your application pods will run.
4. **Network Configuration**: Ensure proper network configuration between the master and worker nodes to enable communication within the cluster.
5. **Security Measures**: Implement necessary security measures such as network policies, RBAC (Role-Based Access Control), and encryption to protect the cluster.

Let's break down each step in more detail:

### Step-by-Step Guide to Setting Up an Unmanaged Kubernetes Cluster

#### 1. Spin Up Linode Instances

First, you need to create six Linode instances. Here’s how you can do it:

```bash
# Log in to Linode CLI
linode-cli login

# Create Linode instances
for i in {1..6}; do
  linode-cli linodes create --type g6-standard-1 --region us-east --image kubernetes-1.24-x86_64 --label node$i
done
```

This command creates six Linode instances with the label `node1` to `node6`. Each instance uses the `g6-standard-1` plan, which is a small virtual machine suitable for a basic Kubernetes setup.

#### 2. Install Master Processes

Next, you need to install the master processes on three of the instances. For simplicity, let's assume `node1`, `node2`, and `node3` will be the master nodes.

```bash
# SSH into each master node
for i in {1..3}; do
  ssh root@$(linode-cli linodes view --id $(linode-cli linodes list --format id --text --no-headers | grep node$i) --format ipv4 --text --no-headers)
  
  # Install Kubernetes master components
  apt-get update && apt-get install -y kube-apiserver kube-scheduler kube-controller-manager
  
  # Configure master components
  # Example configuration files for kube-apiserver, kube-scheduler, and kube-controller-manager
  cat <<EOF > /etc/kubernetes/kube-apiserver.yaml
apiVersion: v1
kind: Config
clusters:
- name: local
  cluster:
    server: https://localhost:6443
    certificate-authority-data: <base64-encoded-ca-cert>
users:
- name: admin
  user:
    client-certificate-data: <base64-encoded-client-cert>
    client-key-data: <base64-encoded-client-key>
contexts:
- context:
    cluster: local
    user: admin
  name: default-context
current-context: default-context
EOF
EOF > /etc/kubernetes/kube-scheduler.yaml
EOF > /etc/kubernetes/kube-controller-manager.yaml

  # Start master components
  systemctl start kube-apiserver kube-scheduler kube-controller-manager
done
```

This script logs into each master node, installs the necessary Kubernetes components, and configures them. Note that the actual configuration files (`kube-apiserver.yaml`, `kube-scheduler.yaml`, `kube-controller-manager.yaml`) should be filled with appropriate values based on your cluster setup.

#### 3. Configure Worker Nodes

The remaining three instances (`node4`, `node5`, and `node6`) will act as worker nodes. You need to install the Kubernetes worker components on these nodes.

```bash
# SSH into each worker node
for i in {4..6}; do
  ssh root@$(linode-cli linodes view --id $(linode-cli linodes list --format id --text --no-headers | grep node$i) --format ipv4 --text --no-headers)
  
  # Install Kubernetes worker components
  apt-get update && apt-get install -y kubelet kubeadm
  
  # Join worker nodes to the cluster
  kubeadm join <master-node-ip>:<port> --token <token> --discovery-token-ca-cert-hash sha256:<hash>
done
```

This script logs into each worker node, installs the necessary components, and joins them to the cluster using `kubeadm`.

#### 4. Network Configuration

Ensure proper network configuration between the master and worker nodes. This involves setting up network policies and ensuring that the nodes can communicate with each other.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

This network policy denies all ingress and egress traffic by default, providing a baseline of security.

#### 5. Security Measures

Implement necessary security measures to protect the cluster. This includes RBAC, encryption, and network policies.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: johndoe
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

This role and role binding grant the user `johndoe` permission to read pods in the `default` namespace.

### Managed Kubernetes Service

Using a managed Kubernetes service simplifies the process significantly. Linode's managed Kubernetes service handles many of the complexities involved in setting up and maintaining a Kubernetes cluster.

#### Benefits of Managed Kubernetes Service

1. **Ease of Use**: Managed services handle the installation and configuration of Kubernetes components, reducing the need for manual intervention.
2. **Scalability**: Managed services often provide built-in scaling capabilities, allowing you to easily scale your cluster as needed.
3. **Maintenance**: Managed services handle updates, patches, and maintenance tasks, freeing you from these responsibilities.
4. **Security**: Managed services often include additional security features and best practices, enhancing the overall security of your cluster.

#### Setting Up a Managed Kubernetes Cluster on Linode

To set up a managed Kubernetes cluster on Linode, you can use the Linode CLI or the Linode dashboard.

```bash
# Create a managed Kubernetes cluster
linode-cli k8s clusters create --region us-east --nodes 6 --version 1.24.0
```

This command creates a managed Kubernetes cluster with six nodes in the `us-east` region, using Kubernetes version `1.24.0`.

### Conclusion

Running a Kubernetes cluster on a cloud platform like Linode offers significant benefits, especially when leveraging a managed Kubernetes service. This approach simplifies the setup and management of the cluster, allowing you to focus on developing and deploying your applications. Whether you choose to set up an unmanaged cluster or opt for a managed service, understanding the underlying principles and configurations is crucial for ensuring a robust and secure environment.

### How to Prevent / Defend

#### Detection

Regularly monitor your Kubernetes cluster for any unusual activity. Use tools like `kubectl` to inspect the state of your cluster and check for unauthorized changes.

```bash
# Check the status of all nodes
kubectl get nodes

# Check the status of all pods
kubectl get pods --all-namespaces
```

#### Prevention

Implement strict security measures to protect your cluster. This includes:

1. **RBAC**: Enforce Role-Based Access Control to restrict access to sensitive resources.
2. **Network Policies**: Use network policies to control traffic within the cluster.
3. **Encryption**: Enable encryption for sensitive data and communications.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of a configuration file to understand the differences.

**Vulnerable Version:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
```

**Secure Version:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
  securityContext:
    runAsNonRoot: true
    readOnlyRootFilesystem: true
```

In the secure version, the `securityContext` ensures that the container runs as a non-root user and the root filesystem is read-only, enhancing security.

### Real-World Examples

Consider recent vulnerabilities and breaches involving Kubernetes clusters. For example, the CVE-2021-25741, which affected Kubernetes versions prior to 1.22.3, allowed attackers to bypass authentication and gain unauthorized access to the cluster.

### Practice Labs

For hands-on experience with Kubernetes on cloud platforms, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **Linode Managed Kubernetes Lab**: Official Linode labs for setting up and managing a Kubernetes cluster.

By following these detailed steps and implementing the recommended security measures, you can effectively run a Kubernetes cluster on a cloud platform like Linode.

---
<!-- nav -->
[[05-Introduction to Running Kubernetes on Cloud Efficiently|Introduction to Running Kubernetes on Cloud Efficiently]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/32-Running Kubernetes on Cloud Efficiently/00-Overview|Overview]] | [[07-Running Kubernetes on Cloud Efficiently|Running Kubernetes on Cloud Efficiently]]
