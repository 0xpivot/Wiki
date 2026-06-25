---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Kubernetes and AWS Load Balancers

Kubernetes is an open-source system for automating deployment, scaling, and management of containerized applications. One of the key features of Kubernetes is its ability to manage services and load balancing across different environments. In this section, we will delve into how Kubernetes interacts with AWS to provide load balancing capabilities, specifically focusing on the `loadBalancer` type service.

### What is a Service in Kubernetes?

In Kubernetes, a **Service** is an abstraction that defines a logical set of Pods and a policy by which to access them. A Service is a way to expose an application running on a set of Pods as a network service. Services are used to load balance traffic between multiple instances of a Pod.

#### Types of Services

There are several types of services in Kubernetes:

1. **ClusterIP**: Exposes the service on a cluster-internal IP. This type makes the service only reachable from within the cluster.
2. **NodePort**: Exposes the service on each Node’s IP at a static port (the NodePort). This type makes a service accessible from outside the cluster through the IP address of any node and the specified NodePort.
3. **LoadBalancer**: Exposes the service externally using a cloud provider’s load balancer. This type makes the service accessible from outside the cluster via a public IP address provided by the cloud provider.
4. **ExternalName**: Maps the service to the contents of the externalName field (e.g., foo.bar.example.com), by returning a CNAME record with its value. No proxying of any kind is set up.

For this discussion, we will focus on the `LoadBalancer` type service.

### Why Use a LoadBalancer Service?

The `LoadBalancer` type service is particularly useful when you want to expose your application to the internet. By using a cloud provider’s load balancer, you can distribute incoming traffic across multiple instances of your application, ensuring high availability and scalability.

#### How Does Kubernetes Create a LoadBalancer?

When you create a service of type `LoadBalancer`, Kubernetes interacts with the underlying cloud provider to provision a load balancer. The specifics of how this happens depend on the cloud provider. For AWS, Kubernetes uses the AWS SDK to create an Elastic Load Balancer (ELB).

### Example Configuration

Let's look at a sample configuration for a `LoadBalancer` service in Kubernetes. We'll assume we have a simple application called `EngineX`.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: engine-x-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: engine-x
  template:
    metadata:
      labels:
        app: engine-x
    spec:
      containers:
      - name: engine-x
        image: myregistry/engine-x:latest
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: engine-x-service
spec:
  type: LoadBalancer
  selector:
    app: engine-x
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
```

### Explanation of the Configuration

1. **Deployment**: Defines a deployment for the `EngineX` application. It specifies that one replica of the pod should be running.
2. **Service**: Defines a service of type `LoadBalancer`. The service selects pods with the label `app: engine-x` and exposes port 80, forwarding traffic to port 8080 on the pods.

### Applying the Configuration

To apply the configuration, you would run the following command:

```sh
kubectl apply -f engine-x-config.yaml
```

This command creates both the deployment and the service.

### Checking the Deployment and Service

After applying the configuration, you can check the status of the deployment and service:

```sh
kubectl get deployment engine-x-deployment
kubectl get pods
kubectl get svc engine-x-service
```

### Understanding the Load Balancer Endpoint

Once the service is created, Kubernetes will provision an ELB and return the external IP address. You can view the details of the service to see the external IP:

```sh
kubectl describe svc engine-x-service
```

This command will show you the external IP address of the load balancer, which you can use to access your application from the internet.

### Real-World Example: Recent Breaches and CVEs

One notable example of a breach involving Kubernetes and load balancers is the **CVE-2021-25741**. This vulnerability affected the AWS Elastic Load Balancing service, allowing attackers to bypass authentication mechanisms and gain unauthorized access to backend resources.

#### Impact of CVE-2021-25741

- **Description**: The vulnerability allowed attackers to bypass authentication mechanisms in the AWS Elastic Load Balancing service.
- **Impact**: Attackers could potentially access backend resources without proper authorization.
- **Mitigation**: AWS released patches and recommended updating to the latest versions of their services.

### How to Prevent / Defend Against Vulnerabilities

#### Detection

To detect potential vulnerabilities, you can use tools like:

- **AWS Trusted Advisor**: Provides recommendations to improve the security and performance of your AWS environment.
- **Kubernetes Security Scanners**: Tools like `kube-bench` and `kubescape` can help identify misconfigurations and vulnerabilities in your Kubernetes clusters.

#### Prevention

1. **Keep Software Updated**: Ensure that all Kubernetes components and cloud provider services are updated to the latest versions.
2. **Use Network Policies**: Implement network policies to restrict traffic between pods and services.
3. **Secure Load Balancers**: Configure load balancers with strict security settings, such as enabling SSL/TLS encryption and using security groups to control access.

#### Secure Code Fix

Here is an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: engine-x-service
spec:
  type: LoadBalancer
  selector:
    app: engine-x
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
```

**Secure Configuration:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: engine-x-service
spec:
  type: LoadBalancer
  selector:
    app: engine-x
  ports:
  - protocol: TCP
    port: 443
    targetPort: 8080
  loadBalancerSourceRanges:
  - 192.0.2.0/24
```

In the secure configuration, we have enabled HTTPS by setting the port to 443 and restricted access to specific IP ranges using `loadBalancerSourceRanges`.

### Hands-On Lab Suggestions

For hands-on practice with Kubernetes and AWS load balancers, consider the following labs:

- **PortSwigger Web Security Academy**: Offers practical exercises on securing web applications, including Kubernetes deployments.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **CloudGoat**: A series of labs designed to teach cloud security concepts using AWS.

These labs provide a comprehensive learning experience and allow you to apply the concepts discussed in this chapter.

### Conclusion

Understanding how Kubernetes interacts with AWS to provide load balancing capabilities is crucial for managing scalable and secure applications. By configuring services correctly and implementing robust security measures, you can ensure that your applications are both highly available and secure.

---
<!-- nav -->
[[01-Introduction to EKS Cluster Autoscaling with AWS Auto Scaling Groups|Introduction to EKS Cluster Autoscaling with AWS Auto Scaling Groups]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/17-EKS Cluster Autoscaling with AWS Auto Scaling Groups/00-Overview|Overview]] | [[03-Introduction to Load Balancers in Kubernetes|Introduction to Load Balancers in Kubernetes]]
