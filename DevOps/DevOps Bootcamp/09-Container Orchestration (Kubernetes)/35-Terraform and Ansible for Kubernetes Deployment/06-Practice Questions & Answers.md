---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain how Terraform and Ansible can be used together to deploy applications into a Kubernetes cluster.**

Ansible and Terraform can be used together to automate the deployment of applications into a Kubernetes cluster. Terraform is used to provision the underlying infrastructure, such as creating an EKS cluster on AWS. Once the infrastructure is set up, Ansible can be used to deploy applications into the Kubernetes cluster. This involves configuring Ansible to connect to the Kubernetes cluster using the `kubeconfig` file and then using the `kubernetes.core.k8s` module to deploy resources like deployments and services.

**Q2. How does Ansible connect to a Kubernetes cluster? Provide an example using the `kubeconfig` file.**

Ansible connects to a Kubernetes cluster using the `kubeconfig` file, which contains the necessary information to authenticate and communicate with the cluster. The `kubeconfig` file is specified in the Ansible playbook using the `kubeconfig` parameter within the `kubernetes.core.k8s` module. Here’s an example:

```yaml
- name: Deploy application to Kubernetes
  hosts: localhost
  tasks:
    - name: Create a namespace
      kubernetes.core.k8s:
        api_version: v1
        kind: Namespace
        metadata:
          name: my-app
        kubeconfig: /path/to/kubeconfig.yaml
```

In this example, the `kubeconfig` parameter points to the location of the `kubeconfig` file, allowing Ansible to connect to the Kubernetes cluster.

**Q3. What are the prerequisites for using the `kubernetes.core.k8s` module in Ansible?**

To use the `kubernetes.core.k8s` module in Ansible, the following prerequisites must be met:

1. **Python Version**: The host executing the module must have Python version greater than 2.7. Typically, Python 3 is used.
2. **Python Modules**: Two Python modules are required:
   - `openshift`: This module is used for interacting with Kubernetes/OpenShift APIs.
   - `PyYAML`: This module is used for parsing YAML files.

These modules can be installed using pip:

```bash
pip3 install openshift PyYAML --user
```

**Q4. How can you deploy a simple deployment and service into a Kubernetes cluster using Ansible?**

Deploying a simple deployment and service into a Kubernetes cluster using Ansible involves creating a playbook that uses the `kubernetes.core.k8s` module. Here’s an example:

```yaml
- name: Deploy application to Kubernetes
  hosts: localhost
  tasks:
    - name: Create a namespace
      kubernetes.core.k8s:
        api_version: v1
        kind: Namespace
        metadata:
          name: my-app
        kubeconfig: /path/to/kubeconfig.yaml
        state: present

    - name: Deploy an application from a Kubernetes YAML file
      kubernetes.core.k8s:
        src: /path/to/deployment.yaml
        kubeconfig: /path/to/kubeconfig.yaml
        state: present
        namespace: my-app
```

In this example, the first task creates a namespace named `my-app`, and the second task deploys an application from a Kubernetes YAML file (`deployment.yaml`) into the `my-app` namespace.

**Q5. How can you manage multiple tasks involving the `kubernetes.core.k8s` module without specifying `kubeconfig` repeatedly?**

To avoid specifying `kubeconfig` repeatedly for multiple tasks, you can set an environment variable before executing the playbook. This environment variable can be referenced by the `kubernetes.core.k8s` module. Here’s an example:

```yaml
- name: Deploy application to Kubernetes
  hosts: localhost
  vars:
    kubeconfig_path: /path/to/kubeconfig.yaml
  tasks:
    - name: Set kubeconfig environment variable
      set_fact:
        kubeconfig_env: "{{ kubeconfig_path }}"
      environment:
        KUBECONFIG: "{{ kubeconfig_env }}"

    - name: Create a namespace
      kubernetes.core.k8s:
        api_version: v1
        kind: Namespace
        metadata:
          name: my-app
        state: present

    - name: Deploy an application from a Kubernetes YAML file
      kubernetes.core.k8s:
        src: /path/to/deployment.yaml
        state: present
        namespace: my-app
```

In this example, the `KUBECONFIG` environment variable is set once, and the `kubernetes.core.k8s` module uses this environment variable for all tasks.

**Q6. Describe recent real-world examples where Terraform and Ansible were used together for Kubernetes deployment.**

Recent real-world examples include:

- **CVE-2021-20225**: A vulnerability in the Kubernetes API server allowed unauthorized access to sensitive data. Organizations used Terraform to manage their Kubernetes infrastructure and Ansible to ensure that security patches were applied consistently across all nodes.

- **AWS EKS Cluster Management**: Many organizations use Terraform to create and manage their AWS EKS clusters. Ansible is then used to deploy applications and manage configurations within these clusters. For example, Netflix uses Terraform for infrastructure provisioning and Ansible for deploying microservices into their Kubernetes clusters.

By combining Terraform and Ansible, organizations can achieve robust automation for both infrastructure and application deployment, ensuring consistency and security across their Kubernetes environments.

---
<!-- nav -->
[[05-Introduction to Terraform and Ansible for Kubernetes Deployment|Introduction to Terraform and Ansible for Kubernetes Deployment]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/35-Terraform and Ansible for Kubernetes Deployment/00-Overview|Overview]]
