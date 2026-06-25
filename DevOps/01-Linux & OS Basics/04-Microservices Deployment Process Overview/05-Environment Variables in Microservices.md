---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Environment Variables in Microservices

### What Are Environment Variables?

Environment variables are dynamic-named values that can affect the way running processes will behave on a computer. They are used to store configuration data such as database connection strings, API keys, and other sensitive information that should not be hardcoded into the application. In the context of microservices, environment variables are crucial because they allow each microservice to be configured independently without changing the codebase.

### Why Use Environment Variables?

Using environment variables provides several benefits:

1. **Configuration Separation**: Environment variables separate configuration from code, making it easier to manage different environments (development, testing, production).
2. **Security**: Sensitive information can be stored securely outside the codebase, reducing the risk of exposure.
3. **Flexibility**: Different instances of the same microservice can have different configurations without modifying the code.

### How Environment Variables Work

When a microservice starts, it reads the environment variables from the operating system or container runtime. These variables are then used to configure the behavior of the microservice at runtime.

#### Example: Database Connection String

Consider a microservice that connects to a database. Instead of hardcoding the connection string, it can read it from an environment variable:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: db-config
data:
  DB_HOST: "localhost"
  DB_PORT: "5432"
  DB_NAME: "mydb"
  DB_USER: "myuser"
  DB_PASSWORD: "mypassword"
```

This `ConfigMap` can be mounted as environment variables in the pod:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-microservice
spec:
  template:
    spec:
      containers:
      - name: my-microservice
        image: my-microservice:latest
        envFrom:
        - configMapRef:
            name: db-config
```

### Pitfalls and How to Prevent

#### Exposing Sensitive Information

One common pitfall is accidentally exposing sensitive information through environment variables. This can happen if the environment variables are logged or displayed in error messages.

**How to Prevent:**

1. **Use Secure Storage Solutions**: Store sensitive information in secure vaults like HashiCorp Vault or AWS Secrets Manager.
2. **Limit Logging**: Ensure that sensitive environment variables are not included in logs or error messages.
3. **Use Encryption**: Encrypt sensitive data before storing it in environment variables.

#### Example of Vulnerable Code

```yaml
# Vulnerable Configuration
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image:latest
    env:
    - name: DB_PASSWORD
      value: "mypassword"
```

#### Secure Configuration

```yaml
# Secure Configuration
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image:latest
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
---
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  password: cGFzc3dvcmQ= # Base64 encoded "mypassword"
```

### Real-World Example: CVE-2021-44228 (Log4Shell)

The Log4Shell vulnerability (CVE-2021-44228) exploited a flaw in the Apache Log4j library that allowed attackers to execute arbitrary code by injecting malicious log messages. One way this could occur was through environment variables that were logged by the application.

**How to Prevent:**

1. **Update Dependencies**: Keep all dependencies up to date, especially security-critical ones like logging libraries.
2. **Validate Inputs**: Ensure that all inputs, including environment variables, are validated and sanitized before being logged.
3. **Use Security Tools**: Utilize tools like Snyk or Trivy to scan for known vulnerabilities in your dependencies.

---
<!-- nav -->
[[05-Deploying Microservices to a Kubernetes Cluster|Deploying Microservices to a Kubernetes Cluster]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/04-Microservices Deployment Process Overview/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/04-Microservices Deployment Process Overview/07-Hands-On Labs|Hands-On Labs]]
