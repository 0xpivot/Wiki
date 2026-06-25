---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Kubernetes Deployment of MongoDB and MongoExpress

In this section, we will delve into the process of deploying MongoDB and MongoExpress within a Kubernetes environment. This involves creating Kubernetes configuration files, setting up services, and ensuring secure communication between the components. We'll cover the theoretical foundations, practical steps, and security considerations involved in this process.

### Background Theory

Kubernetes is an open-source platform designed to automate the deployment, scaling, and management of containerized applications. It provides a framework for managing and orchestrating containers across clusters of hosts. Kubernetes uses a declarative model, where you define the desired state of your application, and the system ensures that the actual state matches the desired state.

MongoDB is a popular NoSQL document-oriented database. It stores data in flexible, JSON-like documents, making it highly scalable and suitable for a wide range of applications. MongoExpress is a web-based interface for MongoDB, providing an easy-to-use GUI for interacting with the database.

### Setting Up the Environment

Before diving into the configuration files, ensure you have a Kubernetes cluster set up. In this example, we'll use Minikube, a local Kubernetes cluster for development purposes.

#### Checking the Cluster Status

To verify the status of your Minikube cluster, run the following command:

```bash
minikube start
```

Once the cluster is started, check the current state of the cluster using `kubectl`:

```bash
kubectl get all
```

This command lists all the resources in the cluster, including pods, services, deployments, etc. Since we are starting from scratch, you should see only the default Kubernetes service.

### Creating the MongoDB Deployment

The first step is to create a deployment for MongoDB. A deployment manages the lifecycle of a set of pods, ensuring that the desired number of replicas are running at all times.

#### Deployment Configuration File

Create a new file named `mongodb-deployment.yaml` in your preferred editor (e.g., Visual Studio Code):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb-deployment
spec:
  replicas: 1
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

Let's break down the components of this configuration file:

- **apiVersion**: Specifies the API version used by the resource.
- **kind**: Indicates the type of resource being defined (`Deployment` in this case).
- **metadata**: Contains metadata about the resource, such as its name.
- **spec**: Defines the specifications of the deployment, including the number of replicas and the pod template.
- **selector**: Ensures that the deployment manages pods with the specified labels.
- **template**: Describes the pod template, including the container details and the image to be used.

#### Applying the Deployment

Apply the deployment configuration to the cluster using `kubectl`:

```bash
kubectl apply -f mongodb-deployment.yaml
```

Verify that the deployment and pod are created successfully:

```bash
kubectl get deployments
kubectl get pods
```

### Creating the MongoDB Service

Next, we need to expose the MongoDB deployment as a service within the cluster. This allows other components to communicate with the MongoDB instance.

#### Service Configuration File

Create a new file named `mongodb-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mongodb-service
spec:
  selector:
    app: mongodb
  ports:
    - protocol: TCP
      port: 27017
      targetPort: 27017
  type: ClusterIP
```

Let's break down the components of this configuration file:

- **apiVersion**: Specifies the API version used by the resource.
- **kind**: Indicates the type of resource being defined (`Service` in this case).
- **metadata**: Contains metadata about the resource, such as its name.
- **spec**: Defines the specifications of the service, including the selector and the ports.
- **selector**: Ensures that the service targets pods with the specified labels.
- **ports**: Specifies the ports to be exposed and the protocol used.
- **type**: Determines the type of service (`ClusterIP` in this case, which exposes the service internally within the cluster).

#### Applying the Service

Apply the service configuration to the cluster using `kubectl`:

```bash
kubectl apply -f mongodb-service.yaml
```

Verify that the service is created successfully:

```bash
kubectl get services
```

### Creating the MongoExpress Deployment

Now, let's create a deployment for MongoExpress, which will provide a web-based interface for interacting with the MongoDB instance.

#### Deployment Configuration File

Create a new file named `mongoexpress-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongoexpress-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongoexpress
  template:
    metadata:
      labels:
        app: mongoexpress
    spec:
      containers:
      - name: mongoexpress
        image: mongo-express:latest
        ports:
        - containerPort: 8081
        env:
        - name: ME_CONFIG_MONGODB_SERVER
          value: mongodb-service
        - name: ME_CONFIG_MONGODB_PORT
          value: "27017"
```

Let's break down the components of this configuration file:

- **apiVersion**: Specifies the API version used by the resource.
- **kind**: Indicates the type of resource being defined (`Deployment` in this case).
- **metadata**: Contains metadata about the resource, such as its name.
- **spec**: Defines the specifications of the deployment, including the number of replicas and the pod template.
- **selector**: Ensures that the deployment manages pods with the specified labels.
- **template**: Describes the pod template, including the container details and the image to be used.
- **env**: Specifies environment variables that configure the MongoExpress instance to connect to the MongoDB service.

#### Applying the Deployment

Apply the deployment configuration to the cluster using `kubectl`:

```bash
kubectl apply -
```

---
<!-- nav -->
[[01-Introduction to Config Maps in Kubernetes|Introduction to Config Maps in Kubernetes]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/15-Deploying MongoDB and MongoExpress in Kubernetes/00-Overview|Overview]] | [[03-Introduction to Kubernetes Secrets|Introduction to Kubernetes Secrets]]
