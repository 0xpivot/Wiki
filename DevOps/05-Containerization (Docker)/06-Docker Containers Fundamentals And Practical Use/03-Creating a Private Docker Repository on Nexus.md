---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Creating a Private Docker Repository on Nexus

### Prerequisites

Ensure you have completed the steps to set up Nexus as a Docker container.

### Step-by-Step Guide

#### Step 1: Log In to Nexus

Navigate to `http://localhost:8081` and log in using the default credentials (`admin`/`admin123`).

#### Step 2: Create a New Docker Hosted Repository

1. Click on **Repositories** in the left-hand menu.
2. Click on **Create Repository**.
3. Select **Docker (Hosted)** from the list of repository types.
4. Fill in the required details:
   - **Repository Name**: Enter a name for your repository (e.g., `my-docker-repo`).
   - **HTTP Port**: Leave this as the default (8081).
   - **HTTPS Port**: Leave this as the default (8082).
5. Click **Create Repository**.

#### Step 3: Configure Docker to Use the Nexus Repository

To use the Nexus repository with Docker, you need to configure Docker to authenticate against Nexus. This typically involves creating a `.docker/config.json` file with the necessary credentials.

1. **Generate Credentials**: In Nexus, go to **Security > Users**, and create a new user with the necessary permissions.
2. **Configure Docker**: On your local machine, create or update the `.docker/config.json` file with the following content:

```json
{
  "auths": {
    "http://localhost:8081": {
      "auth": "<base64-encoded-username-password>"
    }
  }
}
```

Replace `<base64-encoded-username-password>` with the base64-encoded string of your username and password concatenated with a colon (e.g., `admin:admin123`).

#### Step 4: Test the Configuration

Push a Docker image to the Nexus repository to test the configuration:

```bash
docker tag my-image localhost:8081/my-docker-repo/my-image:latest
docker push localhost:8081/my-docker-repo/my-image:latest
```

If successful, you should see the image listed in the Nexus repository.

### Diagram: Docker Repository on Nexus

```mermaid
graph LR
    A[Local Machine] --> B[Docker CLI]
    B --> C[Docker Daemon]
    C --> D[Nexus Repository (Docker Hosted)]
```

### Common Pitfalls and How to Prevent Them

#### Pitfall 1: Authentication Issues

**Problem**: Incorrect credentials or misconfigured authentication can prevent you from pushing or pulling images.

**Solution**: Double-check the credentials and ensure that the `.docker/config.json` file is correctly configured.

#### Pitfall 2: Network Issues

**Problem**: Network issues can prevent Docker from communicating with the Nexus repository.

**Solution**: Ensure that the network is stable and that there are no firewall rules blocking communication between the Docker daemon and the Nexus repository.

### How to Prevent / Defend

#### Detection

- **Network Monitoring**: Monitor network traffic to ensure that there are no connectivity issues.
- **Error Logs**: Check Docker and Nexus logs for any errors related to authentication or network issues.

#### Prevention

- **Secure Communication**: Use HTTPS for communication between Docker and Nexus to ensure secure transmission.
- **Firewall Rules**: Configure firewall rules to allow traffic on the necessary ports.

---
<!-- nav -->
[[02-Introduction to Docker Containers and Nexus Repository Manager|Introduction to Docker Containers and Nexus Repository Manager]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/06-Docker Containers Fundamentals And Practical Use/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/06-Docker Containers Fundamentals And Practical Use/04-Hands-On Practice|Hands-On Practice]]
