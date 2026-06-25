---
course: DevSecOps
topic: Automating Code Security Testing
tags: [devsecops]
---

## Setting Up Dockerfile Linting

### Prerequisites

To set up Dockerfile linting, you need:

- **Docker Installed**: Ensure Docker is installed on your system.
- **Linting Tool**: Choose a linting tool such as Hadolint.

### Installing Hadolint

Hadolint is a popular Dockerfile linter that checks for security vulnerabilities and best practices. To install Hadolint, you can use Docker to run it as a container.

#### Step-by-Step Installation

1. **Pull the Hadolint Docker Image**:
   ```sh
   docker pull hadolint/hadolint
   ```

2. **Run Hadolint**:
   ```sh
   docker run --rm -v $(pwd):/work -w /work hadolint/hadolint hadolint Dockerfile
   ```

This command runs the Hadolint container, mounts the current directory to `/work`, and runs Hadolint on the `Dockerfile`.

### Example Dockerfile

Let's consider a simple Dockerfile for demonstration purposes:

```Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
```

### Running Hadolint on the Dockerfile

To run Hadolint on the above Dockerfile, use the following command:

```sh
docker run --rm -v $(pwd):/work -w /work hadolint/hadolint hadolint Dockerfile
```

### Output Analysis

The output of Hadolint might look something like this:

```
DL4006 warning: CMD should be used in a separate layer to improve cache usage
DL3018 warning: Use multi-stage builds to reduce image size
```

### Understanding the Warnings

- **DL4006**: This warning suggests that the `CMD` instruction should be placed in a separate layer to improve cache usage. This is because Docker caches each layer, and moving the `CMD` to a separate layer can help avoid rebuilding the entire image when the `CMD` changes.
  
- **DL3018**: This warning suggests using multi-stage builds to reduce the final image size. Multi-stage builds allow you to use one build stage to compile your application and another to package the compiled artifacts into a minimal runtime image.

### Correcting the Dockerfile

Here is the corrected Dockerfile using multi-stage builds:

```Dockerfile
# Stage 1: Build the application
FROM python:3.9-slim AS builder

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Create the final runtime image
FROM python:3.9-slim

WORKDIR /app

COPY --from=builder /app .

EXPOSE 80

ENV NAME World

CMD ["python", "app.py"]
```

### Explanation of the Corrected Dockerfile

- **Stage 1**: This stage uses the `python:3.9-slim` image to build the application. It copies the source code and installs the dependencies.
- **Stage 2**: This stage creates the final runtime image. It copies only the necessary files from the build stage, reducing the final image size.

### How to Prevent / Defend

#### Detection

To detect issues in Dockerfiles, regularly run Hadolint or other linting tools as part of your CI/CD pipeline.

#### Prevention

1. **Use Multi-Stage Builds**: Always use multi-stage builds to reduce the final image size.
2. **Optimize Layers**: Place frequently changing instructions in separate layers to improve cache usage.
3. **Regularly Update Base Images**: Keep base images up-to-date to avoid known vulnerabilities.
4. **Automate Linting**: Integrate Dockerfile linting into your CI/CD pipeline to catch issues early.

### Full Example with Jenkins Job

To integrate Dockerfile linting into a Jenkins job, follow these steps:

1. **Install Jenkins Plugin**: Install the Docker Pipeline plugin in Jenkins.
2. **Configure Jenkins Job**: Configure the Jenkins job to run the Dockerfile linting step.

#### Jenkinsfile Example

```groovy
pipeline {
    agent any

    stages {
        stage('Lint Dockerfile') {
            steps {
                script {
                    sh '''
                        docker run --rm -v $(pwd):/work -w /work hadolint/hadolint hadolint Dockerfile
                    '''
                }
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t my-image .'
                }
            }
        }
        stage('Push Docker Image') {
            when {
                expression { return currentBuild.result == 'SUCCESS' }
            }
            steps {
                script {
                    sh 'docker push my-image'
                }
            }
        }
    }
}
```

### Explanation of the Jenkinsfile

- **Lint Dockerfile**: This stage runs Hadolint on the Dockerfile.
- **Build Docker Image**: This stage builds the Docker image.
- **Push Docker Image**: This stage pushes the Docker image to a registry, but only if the previous stages were successful.

### How to Prevent / Defend

#### Detection

- **Integrate Linting into CI/CD**: Ensure that Dockerfile linting is part of your CI/CD pipeline.
- **Monitor Logs**: Regularly monitor logs for linting failures.

#### Prevention

- **Automate Fixes**: Automatically fix common linting issues as part of the CI/CD pipeline.
- **Educate Developers**: Educate developers about best practices for writing Dockerfiles.

### Conclusion

Dockerfile linting is a critical component of DevSecOps, helping to ensure that Docker images are secure, efficient, and adhere to best practices. By integrating linting into your CI/CD pipeline, you can catch and address issues early, preventing serious security breaches and improving the overall quality of your Docker images.

### Practice Labs

For hands-on experience with Dockerfile linting, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to Dockerfile security.
- **OWASP Juice Shop**: Provides a comprehensive set of labs for learning Dockerfile security.
- **DVWA**: Offers a range of labs for practicing Dockerfile security.

By following these steps and integrating Dockerfile linting into your workflow, you can significantly improve the security and efficiency of your Docker images.

---
<!-- nav -->
[[04-Automating Code Security Testing with Linters|Automating Code Security Testing with Linters]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/03-Automating Code Security Testing/Demo Linting a Dockerfile/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/03-Automating Code Security Testing/Demo Linting a Dockerfile/06-Practice Questions & Answers|Practice Questions & Answers]]
