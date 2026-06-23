---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Kubernetes Clusters and Deployment

### What is Kubernetes?

Kubernetes, often abbreviated as K8s, is an open-source system for automating deployment, scaling, and management of containerized applications. It was originally designed by Google and is now maintained by the Cloud Native Computing Foundation. Kubernetes provides a framework for running distributed systems resiliently. It manages workloads and services, making it easier to scale and maintain applications.

### Why Use Kubernetes?

Kubernetes offers several advantages:

1. **Scalability**: Kubernetes allows you to scale your application automatically based on demand.
2. **Resilience**: It ensures that your application remains available even if some nodes fail.
3. **Ease of Management**: Kubernetes simplifies the management of complex applications by providing tools to deploy, manage, and scale applications.

### Setting Up a Kubernetes Cluster on Linode

In this section, we will walk through the process of setting up a Kubernetes cluster on the Linode platform and connecting to it from your local machine.

#### Creating a Kubernetes Cluster on Linode

To create a Kubernetes cluster on Linode, follow these steps:

1. **Sign Up for Linode**: First, sign up for a Linode account if you haven't already.
2. **Create a Kubernetes Cluster**:
    - Navigate to the Linode dashboard.
    - Click on "Kubernetes" in the left-hand menu.
    - Click "Add Cluster".
    - Configure your cluster settings such as the number of nodes, node type, and region.
    - Click "Create".

Once the cluster is created, you will see the nodes listed as "Running" and "Ready". This indicates that your Kubernetes cluster is up and running.

#### Accessing the Kubernetes Cluster from Your Local Machine

To access the Kubernetes cluster from your local machine, you need to download the `kubeconfig` file. This file contains the necessary credentials and certificates to connect to the remote Kubernetes cluster.

1. **Download the `kubeconfig` File**:
    - In the Linode dashboard, navigate to your Kubernetes cluster.
    - Click on the "Config" tab.
    - Download the `kubeconfig` file.

2. **Set the `kubeconfig` File as an Environmental Variable**:
    - Open your terminal.
    - Navigate to the directory where you downloaded the `kubeconfig` file.
    - Set the `kubeconfig` file as an environmental variable using the following command:
      ```sh
      export KUBECONFIG=<path_to_kubeconfig_file>
      ```

3. **Verify the Connection**:
    - Run the following command to verify that you are connected to the remote Kubernetes cluster:
      ```sh
      kubectl get nodes
      ```
    - You should see the list of nodes in your cluster, indicating that you are successfully connected.

### Example of Connecting to a Kubernetes Cluster

Let's go through a detailed example of connecting to a Kubernetes cluster on Linode.

#### Step 1: Download the `kubeconfig` File

Assume you have downloaded the `kubeconfig` file to `/home/user/downloads/kubeconfig`.

```sh
cd /home/user/downloads
```

#### Step 2: Set the `kubeconfig` File as an Environmental Variable

```sh
export KUBECONFIG=/home/user/downloads/kubeconfig
```

#### Step 3: Verify the Connection

```sh
kubectl get nodes
```

Expected output:

```plaintext
NAME          STATUS   ROLES    AGE   VERSION
node-1        Ready    <none>   1h    v1.23.1
node-2        Ready    <none>   1h    v1.23.1
```

This output confirms that you are connected to the remote Kubernetes cluster.

### Deploying MongoDB Stateful Set in the Cluster

Now that we have successfully connected to the Kubernetes cluster, let's proceed to deploy a MongoDB stateful set.

#### What is a Stateful Set?

A Stateful Set is a Kubernetes resource that manages stateful applications. It ensures that each pod has a unique identity and persistent storage. This is particularly useful for databases like MongoDB, which require consistent data storage across restarts.

#### Two Ways to Deploy MongoDB Stateful Set

There are two primary methods to deploy a MongoDB stateful set:

1. **Using Configuration Files**: Create YAML configuration files to define the stateful set and associated resources.
2. **Using Helm Charts**: Use Helm, a package manager for Kubernetes, to deploy pre-configured charts.

### Method 1: Using Configuration Files

#### Step 1: Create the Stateful Set Configuration File

Create a YAML file named `mongodb-statefulset.yaml` with the following content:

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
        - name: mongodb-persistent-storage
          mountPath: /data/db
  volumeClaimTemplates:
  - metadata:
      name: mongodb-persistent-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
```

#### Step 2: Apply the Configuration File

Apply the configuration file using the following command:

```sh
kubectl apply -f mongodb-statefulset.yaml
```

#### Step 3: Verify the Deployment

Check the status of the pods:

```sh
kubectl get pods
```

Expected output:

```plaintext
NAME       READY   STATUS    RESTARTS   AGE
mongodb-0  1/1     Running   0          1m
mongodb-1  1/1     Running   0          1m
mongodb-2  1/1     Running   0          1m
```

### Method 2: Using Helm Charts

#### Step 1: Install Helm

If you haven't installed Helm, you can install it using the following commands:

```sh
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

#### Step 2: Add the MongoDB Helm Repository

Add the MongoDB Helm repository:

```sh
helm repo add bitnami https://charts.bitnami.com/bitnami
```

#### Step 3: Deploy MongoDB Using Helm

Deploy MongoDB using the following command:

```sh
helm install mongodb bitnami/mongodb --set replicaSet.enabled=true
```

#### Step 4: Verify the Deployment

Check the status of the pods:

```sh
kubectl get pods
```

Expected output:

```plaintext
NAME                     READY   STATUS    RESTARTS   AGE
mongodb-mongodb-0        1/1     Running   0          1m
mongodb-mongodb-1        1/1     Running   0          1m
mongodb-mongodb-2        1/1     Running   0          1m
```

### How to Prevent / Defend

#### Secure Configuration Management

Ensure that your configuration files are properly secured:

- **Use Secrets**: Store sensitive information like passwords and keys in Kubernetes secrets.
- **RBAC Policies**: Implement Role-Based Access Control (RBAC) to restrict access to sensitive resources.

Example of creating a secret:

```sh
kubectl create secret generic mongodb-secret --from-literal=MONGO_INITDB_ROOT_PASSWORD=yourpassword
```

#### Network Policies

Implement network policies to control traffic between pods:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

#### Monitoring and Logging

Enable monitoring and logging to detect and respond to security incidents:

- **Prometheus**: Use Prometheus for monitoring.
- **Elastic Stack**: Use Elasticsearch, Logstash, and Kibana for centralized logging.

### Real-World Examples

#### CVE-2021-22555: MongoDB Unauthorized Access

In 2021, a critical vulnerability (CVE-2021-22555) was discovered in MongoDB, allowing unauthorized access to databases. This vulnerability highlights the importance of securing your MongoDB deployments.

**Prevention**:
- Ensure that MongoDB instances are not exposed to the internet.
- Use strong authentication mechanisms.
- Regularly update MongoDB to the latest version.

### Conclusion

In this chapter, we covered the process of deploying a managed Kubernetes cluster on Linode and connecting to it from your local machine. We also explored how to deploy a MongoDB stateful set within the cluster using both configuration files and Helm charts. Additionally, we discussed important security measures to protect your Kubernetes environment.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to Kubernetes and container security.
- **OWASP Juice Shop**: A deliberately insecure web application for learning about web security.
- **Kubernetes Goat**: A Kubernetes-based security training platform.

By completing these labs, you can gain practical experience in deploying and securing Kubernetes clusters and stateful sets.

---
<!-- nav -->
[[01-Introduction to Helm and Kubernetes|Introduction to Helm and Kubernetes]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/13-Deploying Managed Kubernetes Cluster with MongoDB/00-Overview|Overview]] | [[03-Introduction to Kubernetes Ingress Controller and Services|Introduction to Kubernetes Ingress Controller and Services]]
