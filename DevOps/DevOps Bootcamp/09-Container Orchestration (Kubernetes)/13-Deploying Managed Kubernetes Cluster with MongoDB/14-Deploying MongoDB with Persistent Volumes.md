---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Deploying MongoDB with Persistent Volumes

MongoDB is a popular NoSQL database that can be deployed in a Kubernetes cluster using Persistent Volumes for data persistence. In this section, we will cover the steps to deploy MongoDB with Persistent Volumes.

### What is MongoDB?

MongoDB is a document-oriented NoSQL database that stores data in JSON-like documents with dynamic schemas. It provides high performance, availability, and easy scalability.

### Why Use MongoDB in Kubernetes?

Deploying MongoDB in Kubernetes allows for easy scaling, automated recovery, and consistent state management across multiple nodes. Persistent Volumes ensure that data remains intact even if a Pod is rescheduled.

### How to Deploy MongoDB

To deploy MongoDB in Kubernetes, you need to create a StatefulSet and a PersistentVolumeClaim for each replica.

#### Step 1: Create a PersistentVolumeClaim

First, create a PersistentVolumeClaim for each replica:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongodb-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

#### Step 2: Create a StatefulSet

Next, create a StatefulSet to manage the MongoDB replicas:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
spec:
  serviceName: "mongodb"
  replicas: 3
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:latest
        ports:
        - containerPort: 27017
        volumeMounts:
        - name: mongodb-pv
          mountPath: /data/db
  volumeClaimTemplates:
  - metadata:
      name: mongodb-pv
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
```

### How to Prevent / Defend

#### Detection
- Monitor the Kubernetes API for unauthorized changes to StatefulSets and PersistentVolumeClaims.
- Use tools like `kube-bench` to check for misconfigurations.

#### Prevention
- Ensure proper RBAC policies are in place.
- Use Kubernetes secrets to store sensitive information securely.

#### Secure Code Fix
- Always validate input and ensure proper access controls are in place.

### Real--World Examples

- **CVE-2021-25741**: A vulnerability in Kubernetes allowed attackers to escalate privileges by manipulating Persistent Volumes. Ensure your Kubernetes version is up-to-date and apply necessary patches.

---
<!-- nav -->
[[13-Deploying MongoDB with Helm|Deploying MongoDB with Helm]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/13-Deploying Managed Kubernetes Cluster with MongoDB/00-Overview|Overview]] | [[15-Exposing Internal Services Using Ingress|Exposing Internal Services Using Ingress]]
