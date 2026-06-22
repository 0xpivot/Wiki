---
course: DevSecOps
topic: Service Mesh with Istio
tags: [devsecops]
---

## Configuring a Secure Gateway with Istio

### Introduction to Service Mesh and Istio

A service mesh is a dedicated infrastructure layer for handling service-to-service communication. It provides a way to manage and monitor the interactions between microservices in a distributed system. Istio is one of the most popular service meshes, designed to provide a uniform way to secure, control, and observe interactions between microservices.

Istio is built around the concept of a **service mesh** and uses **sidecar proxies** to intercept and manage network traffic between services. This allows Istio to handle tasks such as load balancing, service discovery, and traffic management without requiring changes to the application code.

### Understanding the Gateway Component

In Istio, the **Gateway** is a Kubernetes custom resource definition (CRD) that defines how external traffic reaches the services within the mesh. A Gateway is essentially a load balancer that routes incoming traffic to the appropriate services based on the specified rules.

#### Gateway Configuration

The Gateway configuration is defined using a YAML file. Here is an example of a basic Gateway configuration:

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
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
```

This configuration sets up a Gateway named `my-gateway` that listens on port 80 for HTTP traffic. The `selector` field specifies that this Gateway should be applied to the `istio-ingressgateway` pod, which is typically deployed as part of the Istio installation.

### External Secrets and Istio Integration

To secure the Gateway, we often need to use TLS certificates. These certificates can be stored externally and fetched dynamically using an **External Secret**. An External Secret is a mechanism provided by the `external-secrets` operator, which allows you to fetch secrets from external secret stores and inject them into your Kubernetes cluster.

#### Creating an External Secret

Let's create an External Secret that will be used to configure the Gateway. The External Secret will reference a secret stored in an external secret store, such as AWS Secrets Manager.

Here is an example of an External Secret configuration:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: istio-tls-secret
  namespace: istio-system
spec:
  backendType: aws-secrets-manager
  dataFrom:
  - extract: true
    key: my-tls-secret
    name: tls-secret
```

This configuration does the following:
- Defines an External Secret named `istio-tls-secret`.
- Specifies that the secret should be fetched from AWS Secrets Manager (`backendType: aws-secrets-manager`).
- Extracts the secret with the key `my-tls-secret` and maps it to a Kubernetes secret named `tls-secret`.

### Namespace Considerations

It is crucial to ensure that the External Secret and the Kubernetes secret it creates are in the same namespace as the Gateway component. This is because the Gateway configuration will reference these secrets, and they need to be accessible within the same namespace.

For example, if the Gateway is deployed in the `istio-system` namespace, the External Secret and the Kubernetes secret it creates should also be in the `istio-system` namespace.

### Gateway Configuration with TLS

Now that we have the External Secret set up, we can configure the Gateway to use TLS. Here is an example of a Gateway configuration that includes TLS settings:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: my-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      serverCertificate: /etc/istio/ingressgateway-certs/tls.crt
      privateKey: /etc/istio/ingressgateway-certs/tls.key
    hosts:
    - "*"
```

This configuration sets up two ports:
- Port 80 for HTTP traffic.
- Port 443 for HTTPS traffic, using TLS with the `SIMPLE` mode.

The `serverCertificate` and `privateKey` fields specify the paths to the TLS certificate and private key files, respectively. These files should be mounted into the `istio-ingressgateway` pod using the secrets created by the External Secret.

### Full Example of HTTP Request and Response

Let's consider a full example of an HTTP request and response through the Gateway.

#### HTTP Request

```http
GET /api/data HTTP/1.1
Host: example.com
Accept: application/json
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 30

{"data": "some data"}
```

### Common Pitfalls and Best Practices

#### Pitfall: Incorrect Namespace Configuration

One common pitfall is ensuring that the External Secret and the Kubernetes secret it creates are in the correct namespace. If they are not in the same namespace as the Gateway, the Gateway will not be able to access the secrets.

#### Best Practice: Use Strong TLS Settings

Always use strong TLS settings, including modern cipher suites and protocols. Avoid using deprecated or weak ciphers.

### How to Prevent / Defend

#### Detection

To detect misconfigurations or vulnerabilities, you can use tools like `istioctl` to inspect the Gateway and related resources. Additionally, you can use Kubernetes audit logs to track changes to secrets and configurations.

#### Prevention

- Ensure that all secrets are stored securely in external secret stores.
- Use strong TLS settings and regularly update certificates.
- Regularly audit and review configurations to ensure they are secure.

#### Secure Coding Fixes

Here is an example of a vulnerable Gateway configuration and the corresponding secure configuration:

**Vulnerable Configuration**

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
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
```

**Secure Configuration**

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: my-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      serverCertificate: /etc/istio/ingressgateway-certs/tls.crt
      privateKey: /etc/istio/  ingressgateway-certs/tls.key
    hosts:
    - "*"
```

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-25285**: A vulnerability in Istio's Envoy proxy allowed attackers to bypass authentication mechanisms.
- **Breaches**: Multiple breaches have occurred due to misconfigured Gateways and insecure TLS settings.

### Hands-On Labs

For hands-on practice with configuring a secure Gateway with Istio, consider the following labs:
- **PortSwigger Web Security Academy**: Offers detailed labs on securing web applications.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security configurations.
- **Kubernetes Goat**: Focuses on Kubernetes security and can be adapted for Istio configurations.

By following these steps and best practices, you can ensure that your Istio Gateway is configured securely and efficiently.

---
<!-- nav -->
[[07-Introduction to Service Mesh with Istio|Introduction to Service Mesh with Istio]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/04-Service Mesh with Istio/Configure a Secure Gateway/00-Overview|Overview]] | [[09-Configuring a Secure Gateway with Istio|Configuring a Secure Gateway with Istio]]
