---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Environment Variables in Kubernetes Pods

### What Are Environment Variables?

Environment variables are dynamic-named values that can affect the way running processes will behave on a computer. In the context of Kubernetes, environment variables are used to pass configuration data to containers within pods. These variables can be used to control various aspects of the application, such as enabling or disabling certain features, specifying external service endpoints, or configuring logging levels.

### Why Use Environment Variables?

Using environment variables in Kubernetes offers several advantages:

1. **Configuration Management**: Environment variables allow you to manage configuration settings outside of your application code. This separation of concerns makes it easier to change configurations without modifying the application itself.
   
2. **Dynamic Configuration**: Environment variables can be dynamically set at runtime, allowing you to adjust configurations based on the environment (development, staging, production).

3. **Security**: By using environment variables, sensitive information such as API keys or database credentials can be stored securely outside of the application code, reducing the risk of exposure.

### How to Configure Environment Variables in Kubernetes

To configure environment variables in Kubernetes, you can use the `env` field in the pod specification. Here’s an example of how to set environment variables for a pod:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
    env:
    - name: DISABLE_PROFILER
      value: "true"
    - name: DISABLE_TRACING
      value: "true"
    - name: DISABLE_DEBUGGER
      value: "true"
```

In this example, three environment variables (`DISABLE_PROFILER`, `DISABLE_TRACING`, and `DISABLE_DEBUGGER`) are set to `"true"`. This tells the application to disable the profiler, tracing, and debugger services.

### Real-World Example: Disabling Unnecessary Services

Consider a scenario where you have a microservice application that includes profiling, tracing, and debugging services. However, in a production environment, you might want to disable these services to reduce overhead and improve performance. You can achieve this by setting appropriate environment variables.

#### Vulnerable Configuration

Here’s an example of a vulnerable configuration where the environment variables are not set correctly:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
```

In this configuration, the environment variables are not set, which means the profiler, tracing, and debugger services will be enabled by default.

#### Secure Configuration

To secure this configuration, you should explicitly set the environment variables to disable the unnecessary services:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
    env:
    - name: DISABLE_PROFILER
      value: "true"
    - name: DISABLE_TRACING
      value: "true"
    - name: DISABLE_DEBUGGER
      value: "true"
```

### How to Prevent / Defend

#### Detection

To detect whether environment variables are set correctly, you can use tools like `kubectl` to inspect the pod configuration:

```sh
kubectl describe pod my-pod
```

This command will provide detailed information about the pod, including the environment variables.

#### Prevention

To prevent misconfiguration, follow these best practices:

1. **Use Configuration Management Tools**: Utilize tools like Helm or Kustomize to manage your Kubernetes configurations. These tools can help ensure consistency and prevent errors.

2. **Automated Testing**: Implement automated tests to verify that environment variables are set correctly. You can use tools like `kubectl exec` to run commands inside the container and check the environment variables.

3. **Documentation**: Document the required environment variables and their values. Ensure that developers and operators are aware of the necessary configurations.

### Health Probes in Kubernetes

### What Are Health Probes?

Health probes are mechanisms used by Kubernetes to determine the health of a pod. There are two types of health probes:

1. **Readiness Probes**: Used to determine if a pod is ready to receive traffic. A pod is considered ready if the probe succeeds.
   
2. **Liveness Probes**: Used to determine if a pod is alive. If the probe fails, Kubernetes will restart the pod.

### Why Use Health Probes?

Health probes are essential for ensuring the reliability and availability of your applications. They help Kubernetes make informed decisions about managing the lifecycle of pods.

### How to Configure Health Probes

Health probes can be configured using the `livenessProbe` and `readinessProbe` fields in the pod specification. Here’s an example of how to configure a liveness probe:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image
    livenessProbe:
      exec:
        command:
        - cat
        - /tmp/healthy
      initialDelaySeconds: 5
      periodSeconds: 5
```

In this example, the liveness probe uses an `exec` action to check if the `/tmp/healthy` file exists. If the file does not exist, the probe will fail, and Kubernetes will restart the pod.

### Real-World Example: Using TCP Socket for Health Probes

Consider a scenario where you have a Redis service running in a pod. You can configure a liveness probe using a TCP socket to check the health of the Redis service.

#### Vulnerable Configuration

Here’s an example of a vulnerable configuration where the liveness probe is not set correctly:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: redis-pod
spec:
  containers:
  - name: redis
    image: redis
```

In this configuration, the liveness probe is not set, which means Kubernetes will not be able to determine the health of the Redis service.

#### Secure Configuration

To secure this configuration, you should explicitly set the liveness probe using a TCP socket:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: redis-pod
spec:
  containers:
  - name: redis
    image: redis
    livenessProbe:
      tcpSocket:
        port: 6379
      initialDelaySeconds: 15
      periodSeconds: 10
```

In this configuration, the liveness probe uses a TCP socket to check the health of the Redis service on port 6379.

### How to Prevent / Defend

#### Detection

To detect whether health probes are set correctly, you can use tools like `kubectl` to inspect the pod configuration:

```sh
kubectl describe pod redis-pod
```

This command will provide detailed information about the pod, including the health probes.

#### Prevention

To prevent misconfiguration, follow these best practices:

1. **Use Configuration Management Tools**: Utilize tools like Helm or Kustomize to manage your Kubernetes configurations. These tools can help ensure consistency and prevent errors.

2. **Automated Testing**: Implement automated tests to verify that health probes are set correctly. You can use tools like `kubectl exec` to run commands inside the container and check the health probes.

3. **Documentation**: Document the required health probes and their configurations. Ensure that developers and operators are aware of the necessary configurations.

### Conclusion

In this chapter, we covered the importance of environment variables and health probes in Kubernetes. We discussed how to configure environment variables to disable unnecessary services and how to configure health probes to ensure the reliability and availability of your applications. We also provided real-world examples and best practices for detection and prevention. By following these guidelines, you can ensure that your Kubernetes deployments are secure and reliable.

### Practice Labs

For hands-on practice with Kubernetes configuration best practices, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security best practices.
- **OWASP WrongSecrets**: A series of challenges for learning about secrets management in Kubernetes.
- **kube-hunter**: A tool for discovering and exploiting misconfigurations in Kubernetes clusters.

These labs will help you gain practical experience with the concepts discussed in this chapter.

---
<!-- nav -->
[[02-Ensuring Image Security in Kubernetes Clusters|Ensuring Image Security in Kubernetes Clusters]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/23-Kubernetes Configuration Best Practices For Microservices/00-Overview|Overview]] | [[04-Kubernetes Configuration Best Practices for Microservices|Kubernetes Configuration Best Practices for Microservices]]
