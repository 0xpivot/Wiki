---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Deploying Managed Kubernetes Cluster with MongoDB

### Introduction to Kubernetes and Helm

Kubernetes is an open-source platform designed to automate deploying, scaling, and operating application containers. It was originally designed by Google and is now maintained by the Cloud Native Computing Foundation. Kubernetes aims to provide a portable, extensible, and self-healing infrastructure for managing containerized workloads and services.

Helm is a package manager for Kubernetes. It simplifies the deployment and management of applications on Kubernetes by using charts, which are collections of files that describe a related set of Kubernetes resources. A chart can be used to deploy a simple application or a complex multi-tier application.

### Setting Up the Environment

Before diving into the specifics of deploying MongoDB using Helm, ensure that your environment is properly set up:

1. **Kubernetes Cluster**: You should have a Kubernetes cluster up and running. This can be a managed service like Linode Kubernetes Engine, Amazon EKS, or Google GKE, or a self-managed cluster using tools like Minikube or kubeadm.
2. **Helm**: Install Helm on your local machine. Helm requires `kubectl` to interact with the Kubernetes cluster.

```bash
# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Adding the Chart Repository

To deploy MongoDB, we need to add the Bitnami chart repository to Helm. Bitnami is a popular provider of pre-built charts for various applications.

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### Searching for MongoDB Charts

Once the repository is added, we can search for MongoDB charts using the `helm search repo` command.

```bash
helm search repo bitnami/mongodb
```

This command will list all the MongoDB charts available in the Bitnami repository.

### Understanding the MongoDB Chart

The MongoDB chart provides a way to deploy MongoDB on a Kubernetes cluster. Let's explore the parameters and configurations available in the chart.

#### Viewing Chart Parameters

To view the parameters available in the MongoDB chart, use the following command:

```bash
helm show values bitnami/mongodb > mongodb-values.yaml
```

This command will download the default values of the MongoDB chart into a file named `mongodb-values.yaml`.

```yaml
# mongodb-values.yaml
replicaCount: 1
image:
  registry: docker.io
  repository: bitnami/mongodb
  tag: 4.4.10-debian-10-r15
  pullPolicy: IfNotPresent
  ## Specify a imagePullSecrets secret name or list of secret names to be used for pulling the image from a private registry
  # imagePullSecrets:
  # - myRegistryKeySecretName
```

### Configuring MongoDB Deployment

When deploying MongoDB using Helm, you can override the default values to customize the deployment. Here are some key parameters to consider:

1. **Replica Set Configuration**:
   - To ensure high availability and data redundancy, you can configure MongoDB to run in a replica set mode. This means multiple instances of MongoDB will be deployed, and they will replicate data among themselves.

2. **Root Password**:
   - By default, Helm will generate a random root password for MongoDB. However, you can specify your own password for better control and security.

3. **Volume Configuration**:
   - MongoDB requires persistent storage to store data. You can configure the storage class to use Linode cloud storage, ensuring that the data is stored on Linode's infrastructure.

### Example Configuration

Let's create a custom configuration file (`values.yaml`) to override the default values:

```yaml
# values.yaml
replicaCount: 3
auth:
  enabled: true
  rootPassword: "your-strong-password"
  username: "admin"
  password: "your-strong-password"
metrics:
  enabled: true
persistence:
  enabled: true
  storageClass: "linode-block-storage"
  size: 10Gi
```

### Deploying MongoDB

Now, we can deploy MongoDB using the custom configuration file:

```bash
helm install my-mongodb bitnami/mongodb -f values.yaml
```

This command will install MongoDB with the specified configurations.

### Monitoring and Accessing MongoDB

After deployment, you can monitor the status of the MongoDB pods and services using `kubectl` commands:

```bash
kubectl get pods
kubectl get svc
```

To access MongoDB, you can use the `kubectl port-forward` command to forward the MongoDB service port to your local machine:

```bash
kubectl port-forward svc/my-mongodb 27017:27017
```

Then, you can connect to MongoDB using a client like `mongo`:

```bash
mongo --host 127.0.0.1 --port 27017 -u admin -p your-strong-password
```

### Security Considerations

Deploying MongoDB in a Kubernetes cluster introduces several security considerations:

1. **Network Policies**:
   - Ensure that network policies are in place to restrict access to the MongoDB service. Only allow necessary traffic to the MongoDB pods.

2. **Authentication and Authorization**:
   - Enable authentication and authorization in MongoDB to ensure that only authorized users can access the database.

3. **Encryption**:
   - Use encryption at rest and in transit to protect sensitive data. Ensure that TLS/SSL is enabled for MongoDB connections.

4. **Regular Audits**:
   - Regularly audit the MongoDB deployment to identify and mitigate potential security vulnerabilities.

### How to Prevent / Defend

#### Detection

- **Monitoring Tools**: Use monitoring tools like Prometheus and Grafana to monitor the health and performance of the MongoDB deployment.
- **Logging**: Enable logging and ensure that logs are stored securely and monitored for suspicious activity.

#### Prevention

- **Secure Configuration**: Follow best practices for securing MongoDB deployments, such as enabling authentication, using strong passwords, and configuring network policies.
- **Regular Updates**: Keep the MongoDB version and Helm charts up to date to benefit from the latest security patches.

#### Secure Coding Fixes

Here is an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration**:
```yaml
# Vulnerable values.yaml
replicaCount: 1
auth:
  enabled: false
persistence:
  enabled: false
```

**Secure Configuration**:
```yaml
# Secure values.yaml
replicaCount: 3
auth:
  enabled: true
  rootPassword: "your-strong-password"
  username: "admin"
  password: "your-strong-password"
persistence:
  enabled: true
  storageClass: "linode-block-storage"
  size: 10Gi
```

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-29441**: A vulnerability in MongoDB allowed unauthorized access to the database. This highlights the importance of enabling authentication and using strong passwords.
- **MongoDB Incidents**: Several incidents involving MongoDB deployments have been reported, emphasizing the need for proper security measures.

### Conclusion

Deploying MongoDB on a Kubernetes cluster using Helm provides a scalable and manageable solution for storing and accessing data. By following best practices for security and configuration, you can ensure that your MongoDB deployment is robust and secure.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing MongoDB deployments.
- **OWASP Juice Shop**: Provides a vulnerable web application that includes MongoDB components.
- **Kubernetes Goat**: Focuses on Kubernetes security and includes scenarios involving MongoDB deployments.

By completing these labs, you can gain practical experience in deploying and securing MongoDB on Kubernetes.

---
<!-- nav -->
[[09-Introduction to Managed Kubernetes Clusters|Introduction to Managed Kubernetes Clusters]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/13-Deploying Managed Kubernetes Cluster with MongoDB/00-Overview|Overview]] | [[11-Deploying Mongo Express as a UI for MongoDB|Deploying Mongo Express as a UI for MongoDB]]
