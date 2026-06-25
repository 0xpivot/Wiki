---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Kubernetes Basics and Pod Deployment

Kubernetes is an open-source container orchestration platform designed to automate the deployment, scaling, and management of containerized applications. It was originally developed by Google and is now maintained by the Cloud Native Computing Foundation (CNCF). Kubernetes provides a robust framework for managing containerized applications across clusters of hosts, providing deployment, maintenance, and scaling capabilities.

### Basic Components of Kubernetes

Before diving into the specifics of pod deployment and configuration management, it's essential to understand the fundamental components of Kubernetes:

1. **Pod**: A pod is the smallest deployable unit in Kubernetes. It consists of one or more containers that share storage and network resources. All containers within a pod are guaranteed to be co-located and co-scheduled on the same physical or virtual machine.

2. **Node**: A node is a worker machine in Kubernetes. It can be a physical or virtual machine. Each node runs the Kubernetes runtime, which includes the container runtime, kubelet, and kube-proxy.

3. **Cluster**: A cluster is a set of nodes that run the Kubernetes control plane and worker nodes. The control plane manages the cluster, while the worker nodes host the pods.

4. **Service**: A service is an abstraction that defines a logical set of pods and a policy by which to access them. Services provide a stable IP address and DNS name for a group of pods, allowing them to communicate with each other.

### Simple Setup Example

Let's consider a simple setup where we have a single server with a few containers running and some services. This setup might include a web application and a database. In this scenario, the web application communicates with the database using a service.

#### Communication Between Containers

In our example, the web application needs to communicate with a database, such as MongoDB. The web application will have a database endpoint configured, typically called `MongoDB service`. This service allows the web application to interact with the database.

#### Configuration of Database Endpoint

The database endpoint or URL is usually configured in one of two ways:

1. **Application Properties File**: The endpoint is specified in a properties file within the application.
2. **Environmental Variable**: The endpoint is set as an environmental variable.

However, these configurations are typically embedded within the application image itself. If the service name or endpoint changes, you would need to update the application properties, rebuild the image, push it to the repository, and then redeploy the updated image in the pod.

### ConfigMap for External Configuration

To avoid the tedious process of rebuilding and redeploying the application for minor changes like updating a database URL, Kubernetes provides a component called `ConfigMap`.

#### What is a ConfigMap?

A ConfigMap is a Kubernetes object that stores configuration data as key-value pairs. It allows you to decouple configuration data from your application code, making it easier to manage and update configuration settings without rebuilding the application.

#### How ConfigMap Works

When you define a ConfigMap, you can store configuration data such as database URLs, API keys, or any other environment-specific information. You can then reference this ConfigMap in your pod specifications, allowing the pod to dynamically fetch the configuration data at runtime.

#### Example of ConfigMap

Let's create a ConfigMap for our MongoDB service endpoint. Here’s how you can define a ConfigMap in a YAML file:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mongodb-config
data:
  MONGO_DB_URL: "mongodb://mongo-service:27017/mydatabase"
```

This ConfigMap contains a key-value pair where `MONGO_DB_URL` is the key and the value is the MongoDB service endpoint.

#### Applying ConfigMap

To apply this ConfigMap to your Kubernetes cluster, you can use the `kubectl` command:

```sh
kubectl apply -f mongodb-config.yaml
```

#### Referencing ConfigMap in Pod Specification

Next, you need to reference this ConfigMap in your pod specification. Here’s an example of how to do this:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-app-pod
spec:
  containers:
  - name: web-app-container
    image: my-web-app:latest
    env:
    - name: MONGO_DB_URL
      valueFrom:
        configMapKeyRef:
          name: mongodb-config
          key: MONGO_DB_URL
```

In this pod specification, the `env` section references the `MONGO_DB_URL` from the `mongodb-config` ConfigMap.

### Benefits of Using ConfigMap

Using ConfigMap offers several benefits:

1. **Decoupling Configuration from Code**: By storing configuration data in a ConfigMap, you can easily update the configuration without modifying the application code.
2. **Dynamic Updates**: You can update the ConfigMap without needing to rebuild and redeploy the application.
3. **Environment-Specific Configuration**: You can maintain different ConfigMaps for different environments (development, staging, production).

### Real-World Examples and Recent CVEs

#### Example: MongoDB Service Endpoint Change

Imagine a scenario where the MongoDB service endpoint changes due to a network reconfiguration. Without ConfigMap, you would need to update the application properties, rebuild the image, and redeploy the pod. With ConfigMap, you simply update the ConfigMap and the pod automatically fetches the new endpoint.

#### Recent CVEs Related to Configuration Management

One notable CVE related to configuration management is **CVE-2021-21277**, which affected Kubernetes versions prior to 1.20. This vulnerability allowed attackers to bypass certain security restrictions by manipulating ConfigMap data. To mitigate such vulnerabilities, it's crucial to keep your Kubernetes cluster up-to-date and follow best practices for securing ConfigMap data.

### How to Prevent / Defend

#### Detection

To detect potential issues with ConfigMap usage, you can monitor the following:

1. **Audit Logs**: Enable audit logging in Kubernetes to track changes made to ConfigMaps.
2. **Network Monitoring**: Monitor network traffic to ensure that ConfigMap data is not being accessed or modified improperly.

#### Prevention

To prevent unauthorized access or manipulation of ConfigMap data, implement the following measures:

1. **Role-Based Access Control (RBAC)**: Use RBAC to restrict access to ConfigMaps based on user roles and permissions.
2. **Encryption**: Encrypt sensitive data stored in ConfigMaps using tools like Kubernetes Secrets.
3. **Regular Audits**: Conduct regular audits of ConfigMap usage to identify and address any security concerns.

#### Secure Coding Fixes

Here’s an example of how to securely manage ConfigMap data:

**Vulnerable Code:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: insecure-configmap
data:
  SECRET_KEY: "my-secret-key"
```

**Secure Code:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: secure-secret
type: Opaque
data:
  SECRET_KEY: bXktc2VjcmV0LWtleQ==
```

In the secure version, the secret key is stored in a Kubernetes Secret, which is encrypted and provides better security compared to a plain ConfigMap.

### Conclusion

Understanding the basics of Kubernetes components and how to manage configuration data using ConfigMap is crucial for effective container orchestration. By leveraging ConfigMap, you can decouple configuration from your application code, enabling dynamic updates and improved security. Always follow best practices for securing your Kubernetes cluster and regularly audit your configurations to ensure optimal performance and security.

### Practice Labs

For hands-on practice with Kubernetes and ConfigMap, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security concepts.
- **OWASP WrongSecrets**: A project for practicing secure coding and configuration management in Kubernetes.

These labs provide practical experience in deploying and managing Kubernetes clusters, including the use of ConfigMap and other configuration management techniques.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/04-Kubernetes Basics Pod Deployment Walkthrough/00-Overview|Overview]] | [[02-Introduction to Kubernetes Basics|Introduction to Kubernetes Basics]]
