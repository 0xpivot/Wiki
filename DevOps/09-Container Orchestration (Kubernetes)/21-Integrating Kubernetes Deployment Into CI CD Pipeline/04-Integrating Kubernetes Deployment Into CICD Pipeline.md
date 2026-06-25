---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Integrating Kubernetes Deployment Into CI/CD Pipeline

In the context of modern DevOps practices, integrating Kubernetes deployments into a CI/CD pipeline is essential for ensuring continuous delivery and automated testing. This integration allows for the seamless deployment of applications and ensures that the latest versions are always available. Let's delve into the details of how this is achieved, focusing on the use of environmental variables to manage dynamic image names and application names.

### Dynamic Image Names Using Environmental Variables

When deploying applications in a Kubernetes environment, one of the key challenges is managing the image names dynamically. Each time a pipeline runs, a new Docker image is generated, and this image name needs to be updated accordingly. Hardcoding the image name would lead to outdated references and potential deployment issues.

#### Why Use Environmental Variables?

Environmental variables provide a flexible way to manage dynamic values such as image names. By setting these variables in the Jenkinsfile, you ensure that the correct image name is used every time the pipeline runs. This approach avoids the need to manually update the image name in multiple places, reducing the risk of human error.

#### How to Set Up Environmental Variables

To set up environmental variables in your Jenkinsfile, follow these steps:

1. **Define the Variable**: In your Jenkinsfile, define the environmental variable that will hold the image name.
2. **Substitute the Value**: Use the variable in your Kubernetes deployment YAML file to dynamically set the image name.

Here’s an example of how to define and use an environmental variable in a Jenkinsfile:

```groovy
pipeline {
    agent any
    environment {
        IMAGE_NAME = 'your-docker-repo/your-image-name'
    }
    stages {
        stage('Build') {
            steps {
                script {
                    sh 'docker build -t ${IMAGE_NAME} .'
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    sh 'kubectl set image deployment/your-deployment ${IMAGE_NAME}'
                }
            }
        }
    }
}
```

In this example, `IMAGE_NAME` is an environmental variable that holds the name of the Docker image. The `sh` commands use this variable to build and deploy the image.

### Image Pull Policy

Another important aspect to consider is the image pull policy. This policy determines how Kubernetes handles fetching images from the registry. By default, Kubernetes uses the `IfNotPresent` policy, which means it will only pull the image if it does not already exist locally. However, for CI/CD pipelines, it is often desirable to always fetch the latest image from the registry.

#### Setting the Image Pull Policy

To ensure that the latest image is always fetched, you can set the image pull policy to `Always`. Here’s how you can do this in your Kubernetes deployment YAML:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: your-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: your-app
  template:
    metadata:
      labels:
        app: your-app
    spec:
      containers:
      - name: your-container
        image: ${IMAGE_NAME}
        imagePullPolicy: Always
```

In this YAML, `${IMAGE_NAME}` is replaced with the actual image name from the environmental variable, and `imagePullPolicy` is set to `Always`.

### Replacing Application Names with Environmental Variables

Similar to image names, application names can also be managed using environmental variables. This is particularly useful when the application name is referenced in multiple places, such as in services, deployments, and selectors.

#### Why Replace Application Names?

Replacing application names with environmental variables allows you to centralize the management of these names. If the application name changes, you only need to update it in one place, rather than searching through multiple files.

#### How to Replace Application Names

To replace application names with environmental variables, follow these steps:

1. **Define the Variable**: Define an environmental variable for the application name in your Jenkinsfile.
2. **Use the Variable**: Use this variable in your Kubernetes deployment YAML file wherever the application name is referenced.

Here’s an example of how to define and use an environmental variable for the application name:

```groovy
pipeline {
    agent any
    environment {
        APP_NAME = 'your-app-name'
    }
    stages {
        stage('Build') {
            steps {
                script {
                    sh 'docker build -t ${IMAGE_NAME} .'
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    sh 'kubectl apply -f deployment.yaml'
                }
            }
        }
    }
}
```

In this example, `APP_NAME` is an environmental variable that holds the name of the application. The `sh` commands use this variable to build and deploy the application.

### Complete Example

Let’s put all of this together with a complete example. Here’s a Jenkinsfile that defines both `IMAGE_NAME` and `APP_NAME` environmental variables and uses them in a Kubernetes deployment:

```groovy
pipeline {
    agent any
    environment {
        IMAGE_NAME = 'your-docker-repo/your-image-name'
        APP_NAME = 'your-app-name'
    }
    stages {
        stage('Build') {
            steps {
                script {
                    sh 'docker build -t ${IMAGE_NAME} .'
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    sh 'kubectl apply -f deployment.yaml'
                }
            }
        }
    }
}
```

And here’s the corresponding Kubernetes deployment YAML:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${APP_NAME}-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ${APP
```

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities have highlighted the importance of proper CI/CD pipeline integration with Kubernetes. For instance, the Log4j vulnerability (CVE-2021-44228) affected many applications deployed via CI/CD pipelines. Ensuring that your pipeline is configured correctly and that you are using the latest images can help mitigate such risks.

### Pitfalls and Common Mistakes

1. **Hardcoding Values**: One of the most common mistakes is hardcoding values such as image names and application names. This leads to maintenance issues and potential deployment failures.
2. **Incorrect Image Pull Policy**: Using the wrong image pull policy can result in outdated images being deployed, leading to security vulnerabilities.
3. **Environmental Variable Management**: Mismanagement of environmental variables can lead to incorrect values being used, causing deployment failures.

### How to Prevent / Defend

#### Detection

- **Automated Testing**: Implement automated tests to verify that the correct image and application names are being used.
- **Logging and Monitoring**: Use logging and monitoring tools to track the deployment process and detect any anomalies.

#### Prevention

- **Centralized Configuration Management**: Use centralized configuration management tools like Ansible or Helm to manage your Kubernetes configurations.
- **Immutable Infrastructure**: Adopt immutable infrastructure principles to ensure that your deployments are consistent and reproducible.

#### Secure Coding Fixes

Here’s an example of a vulnerable Jenkinsfile and its secure counterpart:

**Vulnerable Jenkinsfile**

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                script {
                    sh 'docker build -t your-docker-repo/your-image-name .'
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    sh 'kubectl apply -f deployment.yaml'
                }
            }
        }
    }
}
```

**Secure Jenkinsfile**

```groovy
pipeline {
    agent any
    environment {
        IMAGE_NAME = 'your-docker-repo/your-image-name'
        APP_NAME = 'your-app-name'
    }
    stages {
        stage('Build') {
            steps {
                script {
                    sh 'docker build -t ${IMAGE_NAME} .'
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    sh 'kubectl apply -f deployment.yaml'
                }
            }
        }
    }
}
```

### Conclusion

Integrating Kubernetes deployments into a CI/CD pipeline requires careful management of dynamic values such as image names and application names. By using environmental variables, you can ensure that these values are dynamically set and consistently managed across your pipeline. This approach not only simplifies maintenance but also enhances the security and reliability of your deployments.

### Practice Labs

For hands-on practice, consider the following labs:

- **Kubernetes Goat**: A Kubernetes-based security training platform that covers various aspects of Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges designed to teach developers about common security pitfalls in CI/CD pipelines.
- **kube-hunter**: A tool for finding and exploiting misconfigurations in Kubernetes clusters.

These labs provide practical experience in integrating Kubernetes deployments into CI/CD pipelines and help reinforce the concepts covered in this chapter.

---
<!-- nav -->
[[03-Introduction to Kubernetes Integration in CICD Pipelines|Introduction to Kubernetes Integration in CICD Pipelines]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/21-Integrating Kubernetes Deployment Into CI CD Pipeline/00-Overview|Overview]] | [[05-Integrating Kubernetes Deployment into CICD Pipeline|Integrating Kubernetes Deployment into CICD Pipeline]]
