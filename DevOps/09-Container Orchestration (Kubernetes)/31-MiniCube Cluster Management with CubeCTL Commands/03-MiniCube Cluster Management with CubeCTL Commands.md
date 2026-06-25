---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## MiniCube Cluster Management with CubeCTL Commands

### Introduction to MiniCube and CubeCTL

MiniCube is a lightweight Kubernetes cluster management tool designed to simplify the process of setting up and managing Kubernetes clusters. It provides a user-friendly interface and a set of commands to interact with the cluster, making it easier to manage deployments, pods, and other Kubernetes resources.

CubeCTL is the command-line tool used to interact with MiniCube clusters. It allows users to perform various operations such as deploying applications, managing pods, and inspecting the status of different components within the cluster. Understanding CubeCTL commands is crucial for effective cluster management.

### Deploying Applications with CubeCTL

#### Fixating the Version of an Image

When deploying applications in a Kubernetes cluster, it is often necessary to specify the exact version of the Docker image to ensure consistency and reproducibility. This is achieved using CubeCTL commands to edit the deployment configuration.

**Example: Fixating the Version to 116**

Let's consider a scenario where we want to deploy an application using a specific version of a Docker image. We can achieve this by editing the deployment configuration.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-container
        image: my-image:116
```

To apply this configuration, we use the following CubeCTL command:

```bash
cubectl apply -f deployment.yaml
```

This command applies the specified deployment configuration to the cluster, ensuring that the pods are created with the specified image version.

#### Monitoring Pod Status

After applying the deployment configuration, it is essential to monitor the status of the pods to ensure that they are running correctly. This can be done using the `cubectl get pod` command.

```bash
cubectl get pod
```

The output of this command will show the current status of the pods, including whether they are running, terminating, or in any other state.

```plaintext
NAME                    READY   STATUS    RESTARTS   AGE
my-deployment-xxxxx     1/1     Running   0          2m
old-pod                 0/1     Terminating   0          5m
```

In this example, the old pod is terminating, and a new pod is being created with the specified image version.

### Managing Replica Sets

Kubernetes uses ReplicaSets to manage the number of pod replicas required for a deployment. When a deployment is edited, the corresponding ReplicaSet is also updated to reflect the changes.

**Example: Checking Replica Set Status**

To check the status of the ReplicaSets associated with a deployment, we can use the `cubectl get replicaset` command.

```bash
cubectl get replicaset
```

The output will show the current status of the ReplicaSets, including the number of pods managed by each ReplicaSet.

```plaintext
NAME                    DESIRED   CURRENT   READY   AGE
my-deployment-xxxxx     1         1         1       2m
old-replicaset          0         0         0       5m
```

In this example, the old ReplicaSet has no pods, and a new ReplicaSet has been created to manage the updated deployment.

### Viewing Application Logs

Monitoring the logs of applications running inside pods is crucial for debugging and troubleshooting issues. CubeCTL provides the `logs` command to view the logs of a specific pod.

**Example: Viewing Logs of a Pod**

To view the logs of a pod, we need to specify the pod name using the `cubectl logs` command.

```bash
cubectl logs <pod-name>
```

If the application running inside the pod does not generate any logs, the command will return no output.

### Creating a MongoDB Deployment

Creating a new deployment for a MongoDB database involves specifying the image and other necessary configurations.

**Example: Creating a MongoDB Deployment**

To create a MongoDB deployment, we can use the following YAML configuration:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongo-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongo
  template:
    metadata:
      labels:
        app: mongo
    spec:
      containers:
      - name: mongo
        image: mongo
        ports:
        - containerPort: 27017
```

To apply this configuration, we use the following CubeCTL command:

```bash
cubectl apply -f mongo-deployment.yaml
```

This command creates a new deployment for the MongoDB database.

### Monitoring MongoDB Deployment Status

After creating the MongoDB deployment, it is important to monitor its status to ensure that the pods are running correctly.

**Example: Checking MongoDB Deployment Status**

To check the status of the MongoDB deployment, we can use the `cubectl get pod` command.

```bash
cubectl get pod
```

The output will show the current status of the pods, including whether they are running, terminating, or in any other state.

```plaintext
NAME                    READY   STATUS    RESTARTS   AGE
mongo-deployment-xxxxx  1/1     Running   1          2m
```

In this example, the MongoDB deployment is running correctly.

### Viewing MongoDB Pod Logs

To view the logs of the MongoDB pod, we can use the `cubectl logs` command.

**Example: Viewing MongoDB Pod Logs**

To view the logs of the MongoDB pod, we need to specify the pod name using the `cubectl logs` command.

```bash
cubectl logs <mongo-pod-name>
```

The output will show the logs generated by the MongoDB application.

### Common Pitfalls and How to Prevent Them

#### Incorrect Image Version

One common pitfall is specifying an incorrect version of the Docker image. This can lead to inconsistencies and issues with the deployed application.

**How to Prevent:**

- Always verify the image version before deploying.
- Use tags or digests to ensure the exact version is used.

#### Insufficient Logging

Another common issue is insufficient logging, which can make it difficult to debug and troubleshoot issues.

**How to Prevent:**

- Ensure that the application generates sufficient logs.
- Configure the application to log important events and errors.

### Real-World Examples

#### Recent CVEs and Breaches

Recent vulnerabilities and breaches have highlighted the importance of proper cluster management and monitoring. For example, the CVE-2021-25742 vulnerability in Kubernetes allowed attackers to escalate privileges and gain unauthorized access to the cluster.

**How to Prevent:**

- Keep the Kubernetes cluster and all components up to date with the latest security patches.
- Regularly monitor the cluster for suspicious activity and potential vulnerabilities.

### Conclusion

Effective cluster management with MiniCube and CubeCTL commands is essential for maintaining a secure and reliable Kubernetes environment. By understanding and utilizing these commands, users can deploy applications, manage pods, and monitor the status of their clusters effectively.

### Practice Labs

For hands-on practice with MiniCube and CubeCTL commands, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs to practice Kubernetes security.
- **OWASP Juice Shop**: Provides a vulnerable web application to practice security testing and cluster management.
- **DVWA (Damn Vulnerable Web Application)**: Useful for practicing web application security and cluster management.

These labs provide a comprehensive learning experience and help reinforce the concepts covered in this chapter.

---
<!-- nav -->
[[02-Introduction to MiniCube Cluster Management with CubeCTL Commands|Introduction to MiniCube Cluster Management with CubeCTL Commands]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/31-MiniCube Cluster Management with CubeCTL Commands/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/31-MiniCube Cluster Management with CubeCTL Commands/04-Practice Questions & Answers|Practice Questions & Answers]]
