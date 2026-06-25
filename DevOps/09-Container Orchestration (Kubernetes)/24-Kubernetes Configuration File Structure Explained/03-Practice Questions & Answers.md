---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the structure of a Kubernetes configuration file and describe the three main parts.**

The structure of a Kubernetes configuration file is divided into three main parts:

1. **Metadata**: This section contains information about the component being created, such as its name and labels. Labels are key-value pairs that help identify and select components.
   
2. **Specification (Spec)**: This section defines the desired state of the component. It includes various attributes specific to the type of component being created, such as the number of replicas for a deployment or the ports for a service.

3. **Status**: This section is automatically generated and updated by Kubernetes. It reflects the actual state of the component, such as the number of running replicas or the health status. Kubernetes uses this information to ensure the desired state matches the actual state, enabling self-healing features.

For example, in a deployment configuration file, the metadata might include the name and labels, the spec might define the number of replicas and the pod template, and the status would be automatically populated by Kubernetes to reflect the current state of the deployment.

**Q2. How does Kubernetes use labels and selectors to establish connections between components like deployments and services?**

Kubernetes uses labels and selectors to establish connections between components such as deployments and services. Here’s how it works:

1. **Labels**: These are key-value pairs attached to components like pods, deployments, and services. They provide a way to categorize and select objects. For example, a deployment might have a label `app: engineX`.

2. **Selectors**: These are used in the specification of a service to match the labels of the pods it should connect to. For instance, a service might have a selector `app: engineX` to connect to all pods labeled with `app: engineX`.

By using labels and selectors, Kubernetes ensures that services can dynamically discover and communicate with the appropriate pods managed by a deployment. This mechanism allows for flexible and scalable management of components within a Kubernetes cluster.

**Q3. What is the role of the `spec.template` section in a deployment configuration file?**

The `spec.template` section in a deployment configuration file plays a crucial role in defining the characteristics of the pods managed by the deployment. Specifically:

- **Metadata**: Contains information about the pod, such as labels. These labels are essential for identifying and selecting the pods managed by the deployment.
  
- **Spec**: Defines the desired state of the pod, including details like the container image, ports, environment variables, and resource limits. This section acts as a blueprint for the pods that the deployment will create and manage.

For example, in a deployment configuration file, the `spec.template` might look like this:

```yaml
spec:
  template:
    metadata:
      labels:
        app: engineX
    spec:
      containers:
      - name: engineX-container
        image: nginx:latest
        ports:
        - containerPort: 80
```

This template specifies that the deployment should create pods with a single container named `engineX-container`, using the `nginx:latest` image, and exposing port 80.

**Q4. How do you validate that a service is correctly forwarding requests to the right pods?**

To validate that a service is correctly forwarding requests to the right pods, you can follow these steps:

1. **Check Service Endpoints**: Use `kubectl describe service <service-name>` to view the endpoints associated with the service. This command will display the IP addresses and ports of the pods that the service is forwarding requests to.

2. **Compare Pod IPs**: Use `kubectl get pods -o wide` to list the pods along with their IP addresses. Compare these IP addresses with the ones listed in the service endpoints to ensure they match.

For example, if you have a service named `engineX-service`, you can run:

```bash
kubectl describe service engineX-service
```

This will show the endpoints of the service. Then, you can run:

```bash
kubectl get pods -o wide
```

This will list the pods and their IP addresses. By comparing the IP addresses from both commands, you can confirm that the service is correctly forwarding requests to the intended pods.

**Q5. Why is YAML indentation important in Kubernetes configuration files?**

YAML indentation is crucial in Kubernetes configuration files because YAML is a strict format that relies heavily on indentation to define hierarchies and relationships between elements. Incorrect indentation can lead to syntax errors and misinterpretation of the configuration.

For example, consider the following snippet:

```yaml
spec:
  containers:
  - name: engineX-container
    image: nginx:latest
    ports:
    - containerPort: 80
```

If the indentation is incorrect, such as:

```yaml
spec:
  containers:
  - name: engineX-container
image: nginx:latest
ports:
- containerPort: 80
```

This would result in a syntax error because the `image` and `ports` fields are no longer correctly nested under the `containers` field.

To avoid such issues, it is recommended to use YAML validators or linters to check the correctness of the indentation before applying the configuration to the Kubernetes cluster.

---
<!-- nav -->
[[02-Kubernetes Configuration File Structure Explained|Kubernetes Configuration File Structure Explained]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/24-Kubernetes Configuration File Structure Explained/00-Overview|Overview]]
