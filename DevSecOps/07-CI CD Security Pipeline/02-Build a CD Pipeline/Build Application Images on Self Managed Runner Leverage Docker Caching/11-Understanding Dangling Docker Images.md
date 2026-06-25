---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Understanding Dangling Docker Images

### What Are Dangling Docker Images?

Dangling Docker images are intermediate images that are created during the build process but are not tagged and thus are not explicitly referenced. These images are typically used as base images or intermediary steps in the creation of the final Docker image. They are often left behind after a build process completes, especially if the build process is interrupted or fails.

### Why Do Dangling Images Matter?

Dangling images can consume significant disk space on your Docker host. Over time, these images can accumulate and lead to disk space exhaustion, which can affect the performance and stability of your Docker environment. By managing and cleaning up these images, you can free up valuable disk space and ensure that your Docker environment remains efficient.

### How to Identify and Remove Dangling Images

To identify and remove dangling Docker images, you can use the following commands:

```sh
# List all dangling images
docker images -f dangling=true

# Remove all dangling images
docker image prune
```

These commands will list and then remove all dangling images, freeing up disk space. In the provided transcript, the lecturer mentions freeing up seven gigabytes of space by removing dangling images.

### Real-World Example: Disk Space Exhaustion

In a real-world scenario, consider a company that uses Docker extensively for their continuous integration and deployment processes. Over time, the accumulation of dangling images leads to disk space exhaustion on their Docker hosts. This results in failed builds and deployments, causing downtime and affecting the company's ability to deliver updates to their customers. By regularly cleaning up dangling images, the company can prevent such issues and maintain a stable and efficient Docker environment.

### How to Prevent / Defend Against Dangling Image Issues

#### Detection

Regularly monitor the disk usage of your Docker hosts using tools like `df` or `du`. You can also set up alerts to notify you when disk usage exceeds a certain threshold.

#### Prevention

Implement a regular cleanup schedule for dangling images. You can automate this process using a cron job or a scheduled task.

```sh
# Example cron job to clean up dangling images daily
0 0 * * * docker image prune -f
```

#### Secure Coding Practices

Ensure that your Dockerfile and build scripts are optimized to minimize the creation of unnecessary intermediate images. Use multi-stage builds to reduce the number of layers in your final image.

### Multi-Stage Builds Example

Here’s an example of a Dockerfile using multi-stage builds to minimize the creation of intermediate images:

```Dockerfile
# Stage 1: Build the application
FROM node:14 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Create the final image
FROM node:14
WORKDIR /app
COPY --from=builder /app/dist ./dist
CMD ["node", "dist/index.js"]
```

This Dockerfile first builds the application in a separate stage and then copies only the necessary files to the final image, reducing the number of intermediate images.

---
<!-- nav -->
[[10-Troubleshooting Job Execution on Self-Managed Runners|Troubleshooting Job Execution on Self-Managed Runners]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Build Application Images on Self Managed Runner Leverage Docker Caching/00-Overview|Overview]] | [[12-Understanding the Build Process in a CD Pipeline|Understanding the Build Process in a CD Pipeline]]
