---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Deploying MongoDB and Mongo Express in a Kubernetes Cluster

MongoDB is a popular NoSQL database, and Mongo Express is a web-based interface for managing MongoDB databases. To deploy these in a Kubernetes cluster, we need to define the necessary resources and configurations.

### Prerequisites

Before deploying MongoDB and Mongo Express, ensure you have:

1. A running Kubernetes cluster.
2. `kubectl` configured to interact with the cluster.
3. `helm` installed for managing Helm charts.

### Step-by-Step Deployment

#### 1. Deploy MongoDB

First, deploy MongoDB using a Helm chart. There are several Helm charts available for MongoDB, such as `bitnami/mongodb`.

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install my-mongodb bitnami/mongodb --set auth.enabled=true
```

This command installs MongoDB with authentication enabled.

#### 2. Deploy Mongo Express

Next, deploy Mongo Express using a Helm chart. One such chart is `bitnami/mongo-express`.

```bash
helm install my-mongo-express bitnami/mongo-express --set mongodbHost=my-mongodb
```

This command deploys Mongo Express and sets the MongoDB host to the previously deployed MongoDB instance.

### Verifying the Deployment

After deploying both services, verify their status using `kubectl`.

```bash
kubectl get pods
```

Check the logs of the Mongo Express pod to ensure it connects to MongoDB successfully.

```bash
kubectl logs <mongo-express-pod-name>
```

Look for messages indicating successful connection to the MongoDB database.

### Persistence of Data

Ensure that MongoDB data is persisted across restarts. This can be achieved by configuring persistent volumes (PVs) and persistent volume claims (PVCs).

#### Example: Persistent Volume Claim for MongoDB

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

Apply this PVC and ensure MongoDB uses it.

```bash
kubectl apply -f mongodb-pvc.yaml
```

### How to Prevent / Defend

To ensure the security and reliability of your MongoDB deployment:

1. **Enable Authentication**: Always enable authentication for MongoDB to prevent unauthorized access.
2. **Use TLS/SSL**: Enable TLS/SSL for secure communication between MongoDB and clients.
3. **Regular Backups**: Implement regular backups of your MongoDB data to prevent data loss.

### Example: Enabling TLS/SSL in MongoDB

To enable TLS/SSL, configure MongoDB with the appropriate certificates and keys.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mongodb-tls-config
data:
  sslMode: requireSSL
  sslPEMKeyFile: /etc/mongodb/ssl/server.pem
  sslCAFile: /etc/mongodb/ssl/ca.pem
```

Apply this configuration and ensure MongoDB uses it.

```bash
kubectl apply -f mongodb-tls-config.yaml
```

---
<!-- nav -->
[[11-Deploying Mongo Express as a UI for MongoDB|Deploying Mongo Express as a UI for MongoDB]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/13-Deploying Managed Kubernetes Cluster with MongoDB/00-Overview|Overview]] | [[13-Deploying MongoDB with Helm|Deploying MongoDB with Helm]]
