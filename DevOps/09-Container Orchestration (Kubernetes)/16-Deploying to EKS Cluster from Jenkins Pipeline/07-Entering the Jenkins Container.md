---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Entering the Jenkins Container

When deploying applications to an Amazon Elastic Kubernetes Service (EKS) cluster using a Jenkins pipeline, one of the initial steps involves setting up the necessary tools within the Jenkins environment. Specifically, we need to install `kubectl`, the command-line tool for interacting with Kubernetes clusters, inside the Jenkins container.

### Why Enter the Jenkins Container?

The Jenkins container is where the Jenkins agent runs, and it is responsible for executing the pipeline steps. By entering the container, we can ensure that any tools we install are available to the pipeline. This is particularly important because the Jenkins user typically does not have administrative privileges, and we need root access to install new tools.

#### Steps to Enter the Jenkins Container

To enter the Jenkins container, we use the `docker exec` command. This command allows us to run a new process inside a running container. Here’s how we do it:

```sh
docker exec -it <container_id> /bin/bash
```

- `-i`: Keeps STDIN open even if not attached.
- `-t`: Allocates a pseudo-TTY.
- `<container_id>`: The ID of the Jenkins container.
- `/bin/bash`: The shell to start inside the container.

### Installing `kubectl` Inside the Container

Once inside the container, we need to install `kubectl`. This tool is essential for managing Kubernetes clusters, including deploying applications and inspecting cluster resources.

#### Downloading `kubectl`

We use the `curl` command to download the latest stable version of `kubectl` from the official Kubernetes repository:

```sh
curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
```

This command performs the following actions:
- `curl -LO`: Downloads the file and saves it locally.
- `https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl`: Fetches the URL for the latest stable version of `kubectl`.

#### Making `kubectl` Executable

After downloading `kubectl`, we need to make it executable:

```sh
chmod +x kubectl
```

This command changes the file permissions to allow execution.

#### Moving `kubectl` to the PATH

Next, we move the `kubectl` binary to a directory that is included in the system's PATH, such as `/usr/local/bin`:

```sh
mv kubectl /usr/local/bin/
```

This ensures that `kubectl` is accessible from any location within the container.

### Verifying the Installation

To verify that `kubectl` is installed correctly, we can check its version:

```sh
kubectl version --client
```

This command should output the version of `kubectl` installed in the container. If the installation was successful, you should see something like:

```
Client Version: version.Info{Major:"1", Minor:"24", GitVersion:"v1.24.0", GitCommit:"52c56ce7a8272f0c8bd4e0952fe4076476b8d144", GitTreeState:"clean", BuildDate:"2022-06-09T16:52:29Z", GoVersion:"go1.18.1", Compiler:"gc", Platform:"linux/amd64"}
```

### Connecting to the EKS Cluster

At this point, `kubectl` is installed, but we are not yet connected to any Kubernetes cluster. To connect to an EKS cluster, we need to configure `kubectl` with the appropriate credentials and context.

#### Configuring `kubectl` for EKS

To configure `kubectl` for an EKS cluster, we need to set up the `kubeconfig` file. This file contains the necessary information to authenticate and communicate with the EKS cluster.

```sh
aws eks update-kubeconfig --name <cluster_name> --region <region>
```

- `<cluster_name>`: The name of your EKS cluster.
- `<region>`: The AWS region where your EKS cluster is located.

This command updates the `kubeconfig` file to include the necessary credentials and context for the specified EKS cluster.

### Verifying the Connection

To verify that `kubectl` is configured correctly and can communicate with the EKS cluster, we can list the nodes in the cluster:

```sh
kubectl get nodes
```

If the connection is successful, you should see a list of nodes in the cluster.

### Integrating `kubectl` into the Jenkins Pipeline

With `kubectl` installed and configured, we can now integrate it into our Jenkins pipeline. This allows us to automate tasks such as deploying applications to the EKS cluster.

#### Example Jenkins Pipeline

Here’s an example of a Jenkins pipeline that uses `kubectl` to deploy an application to an EKS cluster:

```groovy
pipeline {
    agent { docker 'jenkins-slave' }

    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
        stage('Deploy') {
            steps {
                sh 'kubectl apply -f deployment.yaml'
            }
        }
    }
}
```

In this pipeline:
- The `agent` directive specifies that the pipeline should run inside a Docker container named `jenkins-slave`.
- The `Build` stage builds the application.
- The `Deploy` stage deploys the application to the EKS cluster using `kubectl`.

### Common Pitfalls and How to Prevent Them

#### Insufficient Permissions

One common issue is insufficient permissions. Ensure that the Jenkins user has the necessary permissions to execute `kubectl` commands. This can be achieved by configuring the `kubeconfig` file correctly and ensuring that the Jenkins user has the required roles and permissions in the EKS cluster.

#### Incorrect Configuration

Another common issue is incorrect configuration of the `kubeconfig` file. Ensure that the `kubeconfig` file is correctly set up with the necessary credentials and context for the EKS cluster.

#### How to Detect and Prevent

To detect issues, you can check the logs of the Jenkins pipeline and the output of `kubectl` commands. If there are errors, review the `kubeconfig` file and ensure that the Jenkins user has the necessary permissions.

To prevent these issues, follow these best practices:
- Use IAM roles and policies to grant the Jenkins user the necessary permissions.
- Regularly review and audit the `kubeconfig` file and the Jenkins pipeline configuration.
- Use tools like `kubectl` and `aws eks` to validate the configuration and permissions.

### Secure Coding Practices

#### Vulnerable Code Example

Here’s an example of insecure code that does not properly handle permissions:

```groovy
pipeline {
    agent { docker 'jenkins-slave' }

    stages {
        stage('Deploy') {
            steps {
                sh 'kubectl apply -f deployment.yaml'
            }
        }
    }
}
```

#### Secure Code Example

Here’s an example of secure code that properly handles permissions:

```groovy
pipeline {
    agent { docker 'jenkins-slave' }

    stages {
        stage('Configure Kubeconfig') {
            steps {
                sh 'aws eks update-kubeconfig --name my-cluster --region us-west-2'
            }
        }
        stage('Deploy') {
            steps {
                sh 'kubectl apply -f deployment.yaml'
            }
        }
    }
}
```

In the secure code example, we explicitly configure the `kubeconfig` file with the necessary credentials and context for the EKS cluster.

### Conclusion

By following these steps, you can successfully install and configure `kubectl` inside the Jenkins container and integrate it into your Jenkins pipeline to deploy applications to an EKS cluster. Ensuring proper permissions and configuration is crucial to avoid common pitfalls and maintain the security of your pipeline and cluster.

### Practice Labs

For hands-on practice, consider the following labs:
- **PortSwigger Web Security Academy**: Offers a variety of labs related to Kubernetes and container security.
- **CloudGoat**: Provides scenarios for practicing cloud security, including EKS and Jenkins integration.
- **AWS Official Workshops**: Includes workshops on deploying applications to EKS using Jenkins pipelines.

These labs provide practical experience and help reinforce the concepts covered in this chapter.

---
<!-- nav -->
[[06-Deploying to an EKS Cluster from a Jenkins Pipeline|Deploying to an EKS Cluster from a Jenkins Pipeline]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/16-Deploying to EKS Cluster from Jenkins Pipeline/00-Overview|Overview]] | [[08-Jenkins Home Directory and Configuration|Jenkins Home Directory and Configuration]]
