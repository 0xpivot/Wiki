---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Helm and Kubernetes Secrets

In the world of container orchestration, Kubernetes stands as a leading platform for managing containerized applications. One of the challenges in deploying applications on Kubernetes is the management of secrets and configurations. Secrets are sensitive data such as passwords, API keys, and certificates that should not be stored in plain text within application code. Kubernetes provides a mechanism to manage these secrets securely through the `Secret` resource type.

### What is a Secret in Kubernetes?

A `Secret` in Kubernetes is an object that contains a small amount of sensitive data, such as a password, SSH key, or token. This data can then be consumed by pods in a secure manner. Secrets are encoded in base64 and stored in the etcd store, which is the key-value store used by Kubernetes to store all cluster data. By using Secrets, you can ensure that sensitive information is not exposed in plain text within your application code or configuration files.

#### Why Use Secrets?

Using Secrets in Kubernetes offers several benefits:

1. **Security**: Secrets are encrypted and stored in a secure manner, reducing the risk of exposure.
2. **Isolation**: Secrets can be isolated from the application code, making it easier to manage and rotate sensitive data.
3. **Flexibility**: Secrets can be easily shared among multiple pods and can be updated without redeploying the entire application.

#### How to Create a Secret

To create a Secret in Kubernetes, you can use the `kubectl` command-line tool. Here is an example of creating a Secret containing a username and password:

```bash
kubectl create secret generic my-secret --from-literal=username=admin --from-literal=password=secretpassword
```

This command creates a Secret named `my-secret` with two key-value pairs: `username` and `password`.

### Using Secrets in Pods

Once a Secret is created, it can be referenced in pod specifications to inject the secret data into the pod. Here is an example of a pod specification that uses a Secret:

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
    - name: USERNAME
      valueFrom:
        secretKeyRef:
          name: my-secret
          key: username
    - name: PASSWORD
      valueFrom:
        secretKeyRef:
          name: my-secret
          key: password
```

In this example, the `my-pod` pod references the `my-secret` Secret to inject the `username` and `password` environment variables into the `my-container` container.

### Helm Charts and Kubernetes Deployment

While managing individual resources like Secrets is essential, deploying complex applications often requires managing multiple resources together. This is where Helm comes into play.

#### What is Helm?

Helm is a package manager for Kubernetes that simplifies the deployment and management of applications. A Helm chart is a collection of files that describe a related set of Kubernetes resources. These charts can be used to deploy applications, services, and configurations in a consistent and repeatable manner.

#### Why Use Helm?

Using Helm offers several advantages:

1. **Consistency**: Helm charts provide a standardized way to define and deploy applications, ensuring consistency across different environments.
2. **Reusability**: Helm charts can be reused across different projects and teams, reducing the effort required to deploy similar applications.
3. **Version Control**: Helm charts can be versioned and managed using Git, allowing for easy tracking of changes and rollbacks.

#### Creating a Helm Chart

To create a Helm chart, you can use the `helm create` command. Here is an example of creating a Helm chart for an Elasticsearch deployment:

```bash
helm create elasticsearch
```

This command generates a directory structure for the `elasticsearch` chart, including templates for various Kubernetes resources such as Deployments, Services, and ConfigMaps.

### Example: Deploying Elasticsearch with Helm

Let's walk through an example of deploying Elasticsearch using a Helm chart. First, we need to create a Helm chart for Elasticsearch. We can start by creating a basic chart structure:

```bash
helm create elasticsearch
```

This command generates the following directory structure:

```
elasticsearch/
├── Chart.yaml
├── charts/
├── templates/
│   ├── deployment.yaml
│   ├── _helpers.tpl
│   ├── hpa.yaml
│   ├── ingress.yaml
│   ├── NOTES.txt
│   ├── service.yaml
│   └── svc.yaml
└── values.yaml
```

Next, we need to modify the `templates/deployment.yaml` file to define the Elasticsearch deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-elasticsearch
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}-elasticsearch
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}-elasticsearch
    spec:
      containers:
      - name: elasticsearch
        image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
        ports:
        - containerPort: 9200
        env:
        - name: ES_JAVA_OPTS
          value: "-Xms512m -Xmx512m"
        - name: discovery.type
          value: "single-node"
```

We also need to modify the `values.yaml` file to specify the default values for the chart:

```yaml
replicaCount: 1

image:
  repository: docker.elastic.co/elasticsearch/elasticsearch
  tag: 7.10.2

service:
  type: ClusterIP
  port: 9200
```

Finally, we can deploy the Elasticsearch chart using the `helm install` command:

```bash
helm install my-elasticsearch ./elasticsearch
```

This command deploys the Elasticsearch chart and creates the necessary Kubernetes resources.

### Real-World Examples and Recent CVEs

Deploying complex applications like Elasticsearch using Helm charts can help mitigate security risks associated with manual configuration and deployment. However, it is important to stay aware of recent vulnerabilities and breaches.

#### CVE-2021-22165: Elasticsearch Unauthorized Access

CVE-2021-22165 is a critical vulnerability in Elasticsearch that allows unauthorized access to the system. This vulnerability arises from improper configuration of the Elasticsearch security features, particularly the absence of authentication and authorization mechanisms.

To prevent this vulnerability, it is crucial to enable and configure the Elasticsearch security features properly. Here is an example of how to configure Elasticsearch security using a Helm chart:

```yaml
security:
  enabled: true
  authc:
    anonymous:
      enabled: false
  authz:
    role_mapping:
      admin:
        users:
        - "admin"
        backend_roles:
        - "admin"
```

By enabling security and configuring role mappings, you can ensure that only authorized users can access the Elasticsearch cluster.

### How to Prevent / Defend

#### Detection

To detect potential security issues in your Kubernetes cluster, you can use tools like `kube-bench`, which is a CIS Kubernetes benchmark tool. This tool checks your cluster against the CIS Kubernetes Benchmark and identifies any misconfigurations or vulnerabilities.

Here is an example of running `kube-bench`:

```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v /etc:/etc aquasec/kube-bench:latest --version 1.21 --controls P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,P12,P13,P14,P15,P16,P17,P18,P19,P20,P21,P22,P23,P24,P25,P26,P27,P28,P29,P30,P31,P32,P33,P34,P35,P36,P37,P38,P39,P40,P41,P42,P43,P44,P45,P46,P47,P48,P49,P50,P51,P52,P53,P54,P55,P56,P57,P58,P59,P60,P61,P62,P63,P64,P65,P66,P67,P68,P69,P70,P71,P72,P73,P74,P75,P76,P77,P78,P79,P80,P81,P82,P83,P84,P85,P86,P87,P88,P89,P90,P91,P92,P93,P94,P95,P96,P97,P98,P99,P100,P101,P102,P103,P104,P1
```

#### Prevention

To prevent security issues in your Kubernetes cluster, follow these best practices:

1. **Enable and Configure Security Features**: Ensure that security features like RBAC, network policies, and pod security policies are enabled and configured properly.
2. **Use Secure Images**: Use images from trusted sources and regularly update them to patch known vulnerabilities.
3. **Limit Privileges**: Limit the privileges of containers and pods to the minimum required for their operation.
4. **Monitor and Audit**: Regularly monitor and audit your cluster for any suspicious activity or misconfigurations.

#### Secure Coding Fixes

Here is an example of a vulnerable and secure version of a Kubernetes deployment:

**Vulnerable Version:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 1
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
        image: my-vulnerable-image:latest
        ports:
        - containerPort: 8080
```

**Secure Version:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 1
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
        image: my-secure-image:latest
        ports:
        - containerPort: 8080
        securityContext:
          runAsUser: 1000
          allowPrivilegeEscalation: false
```

In the secure version, the `securityContext` is used to limit the privileges of the container and prevent privilege escalation.

### Conclusion

Managing secrets and deploying complex applications in Kubernetes can be challenging. Using Kubernetes Secrets and Helm charts can simplify these tasks and improve the security and consistency of your deployments. By following best practices and staying aware of recent vulnerabilities, you can ensure that your Kubernetes cluster remains secure and reliable.

### Practice Labs

For hands-on practice with Helm and Kubernetes, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security, including Kubernetes-specific scenarios.
- **OWASP Juice Shop**: A deliberately insecure web application for security training, which includes Kubernetes deployment scenarios.
- **Kubernetes Goat**: A Kubernetes-based penetration testing lab designed to teach security concepts in a Kubernetes environment.

These labs provide practical experience with deploying and securing applications in Kubernetes, helping you master the skills needed for effective DevOps practices.

---
<!-- nav -->
[[02-Introduction to Helm and Its Role in Kubernetes|Introduction to Helm and Its Role in Kubernetes]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/02-Helm Basics and Use Cases for Kubernetes/00-Overview|Overview]] | [[04-Introduction to Helm and Kubernetes|Introduction to Helm and Kubernetes]]
