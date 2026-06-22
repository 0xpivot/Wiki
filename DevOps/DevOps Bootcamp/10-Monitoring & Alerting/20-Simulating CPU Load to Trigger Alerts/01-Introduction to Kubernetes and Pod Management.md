---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Kubernetes and Pod Management

Kubernetes is an open-source system for automating deployment, scaling, and management of containerized applications. At the core of Kubernetes is the concept of a **pod**, which is the smallest deployable unit in the Kubernetes ecosystem. A pod encapsulates one or more containers, storage resources, a unique network IP, and options that govern how the containers should run.

### Why Use Pods?

Pods are essential because they provide a way to group containers that are tightly coupled and need to share resources. They also ensure that containers within the same pod are co-located on the same node, which can improve performance and simplify networking.

### Creating Pods with `kubectl`

In Kubernetes, the `kubectl` command-line tool is used to interact with the cluster. One of the most common tasks is creating pods. While you can define pods using YAML files, `kubectl` provides a simpler way to create temporary pods for testing and debugging purposes.

### Translating Docker Commands to `kubectl`

When working with Docker, you might use commands like `docker run` to start a container. Similarly, `kubectl` provides the `run` command to create a pod. However, the syntax and options differ slightly between Docker and `kubectl`.

#### Example: Simulating CPU Load

Let's consider a scenario where you want to simulate a high CPU load to trigger alerts in your monitoring system. You can achieve this by running a container that consumes CPU cycles. Here’s how you can translate a Docker command to a `kubectl` command.

### Docker Command

First, let's look at a typical Docker command:

```bash
docker run --rm -it --name cpu-test busybox /bin/sh -c "while true; do echo 'CPU load'; sleep 1; done"
```

This command starts a container named `cpu-test` using the `busybox` image and runs a shell script that continuously prints "CPU load" and sleeps for 1 second.

### Translating to `kubectl`

To achieve the same effect using `kubectl`, you would use the following command:

```bash
kubectl run cpu-test --image=busybox --command -- /bin/sh -c "while true; do echo 'CPU load'; sleep 1; done"
```

Here’s a breakdown of the `kubectl run` command:

- `kubectl run`: This is the command to create a pod.
- `cpu-test`: This is the name of the pod.
- `--image=busybox`: This specifies the Docker image to use.
- `--command`: This flag tells `kubectl` to override the default command in the image.
- `/bin/sh -c "while true; do echo 'CPU load'; sleep 1; done"`: This is the command to run inside the container.

### Understanding the Syntax

The `kubectl run` command allows you to specify various options and parameters. One important aspect is passing arguments to the command running inside the container. In `kubectl`, you use `--` to separate the `kubectl` options from the command options.

For example, if you wanted to pass additional arguments to the command inside the container, you would do something like this:

```bash
kubectl run cpu-test --image=busybox --command -- /bin/sh -c "while true; do echo 'CPU load $1'; sleep 1; done" -- arg1
```

Here, `arg1` is passed as `$1` to the shell script inside the container.

### Running the Command

Now, let's execute the `kubectl run` command to create the pod:

```bash
kubectl run cpu-test --image=busybox --command -- /bin/sh -c "while true; do echo 'CPU load'; sleep 1; done"
```

After executing this command, you can verify that the pod has been created and is running:

```bash
kubectl get pods
```

This should output something like:

```plaintext
NAME        READY   STATUS    RESTARTS   AGE
cpu-test    1/1     Running   0          1m
```

### Monitoring CPU Load

Once the pod is running, you can monitor the CPU load using tools like `kubectl top`:

```bash
kubectl top pod cpu-test
```

This command will show the current CPU and memory usage of the pod.

### Real-World Example: Simulating High CPU Load

In a real-world scenario, you might want to simulate a higher CPU load to test your monitoring and alerting systems. For example, you could use a tool like `stress` to consume CPU cycles:

```bash
kubectl run cpu-stress --image=alpine --command -- /bin/sh -c "apk add stress && stress --cpu 4"
```

This command installs the `stress` tool and runs it to consume 4 CPU cores.

### How to Prevent / Defend

While simulating CPU load can be useful for testing and debugging, it's important to ensure that such actions do not affect production environments. Here are some best practices:

#### Detection

- **Monitoring**: Use tools like Prometheus and Grafana to monitor CPU usage and set up alerts for unusual activity.
- **Logging**: Enable detailed logging for all pods and containers to track their behavior.

#### Prevention

- **Namespace Isolation**: Run test pods in a dedicated namespace to avoid affecting other workloads.
- **Resource Limits**: Set resource limits for pods to prevent them from consuming too much CPU or memory.

#### Secure Coding Fixes

Here’s an example of how to securely configure a pod with resource limits:

**Vulnerable Configuration:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cpu-test
spec:
  containers:
  - name: cpu-test
    image: busybox
    command: ["/bin/sh", "-c"]
    args: ["while true; do echo 'CPU load'; sleep 1; done"]
```

**Secure Configuration:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cpu-test
spec:
  containers:
  - name: cpu-test
    image: busybox
    command: ["/bin/sh", "-c"]
    args: ["while true; do echo 'CPU load'; sleep 1; done"]
    resources:
      limits:
        cpu: "1"
        memory: "128Mi"
      requests:
        cpu: "0.5"
        memory: "64Mi"
```

### Conclusion

Using `kubectl run` to create temporary pods for testing and debugging is a powerful feature of Kubernetes. By understanding the syntax and options, you can effectively simulate various scenarios, including high CPU load, to test your monitoring and alerting systems.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to Kubernetes and container security.
- **OWASP Juice Shop**: Provides a vulnerable web application that you can deploy in a Kubernetes environment to practice security testing.
- **CloudGoat**: Focuses on cloud security and includes scenarios related to Kubernetes and container orchestration.

By combining theoretical knowledge with practical experience, you can become proficient in managing and securing Kubernetes environments.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/20-Simulating CPU Load to Trigger Alerts/00-Overview|Overview]] | [[02-Simulating CPU Load to Trigger Alerts|Simulating CPU Load to Trigger Alerts]]
