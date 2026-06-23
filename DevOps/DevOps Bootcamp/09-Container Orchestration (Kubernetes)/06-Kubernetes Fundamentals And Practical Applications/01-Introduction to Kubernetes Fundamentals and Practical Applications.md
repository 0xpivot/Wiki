---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Kubernetes Fundamentals and Practical Applications

Kubernetes, often abbreviated as K8s, is an open-source system for automating deployment, scaling, and management of containerized applications. It was originally designed by Google and is now maintained by the Cloud Native Computing Foundation. Kubernetes provides a platform for automating deployment and scaling of containerized applications, and manages the health of those applications.

### Why Kubernetes?

Kubernetes addresses several challenges faced by modern applications:

1. **Scalability**: Kubernetes allows you to scale applications horizontally across multiple nodes.
2. **Resilience**: It ensures that applications remain available even in the face of hardware failures.
3. **Resource Management**: Kubernetes optimizes resource usage by efficiently scheduling containers across nodes.
4. **Rolling Updates and Rollbacks**: It supports rolling updates and rollbacks, ensuring minimal downtime during deployments.

### Key Concepts

Before diving into practical applications, it’s essential to understand some key concepts:

1. **Pods**: Pods are the smallest deployable units in Kubernetes. A pod can contain one or more containers.
2. **Nodes**: Nodes are the worker machines in a Kubernetes cluster. They can be physical or virtual machines.
3. **Clusters**: A cluster consists of a set of nodes that run containerized applications managed by Kubernetes.
4. **Services**: Services provide a stable IP address and DNS name for a set of pods.
5. **Deployments**: Deployments manage the lifecycle of pods and ensure that a specified number of replicas are running.

### Setting Up a Kubernetes Cluster

To set up a Kubernetes cluster, you can use tools like `minikube` for local development or cloud providers like AWS, GCP, or Azure for production environments.

#### Example: Setting Up a Local Cluster with Minikube

```bash
# Install minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb
sudo dpkg -i minikube_latest_amd64.deb

# Start minikube
minikube start --driver=docker

# Access the dashboard
minikube dashboard
```

### Deploying a Microservices Application

In this section, we will deploy a microservices application into a Kubernetes cluster step by step.

#### Step 1: Define the Application

Let’s assume we have a simple microservices application consisting of two services: `frontend` and `backend`.

#### Step 2: Create Deployment Files

We will create `Deployment` and `Service` definitions for both services.

```yaml
# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: myregistry/frontend:latest
        ports:
        - containerPort: 80
---
# frontend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  selector:
    app: frontend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: LoadBalancer
```

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: myregistry/backend:latest
        ports:
        - containerPort: 8080
---
# backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  selector:
    app: backend
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: ClusterIP
```

#### Step 3: Apply the Definitions

```bash
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml
```

### Production and Security Best Practices

Now that we have deployed our application, let’s improve our configuration files with production and security best practices.

#### 1. Pod Security Policies

Pod Security Policies (PSPs) enforce security rules at the pod level. They can restrict which images can be used, whether privileged containers are allowed, and more.

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
  - ALL
  readOnlyRootFilesystem: true
  seLinux:
    rule: RunAsAny
  runAsUser:
    rule: MustRunAsNonRoot
  supplementalGroups:
    rule: MustRunAs
    ranges:
    - min: 1
      max: 65535
  fsGroup:
    rule: MustRunAs
    ranges:
    - min: 1
      max: 65535
  volumes:
  - configMap
  - secret
  - emptyDir
  - hostPath
  - persistentVolumeClaim
```

#### 2. Network Policies

Network Policies define how groups of pods are allowed to communicate with each other and other network endpoints.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  ingress: []
```

#### 3. Secrets Management

Use Kubernetes secrets to store sensitive data securely.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: dXNlcm5hbWU=
  password: cGFzc3dvcmQ=
```

### Creating a Common Helm Chart

Helm is a package manager for Kubernetes that simplifies the deployment and management of applications. We will create a common Helm chart as a configuration blueprint for all our microservices.

#### Step 1: Initialize a Helm Chart

```bash
helm create mychart
```

#### Step 2: Customize the Chart

Edit the `Chart.yaml`, `values.yaml`, and `templates` directory to define your application.

```yaml
# Chart.yaml
apiVersion: v2
name: mychart
description: A Helm chart for my application
version: 0.1.0
appVersion: "1.0"
```

```yaml
# values.yaml
replicaCount: 3
image:
  repository: myregistry/frontend
  tag: latest
service:
  type: LoadBalancer
  port: 80
```

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-deployment
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
    spec:
      containers:
      - name: {{ .Release.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: 80
```

```yaml
# templates/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-service
spec:
  selector:
    app: {{ .Release.Name }}
  ports:
    - protocol: TCP
      port: {{ .Values.service.port }}
      targetPort: 80
  type: {{ .Values.service.type }}
```

#### Step 3: Validate and Deploy the Chart

```bash
helm lint mychart
helm install myrelease mychart
```

### Authorization in Kubernetes

Authorization in Kubernetes is managed through Role-Based Access Control (RBAC). RBAC allows you to define roles and permissions for users and groups.

#### Roles and Cluster Roles

Roles are namespaced, meaning they apply to a specific namespace. Cluster roles are cluster-wide and apply to all namespaces.

```yaml
# role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

```yaml
# clusterrole.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

#### Role Bindings and Cluster Role Bindings

Role bindings bind roles to subjects (users, groups, or service accounts).

```yaml
# rolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: Group
  name: managers
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

```yaml
# clusterrolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-pods-global
subjects:
- kind: Group
  name: managers
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

#### Service Accounts

Service accounts are used to authenticate and authorize actions within the cluster.

```yaml
# serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  namespace: default
```

### Real-World Examples and CVEs

#### CVE-2021-25741: Kubernetes API Server Privilege Escalation

This CVE affects Kubernetes versions prior to 1.21.4, 1.20.12, and 1.19.15. An attacker could exploit this vulnerability to escalate privileges and gain unauthorized access to the cluster.

**How to Prevent / Defend:**

1. **Update to the Latest Version**: Ensure your Kubernetes cluster is updated to the latest version.
2. **Enable Network Policies**: Restrict network traffic to only necessary endpoints.
3. **Use Pod Security Policies**: Enforce strict security policies to prevent privilege escalation.

#### CVE-2021-25742: Kubernetes API Server Denial of Service

This CVE affects Kubernetes versions prior to 1.21.4, 1.20.12, and 1.19.15. An attacker could exploit this vulnerability to cause a denial of service by sending malicious requests to the API server.

**How to Prevent / Defend:**

1. **Update to the Latest Version**: Ensure your Kubernetes cluster is updated to the latest version.
2. **Enable Network Policies**: Restrict network traffic to only necessary endpoints.
3. **Monitor API Server Logs**: Regularly monitor logs for suspicious activity.

### Conclusion

By following the steps outlined in this chapter, you will have a thorough understanding of Kubernetes and be prepared to use it in your projects. You will learn how to deploy and manage microservices applications, implement security best practices, and use Helm charts for efficient deployment. Additionally, you will understand the importance of authorization and how to prevent and defend against common vulnerabilities.

### Practice Labs

For hands-on experience with Kubernetes, consider the following labs:

- **Kubernetes Goat**: A Kubernetes-themed capture-the-flag (CTF) game designed to teach Kubernetes security.
- **OWASP WrongSecrets**: A CTF game focused on Kubernetes and container security.
- **kube-hunter**: A tool for hunting down security issues in Kubernetes clusters.

These labs will help you solidify your understanding and gain practical experience with Kubernetes.

### Further Reading

- **Kubernetes Documentation**: Official documentation for Kubernetes.
- **Helm Documentation**: Official documentation for Helm.
- **CNCF Security Working Group**: Resources and guidelines for securing Kubernetes clusters.

By mastering these concepts and practices, you will be well-equipped to handle complex Kubernetes deployments and ensure the security and reliability of your applications.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/06-Kubernetes Fundamentals And Practical Applications/00-Overview|Overview]] | [[02-Introduction to Kubernetes|Introduction to Kubernetes]]
