---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Deploying Microservices with Helm Commands

In this section, we will delve into deploying microservices using Helm, a popular package manager for Kubernetes. Helm simplifies the deployment process by managing the installation and upgrade of applications in a Kubernetes cluster. We'll cover the basics of Helm, discuss the two primary methods of deploying microservices, and explore the pros and cons of each approach.

### What is Helm?

Helm is a package manager for Kubernetes that streamlines the deployment and management of applications. It uses a templating engine called Go Templates to generate Kubernetes manifests, which are then applied to the cluster. Helm packages are called charts, and they contain all the necessary information to deploy an application, including templates, values, and metadata.

#### Why Use Helm?

Using Helm offers several advantages:

1. **Reusability**: Helm charts can be reused across different environments, making it easier to manage multiple deployments.
2. **Version Control**: Helm allows you to track and roll back versions of your deployments, ensuring that you can revert to a stable state if needed.
3. **Configuration Management**: Helm charts can be customized using values files, allowing you to adjust settings without modifying the underlying templates.
4. **Dependency Management**: Helm supports dependencies between charts, making it easier to manage complex applications with multiple components.

### Deploying Microservices with Helm

We have two different options for deploying our microservices using Helm:

1. **Manual Installation**
2. **Scripted Installation**

#### Manual Installation

The first option is to manually execute the `helm install` command for each microservice. This method is straightforward but can become cumbersome if you have many services to deploy.

##### Steps for Manual Installation

1. **Identify the Chart**: Each microservice has its own chart. For example, we have a Redis chart and a set of microservice charts.
2. **Provide Values File**: Each chart requires a values file that contains configuration settings specific to the deployment environment.
3. **Execute the Command**: Run the `helm install` command for each service, specifying the release name, values file, and chart name.

Here’s an example of how to manually install a microservice:

```sh
helm install my-release ./microservice-chart --values values.yaml
```

This command installs the microservice chart with the specified values file and assigns it the release name `my-release`.

##### Example: Installing Redis Manually

Let's walk through the process of installing Redis manually:

1. **Chart Location**: Ensure the Redis chart is located in the appropriate directory.
2. **Values File**: Prepare a values file (`redis-values.yaml`) with the necessary configurations.
3. **Install Command**:

```sh
helm install redis-release ./redis-chart --values redis-values.yaml
```

This command installs the Redis chart with the specified values file and assigns it the release name `redis-release`.

#### Scripted Installation

The second option is to create a script file that contains all the `helm install` commands. This method is more efficient and reduces the chance of human error.

##### Steps for Scripted Installation

1. **Create a Script File**: Write a shell script that includes the `helm install` commands for each microservice.
2. **Make the Script Executable**: Ensure the script has the necessary permissions to run.
3. **Run the Script**: Execute the script to deploy all the microservices.

Here’s an example of a script file (`deploy.sh`):

```sh
#!/bin/bash

# Install Redis
helm install redis-release ./redis-chart --values redis-values.yaml

# Install Microservice 1
helm install microservice1-release ./microservice1-chart --values microservice1-values.yaml

# Install Microservice 2
helm install microservice2-release ./microservice2-chart --values microservice2-values.yaml
```

To run the script, make it executable and execute it:

```sh
chmod +x deploy.sh
./deploy.sh
```

##### Example: Scripted Installation of Microservices

Let's create a script to deploy both Redis and the microservices:

1. **Script Content**:

```sh
#!/bin/bash

# Install Redis
helm install redis-release ./redis-chart --values redis-values.yaml

# Install Microservice 1
helm install microservice1-release ./microservice1-chart --values microservice1-values.yaml

# Install Microservice 2
helm install microservice2-release ./microservice2-chart --values microservice2-values.yaml
```

2. **Make the Script Executable**:

```sh
chmod +x deploy.sh
```

3. **Run the Script**:

```sh
./deploy.sh
```

### Pros and Cons of Each Method

#### Manual Installation

**Pros**:
- Simple and straightforward.
- Easy to understand and debug.

**Cons**:
- Time-consuming if you have many services.
- Higher risk of human error.

#### Scripted Installation

**Pros**:
- Efficient and scalable.
- Reduces the chance of human error.
- Can be easily modified and reused.

**Cons**:
- Requires additional setup to create and maintain the script.
- Debugging can be more complex if issues arise.

### Real-World Examples

#### Recent CVEs and Breaches

While Helm itself has not been the direct target of major CVEs, misconfigurations and insecure practices during deployment can lead to vulnerabilities. For example, if sensitive data is included in the values files, it can be exposed if the files are not properly secured.

#### Example: Insecure Values File

Consider a scenario where a values file contains sensitive information such as database credentials:

```yaml
# values.yaml
database:
  username: admin
  password: supersecret
```

If this file is not properly secured, it can be accessed by unauthorized users, leading to potential security breaches.

### How to Prevent / Defend

#### Secure Configuration Management

1. **Use Environment Variables**: Instead of hardcoding sensitive information in values files, use environment variables to pass secrets at runtime.
2. **Kubernetes Secrets**: Store sensitive data in Kubernetes secrets and reference them in your Helm charts.
3. **Encryption**: Encrypt sensitive data in values files using tools like `sops`.

#### Example: Using Environment Variables

Instead of hardcoding database credentials in the values file, use environment variables:

```yaml
# values.yaml
database:
  username: {{ .Values.database.username }}
  password: {{ .Values.database.password }}
```

Then, set the environment variables when running the Helm command:

```sh
export DATABASE_USERNAME=admin
export DATABASE_PASSWORD=supersecret
helm install my-release ./chart --set database.username=$DATABASE_USERNAME,database.password=$DATABASE_PASSWORD
```

#### Example: Using Kubernetes Secrets

Store sensitive data in Kubernetes secrets and reference them in your Helm charts:

1. **Create a Secret**:

```sh
kubectl create secret generic db-credentials --from-literal=username=admin --from-literal=password=supersecret
```

2. **Reference the Secret in the Chart**:

```yaml
# values.yaml
database:
  username: {{ .Values.database.username }}
  password: {{ .Values.database.password }}
```

3. **Deploy the Chart**:

```sh
helm install my-release ./chart --set database.username=$(kubectl get secret db-credentials -o jsonpath='{.data.username}' | base64 --decode),database.password=$(kubectl get secret db-credentials -o jsonpath='{.data.password}' | base64 --decode)
```

### Pitfalls and Common Mistakes

#### Incorrect Values Files

One common mistake is using incorrect or outdated values files. Always ensure that the values file matches the requirements of the chart.

#### Example: Incorrect Values File

If the values file does not match the expected structure, the deployment may fail:

```yaml
# incorrect-values.yaml
database:
  user: admin
  pass: supersecret
```

The correct structure should be:

```yaml
# correct-values.yaml
database:
  username: admin
  password: supersecret
```

#### Missing Dependencies

Another common issue is missing dependencies. Ensure that all required dependencies are included in the chart.

#### Example: Missing Dependency

If a chart depends on another chart, ensure that the dependency is included:

```yaml
# Chart.yaml
dependencies:
  - name: redis
    version: 1.0.0
    repository: https://charts.example.com
```

### Conclusion

Deploying microservices with Helm provides a powerful and flexible way to manage Kubernetes applications. Whether you choose to deploy manually or through a script, understanding the nuances of Helm charts and values files is crucial for successful and secure deployments. By following best practices and securing your configurations, you can ensure that your microservices are deployed efficiently and securely.

### Practice Labs

For hands-on practice with Helm and microservices deployment, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security, including some that involve deploying microservices.
- **OWASP Juice Shop**: A deliberately insecure web application for security training, which can be deployed using Helm.
- **Kubernetes Goat**: A security-focused Kubernetes lab that includes exercises on deploying and securing microservices.

These labs provide practical experience in deploying and securing microservices using Helm, helping you to master the concepts covered in this chapter.

---
<!-- nav -->
[[02-Creating a Helmfile|Creating a Helmfile]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/14-Deploying Microservices with Helm Commands/00-Overview|Overview]] | [[04-Uninstalling Microservices with Helm|Uninstalling Microservices with Helm]]
