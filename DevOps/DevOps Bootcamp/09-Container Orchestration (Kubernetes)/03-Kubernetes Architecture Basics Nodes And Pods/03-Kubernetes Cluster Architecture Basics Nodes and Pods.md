---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Kubernetes Cluster Architecture Basics: Nodes and Pods

### Introduction to Kubernetes Clusters

Kubernetes, often abbreviated as K8s, is an open-source system for automating deployment, scaling, and management of containerized applications. At its core, a Kubernetes cluster consists of a set of worker machines, called nodes, that run containerized applications. Every cluster has at least one node. A cluster also includes a set of master components that manage the cluster. 

The architecture of a Kubernetes cluster is designed to be highly scalable and resilient. This scalability is achieved by allowing the addition of new master or node servers to the cluster. In this section, we will delve into the details of how to add new nodes and masters to a Kubernetes cluster, and explore the underlying processes involved.

### Adding New Master Servers

#### What is a Master Server?

A master server in a Kubernetes cluster is responsible for managing the cluster. It runs the control plane components, which include:

- **etcd**: A distributed key-value store that stores the configuration data of the cluster.
- **API Server**: Exposes the Kubernetes API, which allows communication between the control plane and the user.
- **Controller Manager**: Runs controllers that watch the state of the cluster and make changes to bring the actual state closer to the desired state.
- **Scheduler**: Watches for newly created pods that have not yet been assigned to a node and selects a node for them to run on.

#### How to Add a New Master Server

To add a new master server to an existing Kubernetes cluster, follow these steps:

1. **Get a New Bare Server**: Obtain a new server that meets the hardware requirements for a Kubernetes master node. This typically includes sufficient CPU, memory, and storage resources.

2. **Install Master Processes**: Install the necessary master processes on the new server. This involves installing the etcd, API Server, Controller Manager, and Scheduler components. These components can be installed using tools such as `kubeadm`, which simplifies the process of setting up a Kubernetes cluster.

3. **Join the Cluster**: Add the new master server to the existing Kubernetes cluster. This involves configuring the new master to communicate with the existing master(s) and joining the etcd cluster.

Here is an example of how to add a new master server using `kubeadm`:

```bash
# On the new master server
sudo kubeadm init --control-plane-endpoint=<existing-master-ip>:<port> --upload-certs
```

This command initializes the new master server and joins it to the existing cluster. The `--control-plane-endpoint` flag specifies the endpoint of the existing master, and the `--upload-certs` flag uploads the necessary certificates to the existing master.

#### Example: Adding a New Master Server

Suppose we have an existing Kubernetes cluster with a single master server at `192.168.1.10`. We want to add a new master server at `192.168.1.20`.

1. **Prepare the New Master Server**:
   - Ensure the new server has the necessary hardware and software requirements.
   - Install the required packages and dependencies.

2. **Initialize the New Master Server**:
   ```bash
   sudo kubeadm init --control-plane-endpoint=192.168.1.10:6443 --upload-certs
   ```

3. **Configure the New Master Server**:
   - Copy the necessary configuration files from the existing master to the new master.
   - Ensure the new master can communicate with the existing master and join the etcd cluster.

### Adding New Worker Nodes

#### What is a Worker Node?

A worker node in a Kubernetes cluster is a machine that runs the applications. Each worker node runs the following components:

- **kubelet**: An agent that runs on each node and ensures that the containers are running in a pod.
- **kube-proxy**: A network proxy that runs on each node and maintains network rules.
- **Container Runtime**: A container runtime that is responsible for running containers. Common runtimes include Docker, containerd, and CRI-O.

#### How to Add a New Worker Node

To add a new worker node to an existing Kubernetes cluster, follow these steps:

1. **Get a New Bare Server**: Obtain a new server that meets the hardware requirements for a Kubernetes worker node. This typically includes sufficient CPU, memory, and storage resources.

2. **Install Worker Node Processes**: Install the necessary worker node processes on the new server. This involves installing the kubelet, kube-proxy, and container runtime components.

3. **Join the Cluster**: Add the new worker node to the existing Kubernetes cluster. This involves configuring the new worker to communicate with the master and join the cluster.

Here is an example of how to add a new worker node using `kubeadm`:

```bash
# On the new worker node
sudo kubeadm join <master-ip>:<port> --token <token>
```

This command joins the new worker node to the existing cluster. The `<master-ip>` and `<port>` specify the endpoint of the master, and the `<token>` is a unique token generated by the master for joining new nodes.

#### Example: Adding a New Worker Node

Suppose we have an existing Kubernetes cluster with a single worker node at `192.168.1.30`. We want to add a new worker node at `192.168.1.40`.

1. **Prepare the New Worker Node**:
   - Ensure the new server has the necessary hardware and software requirements.
   - Install the required packages and dependencies.

2. **Join the New Worker Node**:
   ```bash

   sudo kubeadm join 192.168.1.30:6443 --token abcdef.0123456789abcdef
   ```

3. **Verify the New Worker Node**:
   - Check the status of the new worker node using the `kubectl` command.
   - Ensure the new worker node is communicating with the master and running the necessary processes.

### Scalability and Resource Management

One of the key benefits of Kubernetes is its ability to scale and manage resources dynamically. By adding new master or worker nodes to the cluster, you can increase the power and resources available to the cluster. This is particularly useful as the complexity and resource demands of your applications increase.

#### Real-World Example: Scaling a Kubernetes Cluster

Consider a scenario where a company is running a web application on a Kubernetes cluster. Initially, the cluster consists of a single master and two worker nodes. As the number of users increases, the resource demands of the application also increase. To handle this increased load, the company decides to add more worker nodes to the cluster.

1. **Monitor Resource Usage**: Use tools such as `kubectl top nodes` and `kubectl top pods` to monitor the resource usage of the nodes and pods in the cluster.

2. **Add New Worker Nodes**: Add new worker nodes to the cluster using the steps outlined above.

3. **Scale Applications**: Scale the applications running on the cluster using the `kubectl scale` command. For example, to scale a deployment named `webapp` to 5 replicas:

   ```bash
   kubectl scale deployment webapp --replicas=5
   ```

4. **Verify Performance**: Monitor the performance of the scaled application and ensure it is handling the increased load efficiently.

### Pitfalls and Best Practices

While adding new nodes to a Kubernetes cluster is straightforward, there are several pitfalls to be aware of:

- **Network Configuration**: Ensure that the new nodes can communicate with the existing nodes and the master. Misconfigured network settings can lead to connectivity issues.
- **Security**: Secure the communication between the new nodes and the existing nodes. Use TLS encryption and mutual authentication to protect against eavesdropping and man-in-the-middle attacks.
- **Resource Allocation**: Allocate resources appropriately to avoid overloading the nodes. Use resource quotas and limits to manage the resource usage of the pods.

### How to Prevent / Defend

#### Detection

- **Monitor Network Traffic**: Use network monitoring tools to detect any unauthorized access attempts or suspicious traffic patterns.
- **Audit Logs**: Enable audit logging on the Kubernetes API server to track all API requests and responses. Analyze the logs to identify any unauthorized actions.

#### Prevention

- **Secure Communication**: Use TLS encryption and mutual authentication to secure the communication between the nodes and the master.
- **Access Control**: Implement role-based access control (RBAC) to restrict access to the Kubernetes API. Define roles and bindings to grant permissions to specific users or groups.
- **Hardening**: Harden the nodes by disabling unnecessary services and ports. Use security policies to enforce strict security configurations.

#### Secure Coding Fixes

- **Vulnerable Code Example**:
  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: insecure-pod
  spec:
    containers:
    - name: insecure-container
      image: myimage:latest
      ports:
      - containerPort: 80
  ```

- **Fixed Code Example**:
  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: secure-pod
  spec:
    containers:
    - name: secure-container
      image: myimage:latest
      ports:
      - containerPort: 80
        protocol: TCP
      securityContext:
        capabilities:
          drop:
          - ALL
        readOnlyRootFilesystem: true
  ```

### Conclusion

Adding new master or worker nodes to a Kubernetes cluster is a straightforward process that can significantly enhance the scalability and resilience of the cluster. By understanding the underlying processes and best practices, you can effectively manage and scale your Kubernetes cluster to meet the growing demands of your applications.

### Practice Labs

For hands-on experience with Kubernetes architecture and node management, consider the following practice labs:

- **Kubernetes Goat**: A hands-on lab that simulates a real-world Kubernetes environment and provides challenges to test your skills.
- **OWASP WrongSecrets**: A series of challenges that focus on securing Kubernetes clusters and preventing common vulnerabilities.
- **kube-hunter**: A tool that helps you discover and mitigate security issues in your Kubernetes cluster.

These labs provide practical experience and reinforce the concepts covered in this chapter.

---
<!-- nav -->
[[02-Kubernetes Architecture Basics Nodes and Pods|Kubernetes Architecture Basics Nodes and Pods]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/03-Kubernetes Architecture Basics Nodes And Pods/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/03-Kubernetes Architecture Basics Nodes And Pods/04-Practice Questions & Answers|Practice Questions & Answers]]
