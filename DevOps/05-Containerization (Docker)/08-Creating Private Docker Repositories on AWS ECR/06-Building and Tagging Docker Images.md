---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Building and Tagging Docker Images

Before pushing images to the ECR repository, you need to build and tag them locally. Here’s how you can do it:

### Step 1: Build the Docker Image

Assume you have a Dockerfile in your project directory. The Dockerfile specifies the instructions to build the Docker image. Here is an example Dockerfile:

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

To build the Docker image, run the following command in your terminal:

```bash
docker build -t myapp .
```

This command builds the Docker image and tags it as `myapp`.

### Step 2: Tag the Docker Image for ECR

To push the image to ECR, you need to tag it with the full domain of the ECR repository. Use the following command:

```bash
docker tag myapp:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp:latest
```

This command tags the local image `myapp:latest` with the full domain of the ECR repository.

---
<!-- nav -->
[[05-Introduction to Private Docker Repositories on AWS ECR|Introduction to Private Docker Repositories on AWS ECR]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/08-Creating Private Docker Repositories on AWS ECR/00-Overview|Overview]] | [[07-Logging into ECR|Logging into ECR]]
