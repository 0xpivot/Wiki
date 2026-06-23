---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Deploying MongoDB with Helm

To deploy MongoDB in a Kubernetes cluster using Helm, we need to follow these steps:

1. **Install Helm**: Ensure that Helm is installed on your system.
2. **Add MongoDB Chart Repository**: Add the MongoDB chart repository to Helm.
3. **Create Values File**: Create a `values.yaml` file to override default values.
4. **Install MongoDB Chart**: Use the `helm install` command to install the MongoDB chart.

### Step 1: Install Helm

Before we can use Helm, we need to ensure that it is installed on our system. You can install Helm by following the instructions on the official Helm documentation.

```bash
# Download and install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Step 2: Add MongoDB Chart Repository

Next, we need to add the MongoDB chart repository to Helm. This repository contains the Helm charts for MongoDB.

```bash
# Add MongoDB chart repository
helm repo add bitnami https://charts.bitnami.com/bitnami
```

### Step 3: Create Values File

We need to create a `values.yaml` file to override default values for the MongoDB chart. This file will contain custom configurations such as the number of replicas, storage settings, and other parameters.

```yaml
# values.yaml
replicaCount: 3
auth:
  enabled: true
  username: admin
  password: adminpassword
storage:
  size: 10Gi
```

### Step 4: Install MongoDB Chart

Now we can use the `helm install` command to install the MongoDB chart. We will specify the name of the release, the path to the `values.yaml` file, and the name of the chart.

```bash
# Install MongoDB chart
helm install mongodb bitnami/mongodb --values ./values.yaml
```

### Explanation of the Command

- `helm install`: This command installs a new release of a chart.
- `mongodb`: This is the name of the release. You can choose any name you like.
- `bitnami/mongodb`: This specifies the chart to be installed. `bitnami` is the repository, and `mongodb` is the chart name.
- `--values ./values.yaml`: This specifies the path to the `values.yaml` file that overrides default values.

### Monitoring the Deployment

After executing the `helm install` command, Kubernetes will start deploying the MongoDB pods. You can monitor the progress using the `kubectl` command.

```bash
# Monitor the deployment
kubectl get pods
```

You should see the MongoDB pods being created and eventually reaching the `Running` state.

### Example Output

```bash
NAME                          READY   STATUS    RESTARTS   AGE
mongodb-0                     1/1     Running   0          1m
mongodb-1                     1/1     Running   0          1m
mongodb-2                     1/1     Running   0          1m
mongodb-arbiter-0             1/1     Running   0          1m
```

### Understanding the Deployment

When you deploy MongoDB using Helm, Kubernetes creates a stateful set for the MongoDB pods. Each pod is assigned a unique identifier, and a separate arbiter pod is created to manage replication.

#### Stateful Set

A stateful set is a Kubernetes resource that manages stateful applications. It ensures that each pod has a stable identity and persistent storage.

#### Replication

MongoDB uses replication to ensure high availability. The `replicaCount` parameter in the `values.yaml` file specifies the number of replicas to create. Each replica runs in its own pod, and an arbiter pod manages the replication process.

### Common Pitfalls and How to Avoid Them

#### Incorrect Configuration

One common pitfall is incorrect configuration in the `values.yaml` file. Ensure that all required parameters are correctly specified.

#### Insufficient Resources

Another issue is insufficient resources allocated to the MongoDB pods. Ensure that the `resources` section in the `values.yaml` file is configured appropriately.

#### Network Issues

Network issues can also cause problems. Ensure that the network policies and services are correctly configured.

### How to Prevent / Defend

#### Secure Configuration

Ensure that sensitive information such as passwords is encrypted and stored securely. Use Kubernetes secrets to store sensitive data.

#### Resource Management

Monitor the resource usage of the MongoDB pods and adjust the `resources` section in the `values.yaml` file as needed.

#### Network Policies

Implement network policies to restrict access to the MongoDB pods. Use Kubernetes network policies to control traffic between pods.

### Real-World Examples

#### CVE-2021-22817

CVE-2021-22817 is a vulnerability in MongoDB that allows unauthorized access to the database. To prevent this vulnerability, ensure that authentication is enabled and that only authorized users have access to the database.

#### Example Exploit

An attacker could exploit this vulnerability by sending a crafted request to the MongoDB server. To defend against this, ensure that the MongoDB server is properly configured and that only authorized users have access.

### Conclusion

Deploying MongoDB in a Kubernetes cluster using Helm is a straightforward process. By following the steps outlined above, you can easily install and manage a MongoDB instance within a Kubernetes environment. Ensure that you configure the `values.yaml` file correctly and monitor the deployment to avoid common pitfalls.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.
- **WebGoat**: An interactive, gamified web application security training tool.

These labs provide practical experience in deploying and managing applications in a Kubernetes environment.

### Summary

In this section, we covered the process of deploying MongoDB in a Kubernetes cluster using Helm. We explained the concepts of Helm and Kubernetes, and provided a step-by-step guide to installing MongoDB. We also discussed common pitfalls and how to prevent them, and provided real-world examples of vulnerabilities and exploits. Finally, we suggested practice labs for hands-on experience.

---
<!-- nav -->
[[12-Deploying MongoDB and Mongo Express in a Kubernetes Cluster|Deploying MongoDB and Mongo Express in a Kubernetes Cluster]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/13-Deploying Managed Kubernetes Cluster with MongoDB/00-Overview|Overview]] | [[14-Deploying MongoDB with Persistent Volumes|Deploying MongoDB with Persistent Volumes]]
