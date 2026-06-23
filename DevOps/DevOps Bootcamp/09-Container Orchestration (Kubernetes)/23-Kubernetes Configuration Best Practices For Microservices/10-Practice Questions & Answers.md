---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Why is it important to specify specific image versions in Kubernetes configuration files?**

Specifying specific image versions in Kubernetes configuration files is crucial for maintaining control and visibility over the exact versions of applications running in the cluster. Without specifying a version, Kubernetes will pull the latest version of the image, which can lead to unpredictability and potential issues if newer versions introduce breaking changes or bugs. Fixating the image version ensures consistency and stability across the cluster.

**Q2. How do you implement a liveness probe in a Kubernetes configuration file?**

A liveness probe is implemented in a Kubernetes configuration file by adding the `livenessProbe` attribute within the container definition. This attribute includes parameters such as `periodSeconds`, which defines how often the probe should be executed, and `exec`, which specifies the command to be executed to check the application’s health. Here is an example:

```yaml
containers:
- name: my-container
  image: my-image:0.2.3
  livenessProbe:
    exec:
      command:
      - /bin/sh
      - -c
      - /bin/grpc_health_probe -addr=:8080
    periodSeconds: 5
```

**Q3. What is the difference between a liveness probe and a readiness probe in Kubernetes?**

A liveness probe checks if the application inside a pod is running correctly and can be restarted if it fails. A readiness probe, on the other hand, checks if the application is ready to serve traffic. While a liveness probe ensures the application is running, a readiness probe ensures the application is fully initialized and ready to handle requests. This distinction is important because it prevents traffic from being sent to an application that is still starting up.

**Q4. How can you expose an external service securely in Kubernetes?**

Exposing an external service securely in Kubernetes involves avoiding the use of `NodePort` service type, which exposes the service on all worker nodes and increases the attack surface. Instead, you can use a `LoadBalancer` type, which leverages the cloud provider’s load balancer to create a single entry point for the cluster. Alternatively, an `Ingress Controller` can be used to manage traffic routing to internal services. Here is an example of changing the service type to `LoadBalancer`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
```

**Q5. Explain the importance of setting resource requests and limits in Kubernetes.**

Setting resource requests and limits in Kubernetes is essential for ensuring that containers have enough resources to function properly and to prevent a single container from consuming all available resources, leading to potential downtime of other services. Resource requests define the minimum amount of resources a container needs, while limits define the maximum amount of resources a container can use. This helps in efficient resource allocation and management. Here is an example:

```yaml
resources:
  requests:
    cpu: 100m
    memory: 64Mi
  limits:
    cpu: 200m
    memory: 128Mi
```

**Q6. How do labels and namespaces contribute to better management of Kubernetes resources?**

Labels in Kubernetes are key-value pairs attached to objects like pods, services, and deployments. They help in identifying and organizing resources, making it easier to select and manipulate groups of objects. Namespaces, on the other hand, provide a way to divide cluster resources between multiple users or projects. They help in isolating different applications or environments, improving organization and security. For example, you can label a pod and refer to it in a service:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
  labels:
    app: my-app
spec:
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
        image: my-image:0.2.3
```

**Q7. Discuss recent security best practices for Kubernetes, including image scanning and non-root user usage.**

Recent security best practices for Kubernetes include:

1. **Image Scanning**: Regularly scanning container images for known vulnerabilities using tools like Clair, Trivy, or Aqua Security. This ensures that the images used in the cluster are free from security risks.

2. **Non-root User Usage**: Running containers with non-root users to minimize the potential damage if a container is compromised. This can be achieved by configuring the container to run as a specific user ID (UID). For example:

   ```yaml
   securityContext:
     runAsUser: 1000
   ```

3. **Cluster Updates**: Keeping the Kubernetes cluster updated to the latest version to benefit from security patches and bug fixes. This is typically done node-by-node to avoid downtime.

These practices help in maintaining a secure and robust Kubernetes environment.

---
<!-- nav -->
[[09-Specifying and Fixating Image Versions|Specifying and Fixating Image Versions]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/23-Kubernetes Configuration Best Practices For Microservices/00-Overview|Overview]]
