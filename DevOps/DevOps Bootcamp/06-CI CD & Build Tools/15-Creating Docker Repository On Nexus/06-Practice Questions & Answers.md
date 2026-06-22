---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the process of creating a Docker repository on Nexus and configuring it for use.**

To create a Docker repository on Nexus and configure it for use, follow these steps:

1. **Create the Repository:**
   - Go to the administration and configuration view in Nexus.
   - Choose to create a new repository.
   - Select "Docker hosted" from the list.
   - Name the repository (e.g., "Docker hosted").
   - Assign a BlobStore (e.g., "My Store").
   - Click "Create".

2. **Configure the Repository:**
   - Edit the repository settings to specify a unique port for the Docker repository (e.g., 8083).
   - Ensure the repository connector is configured for HTTP.
   - Open the specified port (e.g., 8083) on the server’s firewall.

3. **Set Up Authentication:**
   - Create a new role (e.g., "NX Docker") with privileges to access the Docker hosted repository.
   - Assign this role to an existing user who has access to the Maven repository.
   - Activate the Docker Bearer Token realm in Nexus.

4. **Configure Docker Client:**
   - Configure Docker to allow the Nexus repository as an insecure registry.
   - For Linux systems, edit the `daemon.json` file to include the insecure registry setting.
   - For Docker Desktop, add the insecure registry setting via the preferences UI.

5. **Log In and Use the Repository:**
   - Log in to the Docker repository using the Nexus user credentials.
   - Build and tag Docker images with the repository endpoint included.
   - Push images to the repository using the `docker push` command.
   - Pull images from the repository using the `docker pull` command.

**Q2. How would you troubleshoot issues when pushing Docker images to a Nexus repository?**

Troubleshooting issues when pushing Docker images to a Nexus repository involves several steps:

1. **Check Network Connectivity:**
   - Ensure that the Docker client can reach the Nexus server on the specified port (e.g., 8083).
   - Verify that the firewall rules allow traffic on the required port.

2. **Verify Repository Configuration:**
   - Confirm that the Docker repository is correctly configured in Nexus.
   - Check that the repository connector is set to HTTP and the port is correctly specified.

3. **Authentication Issues:**
   - Ensure that the user has the necessary roles and permissions to access the Docker repository.
   - Verify that the Docker Bearer Token realm is activated in Nexus.

4. **Insecure Registry Configuration:**
   - Ensure that Docker is configured to allow the Nexus repository as an insecure registry.
   - Check the `daemon.json` file or Docker Desktop preferences for the insecure registry setting.

5. **Logs and Error Messages:**
   - Review the logs in both Nexus and the Docker client for error messages.
   - Look for specific errors related to network connectivity, authentication, or repository configuration.

6. **Test Connectivity:**
   - Use tools like `curl` to test connectivity to the Nexus repository endpoint.
   - Ensure that the repository is reachable and responding correctly.

By systematically checking these areas, you can identify and resolve common issues when pushing Docker images to a Nexus repository.

**Q3. What recent real-world examples demonstrate the importance of securing Docker repositories?**

Recent real-world examples highlight the importance of securing Docker repositories:

1. **CVE-2021-21315:**
   - A vulnerability was found in Docker that allowed unauthorized access to the Docker daemon through the Docker API.
   - This could potentially lead to unauthorized access to Docker images and repositories.
   - Organizations should ensure that their Docker daemons are properly secured and that access controls are in place.

2. **Supply Chain Attacks:**
   - There have been instances where malicious actors have compromised Docker images in public repositories.
   - These compromised images can be used to deploy malware or gain unauthorized access to systems.
   - It is crucial to verify the authenticity and integrity of Docker images before deploying them.

3. **Misconfigured Repositories:**
   - Misconfigured Docker repositories can expose sensitive data and allow unauthorized access.
   - Ensuring that repositories are properly secured and that access controls are enforced is critical.
   - Regularly auditing and reviewing repository configurations can help prevent such issues.

These examples underscore the need for robust security measures when managing Docker repositories, including proper authentication, authorization, and regular audits.

**Q4. How would you configure a Nexus Docker repository to support secure connections (HTTPS)?**

Configuring a Nexus Docker repository to support secure connections (HTTPS) involves several steps:

1. **Obtain SSL/TLS Certificates:**
   - Obtain SSL/TLS certificates for the Nexus server. This can be done using a trusted certificate authority (CA) or self-signed certificates.
   - Ensure that the certificates are valid and trusted by the Docker clients.

2. **Configure Nexus for HTTPS:**
   - In Nexus, go to the server configuration and enable HTTPS.
   - Specify the path to the SSL/TLS certificate and key files.
   - Set the HTTPS port (e.g., 8443).

3. **Update Repository Configuration:**
   - Update the Docker repository configuration to use HTTPS.
   - Ensure that the repository connector is set to HTTPS and the port is correctly specified.

4. **Update Docker Client Configuration:**
   - Ensure that Docker clients are configured to use HTTPS for the Nexus repository.
   - Remove any insecure registry settings if they were previously configured.

5. **Test Secure Connections:**
   - Test the secure connection to the Nexus repository using tools like `curl`.
   - Ensure that Docker clients can authenticate and interact with the repository over HTTPS.

By following these steps, you can configure a Nexus Docker repository to support secure connections, enhancing the overall security of your Docker environment.

**Q5. How would you use the Nexus API to retrieve information about Docker images in a repository?**

To use the Nexus API to retrieve information about Docker images in a repository, follow these steps:

1. **Identify the API Endpoint:**
   - Determine the API endpoint for retrieving Docker images. Typically, this would be something like `/service/rest/v1/components?repository=<repository-name>`.

2. **Authenticate with Nexus:**
   - Use basic authentication with a Nexus user that has access to the repository.
   - Provide the username and password in the API request.

3. **Execute the API Request:**
   - Use a tool like `curl` to execute the API request.
   - Example command:
     ```sh
     curl -u <username>:<password> "http://<nexus-server>:<port>/service/rest/v1/components?repository=Docker%20hosted"
     ```

4. **Parse the Response:**
   - The response will be in JSON format, containing information about the Docker images in the repository.
   - Parse the JSON response to extract the desired information, such as image names, tags, and manifests.

5. **Handle Pagination:**
   - If the repository contains many images, the API response may be paginated.
   - Handle pagination by iterating through the pages until all images are retrieved.

By using the Nexus API, you can programmatically retrieve and manage information about Docker images in a repository, facilitating automation and integration with other tools and processes.

---
<!-- nav -->
[[05-Configuring a Docker Repository on Nexus|Configuring a Docker Repository on Nexus]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/15-Creating Docker Repository On Nexus/00-Overview|Overview]]
