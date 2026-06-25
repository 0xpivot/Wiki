---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Deploying Jenkins to Kubernetes on Linode

### Introduction to Jenkins and Kubernetes

Jenkins is an open-source automation server that provides hundreds of plugins to support building, deploying, and automating any project. Kubernetes, on the other hand, is an open-source system for automating deployment, scaling, and management of containerized applications. Together, Jenkins and Kubernetes form a powerful combination for continuous integration and continuous delivery (CI/CD).

### Setting Up Jenkins on Kubernetes

To deploy Jenkins on Kubernetes, you first need to set up a Kubernetes cluster. Linode offers a managed Kubernetes service called LKE (Linode Kubernetes Engine), which simplifies the process of setting up and managing a Kubernetes cluster.

#### Creating a Kubernetes Cluster on Linode

1. **Sign Up for Linode**: If you haven't already, sign up for a Linode account.
2. **Create a Kubernetes Cluster**:
    - Navigate to the Linode dashboard.
    - Click on "Kubernetes" in the left-hand menu.
    - Click on "Create Kubernetes Cluster".
    - Configure your cluster settings, such as the number of nodes, region, and node type.
    - Click "Create".

Once your cluster is created, you can access it using `kubectl`, the Kubernetes command-line tool.

#### Deploying Jenkins to Kubernetes

To deploy Jenkins to your Kubernetes cluster, you can use a Helm chart. Helm is a package manager for Kubernetes that makes it easy to install and manage applications.

1. **Install Helm**:
    - Follow the official Helm documentation to install Helm on your machine.
    - Initialize Helm by running `helm init`.

2. **Deploy Jenkins**:
    - Add the Jenkins Helm repository:
      ```bash
      helm repo add jenkinsci https://charts.jenkins.io
      ```
    - Update the Helm repository:
      ```bash
      helm repo update
      ```
    - Install Jenkins using the Helm chart:
      ```bash
      helm install my-jenkins jenkinsci/jenkins
      ```

This will deploy Jenkins to your Kubernetes cluster. You can verify the deployment by running:

```bash
kubectl get pods
```

You should see a Jenkins pod running in the default namespace.

### Configuring Jenkins for Kubernetes Deployment

Once Jenkins is deployed, you need to configure it to interact with your Kubernetes cluster. This involves setting up credentials and configuring the Kubernetes plugin.

#### Setting Up Credentials

1. **Access Jenkins**:
    - Open your browser and navigate to `http://<your-jenkins-server>:8080`.
    - Log in using the initial admin password, which you can find in the Jenkins pod logs.

2. **Add Kubernetes Credentials**:
    - Go to `Manage Jenkins` > `Manage Credentials` > `System`.
    - Click on `Global credentials (unrestricted)` and then `Add Credentials`.
    - Select `Kind` as `Secret Text`.
    - Enter the path to your Kubernetes configuration file (e.g., `~/.kube/config`) as the `Secret`.
    - Give it a meaningful ID and description, then click `OK`.

#### Configuring the Kubernetes Plugin

1. **Install the Kubernetes Plugin**:
    - Go to `Manage Jenkins` > `Manage Plugins`.
    - Search for `Kubernetes` and install the `Kubernetes` plugin.

2. **Configure the Kubernetes Cloud**:
    - Go to `Manage Jenkins` > `Configure System`.
    - Scroll down to the `Cloud` section.
    - Click on `Add a new cloud` and select `Kubernetes`.
    - Fill in the required fields:
        - **Name**: A name for your Kubernetes cloud.
        - **Kubernetes URL**: The URL of your Kubernetes API server.
        - **Kubernetes server certificate key**: If your Kubernetes server uses a custom certificate, upload it here.
        - **Credentials**: Select the credentials you added earlier.
        - **Container Capabilities**: Define the capabilities of your containers.
        - **Pod Template**: Define the pod template for your Jenkins agents.

3. **Save Configuration**:
    - Click `Save` to apply the changes.

### Deploying Applications Using Jenkins Pipeline

Now that Jenkins is configured to interact with your Kubernetes cluster, you can use Jenkins pipelines to automate the deployment of your applications.

#### Example Pipeline for a Java Maven Project

Let's walk through an example pipeline that builds a Java Maven project and deploys it to Kubernetes.

1. **Create a Jenkinsfile**:
    - Create a `Jenkinsfile` in the root of your project repository.

```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }

        stage('Deploy') {
            steps {
                script {
                    def dockerImage = docker.build("my-java-app:${env.BUILD_ID}")
                    docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-credentials') {
                        dockerImage.push()
                    }
                    kubernetesDeploy(
                        configs: 'k8s/deployment.yaml',
                        enableConfigSubstitution: true
                    )
                }
            }
        }
    }
}
```

2. **Define Kubernetes Deployment Configuration**:
    - Create a `deployment.yaml` file in the `k8s` directory of your project.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-java-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-java-app
  template:
    metadata:
      labels:
        app: my-java-app
    spec:
      containers:
      - name: my-java-app
        image: my-java-app:${BUILD_ID}
        ports:
        - containerPort: 8080
```

3. **Push the Branch to Jenkins**:
    - Push the branch containing the `Jenkinsfile` and `deployment.yaml` to your Git repository.
    - Trigger the Jenkins pipeline by pushing the branch.

### Verifying the Deployment

Once the pipeline completes, you can verify the deployment by checking the status of the pods in your Kubernetes cluster.

1. **Check Pod Status**:
    - Run the following command to list the pods:
      ```bash
      kubectl get pods
      ```

You should see the `my-java-app` pod running.

### Handling Platform Authentication

In the previous example, we used a simple setup without additional platform authentication. However, in many real-world scenarios, you need to handle platform-specific authentication mechanisms.

#### Example: AWS EKS Authentication

When deploying to Amazon Elastic Kubernetes Service (EKS), you need to authenticate using AWS IAM roles.

1. **Set Up IAM Role**:
    - Create an IAM role in AWS with permissions to access EKS.
    - Attach the role to your EC2 instances or EKS nodes.

2. **Configure Jenkins for EKS**:
    - In Jenkins, go to `Manage Jenkins` > `Manage Credentials` > `System`.
    - Add a new credential of type `AWS Access Key with Secret`.
    - Fill in the access key and secret key.

3. **Update Kubernetes Plugin Configuration**:
    - In the Kubernetes plugin configuration, specify the IAM role ARN and the region.

### Real-World Examples and Recent CVEs

#### CVE-2021-25741: Jenkins Script Security Plugin Vulnerability

CVE-2021-25741 is a critical vulnerability in the Jenkins Script Security Plugin that allows attackers to execute arbitrary code. This vulnerability highlights the importance of keeping Jenkins and its plugins up to date.

#### How to Prevent / Defend

1. **Keep Jenkins and Plugins Updated**:
    - Regularly update Jenkins and all installed plugins to the latest versions.
    - Monitor the Jenkins security advisories and apply patches promptly.

2. **Secure Jenkins Configuration**:
    - Restrict access to Jenkins using authentication and authorization mechanisms.
    - Disable unnecessary plugins and features.

3. **Use Secure Coding Practices**:
    - Avoid using scripts that execute arbitrary code.
    - Validate user input and sanitize data.

### Hands-On Labs

For practical experience with deploying Jenkins to Kubernetes, consider the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs for web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning web security.
- **WebGoat**: An interactive web application that teaches web security lessons.

These labs provide a comprehensive environment to practice and master the concepts covered in this chapter.

### Conclusion

Deploying Jenkins to Kubernetes on Linode is a powerful way to automate your CI/CD processes. By following the steps outlined in this chapter, you can set up a robust and scalable Jenkins environment that integrates seamlessly with your Kubernetes cluster. Remember to keep your setup secure by following best practices and staying updated with the latest security advisories.

---
<!-- nav -->
[[04-Introduction to Kubernetes and Linode|Introduction to Kubernetes and Linode]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/12-Deploying Jenkins to Kubernetes on Linode/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/12-Deploying Jenkins to Kubernetes on Linode/06-Practice Questions & Answers|Practice Questions & Answers]]
