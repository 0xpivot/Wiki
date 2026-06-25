---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Kubernetes Configuration File Structure Explained

In this section, we will delve into the structure of Kubernetes configuration files, focusing on the metadata, specification, and status components. Understanding these elements is crucial for managing and maintaining Kubernetes clusters effectively.

### Metadata

Metadata in a Kubernetes configuration file contains descriptive information about the resource being defined. This includes labels, annotations, and the name of the resource. Metadata is essential because it helps in identifying and organizing resources within the cluster.

#### Labels and Annotations

Labels are key-value pairs that are attached to objects such as pods, services, and deployments. They are used for identification purposes and can be used to select subsets of objects. For example:

```yaml
metadata:
  name: my-deployment
  labels:
    app: web
    environment: production
```

Annotations, on the other hand, are also key-value pairs but are used for storing arbitrary non-identifying metadata. They are often used by tools and libraries to store additional information:

```yaml
metadata:
  name: my-deployment
  annotations:
    build-date: "2023-10-01"
    version: "1.0.0"
```

### Specification

The specification section defines the desired state of the resource. This is where you specify the configuration details that Kubernetes should enforce. For example, in a deployment, you might define the number of replicas, the container image, and the ports to expose.

#### Example Deployment

Here is an example of a deployment configuration file:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: engine-x
        image: nginx:latest
        ports:
        - containerPort: 80
```

In this example:
- `replicas: 2` specifies that two instances of the pod should be running.
- `selector.matchLabels` ensures that the deployment manages pods labeled with `app: web`.
- `template.spec.containers` defines the container details, including the image and port.

### Status

The status section is automatically generated and updated by Kubernetes. It reflects the current state of the resource, allowing Kubernetes to compare the desired state with the actual state and take corrective actions if necessary.

#### Self-Healing Mechanism

Kubernetes uses the status to implement its self-healing mechanism. If the status indicates that the actual state does not match the desired state, Kubernetes will attempt to reconcile the difference. For example, if one of the replicas in a deployment fails, Kubernetes will automatically start a new replica to maintain the desired state.

#### Example Status Update

Consider the following scenario where a deployment has two replicas specified, but only one is running due to a failure:

```yaml
status:
  replicas: 2
  availableReplicas: 1
  conditions:
  - type: Available
    status: "False"
    reason: MinimumReplicasUnavailable
    message: Deployment does not have minimum availability.
```

In this case, Kubernetes will detect the discrepancy and attempt to start a new replica to restore the desired state.

### Where Does the Status Data Come From?

The status data is derived from the etcd database, which serves as the central store for all cluster state data. etcd is a distributed key-value store that provides reliable and consistent storage for Kubernetes.

#### etcd Overview

etcd is a critical component of the Kubernetes control plane. It stores all the configuration data and state information for the cluster. When a resource is created or updated, the changes are stored in etcd, and Kubernetes continuously monitors etcd to update the status of resources.

#### Example etcd Interaction

When a deployment is created, the configuration is stored in etcd. Kubernetes periodically checks etcd to ensure that the actual state matches the desired state. If there is a mismatch, Kubernetes takes action to correct it.

### Real-World Examples and Security Implications

Recent vulnerabilities and breaches involving Kubernetes highlight the importance of proper configuration and monitoring. For instance, CVE-2021-25742 affected Kubernetes versions prior to 1.21.0, allowing unauthorized access to sensitive information through misconfigured RBAC permissions.

#### Secure Configuration Practices

To prevent such issues, it is crucial to follow secure configuration practices:

1. **RBAC Permissions**: Ensure that roles and role bindings are strictly defined and limited to the minimum required permissions.
2. **Pod Security Policies**: Implement PodSecurityPolicies to restrict what types of pods can run in the cluster.
3. **Network Policies**: Use NetworkPolicies to control traffic flow between pods and external networks.

#### Example Secure Configuration

Here is an example of a secure deployment configuration with RBAC and PodSecurityPolicy:

```yaml
# Deployment configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-secure-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: engine-x
        image: nginx:latest
        ports:
        - containerPort: 80
      securityContext:
        runAsUser: 1000
        runAsGroup: 3000
        fsGroup: 2000

# Role definition
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

# Role binding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: ServiceAccount
  name: default
  apiGroup: ""
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io

# PodSecurityPolicy
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  seLinux:
    rule: RunAsAny
  supplementalGroups:
    rule: RunAsAny
  runAsUser:
    rule: MustRunAs
    ranges:
    - min: 1000
      max: 65535
  fsGroup:
    rule: MustRunAs
    ranges:
    - min: 1000
      max:  65535
  volumes:
  - configMap
  - secret
  - emptyDir
  - hostPath
  - persistentVolumeClaim
```

### How to Prevent / Defend

#### Detection

Regularly monitor the cluster for discrepancies between the desired and actual states. Tools like Prometheus and Grafana can be used to visualize and alert on such issues.

#### Prevention

1. **Strict RBAC**: Define roles and role bindings with minimal permissions.
2. **PodSecurityPolicies**: Enforce strict policies to limit pod capabilities.
3. **Network Policies**: Control traffic flow to prevent unauthorized access.

#### Secure Coding Fixes

Compare the insecure and secure configurations side by side:

**Insecure Configuration**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-insecure-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: engine-x
        image: nginx:latest
        ports:
        - containerPort: 80
```

**Secure Configuration**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-secure-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: engine-x
        image: nginx:latest
        ports:
        - containerPort: 80
      securityContext:
        runAsUser: 1000
        runAsGroup: 3000
        fsGroup: 2000
```

### Hands-On Labs

For practical experience with Kubernetes configuration and security, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges to learn about Kubernetes security.
- **kube-hunter**: A tool for hunting down security issues in Kubernetes clusters.

These labs provide real-world scenarios and challenges to help you master Kubernetes configuration and security.

### Conclusion

Understanding the structure of Kubernetes configuration files, including metadata, specification, and status, is fundamental to effective cluster management. By following secure configuration practices and regularly monitoring the cluster, you can ensure that your Kubernetes environment remains robust and secure.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/24-Kubernetes Configuration File Structure Explained/01-Introduction to Kubernetes Configuration Files|Introduction to Kubernetes Configuration Files]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/24-Kubernetes Configuration File Structure Explained/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/24-Kubernetes Configuration File Structure Explained/03-Practice Questions & Answers|Practice Questions & Answers]]
