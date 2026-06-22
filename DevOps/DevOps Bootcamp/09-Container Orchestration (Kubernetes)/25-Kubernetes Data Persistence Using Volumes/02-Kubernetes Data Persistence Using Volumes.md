---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Kubernetes Data Persistence Using Volumes

In the context of Kubernetes, data persistence is a critical aspect of managing stateful applications. One of the primary mechanisms for achieving this is through the use of volumes. Volumes provide a way to store and manage data that persists beyond the lifetime of individual pods. This chapter delves into the intricacies of Kubernetes volumes, their types, and how they can be effectively used to ensure data persistence.

### Understanding Persistent Volumes (PVs)

Persistent Volumes (PVs) are storage resources in Kubernetes that are provisioned independently of any individual pod. They are analogous to physical storage devices in a traditional computing environment. PVs are not bound to a specific namespace; instead, they are globally accessible across the entire cluster. This means that any pod within any namespace can potentially access a PV, provided it has the appropriate permissions and configuration.

#### Attributes and Storage Backends

The attributes of a PV depend on the underlying storage backend. Kubernetes supports over 25 different storage backends, including:

- **Local Storage**: Storage that resides on the node itself.
- **Network-Attached Storage (NAS)**: Storage that is accessible via a network protocol.
- **Block Storage**: Storage that provides raw block devices.
- **Cloud Storage**: Storage services provided by cloud providers such as AWS EBS, Google Cloud Persistent Disks, and Azure Managed Disks.

Each storage backend has its own set of attributes and configurations. For example, local storage might have additional node affinity attributes, which specify that the PV should only be used by pods scheduled on the same node.

```mermaid
graph TD
    A[Persistent Volume (PV)] --> B[Storage Backend]
    B --> C{Local}
    B --> D{Network-Attached}
    B --> E{Block}
    B --> F{Cloud}
```

### Local vs. Remote Volumes

Volumes in Kubernetes can be categorized into two main types: local and remote.

#### Local Volumes

Local volumes are storage resources that reside on the node itself. These volumes are tied to the specific node where they are located. While local volumes can be useful for certain use cases, they come with significant limitations:

1. **Node Affinity**: Pods using local volumes must be scheduled on the same node where the volume is located. This can limit the flexibility of pod scheduling.
2. **Cluster Crash Scenarios**: If the node where the local volume is located fails, the data stored in that volume may be lost unless proper backups are in place.

#### Remote Volumes

Remote volumes, on the other hand, are storage resources that are accessible via a network. These volumes are not tied to a specific node and can be accessed by pods running on any node in the cluster. Remote volumes are generally preferred for stateful applications, especially databases, due to the following advantages:

1. **Node Independence**: Pods can be scheduled on any node, and the volume remains accessible regardless of the node.
2. **High Availability**: In the event of a node failure, the data stored in remote volumes remains intact and can be accessed by pods scheduled on other nodes.

### Creating Persistent Volumes

Persistent volumes are created and managed separately from pods. They can be manually provisioned or dynamically provisioned based on storage classes. Here’s an example of a manually provisioned PV using local storage:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: local-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /mnt/data
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - node1
```

This PV is configured to use local storage on `node1`. The `hostPath` field specifies the path on the node where the storage is located, and the `nodeAffinity` field ensures that the PV can only be used by pods scheduled on `node1`.

### Persistent Volume Claims (PVCs)

Persistent Volume Claims (PVCs) are requests for storage resources by pods. PVCs are namespace-scoped and can be dynamically provisioned based on storage classes. Here’s an example of a PVC:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

This PVC requests 10Gi of storage with `ReadWriteOnce` access mode. When a pod requests this PVC, Kubernetes will bind it to an available PV that meets the specified criteria.

### Example: Deploying a Stateful Application with Persistent Volumes

Let’s walk through an example of deploying a stateful application, such as a MySQL database, using persistent volumes.

#### Step 1: Create a Persistent Volume

First, create a PV using a cloud storage service like AWS EBS:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: ebs-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  awsElasticBlockStore:
    volumeID: vol-0123456789abcdef0
    fsType: ext4
```

#### Step 2: Create a Persistent Volume Claim

Next, create a PVC that requests the PV:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

#### Step 3: Deploy the StatefulSet

Finally, deploy a StatefulSet that uses the PVC:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: "mysql"
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:5.7
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: mysql-persistent-storage
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: mysql-persistent-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
```

### Pitfalls and Best Practices

#### Node Affinity and Pod Scheduling

When using local volumes, it is crucial to ensure that pods are scheduled on the correct node. Misconfiguration can lead to pod scheduling failures or data loss. Always verify the node affinity settings and ensure that the pod scheduler respects these constraints.

#### High Availability and Data Redundancy

For mission-critical applications, consider using remote volumes and implementing data redundancy strategies. This can involve using multiple replicas of the volume across different nodes or regions to ensure high availability.

### How to Prevent / Defend

#### Detection

Regularly monitor the health and status of your PVs and PVCs. Use tools like `kubectl describe` to check the status of volumes and claims:

```sh
kubectl describe pv <pv-name>
kubectl describe pvc <pvc-name>
```

#### Prevention

1. **Use Remote Volumes**: Prefer remote volumes over local volumes for stateful applications to ensure high availability and data redundancy.
2. **Implement Backup Strategies**: Regularly back up data stored in PVs to prevent data loss in case of node or cluster failures.
3. **Secure Access**: Ensure that PVCs and PVs are properly secured and only accessible to authorized pods. Use RBAC (Role-Based Access Control) to manage access to storage resources.

#### Secure Coding Fixes

Compare the insecure and secure versions of a PVC configuration:

**Insecure Version:**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: insecure-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

**Secure Version:**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: secure-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  volumeName: secure-pv
```

In the secure version, the `volumeName` field explicitly binds the PVC to a specific PV, ensuring that the PVC is only used with the intended volume.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example is the breach of a Kubernetes cluster in 2021, where misconfigured PVCs led to unauthorized access to sensitive data stored in PVs. This highlights the importance of proper configuration and access control for storage resources.

### Practice Labs

To gain hands-on experience with Kubernetes data persistence using volumes, consider the following practice labs:

- **Kubernetes Goat**: A hands-on lab that covers various aspects of Kubernetes security, including data persistence.
- **OWASP WrongSecrets**: A series of challenges that focus on securing secrets and data in Kubernetes environments.

These labs provide practical scenarios and exercises to reinforce the concepts covered in this chapter.

### Conclusion

Understanding and effectively using Kubernetes volumes is essential for managing stateful applications in a Kubernetes cluster. By leveraging the right types of volumes and implementing best practices, you can ensure high availability, data redundancy, and secure access to your storage resources.

---
<!-- nav -->
[[01-Introduction to Kubernetes Data Persistence Using Volumes|Introduction to Kubernetes Data Persistence Using Volumes]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/25-Kubernetes Data Persistence Using Volumes/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/25-Kubernetes Data Persistence Using Volumes/03-Practice Questions & Answers|Practice Questions & Answers]]
