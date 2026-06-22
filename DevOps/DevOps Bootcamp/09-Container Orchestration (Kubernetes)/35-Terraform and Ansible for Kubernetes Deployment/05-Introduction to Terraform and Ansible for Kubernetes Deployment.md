---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Terraform and Ansible for Kubernetes Deployment

In this section, we will explore how to use Terraform and Ansible to deploy applications into a Kubernetes cluster. This is a common and widely-used approach in modern DevOps practices. We'll start by setting up a Kubernetes cluster on AWS using Terraform, and then we'll use Ansible to deploy application components within that cluster.

### Background Theory

#### What is Terraform?

Terraform is an open-source infrastructure as code (IaC) tool developed by HashiCorp. It allows you to define and provision your infrastructure using declarative configuration files written in the HashiCorp Configuration Language (HCL). Terraform supports a wide range of cloud providers, including AWS, Azure, Google Cloud, and more.

**Why Use Terraform?**
- **Consistency**: Terraform ensures that your infrastructure is consistent across different environments (development, staging, production).
- **Version Control**: You can store your Terraform configuration files in version control systems like Git, allowing you to track changes and collaborate with team members.
- **Automation**: Terraform automates the provisioning and management of your infrastructure, reducing the risk of human error.

#### What is Ansible?

Ansible is an open-source automation tool that simplifies IT automation, including configuration management, application deployment, and orchestration. Ansible uses a simple YAML-based language called playbooks to define tasks and workflows.

**Why Use Ansible?**
- **Agentless**: Ansible does not require agents to be installed on managed nodes, making it easier to manage large numbers of servers.
- **Idempotent**: Ansible playbooks are idempotent, meaning they can be run multiple times without causing unintended side effects.
- **Role-Based**: Ansible supports roles, which allow you to organize and reuse code across different projects.

### Setting Up a Kubernetes Cluster on AWS Using Terraform

To set up a Kubernetes cluster on AWS, we will use Terraform to automate the process. We'll start by creating a Terraform project and defining the necessary resources.

#### Step-by-Step Guide

1. **Initialize Terraform Project**

   First, initialize your Terraform project by creating a `main.tf` file and specifying the required provider.

   ```hcl
   provider "aws" {
     region = "us-west-2"
   }
   ```

2. **Create EKS Cluster**

   Next, we'll define the EKS cluster using the `aws_eks_cluster` resource.

   ```hcl
   resource "aws_eks_cluster" "example" {
     name     = "example-cluster"
     role_arn = aws_iam_role.example.arn
     vpc_config {
       subnet_ids = [aws_subnet.example.id]
       security_group_ids = [aws_security_group.example.id]
     }
   }

   resource "aws_iam_role" "example" {
     name = "example-role"

     assume_role_policy = jsonencode({
       Version = "2012-10-17"
       Statement = [
         {
           Action = "sts:AssumeRole"
           Effect = "Allow"
           Principal = {
             Service = "eks.amazonaws.com"
           }
         },
       ]
     })
   }

   resource "aws_subnet" "example" {
     vpc_id     = aws_vpc.example.id
     cidr_block = "10.0.1.0/24"
     availability_zone = "us-west-2a"
   }

   resource "aws_vpc" "example" {
     cidr_block = "10.0.0.0/16"
   }

   resource "aws_security_group" "example" {
     vpc_id = aws_vpc.example.id

     ingress {
       from_port   = 443
       to_port     = 443
       protocol    = "tcp"
       cidr_blocks = ["0.0.0.0/0"]
     }
   }
   ```

3. **Apply Terraform Configuration**

   Run the following commands to initialize and apply the Terraform configuration:

   ```sh
   terraform init
   terraform apply
   ```

   This will create the EKS cluster and associated resources on AWS.

### Configuring Ansible to Connect to the EKS Cluster

Once the EKS cluster is up and running, we can use Ansible to deploy application components within the cluster.

#### Step-by-Step Guide

1. **Install Ansible**

   Ensure that Ansible is installed on your local machine. You can install it using pip:

   ```sh
   pip install ansible
   ```

2. **Define Ansible Playbook**

   Create an Ansible playbook (`deploy.yml`) to deploy a simple deployment and service components inside the EKS cluster.

   ```yaml
   ---
   - name: Deploy application to EKS cluster
     hosts: localhost
     gather_facts: false
     tasks:
       - name: Add kubectl to PATH
         shell: |
           export PATH=$PATH:/home/user/.local/bin
           kubectl config view
         register: kubectl_output
         changed_when: false

       - name: Deploy application
         k8s:
           api_key: "{{ lookup('env', 'KUBECONFIG') }}"
           definition:
             apiVersion: apps/v1
             kind: Deployment
             metadata:
               name: example-deployment
             spec:
               replicas: 3
               selector:
                 matchLabels:
                   app: example
               template:
                 metadata:
                   labels:
                     app: example
                 spec:
                   containers:
                   - name: example-container
                     image: nginx:latest
                     ports:
                     - containerPort: 80
           state: present

       - name: Expose service
         k8s:
           api_key: "{{ lookup('env', 'KUBECONFIG') }}"
           definition:
             apiVersion: v1
             kind: Service
             metadata:
               name: example-service
             spec:
               type: LoadBalancer
               selector:
                 app: example
               ports:
               - port: 80
                 targetPort: 80
           state: present
   ```

3. **Run Ansible Playbook**

   Execute the Ansible playbook to deploy the application components:

   ```sh
   ansible-playbook -i inventory.ini deploy.yml
   ```

### Full Example: Terraform and Ansible for Kubernetes Deployment

#### Terraform Configuration

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_eks_cluster" "example" {
  name     = "example-cluster"
  role_arn = aws_iam_role.example.arn
  vpc_config {
    subnet_ids = [aws_subnet.example.id]
    security_group_ids = [aws_security_group.example.id]
  }
}

resource "aws_iam_role" "example" {
  name = "example-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_subnet" "example" {
  vpc_id     = aws_vpc.example.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-west-2a"
}

resource "aws_vpc" "example" {
  cidr_block = "1.0.0.0/16"
}

resource "aws_security_group" "example" {
  vpc_id = aws_vpc.example.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

#### Ansible Playbook

```yaml
---
- name: Deploy application to EKS cluster
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Add kubectl to PATH
      shell: |
        export PATH=$PATH:/home/user/.local/bin
        kubectl config view
      register: kubectl_output
      changed_when: false

    - name: Deploy application
      k8s:
        api_key: "{{ lookup('env', 'KUBECONFIG') }}"
        definition:
          apiVersion: apps/v1
          kind: Deployment
          metadata:
            name: example-deployment
          spec:
            replicas: 3
            selector:
              matchLabels:
                app: example
            template:
              metadata:
                labels:
                  app: example
              spec:
                containers:
                - name: example-container
                  image: nginx:latest
                  ports:
                  - containerPort: 80
        state: present

    - name: Expose service
      k8s:
        api_key: "{{ lookup('env', 'KUBECONFIG') }}"
        definition:
          apiVersion: v1
          kind: Service
          metadata:
            name: example-service
          spec:
            type: LoadBalancer
            selector:
              app: example
            ports:
            - port: 80
              targetPort: 80
        state: present
```

### Common Pitfalls and How to Prevent Them

#### Terraform Pitfalls

1. **Resource Dependencies**
   - **Problem**: Terraform may fail to apply changes due to incorrect resource dependencies.
   - **Solution**: Ensure that resources are defined in the correct order and use explicit dependencies where necessary.

2. **State Management**
   - **Problem**: Losing the Terraform state file can result in data loss and inconsistencies.
   - **Solution**: Store the state file in a remote backend like AWS S3 or Azure Blob Storage.

#### Ansible Pitfalls

1. **Incorrect Configuration**
   - **Problem**: Incorrect configuration in the Ansible playbook can lead to deployment failures.
   - **Solution**: Validate the playbook using `ansible-playbook --check` before applying changes.

2. **Security Risks**
   - **Problem**: Exposing sensitive information in playbooks can lead to security vulnerabilities.
   - **Solution**: Use Ansible Vault to encrypt sensitive data and ensure proper access controls.

### Real-World Examples and Recent CVEs

#### Real-World Example: Kubernetes Cluster Deployment

A recent real-world example of deploying a Kubernetes cluster using Terraform and Ansible can be found in the [HashiCorp Learn](https://learn.hashicorp.com/) tutorials. These tutorials provide step-by-step guides and practical examples for deploying Kubernetes clusters on various cloud providers.

#### Recent CVEs

1. **CVE-2021-25741**
   - **Description**: A vulnerability in Kubernetes allowed unauthorized access to the API server.
   - **Impact**: Attackers could gain unauthorized access to the cluster and execute arbitrary commands.
   - **Mitigation**: Ensure that the Kubernetes API server is properly configured with RBAC (Role-Based Access Control) and that all nodes are up-to-date with the latest security patches.

2. **CVE-2021-25742**
   - **Description**: A vulnerability in Kubernetes allowed unauthorized access to the etcd database.
   - **Impact**: Attackers could read and modify the etcd database, leading to potential data breaches.
   - **Mitigation**: Ensure that the etcd database is properly secured with TLS encryption and that all nodes are up-to-date with the latest security patches.

### How to Prevent / Defend

#### Detection

1. **Logging and Monitoring**
   - **Solution**: Implement logging and monitoring solutions like ELK Stack (Elasticsearch, Logstash, Kibana) to detect and respond to security incidents in real-time.

2. **Security Scanning**
   - **Solution**: Use tools like Trivy and Aqua Security to scan your Kubernetes cluster for vulnerabilities and misconfigurations.

#### Prevention

1. **Secure Configuration**
   - **Solution**: Follow the Kubernetes security best practices and ensure that all nodes are properly configured with RBAC and network policies.

2. **Regular Updates**
   - **Solution**: Keep your Kubernetes cluster and all related components up-to-date with the latest security patches and updates.

#### Secure Coding Fixes

##### Vulnerable Code

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
spec:
  containers:
  - name: example-container
    image: nginx:latest
    ports:
    - containerPort: 80
```

##### Fixed Code

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
spec:
  containers:
  - name: example-container
    image: nginx:latest
    ports:
    - containerPort: 80
    securityContext:
      capabilities:
        drop:
        - ALL
      readOnlyRootFilesystem: true
```

### Practice Labs

For hands-on practice with Terraform and Ansible for Kubernetes deployment, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs for learning web security concepts.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.
- **WebGoat**: An interactive web application that teaches web security lessons.

These labs provide a safe environment to practice and learn DevOps and security concepts.

### Conclusion

In this section, we explored how to use Terraform and Ansible to deploy applications into a Kubernetes cluster. We covered the background theory, step-by-step guide, common pitfalls, real-world examples, and how to prevent and defend against security risks. By following these guidelines, you can effectively manage your infrastructure and ensure the security of your applications.

---
<!-- nav -->
[[04-Introduction to Python Modules and Package Management|Introduction to Python Modules and Package Management]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/35-Terraform and Ansible for Kubernetes Deployment/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/35-Terraform and Ansible for Kubernetes Deployment/06-Practice Questions & Answers|Practice Questions & Answers]]
