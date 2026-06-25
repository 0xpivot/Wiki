---
course: DevSecOps
topic: Introduction to Kubernetes Security
tags: [devsecops]
---

## Running Applications with Non-Root Users in Kubernetes

When deploying applications in Kubernetes, it is crucial to ensure that the application runs with the least privilege necessary. One of the best practices is to create a service user and run the application with that user instead of using the root user. This approach significantly reduces the attack surface and limits the potential damage if the application is compromised.

### Why Use a Service User?

Using a service user instead of the root user is a fundamental principle of least privilege. By running the application with a non-root user, you limit the capabilities of the process within the container. If an attacker gains control of the application, they will not have elevated privileges, making it much harder to escalate their access to the underlying system.

### How to Create and Use a Service User

To create a service user within a Docker image, you typically add a new user during the image build process. Here’s an example of how to do this:

```Dockerfile
FROM ubuntu:latest

# Create a new user
RUN groupadd -r myservicegroup && useradd -r -g myservicegroup myserviceuser

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . .

# Switch to the new user
USER myserviceuser

# Run the application
CMD ["./myapplication"]
```

In this Dockerfile, a new user `myserviceuser` is created, and the application is run with this user. This ensures that the application does not have root privileges.

### Pod Configuration and Privileged Containers

Even if the image is built with a service user, the pod configuration can override this setting. A pod can be configured to run with root privileges or as a privileged container, which grants extensive access to the host system. This is generally not recommended because it increases the risk of a security breach.

#### Example of Misconfigured Pod

Here is an example of a pod configuration that runs with root privileges:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: myimage:latest
    securityContext:
      runAsUser: 0  # Root user
```

In this configuration, the `runAsUser` field is set to `0`, which corresponds to the root user. This overrides the service user defined in the Docker image.

#### Privileged Containers

A privileged container has access to all devices and capabilities of the host system. This is highly risky because it allows the container to perform operations that could compromise the entire host.

Here is an example of a pod configuration that uses a privileged container:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: myimage:latest
    securityContext:
      privileged: true
```

In this configuration, the `privileged` field is set to `true`, which grants the container full access to the host system.

### How to Prevent / Defend Against Misconfigured Pods

To prevent misconfigured pods from running with elevated privileges, you should enforce strict security policies at the cluster level. Here are some steps to take:

1. **Use Pod Security Policies (PSP)**: Pod Security Policies allow you to define constraints on pod creation and update operations. You can specify that pods must run with non-root users and cannot be privileged.

2. **Role-Based Access Control (RBAC)**: Implement RBAC to restrict who can create or modify pod configurations. Ensure that only trusted users or automated systems can deploy pods.

3. **Audit and Monitor**: Regularly audit pod configurations to ensure they comply with security policies. Use tools like Kubernetes Audit Logs to monitor and detect unauthorized changes.

#### Example of a Pod Security Policy

Here is an example of a Pod Security Policy that enforces non-root users and disallows privileged containers:

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: nonroot-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
  - ALL
  runAsUser:
    rule: MustRunAsNonRoot
  seLinux:
    rule: RunAsAny
  supplementalGroups:
    rule: MustRunAs
    ranges:
    - min: 1
      max: 65535
  fsGroup:
    rule: MustRunAs
    ranges:
    - min: 1
      max:  65535
  readOnlyRootFilesystem: false
```

This PSP ensures that pods must run with a non-root user and cannot be privileged.

### Real-World Examples and CVEs

One notable example of a security issue related to misconfigured pods is the Kubernetes API server vulnerability (CVE-2020-8558). This vulnerability allowed an attacker to bypass authentication and gain unauthorized access to the cluster. While this specific issue was not directly related to pod misconfiguration, it highlights the importance of securing all aspects of a Kubernetes deployment.

Another example is the container breakout vulnerability (CVE-2019-5736) in the Linux kernel, which allowed a container to escape its namespace and gain access to the host system. This vulnerability underscores the risks associated with running privileged containers.

### Summary

Running applications with non-root users is a critical security practice in Kubernetes. By creating and using a service user, you reduce the attack surface and limit the potential damage if the application is compromised. However, it is essential to ensure that pod configurations do not override these settings and that strict security policies are enforced at the cluster level.

---
<!-- nav -->
[[16-Pod Communication and Encryption in Kubernetes|Pod Communication and Encryption in Kubernetes]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/08-Introduction to Kubernetes Security/Kubernetes Security Best Practices/00-Overview|Overview]] | [[18-Securing Secrets in Kubernetes|Securing Secrets in Kubernetes]]
