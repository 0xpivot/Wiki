---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Creating Deployment and Service Configuration Files

### What Are Deployment and Service Configuration Files?

Deployment and service configuration files are YAML files that define how microservices should be deployed and managed within a Kubernetes cluster.

### Why Create These Files?

Creating these files allows you to:

1. **Define Deployment Strategies**: Specify how many replicas of a microservice should be running.
2. **Configure Services**: Define how traffic should be routed to the microservices.
3. **Manage Resources**: Allocate resources such as CPU and memory to microservices.

### How to Create Deployment and Service Configuration Files

To create deployment and service configuration files, you need to define the necessary fields in YAML format.

#### Example: Deployment Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-microservice
  namespace: online-shop
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-microservice
  template:
    metadata:
      labels:
        app: my-microservice
    spec:
      containers:
      - name: my-microservice
        image: my-microservice:latest
        ports:
        - containerPort: 8080
        envFrom:
        - configMapRef:
            name: db-config
```

#### Example: Service Configuration

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
  namespace: online-shop
spec:
  selector:
    app: my-microservice
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: ClusterIP
```

### Pitfalls and How to Prevent

#### Incorrect Configuration

Incorrect configuration can lead to issues such as incorrect routing, resource allocation problems, and security vulnerabilities.

**How to Prevent:**

1. **Validation Tools**: Use tools like `kubectl apply --validate=true` to validate configuration files.
2. **Code Reviews**: Conduct regular code reviews to catch configuration errors.
3. **Testing**: Test deployments in a staging environment before moving them to production.

#### Example of Vulnerable Configuration

```yaml
# Vulnerable Configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-microservice
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-microservice
  template:
    metadata:
      labels:
        app: my-microservice
    spec:
      containers:
      - name: my-microservice
        image: my-microservice:latest
        ports:
        - containerPort: 8080
        env:
        - name: DB_PASSWORD
          value: "mypassword"
---
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-microservice
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: ClusterIP
```

#### Secure Configuration

```yaml
# Secure Configuration
apiVersion: v1
kind: Namespace
metadata:
  name: online-shop
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-microservice
  namespace: online-shop
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-microservice
  template:
    metadata:
      labels:
        app: my-microservice
    spec:
      containers:
      - name: my-microservice
        image: my-microservice:latest
        ports:
        - containerPort: 8080
        envFrom:
        - configMapRef:
            name: db-config
---
apiVersion: v1
kind: Service
metadata:
  name: my-service
  namespace: online-shop
spec:
  selector:
    app: my-microservice
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: ClusterIP
```

### Real-World Example: Kubernetes Dashboard Vulnerability (CVE-2019-11249)

The Kubernetes Dashboard vulnerability (CVE-2019-11249) allowed attackers to bypass authentication and gain unauthorized access to the dashboard. This could potentially allow access to sensitive namespaces and resources.

**How to Prevent:**

1. **Regular Updates**: Keep all Kubernetes components up to date.
2. **RBAC Policies**: Implement RBAC policies to restrict access to the dashboard and other sensitive resources.
3. **Monitoring**: Monitor access attempts to the dashboard and other sensitive resources.

---
<!-- nav -->
[[03-Container Naming and Configuration|Container Naming and Configuration]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/04-Microservices Deployment Process Overview/00-Overview|Overview]] | [[05-Deploying Microservices to a Kubernetes Cluster|Deploying Microservices to a Kubernetes Cluster]]
