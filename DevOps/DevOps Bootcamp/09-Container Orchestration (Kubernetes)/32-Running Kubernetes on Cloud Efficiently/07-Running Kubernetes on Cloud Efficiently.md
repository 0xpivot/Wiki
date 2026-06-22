---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Running Kubernetes on Cloud Efficiently

### Introduction to Kubernetes Clusters

Kubernetes (often abbreviated as K8s) is an open-source system for automating deployment, scaling, and management of containerized applications. It was originally designed by Google and is now maintained by the Cloud Native Computing Foundation. A Kubernetes cluster consists of a set of worker machines, called nodes, that run containerized applications. Every cluster has at least one node.

To get started with Kubernetes, you typically create a cluster on a cloud provider such as AWS, GCP, or Linode. Once the cluster is up and running, you can connect to it using `kubectl`, the command-line tool for interacting with the Kubernetes API.

#### Connecting to the Cluster Using `kubectl`

The first step after setting up your Kubernetes cluster is to connect to it using `kubectl`. This tool allows you to manage your cluster and deploy applications.

```bash
# Example of connecting to a Kubernetes cluster using kubectl
kubectl get nodes
```

This command lists all the nodes in your cluster. Each node runs a container runtime (such as Docker) and is managed by the Kubernetes control plane.

### Deploying Applications and Services

Once connected, you can deploy applications and services to the cluster. For instance, you might want to deploy a MongoDB database for a Node.js application. In Kubernetes, you define your applications using YAML files that describe the desired state of your cluster.

#### Example Deployment YAML

Here’s an example of a YAML file for deploying a MongoDB database:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb-deployment
spec:
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
```

This YAML defines a deployment with three replicas of a MongoDB container. Each replica will run the latest version of the MongoDB image.

### Data Persistence in Kubernetes

Applications often require data persistence to store and retrieve data reliably. In Kubernetes, data persistence is achieved through Persistent Volumes (PVs) and Persistent Volume Claims (PVCs).

#### Persistent Volumes (PVs)

A Persistent Volume (PV) is a piece of storage in the cluster that has been provisioned by an administrator or dynamically using Storage Classes. PVs are resources in the cluster just like a node is a cluster resource.

#### Persistent Volume Claims (PVCs)

A Persistent Volume Claim (PVC) is a request for storage by a user. It is similar to a Pod. Pods consume node resources and PVCs consume PV resources. PVCs are defined in YAML files and are bound to PVs.

#### Example PVC YAML

Here’s an example of a PVC YAML file:

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

This PVC requests 10 GiB of storage with read-write access.

### Configuring Storage in Kubernetes

Kubernetes does not automatically configure storage for you. You need to create and configure the storage yourself. There are several types of storage options available:

- **Cloud Storage Providers**: Services like AWS EBS, GCP Persistent Disks, Azure Disk Storage.
- **NFS**: Network File System.
- **Local Storage**: Storage attached directly to the nodes.

#### Example: Configuring Local Storage

Here’s an example of configuring local storage on a node:

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
```

This PV uses local storage on the node at `/mnt/data`.

### Dynamic Volume Provisioning

Dynamic volume provisioning allows Kubernetes to automatically create new PersistentVolumes based on PersistentVolumeClaims. This is typically done using Storage Classes.

#### Example: Using Linode Block Storage

Linode provides block storage that can be used for dynamic volume provisioning. Here’s an example of a Storage Class using Linode block storage:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: linode-block-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
parameters:
  type: linode-block-storage
```

This Storage Class uses Linode block storage for dynamic volume provisioning.

### Attaching Volumes to Pods

Once you have configured the storage, you can attach these volumes to your pods. This is done by specifying the PVC in the pod specification.

#### Example: Attaching PVC to a Pod

Here’s an example of a pod specification that attaches a PVC:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mongodb-pod
spec:
  containers:
  - name: mongodb
    image: mongo:latest
    volumeMounts:
    - mountPath: /data/db
      name: mongodb-pvc
  volumes:
  - name: mongodb-p
    persistentVolumeClaim:
      claimName: mongodb-pvc
```

This pod mounts the PVC to the `/data/db` directory in the container.

### How to Prevent / Defend

#### Detection

To detect misconfigurations or vulnerabilities related to storage in Kubernetes, you can use tools like `kube-bench` and `kubescape`. These tools help ensure that your cluster is configured securely.

#### Prevention

1. **Use Secure Storage Classes**: Ensure that your Storage Classes are configured securely. For example, use encryption for sensitive data.
2. **Regular Audits**: Regularly audit your cluster configurations and storage settings to identify and mitigate risks.
3. **Secure Access Controls**: Implement strict access controls for your storage resources to prevent unauthorized access.

#### Secure Coding Fixes

Here’s an example of a vulnerable and secure version of a PVC YAML:

**Vulnerable Version**

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

**Secure Version**

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
  storageClassName: encrypted-storage
```

In the secure version, we specify a secure Storage Class (`encrypted-storage`) that ensures data encryption.

### Real-World Examples

#### Recent CVEs and Breaches

One notable breach involving Kubernetes storage was the 2021 incident where a misconfigured Kubernetes cluster led to the exposure of sensitive data. This highlights the importance of proper configuration and access controls.

### Practice Labs

For hands-on practice with Kubernetes and storage, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A project that includes challenges related to Kubernetes and storage.

These labs provide practical experience in configuring and securing Kubernetes clusters and their storage resources.

### Conclusion

Running Kubernetes on the cloud efficiently requires careful planning and configuration, especially when it comes to data persistence. By understanding the concepts of Persistent Volumes, Persistent Volume Claims, and dynamic volume provisioning, you can ensure that your applications have reliable and secure storage. Always follow best practices for detection and prevention to secure your Kubernetes environment.

---
<!-- nav -->
[[06-Introduction to Running Kubernetes on Cloud|Introduction to Running Kubernetes on Cloud]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/32-Running Kubernetes on Cloud Efficiently/00-Overview|Overview]] | [[08-Session Stickiness in Load Balancing|Session Stickiness in Load Balancing]]
