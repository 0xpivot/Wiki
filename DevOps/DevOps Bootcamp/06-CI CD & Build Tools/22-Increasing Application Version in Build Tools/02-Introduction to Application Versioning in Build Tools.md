---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Application Versioning in Build Tools

In modern DevOps practices, managing application versions is crucial for maintaining a consistent and reliable deployment process. One of the key aspects of this is ensuring that each new version of an application is uniquely identifiable, especially when deploying containerized applications using Docker images. This chapter delves into the details of increasing application versions in build tools, focusing on Docker images and the importance of versioning in continuous integration and delivery (CI/CD) pipelines.

### Why Versioning Matters

Versioning is essential for several reasons:

1. **Tracking Changes**: Each version allows you to track changes made to the application, making it easier to identify and revert to previous states if necessary.
2. **Rollback Mechanism**: In case of issues with a new version, having unique identifiers enables quick rollbacks to a stable version.
3. **Dependency Management**: Different components or services might depend on specific versions of your application. Unique versioning ensures compatibility and avoids conflicts.
4. **Auditability**: Detailed version history provides a clear audit trail, which is crucial for compliance and debugging purposes.

### Common Practices in Versioning

The most common practice is to use semantic versioning (SemVer), which follows the format `MAJOR.MINOR.PATCH`. This format helps in understanding the nature of changes:

- **MAJOR**: Significant changes that may break backward compatibility.
- **MINOR**: New features that are backward compatible.
- **PATCH**: Bug fixes and minor improvements that are backward compatible.

For example, if your application starts at version `1.0.0` and you introduce a major change, the next version would be `2.0.0`.

### Docker Image Versioning

When deploying applications using Docker, each Docker image should have a unique version tag. This ensures that different builds can be distinguished and managed effectively. The version tag is typically appended to the image name, such as `myapp:1.0.0`.

#### Hard-Coded Values vs. Dynamic Values

In the given transcript, the initial approach uses a hard-coded value (`JMA 2.0`) for the Docker image version. This approach has significant drawbacks:

- **Lack of Uniqueness**: Every build generates an image with the same version tag, making it impossible to distinguish between different builds.
- **No Rollback Mechanism**: Without unique tags, rolling back to a previous version becomes challenging.
- **Inconsistent Deployment**: Different environments might end up with inconsistent versions due to the lack of proper versioning.

To address these issues, the version should be dynamically generated based on the application version. This ensures that each build produces a uniquely tagged Docker image.

### Setting Up Dynamic Versioning in Build Tools

To implement dynamic versioning, you need to define a variable that holds the current application version and pass this variable to the Docker build command. Let's walk through the steps to achieve this.

#### Step 1: Define the Variable

First, define a variable that holds the current application version. This variable can be set in your CI/CD pipeline configuration or in a script that runs before the build process.

```yaml
# Example in a CI/CD pipeline configuration (e.g., Jenkinsfile)
pipeline {
    agent any
    environment {
        APP_VERSION = '1.0.0'
    }
    stages {
        stage('Build') {
            steps {
                script {
                    // Set the image name variable
                    IMAGE_NAME = "myapp:${APP_VERSION}"
                }
            }
        }
    }
}
```

#### Step 2: Pass the Variable to Docker Build Command

Next, modify the Docker build command to use the dynamically generated image name.

```bash
# Example Docker build command
docker build -t "${IMAGE_NAME}" .
```

This command ensures that each build generates a Docker image with a unique version tag based on the current application version.

### Full Example with Raw HTTP Messages

Let's consider a more detailed example involving a CI/CD pipeline that triggers a Docker build. Here’s how the entire process might look:

#### Pipeline Configuration

```yaml
# Jenkinsfile example
pipeline {
    agent any
    environment {
        APP_VERSION = '1.0.0'
    }
    stages {
        stage('Build') {
            steps {
                script {
                    // Set the image name variable
                    IMAGE_NAME = "myapp:${APP_VERSION}"
                    
                    // Execute the Docker build command
                    sh "docker build -t ${IMAGE_NAME} ."
                }
            }
        }
        stage('Push to Registry') {
            steps {
                script {
                    // Push the built image to a registry
                    sh "docker push ${IMAGE_NAME}"
                }
            }
        }
    }
}
```

#### Docker Build Command

```bash
# Full Docker build command
docker build -t myapp:1.0.0 .
```

#### Docker Push Command

```bash
# Full Docker push command
docker push myapp:1.0.0
```

### How to Prevent / Defend Against Versioning Issues

#### Detection

To ensure that your pipeline is correctly generating unique version tags, you can implement checks in your CI/CD pipeline:

1. **Version Check**: Before building the image, verify that the `APP_VERSION` variable is set and is a valid SemVer string.
2. **Tag Existence Check**: Before pushing the image, check if the tag already exists in the registry to avoid overwriting existing images.

#### Prevention

1. **Automated Version Increment**: Use tools like `git describe` or `git rev-parse` to automatically generate version numbers based on Git tags or commit hashes.
2. **Environment Variables**: Ensure that environment variables used for versioning are properly configured and updated in your CI/CD pipeline.
3. **Validation Scripts**: Write scripts to validate the version number format and uniqueness before proceeding with the build.

#### Secure Coding Fixes

Here’s an example of how to implement a secure versioning mechanism in a CI/CD pipeline:

```yaml
# Jenkinsfile example with validation
pipeline {
    agent any
    environment {
        APP_VERSION = '1.0.0'
    }
    stages {
        stage('Validate Version') {
            steps {
                script {
                    // Validate the version format
                    def isValidVersion = APP_VERSION =~ /^(\d+)\.(\d+)\.(\d+)$/
                    if (!isValidVersion) {
                        error "Invalid version format: ${APP_VERSION}"
                    }
                }
            }
        }
        stage('Build') {
            steps {
                script {
                    // Set the image name variable
                    IMAGE_NAME = "myapp:${APP_VERSION}"
                    
                    // Execute the Docker build command
                    sh "docker build -t ${IMAGE_NAME} ."
                }
            }
        }
        stage('Push to Registry') {
            steps {
                script {
                    // Push the built image to a registry
                    sh "docker push ${IMAGE_NAME}"
                }
            }
        }
    }
}
```

### Real-World Examples and Breaches

#### Example: Docker Image Overwrite

Consider a scenario where a company deploys a new version of their application without proper versioning. Due to a misconfiguration, the new version overwrites the previous version in the Docker registry. This leads to a situation where all instances of the application are suddenly running the new version, potentially introducing bugs or breaking functionality.

**CVE Example**: CVE-2021-21287 - A vulnerability in Docker Desktop allowed unauthorized access to the Docker daemon, potentially leading to unauthorized image overwrites.

### Conclusion

Proper versioning in build tools is crucial for maintaining a robust and reliable CI/CD pipeline. By dynamically generating version tags based on the application version, you ensure that each build produces a uniquely identifiable Docker image. This practice enhances traceability, rollback capabilities, and overall system stability.

### Hands-On Labs

For practical experience, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes modules on CI/CD pipelines and Docker.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including CI/CD pipeline management.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for learning web security, which can be integrated into CI/CD pipelines for testing purposes.

These labs provide real-world scenarios and challenges to reinforce the concepts learned in this chapter.

---
<!-- nav -->
[[01-General Concepts of Application Versioning in Build Tools|General Concepts of Application Versioning in Build Tools]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/22-Increasing Application Version in Build Tools/00-Overview|Overview]] | [[03-Introduction to Application Versioning|Introduction to Application Versioning]]
