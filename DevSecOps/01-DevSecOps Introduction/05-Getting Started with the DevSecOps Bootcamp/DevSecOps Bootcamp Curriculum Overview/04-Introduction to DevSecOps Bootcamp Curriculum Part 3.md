---
course: DevSecOps
topic: Getting Started with the DevSecOps Bootcamp
tags: [devsecops]
---

## Introduction to DevSecOps Bootcamp Curriculum

Welcome to the DevSecOps Bootcamp curriculum overview. This section will delve into the core concepts and tools you'll be learning throughout the course, focusing specifically on the automation of security scanning for Kubernetes manifest files and the implementation of policy as code within the CI/CD pipeline. By the end of this chapter, you will have a comprehensive understanding of how to manage security issues and misconfigurations in Kubernetes environments effectively.

### What is Kubernetes?

Kubernetes, often abbreviated as K8s, is an open-source system for automating deployment, scaling, and management of containerized applications. It was originally designed by Google and is now maintained by the Cloud Native Computing Foundation. Kubernetes provides a platform for automating deployment, scaling, and operations of application containers across clusters of hosts.

#### Why Kubernetes?

Kubernetes offers several advantages:

- **Scalability**: It allows you to scale applications horizontally and vertically.
- **Automation**: It automates the deployment and management of applications.
- **Resilience**: It ensures high availability and fault tolerance through self-healing mechanisms.
- **Resource Management**: It optimizes resource usage across the cluster.

### Kubernetes Manifest Files

Kubernetes uses YAML or JSON files, known as manifest files, to describe the desired state of the system. These files define various resources such as deployments, services, pods, and more. Here’s an example of a simple Kubernetes deployment manifest:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 3
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
        image: my-image:latest
        ports:
        - containerPort: 80
```

This manifest defines a deployment with three replicas of a container running the `my-image:latest` image.

### Automatic Scanning of Kubernetes Manifests

One of the primary goals of DevSecOps is to integrate security practices into the development lifecycle. This includes automatically scanning Kubernetes manifest files for security misconfigurations and vulnerabilities.

#### Tools for Automatic Scanning

Several tools are available for scanning Kubernetes manifest files:

- **kube-bench**: A tool that checks Kubernetes clusters against the CIS Kubernetes Benchmark.
- **kube-hunter**: A tool that hunts for security weaknesses in Kubernetes clusters.
- **kubescape**: A tool that scans Kubernetes configurations and checks them against security benchmarks like the CIS Kubernetes Benchmark.

Let’s look at an example using `kubescape`:

```sh
# Install kubescape
curl -sS https://get.kubescape.io | sh

# Scan a Kubernetes manifest file
kubescape scan --path ./my-manifest.yaml
```

The output of `kubescape` will provide details about any security issues found in the manifest file.

### Policy as Code

Policy as code is the practice of defining security policies in code, which can then be enforced programmatically. In the context of Kubernetes, this means defining security policies that can be checked against Kubernetes manifest files during the CI/CD pipeline.

#### Tools for Policy as Code

Some popular tools for implementing policy as code include:

- **OPA (Open Policy Agent)**: A powerful, general-purpose policy engine.
- **Kyverno**: A Kubernetes-native policy controller.
- **Falco**: An open-source runtime security tool.

Let’s explore Kyverno in more detail:

#### Kyverno Example

Kyverno allows you to define policies in YAML format. Here’s an example policy that ensures all containers in a pod use a non-root user:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: run-as-nonroot-user
spec:
  validationFailureAction: enforce
  background: false
  rules:
  - name: check-run-as-user
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: All containers must run as a non-root user.
      pattern:
        spec:
          containers:
          - securityContext:
              runAsUser: 1000
```

To apply this policy, you would create a Kubernetes resource with the above YAML definition.

### Integrating Policies into CI/CD Pipeline

Integrating these policies into the CI/CD pipeline ensures that security checks are performed automatically whenever changes are made to the Kubernetes manifest files.

#### Example CI/CD Pipeline

Here’s an example of a CI/CD pipeline using GitLab CI/CD:

```yaml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - docker build -t my-image .

test:
  stage: test
  script:
    - kubescape scan --path ./my-manifest.yaml
    - kyverno validate --policy ./run-as-nonroot-user.yaml

deploy:
  stage: deploy
  script:
    - kubectl apply -f ./my-manifest.yaml
```

In this pipeline, the `test` stage runs both `kubescape` and `kyverno` to ensure that the manifest files are free of security issues before deploying them to the Kubernetes cluster.

### Compliance in DevSecOps

Compliance is a critical aspect of DevSecOps. Traditionally, compliance has been a manual and bureaucratic process, but in the DevSecOps world, compliance can be automated and integrated into the CI/CD pipeline.

#### Automated Compliance Checks

Automated compliance checks can be performed using tools like `kube-bench`, which checks Kubernetes clusters against the CIS Kubernetes Benchmark. Here’s an example of how to use `kube-bench`:

```sh
# Run kube-bench
kube-bench run --version 1.24 --controls CIS-1.24.0 --check
```

This command will run the CIS benchmark checks on the Kubernetes cluster and report any compliance issues.

### Real-World Examples and Recent Breaches

Recent breaches and CVEs highlight the importance of integrating security into the development lifecycle. For example, the Log4j vulnerability (CVE-2021-44228) affected numerous applications, including those deployed in Kubernetes clusters. Ensuring that Kubernetes manifests are scanned for vulnerabilities and that security policies are enforced can help mitigate such risks.

### How to Prevent / Defend

#### Detection

Detection involves regularly scanning Kubernetes manifest files and clusters for security issues. Tools like `kubescape`, `kube-hunter`, and `kube-bench` can be used to perform these scans.

#### Prevention

Prevention involves enforcing security policies as part of the CI/CD pipeline. Tools like `Kyverno` can be used to define and enforce these policies.

#### Secure Coding Fixes

Here’s an example of a vulnerable Kubernetes manifest and its secure version:

**Vulnerable Manifest:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 3
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
        image: my-image:latest
        ports:
        - containerPort: 80
```

**Secure Manifest:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
spec:
  replicas: 3
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
        image: my-image:latest
        ports:
        - containerPort: 80
        securityContext:
          runAsUser: 1000
```

### Conclusion

By the end of this chapter, you should have a solid understanding of how to integrate security into the development lifecycle using Kubernetes manifest scanning and policy as code. You will be equipped with the knowledge and tools to manage security issues and misconfigurations in Kubernetes environments effectively.

### Practice Labs

For hands-on experience, consider the following labs:

- **Kubernetes Goat**: A Kubernetes-based security training platform.
- **OWASP WrongSecrets**: A series of challenges to learn about security in Kubernetes.
- **kube-hunter**: A tool to hunt for security weaknesses in Kubernetes clusters.

These labs will provide practical experience in applying the concepts learned in this chapter.

---
<!-- nav -->
[[05-Introduction to DevSecOps Bootcamp Curriculum Part 2|Introduction to DevSecOps Bootcamp Curriculum Part 2]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/05-Getting Started with the DevSecOps Bootcamp/DevSecOps Bootcamp Curriculum Overview/00-Overview|Overview]] | [[07-Introduction to DevSecOps Bootcamp Curriculum|Introduction to DevSecOps Bootcamp Curriculum]]
