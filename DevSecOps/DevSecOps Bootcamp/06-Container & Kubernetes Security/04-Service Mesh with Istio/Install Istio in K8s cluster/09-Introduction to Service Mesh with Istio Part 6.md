---
course: DevSecOps
topic: Service Mesh with Istio
tags: [devsecops]
---

## Introduction to Service Mesh with Istio

Service mesh is a dedicated infrastructure layer for handling service-to-service communication. It provides a way to manage and monitor interactions between services in a microservices architecture. Istio is one of the most popular service meshes, designed to provide a uniform way to secure, control, and observe interactions between microservices.

### What is a Service Mesh?

A service mesh is a dedicated infrastructure layer for handling service-to-service communication. It provides a way to manage and monitor interactions between services in a microservices architecture. A service mesh typically includes:

- **Traffic Management**: Routing, load balancing, retries, timeouts, etc.
- **Observability**: Metrics, tracing, logging.
- **Security**: Mutual TLS, authentication, authorization, encryption.

### Why Use Istio?

Istio is an open-source service mesh that provides a robust set of features for managing and securing microservices. Some key reasons to use Istio include:

- **Traffic Management**: Istio allows you to control and route traffic between services.
- **Security**: Istio provides mutual TLS, authentication, and authorization out-of-the-box.
- **Observability**: Istio integrates with monitoring tools like Prometheus and Jaeger for tracing.
- **Compatibility**: Istio supports various platforms, including Kubernetes, VMs, and bare metal.

### Installing Istio in a Kubernetes Cluster

To install Istio in a Kubernetes cluster, you need to follow several steps. These include setting up the necessary configurations and deploying the Istio components.

#### Prerequisites

Before installing Istio, ensure you have the following:

- A working Kubernetes cluster.
- `kubectl` installed and configured to access your cluster.
- `istioctl` installed on your local machine.

#### Step-by-Step Installation

1. **Download Istio**:
   ```sh
   curl -L https://istio.io/downloadIstio | sh -
   cd istio-*
   ```

2. **Install Istio Control Plane**:
   ```sh
   istioctl install --set profile=demo -y
   ```

3. **Enable Automatic Sidecar Injection**:
   ```sh
   kubectl label namespace default istio-injection=enabled
   ```

### Configuring Istio Ingress Gateway

The Istio Ingress Gateway is responsible for routing external traffic into the cluster. To configure it properly, you need to set up the necessary annotations and security groups.

#### Annotations for AWS Load Balancer

Annotations allow you to customize the behavior of the Istio Ingress Gateway. Specifically, you can define the type of AWS load balancer and its configuration.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: istio-ingressgateway
  namespace: istio-system
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-scheme: "internet-facing"
```

- **service.beta.kubernetes.io/aws-load-balancer-type**: Specifies the type of load balancer (NLB in this case).
- **service.beta.kubernetes.io/aws-load-balancer-scheme**: Specifies whether the load balancer is internet-facing or internal.

#### Isolating Traffic with Security Groups

To isolate traffic coming to the load balancer, you should create a separate security group for the Istio Ingress Gateway.

##### Creating Security Group in Terraform

First, define the security group in Terraform:

```hcl
resource "aws_security_group" "istio_ingress_gateway" {
  name        = "istio-ingress-gateway"
  description = "Security group for Istio Ingress Gateway"

  vpc_id = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

Next, reference this security group in your Kubernetes service definition:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: istio-ingressgateway
  namespace: istio-system
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-scheme: "internet-facing"
    service.beta.kubernetes.io/aws-load-balancer-security-groups: "${aws_security_group.istio_ingress_gateway.id}"
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
      name: http
    - port: 443
      targetPort: 443
      protocol: TCP
      name: https
  selector:
    app: istio-ingressgateway
```

### Full Example of HTTP Request and Response

Let's consider a full example of an HTTP request and response through the Istio Ingress Gateway.

#### HTTP Request

```http
GET /api/v1/users HTTP/1.1
Host: example.com
User-Agent: curl/7.64.1
Accept: */*
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Content-Type: application/json
Content-Length: 123
Connection: keep-alive

{
  "users": [
    { "id": 1, "name": "Alice" },
    { "id": 2, "name": "Bob" }
  ]
}
```

### Observability with Istio

Istio integrates with monitoring tools like Prometheus and Jaeger for tracing. Here’s how you can set up observability:

#### Prometheus Configuration

Add the following to your `values.yaml` file:

```yaml
prometheus:
  enabled: true
  serviceMonitor:
    enabled: true
```

#### Jaeger Configuration

Add the following to your `values.yaml` file:

```yaml
tracing:
  sampling: 1.0
  zipkin:
    address: http://zipkin:9411/api/v2/spans
```

### Security Considerations

#### Mutual TLS

Mutual TLS ensures that both the client and server authenticate each other. To enable mutual TLS in Istio, you need to configure the `Gateway` and `VirtualService`.

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: my-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: MUTUAL
      serverCertificate: /etc/istio/ingressgateway-certs/tls.crt
      privateKey: /etc/istio/ingressgateway-certs/tls.key
      caCertificates: /etc/istio/ingressgateway-certs/root-cert.pem
    hosts:
    - "*"
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: my-virtual-service
spec:
  hosts:
  - "*"
  gateways:
  - my-gateway
  http:
  - match:
    - uri:
        prefix: /
    route:
    - destination:
        host: my-service
        port:
          number: 80
```

### How to Prevent / Defend

#### Detection

Use monitoring tools like Prometheus and Grafana to detect anomalies in traffic patterns. Set up alerts for unusual spikes in traffic or failed requests.

#### Prevention

- **Network Policies**: Use Kubernetes Network Policies to restrict traffic between pods.
- **RBAC**: Implement Role-Based Access Control (RBAC) to limit access to sensitive resources.
- **Secure Configurations**: Ensure that all configurations are secure and follow best practices.

#### Secure Coding Fixes

Compare the insecure and secure versions of the code:

**Insecure Version**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: istio-ingressgateway
  namespace: istio-system
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
      name: http
    - port: 443
      targetPort: 443
      protocol: TCP
      name: https
  selector:
    app: istio-ingressgateway
```

**Secure Version**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: istio-ingressgateway
  namespace: istio-system
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-scheme: "internet-facing"
    service.beta.kubernetes.io/aws-load-balancer-security-groups: "${aws_security_group.istio_ingress_gateway.id}"
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 80
      protocol: TCP
      name: http
    - port:  443
      targetPort: 443
      protocol: TCP
      name: https
  selector:
    app: istio-ingressgateway
```

### Real-World Examples

#### Recent CVEs/Breaches

- **CVE-2021-25282**: A vulnerability in Istio's Envoy proxy allowed attackers to bypass authentication mechanisms.
- **CVE-2021-25283**: Another vulnerability in Istio's Envoy proxy allowed attackers to inject arbitrary HTTP headers.

### Hands-On Labs

For hands-on practice with Istio, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **Kubernetes Goat**: A vulnerable Kubernetes cluster for learning about Kubernetes security.

### Conclusion

In this chapter, we covered the installation and configuration of Istio in a Kubernetes cluster, focusing on the setup of the Istio Ingress Gateway. We also explored the importance of security groups and annotations for configuring the load balancer. Additionally, we discussed observability and security considerations, providing practical examples and secure coding fixes. By following these guidelines, you can effectively manage and secure your microservices architecture using Istio.

---
<!-- nav -->
[[08-Introduction to Service Mesh with Istio Part 5|Introduction to Service Mesh with Istio Part 5]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/04-Service Mesh with Istio/Install Istio in K8s cluster/00-Overview|Overview]] | [[10-Introduction to Service Mesh with Istio Part 7|Introduction to Service Mesh with Istio Part 7]]
