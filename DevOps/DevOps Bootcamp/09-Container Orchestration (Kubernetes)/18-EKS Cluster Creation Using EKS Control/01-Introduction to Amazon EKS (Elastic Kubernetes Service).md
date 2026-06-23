---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Amazon EKS (Elastic Kubernetes Service)

Amazon Elastic Kubernetes Service (EKS) is a managed service that makes it easy to run Kubernetes on AWS without needing to stand up or maintain your own Kubernetes control plane. With EKS, you can use Kubernetes to run and manage containerized applications on AWS without needing to install and operate your own Kubernetes cluster. This allows you to focus on deploying and maintaining your applications, rather than managing the underlying infrastructure.

### Key Concepts

- **Kubernetes**: An open-source system for automating deployment, scaling, and management of containerized applications.
- **Control Plane**: The core components of Kubernetes that manage the cluster, including the API server, etcd, scheduler, controller manager, and cloud controller manager.
- **Worker Nodes**: The machines that run your applications and pods. They listen to the control plane for instructions on what to run.

### EKS Managed Node Groups

One of the key features of EKS is the ability to create and manage node groups. A node group is a collection of worker nodes that share similar configurations and are managed together. EKS provides managed node groups, which are fully managed by AWS, simplifying the process of provisioning and maintaining worker nodes.

#### Example: Creating an EKS Managed Node Group

To create an EKS managed node group, you can use the `eksctl` command-line tool, which is a powerful tool for creating and managing EKS clusters. Here’s an example of how to create a managed node group:

```bash
eksctl create nodegroup --cluster my-cluster --region us-west-2 --name my-node-group --instance-type t3.medium --nodes 2 --nodes-min 1 --nodes-max 3
```

This command creates a node group named `my-node-group` in the `us-west-2` region with two initial nodes, a minimum of one node, and a maximum of three nodes.

### Fargate Support

Fargate is a compute engine for AWS that allows you to run containers without having to manage servers or clusters. When used with EKS, Fargate enables you to run Kubernetes workloads without provisioning or managing any worker nodes. This can significantly reduce the operational overhead associated with running a Kubernetes cluster.

#### Example: Enabling Fargate Support

To enable Fargate support in your EKS cluster, you can use the following `eksctl` command:

```bash
eksctl create fargate-profile --cluster my-cluster --namespace default --name my-fargate-profile
```

This command creates a Fargate profile named `my-fargate-profile` in the `default` namespace of the `my-cluster` EKS cluster.

### Fully Private Cluster

A fully private cluster is an EKS cluster where the worker nodes are deployed in a private subnet and are not accessible from the internet. This enhances security by ensuring that the worker nodes cannot be accessed directly from the internet.

#### Example: Creating a Fully Private Cluster

To create a fully private EKS cluster, you can use the following `eksctl` command:

```bash
eksctl create cluster --name my-private-cluster --region us-west-2 --vpc-private-subnets=subnet-12345678,subnet-87654321 --vpc-public-subnets= --vpc-cidr=10.0.0.0/16 --private-networking
```

This command creates a private EKS cluster named `my-private-cluster` in the `us-west-2` region with private subnets and no public subnets.

### Configuration Using YAML Files

EKS Control allows you to configure and manage your EKS cluster using YAML files. This approach provides a declarative way to define your cluster configuration, making it easier to manage and version control your configurations.

#### Example YAML File

Here is an example of a YAML file that defines an EKS cluster configuration:

```yaml
apiVersion: eks.aws.amazon.com/v1alpha1
kind: Cluster
metadata:
  name: my-cluster
spec:
  version: "1.21"
  endpointPrivateAccess: true
  endpointPublicAccess: false
  resourcesVpcConfig:
    subnetIds:
      - subnet-12345678
      - subnet-87654321
    securityGroupIds:
      - sg-12345678
  nodeGroups:
    - name: my-node-group
      instanceType: t3.medium
      desiredSize: 2
      minSize: 1
      maxSize: 3
```

This YAML file defines an EKS cluster named `my-cluster` with a private endpoint, two subnets, a security group, and a node group with two initial nodes.

### Managing the Cluster After Creation

EKS Control is not just for creating the cluster; it is also used for managing and configuring the cluster after it is created. This includes upgrading the cluster, adding or removing nodes, changing node groups, and adding Fargate profiles.

#### Example: Upgrading the Cluster

To upgrade the cluster, you can use the following `eksctl` command:

```bash
eksctl upgrade cluster --name my-cluster --region us-west-2 --version 1.22
```

This command upgrades the `my-cluster` EKS cluster to version `1.22`.

### Default AMI

When creating an EKS cluster, a default Amazon Machine Image (AMI) is used for the worker nodes. The AMI contains the necessary software and configurations to run Kubernetes on the worker nodes.

#### Example: Specifying a Custom AMI

To specify a custom AMI, you can modify the YAML file as follows:

```yaml
apiVersion: eks.aws.amazon.com/v1alpha1
kind: Cluster
metadata:
  name: my-cluster
spec:
  version: "1.21"
  endpointPrivateAccess: true
  endpointPublicAccess: false
  resourcesVpcConfig:
    subnetIds:
      - subnet-12345678
      - subnet-87654321
    securityGroupIds:
      - sg-12345678
  nodeGroups:
    - name: my-node-group
      ami: ami-12345678
      instanceType: t3.medium
      desiredSize: 2
      minSize: 1
      maxSize: 3
```

This YAML file specifies a custom AMI for the worker nodes.

### How to Prevent / Defend

#### Detection

To detect potential issues with your EKS cluster, you can use AWS CloudTrail to log and monitor API calls made to your EKS cluster. Additionally, you can use AWS Config to track changes to your EKS resources and ensure compliance with your security policies.

#### Prevention

To prevent unauthorized access to your EKS cluster, you should:

- Enable IAM roles for service accounts (IRSA) to control access to your cluster.
- Use network policies to restrict traffic between pods.
- Enable encryption at rest for your EKS cluster.

#### Secure Coding Fixes

Here is an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration:**

```yaml
apiVersion: eks.aws.amazon.com/v1alpha1
kind: Cluster
metadata:
  name: my-cluster
spec:
  version: "1.21"
  endpointPrivateAccess: true
  endpointPublicAccess: true
  resourcesVpcConfig:
    subnetIds:
      - subnet-12345678
      - subnet-87654321
    securityGroupIds:
      - sg-12345678
  nodeGroups:
    - name: my-node-group
      instanceType: t3.medium
      desiredSize: 2
      minSize: 1
      maxSize: 3
```

**Secure Configuration:**

```yaml
apiVersion: eks.aws.amazon.com/v1alpha1
kind: Cluster
metadata:
  name: my-cluster
spec:
  version: "1.21"
  endpointPrivateAccess: true
  endpointPublicAccess: false
  resourcesVpcConfig:
    subnetIds:
      - subnet-12345678
      - subnet-87654321
    securityGroupIds:
      - sg-12345678
  nodeGroups:
    - name: my-node-group
      instanceType: t3.medium
      desiredSize: 2
      minSize: 1
      maxSize: 3
```

In the secure configuration, the `endpointPublicAccess` is set to `false`, preventing public access to the cluster.

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-25741**: A vulnerability in Kubernetes allowed attackers to bypass authentication and gain unauthorized access to the cluster. This highlights the importance of keeping your Kubernetes version up to date and using network policies to restrict access.
- **AWS RDS Data Exfiltration**: In 2022, a misconfigured AWS RDS instance led to data exfiltration. This underscores the importance of properly securing your EKS clusters and ensuring that sensitive data is encrypted both in transit and at rest.

### Conclusion

Creating and managing an EKS cluster using EKS Control provides a powerful and flexible way to deploy and manage containerized applications on AWS. By leveraging managed node groups, Fargate support, and fully private clusters, you can enhance the security and reliability of your EKS clusters. Using YAML files for configuration provides a declarative and versionable approach to managing your cluster, while the ability to manage the cluster after creation ensures that you can adapt to changing requirements.

### Practice Labs

For hands-on practice with EKS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web application security.
- **OWASP Juice Shop**: A deliberately insecure web application designed for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

These labs provide practical experience in deploying and securing EKS clusters, helping you to master the concepts covered in this chapter.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/18-EKS Cluster Creation Using EKS Control/00-Overview|Overview]] | [[02-Introduction to EKS Cluster Creation Using EKS Control|Introduction to EKS Cluster Creation Using EKS Control]]
