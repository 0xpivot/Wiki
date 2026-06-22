---
course: API Security
topic: Using Postman tool for API Security Testing
tags: [api-security]
---

## Sidebar Navigation in Postman

Postman is a powerful tool used for testing APIs. It provides a user-friendly interface that allows developers to send HTTP requests and view responses. One of the key features of Postman is its sidebar navigation, which organizes various aspects of API testing into distinct sections. Let's explore each section in detail.

### History Collection

The **History Collection** is located in the sidebar of Postman. This section keeps track of all the requests you have made during your current session. Each request is stored with its corresponding response, allowing you to review past interactions with an API.

#### What is the History Collection?

The History Collection is essentially a log of all the HTTP requests you have sent using Postman. It includes details such as the request method (GET, POST, etc.), the URL, and the response status code. This feature is particularly useful for debugging purposes, as it allows you to revisit previous requests and compare them with new ones.

#### Why is the History Collection Important?

The History Collection serves several important purposes:

- **Debugging**: You can easily review past requests to identify issues or errors.
- **Testing**: It helps in verifying that changes in the API are working as expected.
- **Documentation**: You can use the History Collection to document your testing process and share it with team members.

#### How Does the History Collection Work?

When you send a request in Postman, it automatically gets added to the History Collection. You can access this collection by clicking on the "History" tab in the sidebar. Each entry in the History Collection includes the following information:

- **Request Method**: The HTTP method used (e.g., GET, POST).
- **URL**: The endpoint of the API.
- **Response Status Code**: The status code returned by the server (e.g., 200 OK, 404 Not Found).

#### Example of Using the History Collection

Suppose you are testing an API that returns user data. You send a GET request to `/users/1` and receive a response. Later, you make another request to the same endpoint and notice that the response is different. By reviewing the History Collection, you can compare the two requests and their responses to identify any discrepancies.

```mermaid
sequenceDiagram
    participant User
    participant Postman
    participant API
    User->>Postman: Send GET request to /users/1
    Postman->>API: Forward GET request to /users/1
    API-->>Postman: Return response
    Postman-->>User: Display response
    User->>Postman: Review History Collection
```

### Collections

Collections in Postman are a way to organize and group related requests together. They allow you to manage multiple requests in a structured manner, making it easier to navigate and test complex APIs.

#### What are Collections?

Collections are folders that contain multiple requests. Each request within a collection can be organized into subfolders, creating a hierarchical structure. Collections can also include environment variables, which are used to store configuration data that can be shared across requests.

#### Why are Collections Important?

Collections provide several benefits:

- **Organization**: They help keep related requests together, making it easier to manage large numbers of requests.
- **Reusability**: You can reuse requests across different environments or scenarios.
- **Collaboration**: Collections can be shared with team members, facilitating collaboration and standardization.

#### How Do Collections Work?

To create a collection in Postman, follow these steps:

1. Click on the "Collections" tab in the sidebar.
2. Click on the "Create Collection" button.
3. Enter a name for your collection and click "Save."

Once you have created a collection, you can add requests to it by clicking on the "Add Request" button. You can also create subfolders within the collection to further organize your requests.

#### Example of Using Collections

Suppose you are testing an API that manages user accounts. You might create a collection called "User Management" and add requests for creating, updating, and deleting users. Each request can be organized into subfolders based on the type of operation (e.g., "Create User," "Update User," "Delete User").

```mermaid
flowchart TD
    A[User Management] --> B[Create User]
    A --> C[Update User]
    A --> D[Delete User]
    B --> E[POST /users]
    C --> F[PATCH /users/{id}]
    D --> G[DELETE /users/{id}]
```

### Header Sections

The header sections in Postman provide various options for managing your workspace and performing advanced operations.

#### What are the Header Sections?

The header sections include options such as:

- **New**: Create a new request.
- **Import**: Import requests from external sources.
- **Runner**: Run multiple requests in a sequence.
- **My Workspace**: Manage your workspace settings.
- **Sync**: Sync your API definitions across devices.

#### Why are the Header Sections Important?

The header sections offer several functionalities that enhance your API testing experience:

- **Creating Requests**: Quickly create new requests without navigating through multiple menus.
- **Importing Requests**: Import existing requests from files or other tools.
- **Running Scripts**: Execute multiple requests in a predefined order.
- **Managing Workspace**: Customize your workspace settings to suit your preferences.
- **Syncing Across Devices**: Ensure consistency across different devices by syncing your API definitions.

#### How Do the Header Sections Work?

To access the header sections, click on the top menu bar in Postman. Each option provides a specific functionality:

- **New**: Click on "New" to create a new request. You can specify the request method and URL.
- **Import**: Click on "Import" to import requests from a file or another tool. Supported formats include JSON, CSV, and more.
- **Runner**: Click on "Runner" to run multiple requests in a sequence. You can define the order of execution and pass variables between requests.
- **My Workspace**: Click on "My Workspace" to manage your workspace settings. You can customize themes, shortcuts, and other preferences.
- **Sync**: Click on "Sync" to sync your API definitions across devices. This ensures that your work is consistent regardless of the device you are using.

#### Example of Using the Header Sections

Suppose you are testing an API that requires authentication. You can use the "New" option to create a request that sends an authentication token in the headers. You can also use the "Import" option to import existing requests from a file, and the "Runner" option to run a series of requests in a specific order.

```mermaid
sequenceDiagram
    participant User
    participant Postman
    participant API
    User->>Postman: Click on New
    Postman->>User: Create a new request
    User->>Postman: Specify request method and URL
    Postman->>API: Send request
    API-->>Postman: Return response
    Postman-->>User: Display response
```

### Builder Section

The builder section in Postman is where you create and configure individual requests. It provides a comprehensive set of tools for specifying the details of each request.

#### What is the Builder Section?

The builder section is the main area where you define the details of a request. It includes fields for specifying the request method, URL, headers, parameters, authorization, body, pre-request scripts, tests, and settings.

#### Why is the Builder Section Important?

The builder section is crucial because it allows you to precisely control every aspect of a request. This level of detail is essential for thorough API testing and debugging.

#### How Does the Builder Section Work?

To use the builder section, follow these steps:

1. Click on the "Builder" tab in the sidebar.
2. Specify the request method (e.g., GET, POST).
3. Enter the URL of the API endpoint.
4. Add headers, parameters, and authorization details as needed.
5. Configure the body of the request if required.
6. Write pre-request scripts and tests to automate tasks and validate responses.
7. Adjust settings to customize the behavior of the request.

#### Example of Using the Builder Section

Suppose you are testing an API that requires basic authentication. You can use the builder section to specify the request method, URL, and authorization details. Here is an example of a request with basic authentication:

```http
POST /users HTTP/1.1
Host: api.example.com
Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secret_password"
}
```

In the builder section, you would specify the following:

- **Method**: POST
- **URL**: `https://api.example.com/users`
- **Headers**: 
  - `Authorization`: `Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==`
  - `Content-Type`: `application/json`
- **Body**: Raw JSON payload

```mermaid
sequenceDiagram
    participant User
    participant Postman
    participant API
    User->>Postman: Click on Builder
    Postman->>User: Specify request details
    User->>Postman: Enter URL and headers
    Postman->>API: Send request
    API-->>Postman: Return response
    Postman-->>User: Display response
```

### Response Section

The response section in Postman displays the results of the requests you send. It provides detailed information about the response received from the API.

#### What is the Response Section?

The response section shows the raw response from the API, including the status code, headers, and body. It also provides additional features such as formatting the response and displaying it in different views (e.g., JSON, HTML).

#### Why is the Response Section Important?

The response section is crucial because it allows you to verify that the API is returning the expected results. It provides detailed information that can be used for debugging and validation.

#### How Does the Response Section Work?

To view the response section, send a request in Postman. Once the request is completed, the response section will display the following information:

- **Status Code**: The HTTP status code returned by the server (e.g., 200 OK, 404 Not Found).
- **Headers**: The headers included in the response.
- **Body**: The content of the response, which can be displayed in different views (e.g., JSON, HTML).

#### Example of Using the Response Section

Suppose you are testing an API that returns user data. After sending a GET request to `/users/1`, the response section will display the status code, headers, and body of the response. Here is an example of a response:

```http
HTTP/1.1 200 OK
Date: Mon, 23 Jan 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: application/json
Content-Length: 57

{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

In the response section, you would see the following:

- **Status Code**: `200 OK`
- **Headers**: 
  - `Date`: `Mon, 23 Jan 2023 12:00:00 GMT`
  - `Server`: `Apache/2.4.41 (Ubuntu)`
  - `Content-Type`: `application/json`
  - `Content-Length`: `57`
- **Body**: JSON payload containing user data

```mermaid
sequenceDiagram
    participant User
    participant Postman
    participant API
    User->>Postman: Send GET request to /users/1
    Postman->>API: Forward GET request to /users/1
    API-->>Postman: Return response
    Postman-->>User: Display response in Response Section
```

### How to Prevent / Defend

While Postman is a powerful tool for testing APIs, it is important to ensure that your testing environment is secure. Here are some best practices to prevent security vulnerabilities:

#### Secure Configuration

- **Use Strong Authentication**: Always use strong authentication mechanisms (e.g., OAuth, JWT) to protect your API.
- **Enable HTTPS**: Ensure that your API uses HTTPS to encrypt data in transit.
- **Limit Access**: Restrict access to your API endpoints to authorized users only.

#### Secure Coding Practices

- **Input Validation**: Validate all input data to prevent injection attacks (e.g., SQL injection, XSS).
- **Error Handling**: Implement proper error handling to avoid exposing sensitive information.
- **Rate Limiting**: Implement rate limiting to prevent abuse of your API.

#### Secure Environment

- **Isolate Test Environments**: Keep your test environments isolated from production environments to prevent accidental exposure of sensitive data.
- **Regular Audits**: Regularly audit your API and testing environment to identify and mitigate potential security risks.

#### Example of Secure Configuration

Here is an example of a secure configuration for an API endpoint:

```json
{
  "method": "POST",
  "url": "https://api.example.com/users",
  "headers": {
    "Authorization": "Bearer {{access_token}}",
    "Content-Type": "application/json"
  },
  "body": {
    "mode": "raw",
    "raw": "{\n  \"username\": \"john_doe\",\n  \"password\": \"secret_password\"\n}"
  }
}
```

In this example, the API endpoint uses HTTPS and requires a valid access token for authentication. The request body contains the user credentials, which should be securely transmitted.

#### Example of Secure Coding Practices

Here is an example of secure coding practices for validating input data:

```javascript
function createUser(username, password) {
  // Validate username and password
  if (!isValidUsername(username)) {
    throw new Error("Invalid username");
  }
  if (!isValidPassword(password)) {
    throw new Error("Invalid password");
  }

  // Create user
  const user = {
    username: username,
    password: hashPassword(password)
  };

  return user;
}

function isValidUsername(username) {
  // Check if username meets criteria
  return /^[a-zA-Z0-9_]{3,20}$/.test(username);
}

function isValidPassword(password) {
  // Check if password meets criteria
  return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(password);
}

function hashPassword(password) {
  // Hash password using a secure algorithm
  return bcrypt.hashSync(password, 10);
}
```

In this example, the `createUser` function validates the username and password before creating a new user. The `isValidUsername` and `isValidPassword` functions check if the input data meets the specified criteria. The `hashPassword` function hashes the password using a secure algorithm.

#### Example of Secure Environment

Here is an example of isolating test environments:

```yaml
# Dockerfile for test environment
FROM node:14

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

In this example, the test environment is isolated using a Docker container. The Dockerfile specifies the base image, working directory, dependencies, and startup command. This ensures that the test environment is separate from the production environment.

### Practice Labs

For hands-on practice with API security testing using Postman, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs for learning web security concepts, including API security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including API testing.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates common web application vulnerabilities, including API-related issues.
- **WebGoat**: An interactive, gamified training application for learning web security concepts, including API security.

These labs provide real-world scenarios and challenges that can help you improve your API security testing skills using Postman.

By mastering the various sections of Postman and following best practices for secure configuration and coding, you can effectively test and secure your APIs.

---
<!-- nav -->
[[API Security/04-Using Postman tool for API Security Testing/07-Postman Navigation/02-Introduction to Postman for API Security Testing|Introduction to Postman for API Security Testing]] | [[API Security/04-Using Postman tool for API Security Testing/07-Postman Navigation/00-Overview|Overview]] | [[API Security/04-Using Postman tool for API Security Testing/07-Postman Navigation/04-Practice Questions & Answers|Practice Questions & Answers]]
