---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Kubernetes Data Persistence Using Volumes

In this section, we delve into the critical aspect of data persistence in Kubernetes using volumes. This is essential for applications that require data to be retained across pod restarts, such as databases, logs, and configurations. We will explore three key components of Kubernetes storage: Persistent Volumes (PVs), Persistent Volume Claims (PVCs), and Storage Classes. Each component plays a crucial role in ensuring data persistence and availability within a Kubernetes cluster.

### What is Data Persistence?

Data persistence refers to the ability of an application to retain its data across different lifecycle events, such as pod restarts, node failures, or even cluster-wide disruptions. Without proper data persistence mechanisms, data stored in pods would be lost whenever the pod is terminated or restarted. This is particularly problematic for stateful applications like databases, where data integrity and availability are paramount.

### Why is Data Persistence Important?

Consider a scenario where you have a MySQL database pod that your application uses. As users interact with the application, data gets added, updated, and deleted in the database. If the pod is restarted due to maintenance, scaling, or a node failure, all the changes made to the database would be lost unless the data is persisted outside the pod’s lifecycle. This could lead to significant data loss and service disruption.

### How Does Kubernetes Handle Data Persistence?

Kubernetes provides several mechanisms to handle data persistence, including:

1. **Persistent Volumes (PVs)**: These are storage resources that are provisioned by an administrator or dynamically based on the specifications provided by a Storage Class.
2. **Persistent Volume Claims (PVCs)**: These are requests for storage by users that consume the storage provided by PVs.
3. **Storage Classes**: These define the type of storage to be used and the parameters for provisioning PVs.

Let's explore each of these components in detail.

### Persistent Volumes (PVs)

A Persistent Volume (PV) is a piece of storage in the cluster that has been provisioned by an administrator or dynamically based on the specifications provided by a Storage Class. PVs are resources in the cluster just like a node is a resource in the cluster.

#### What is a PV?

A PV is a volume plugin that is bound to a particular storage system. It has a specific size and access modes (e.g., ReadWriteOnce, ReadOnlyMany, ReadWriteMany). PVs can be backed by various types of storage, such as local storage, NFS, iSCSI, or cloud-based storage services like AWS EBS, GCP Persistent Disks, or Azure Disk.

#### Why Use PVs?

PVs provide a way to manage storage resources independently of the pods that use them. This allows for more flexible and scalable storage management, especially in large clusters where multiple teams might be using the same storage infrastructure.

#### How to Create a PV

To create a PV, you define a YAML manifest that specifies the storage details. Here is an example of a PV definition:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /data/pv
```

This PV is backed by a host path on the node where the PV is created. The `capacity` field specifies the size of the PV, and the `accessModes` field defines the access mode for the PV.

#### Access Modes

PVs support the following access modes:

- **ReadWriteOnce**: The volume can be mounted as read-write by a single node.
- **ReadOnlyMany**: The volume can be mounted as read-only by many nodes.
- **ReadWriteMany**: The volume can be mounted as read-write by many nodes.

The choice of access mode depends on the type of storage being used and the requirements of the application.

### Persistent Volume Claims (PVCs)

A Persistent Volume Claim (PVC) is a request for storage by a user. It is a request for a certain amount of storage with specific access modes. PVCs are consumed by pods and are bound to PVs.

#### What is a PVC?

A PVC is a request for storage that is fulfilled by a PV. It is a way for users to request storage without having to know the specifics of the underlying storage infrastructure. PVCs are defined in YAML manifests and are associated with a specific namespace.

#### Why Use PVCs?

PVCs provide a way for users to request storage without having to worry about the specifics of the underlying storage infrastructure. This abstraction allows for more flexible and scalable storage management, especially in large clusters where multiple teams might be using the same storage infrastructure.

#### How to Create a PVC

To create a PVC, you define a YAML manifest that specifies the storage requirements. Here is an example of a PVC definition:

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
      storage: 12Gi
  storageClassName: manual
```

This PVC requests 12Gi of storage with the `ReadWriteOnce` access mode. The `storageClassName` field specifies the Storage Class to be used for provisioning the PV.

### Storage Classes

A Storage Class is a way to define the type of storage to be used and the parameters for provisioning PVs. Storage Classes allow for dynamic provisioning of PVs based on the specifications provided by a PVC.

#### What is a Storage Class?

A Storage Class is a way to define the type of storage to be used and the parameters for provisioning PVs. It allows for dynamic provisioning of PVs based on the specifications provided by a PVC. Storage Classes can be used to define different types of storage, such as SSD, HDD, or cloud-based storage services.

#### Why Use Storage Classes?

Storage Classes provide a way to define the type of storage to be used and the parameters for provisioning PVs. This allows for more flexible and scalable storage management, especially in large clusters where multiple teams might be using the same storage infrastructure.

#### How to Create a Storage Class

To create a Storage Class, you define a YAML manifest that specifies the storage parameters. Here is an example of a Storage Class definition:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: kubernetes.io/aws-ebs
parameters:
  type: io1
  iopsPerGB: "10"
  fsType: ext4
reclaimPolicy: Delete
allowVolumeExpansion: true
mountOptions:
  - debug
volumeBindingMode: Immediate
```

This Storage Class defines the parameters for provisioning PVs using AWS EBS. The `provisioner` field specifies the provisioner to be used, and the `parameters` field specifies the storage parameters.

### Example: MySQL Database with Persistent Storage

Let's consider a scenario where you have a MySQL database pod that your application uses. To ensure data persistence, you can use PVs, PVCs, and Storage Classes.

#### Step 1: Define the PV

First, define a PV that will be used to store the MySQL data. Here is an example of a PV definition:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mysql-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /data/mysql
```

#### Step 2: Define the PVC

Next, define a PVC that will be used to request the PV. Here is an example of a PVC definition:

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
  storageClassName: manual
```

#### Step 3: Define the Storage Class

Define a Storage Class that will be used to provision the PV. Here is an example of a Storage Class definition:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: manual
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
```

#### Step 4: Define the MySQL Deployment

Finally, define a deployment for the MySQL database that uses the PVC. Here is an example of a deployment definition:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql-deployment
spec:
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
        - name: mysql-storage
          mountPath: /var/lib/mysql
      volumes:
      - name: mysql-storage
        persistentVolumeClaim:
          claimName: mysql-pvc
```

### Diagram: Kubernetes Data Persistence Architecture

Here is a mermaid diagram illustrating the architecture of Kubernetes data persistence using volumes:

```mermaid
graph TB
    A[Application Pod] --> B[Persistent Volume Claim (PVC)]
    B --> C[Persistent Volume (PV)]
    C --> D[Storage System]
    E[Storage Class] --> C
```

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Incorrect Access Modes**: Ensure that the access modes specified in the PV and PVC match the requirements of the application.
2. **Insufficient Storage Capacity**: Ensure that the storage capacity specified in the PV and PVC is sufficient for the application.
3. **Incorrect Storage Class**: Ensure that the Storage Class specified in the PVC matches the requirements of the application.

#### Best Practices

1. **Use Dynamic Provisioning**: Use dynamic provisioning to automatically provision PVs based on the specifications provided by a PVC.
2. **Use Multiple Storage Classes**: Use multiple Storage Classes to define different types of storage, such as SSD, HDD, or cloud-based storage services.
3. **Monitor Storage Usage**: Monitor the usage of storage resources to ensure that the storage capacity is sufficient for the application.

### Real-World Examples

#### Example: CVE-2021-25741

CVE-2021-25741 is a vulnerability in Kubernetes that allows an attacker to gain unauthorized access to sensitive data stored in PVs. This vulnerability was caused by a flaw in the way Kubernetes handles PVs and PVCs.

#### How to Prevent / Defend

1. **Secure Storage**: Ensure that the storage system used for PVs is secure and protected against unauthorized access.
2. **Monitor Access**: Monitor access to PVs and PVCs to detect any unauthorized access attempts.
3. **Use Encryption**: Use encryption to protect sensitive data stored in PVs.

### Conclusion

In this section, we explored the critical aspect of data persistence in Kubernetes using volumes. We covered the three key components of Kubernetes storage: Persistent Volumes (PVs), Persistent Volume Claims (PVCs), and Storage Classes. We also provided a detailed example of how to use these components to ensure data persistence for a MySQL database pod. Finally, we discussed common pitfalls and best practices for using Kubernetes data persistence, and provided real-world examples of vulnerabilities and how to prevent them.

### Practice Labs

For hands-on practice with Kubernetes data persistence, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A hands-on lab for learning Kubernetes security and data persistence.
- **kube-hunter**: A tool for hunting down security issues in Kubernetes clusters, including data persistence.

These labs provide a practical way to learn and apply the concepts covered in this section.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/25-Kubernetes Data Persistence Using Volumes/00-Overview|Overview]] | [[02-Kubernetes Data Persistence Using Volumes|Kubernetes Data Persistence Using Volumes]]
