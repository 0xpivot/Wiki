---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Kubernetes Namespace Usage and Best Practices

### Introduction to Kubernetes Namespaces

Kubernetes namespaces provide a mechanism for isolating groups of resources within a single cluster. This isolation is particularly useful in environments where multiple teams or applications share the same cluster. By using namespaces, you can logically group related resources together, making it easier to manage and monitor them.

#### What Are Namespaces?

Namespaces are virtual clusters backed by the same physical cluster. They allow you to partition resources like Pods, Services, Deployments, ConfigMaps, and Secrets into distinct groups. Each namespace has its own set of resources, and these resources are isolated from those in other namespaces.

#### Why Use Namespaces?

Using namespaces offers several benefits:

1. **Isolation**: Resources in one namespace are isolated from those in another. This prevents conflicts between resources with the same name but in different namespaces.
2. **Scalability**: As your cluster grows, namespaces help manage complexity by allowing you to organize resources into logical groups.
3. **Access Control**: Namespaces can be used to enforce access control policies. Different teams or applications can have their own namespaces, and access can be restricted based on namespace.
4. **Resource Management**: Namespaces can be used to manage resource quotas and limits. You can set quotas for CPU, memory, and other resources at the namespace level.

### Complex Applications and Multiple Users

In a complex application with multiple deployments, each deployment creates replicas of many pods. Additionally, you may have resources such as services, config maps, secrets, and more. Very soon, the default namespace will become cluttered with various components, making it difficult to maintain an overview of what is in there, especially when multiple users are creating resources.

#### Example Scenario

Consider a scenario where you have a microservices-based application with the following components:

- A database service
- A monitoring system (Prometheus)
- An Elastic Stack (Elasticsearch, Kibana)
- An NGINX Ingress controller

Without namespaces, all these components would be deployed in the default namespace, leading to a cluttered and unmanageable environment.

### Grouping Resources into Namespaces

A better approach is to group resources into namespaces. For example:

- **Database Namespace**: Deploy your database and all its required resources.
- **Monitoring Namespace**: Deploy Prometheus and all its dependencies.
- **Elastic Stack Namespace**: Deploy Elasticsearch, Kibana, and other related resources.
- **Ingress Namespace**: Deploy the NGINX Ingress controller and related resources.

This logical grouping makes it easier to manage and monitor resources.

#### Creating Namespaces

To create a namespace, you can use the `kubectl` command-line tool. Here is an example of creating a namespace called `database`:

```bash
kubectl create namespace database
```

You can also define namespaces using YAML files. Here is an example of a YAML file for creating a namespace:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: database
```

To apply this YAML file, use the following command:

```bash
kubectl apply -f namespace.yaml
```

### Official Documentation Recommendations

According to the official Kubernetes documentation, namespaces should not be used for smaller projects with up to 10 users. However, it is often a good practice to use namespaces even for smaller projects. Even with a small number of users, you might still need additional resources like logging systems and monitoring systems. These additional resources can quickly make the default namespace cluttered.

### Real-World Examples

#### Recent Breaches and CVEs

One recent example of a breach involving Kubernetes is the CVE-2021-25741, which affected the Kubernetes API server. This vulnerability allowed attackers to bypass authentication and gain unauthorized access to the cluster. Using namespaces can help mitigate such risks by isolating sensitive resources and enforcing stricter access controls.

#### Example Scenario: Logging System

Consider a scenario where you have a logging system that collects logs from various services. Without namespaces, all log data would be stored in the default namespace, making it difficult to manage and secure. By using namespaces, you can isolate the logging system and enforce stricter access controls.

Here is an example of a logging system deployed in a namespace:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: logging
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fluentd
  namespace: logging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemon:latest
        volumeMounts:
        - name: varlog
          mountPath: /var/log
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
```

To apply this YAML file, use the following command:

```bash
kubectl apply -f logging-system.yaml
```

### Pitfalls and Common Mistakes

#### Overusing Namespaces

While namespaces are useful, overusing them can lead to management overhead. Each namespace requires its own set of resources and access controls, which can be time-consuming to manage.

#### Lack of Access Control

Failing to enforce strict access controls can lead to security vulnerabilities. Ensure that access to each namespace is restricted to authorized users and roles.

#### Resource Quotas

Not setting resource quotas can lead to resource exhaustion. Ensure that each namespace has appropriate resource quotas to prevent one namespace from consuming all available resources.

### How to Prevent / Defend

#### Detection

Use tools like `kubectl` to monitor the status of namespaces and resources. Regularly check for unauthorized access and resource usage.

#### Prevention

1. **Strict Access Controls**: Enforce strict access controls using Role-Based Access Control (RBAC). Define roles and bindings to restrict access to specific namespaces.
2. **Resource Quotas**: Set resource quotas for each namespace to prevent resource exhaustion.
3. **Network Policies**: Use network policies to restrict communication between namespaces.

#### Secure Coding Fixes

Here is an example of a vulnerable configuration and a secure configuration:

**Vulnerable Configuration**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: insecure-namespace
```

**Secure Configuration**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: secure-namespace
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: secure-namespace
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: secure-namespace
  name: read-pods
subjects:
- kind: User
  name: alice
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### Conclusion

Using namespaces in Kubernetes provides a powerful mechanism for managing and isolating resources. By logically grouping related resources into namespaces, you can improve manageability and security. Follow best practices and use tools like RBAC and resource quotas to ensure that your namespaces are secure and efficient.

### Practice Labs

For hands-on experience with Kubernetes namespaces, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges for learning about Kubernetes security.
- **kube-hunter**: A tool for hunting security issues in Kubernetes clusters.

These labs provide practical experience in deploying and managing namespaces in a Kubernetes cluster.

---
<!-- nav -->
[[01-Introduction to Kubernetes Namespaces|Introduction to Kubernetes Namespaces]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/26-Kubernetes Namespace Usage And Best Practices/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/26-Kubernetes Namespace Usage And Best Practices/03-Practice Questions & Answers|Practice Questions & Answers]]
