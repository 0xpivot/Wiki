---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## StatefulSets and Deployments

### What Are StatefulSets and Deployments?

StatefulSets and Deployments are two fundamental Kubernetes controllers used to manage pods. Both are essential for ensuring that applications run reliably and efficiently within a Kubernetes cluster. However, they serve different purposes and are suited to different types of workloads.

#### Deployments

Deployments are used for stateless applications, where individual instances can be replaced without any loss of data or functionality. They ensure that a specified number of replicas of a pod are running at any given time. If a pod fails, the Deployment controller automatically replaces it. This makes Deployments ideal for applications such as web servers, where each instance is identical and interchangeable.

**Example:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: nginx:latest
```

In this example, a Deployment named `web-deployment` is created with three replicas. Each replica runs an Nginx container.

#### StatefulSets

StatefulSets, on the other hand, are designed for stateful applications, where each instance has a unique identity and persistent storage. They ensure that each pod has a stable, unique network identifier and persistent storage. This makes StatefulSets suitable for applications such as databases, where each instance holds unique data and cannot be easily replaced.

**Example:**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: db-statefulset
spec:
  serviceName: "db"
  replicas: 3
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
      - name: db
        image: postgres:latest
        volumeMounts:
        - name: db-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: db-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
```

In this example, a StatefulSet named `db-statefulset` is created with three replicas. Each replica runs a PostgreSQL container and mounts a PersistentVolumeClaim for persistent storage.

### How Do They Work Under the Hood?

Both Deployments and StatefulSets use the Kubernetes API to manage pods. When a Deployment or StatefulSet is created, the Kubernetes controller watches for changes and ensures that the desired state is maintained.

#### Deployments

For Deployments, the controller maintains a set of replicas by creating new pods if existing ones fail or are deleted. It also supports rolling updates, allowing you to update the application gradually without downtime.

#### StatefulSets

For StatefulSets, the controller ensures that each pod has a unique network identifier and persistent storage. It also manages the order in which pods are created and destroyed, ensuring that dependencies are respected.

### Why Do We Need Them?

Without these controllers, managing pods would be much more complex and error-prone. Deployments and StatefulSets provide a high-level abstraction that simplifies the management of stateless and stateful applications, respectively.

### Common Pitfalls

One common pitfall is using the wrong controller for the workload. Deployments should be used for stateless applications, while StatefulSets should be used for stateful applications. Mixing them can lead to unexpected behavior and data loss.

### How to Prevent / Defend

To prevent issues, always choose the appropriate controller based on the nature of your application. For stateless applications, use Deployments, and for stateful applications, use StatefulSets. Additionally, ensure that you have proper monitoring and logging in place to detect and respond to issues quickly.

---
<!-- nav -->
[[08-Setting Up an Amazon EKS Cluster|Setting Up an Amazon EKS Cluster]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/08-Deploying Prometheus on EKS Using Operators/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/08-Deploying Prometheus on EKS Using Operators/10-Practice Questions & Answers|Practice Questions & Answers]]
