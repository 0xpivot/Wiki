---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Connecting Node.js with MongoDB Using Docker

### Introduction to Dockerizing Node.js and MongoDB

Dockerizing applications allows developers to package their applications along with their dependencies into lightweight, portable containers. This ensures consistency across development, testing, and production environments. In this section, we will focus on setting up a development environment for a Node.js application that connects to a MongoDB database, both running in Docker containers.

### Setting Up MongoDB in Docker

#### MongoDB Container Configuration

To run MongoDB in a Docker container, we need to define the necessary parameters such as the image, ports, and environment variables. Here is an example of a `docker-compose.yml` file that sets up a MongoDB instance:

```yaml
version: '3'
services:
  mongodb:
    image: mongo:latest
    container_name: mongodb_container
    environment:
      - MONGO_INITDB_ROOT_USERNAME=root
      - MONGO_INITDB_ROOT_PASSWORD=rootpassword
    volumes:
      - ./data:/data/db
    ports:
      - "27017:27017"
```

This configuration does the following:
- Uses the latest MongoDB image.
- Sets the root username and password as environment variables.
- Mounts a volume to persist data.
- Maps port 27017 of the container to port 27017 on the host machine.

#### Running the MongoDB Container

To start the MongoDB container, run the following command:

```bash
docker-compose up -d
```

This command starts the MongoDB service in detached mode (`-d`).

### Connecting Node.js to MongoDB

#### MongoDB Client Setup in Node.js

To connect Node.js to MongoDB, we can use the `mongodb` driver provided by the official MongoDB Node.js driver. First, install the driver using npm:

```bash
npm install mongodb
```

Next, we can create a connection string to connect to the MongoDB instance running in the Docker container. The connection string typically includes the protocol, host, port, and authentication details.

Here is an example of a Node.js script that connects to MongoDB:

```javascript
const { MongoClient } = require('mongodb');

// Connection URL
const url = 'mongodb://root:rootpassword@localhost:27017';

// Database Name
const dbName = 'useraccountdb';

async function main() {
  const client = new MongoClient(url);

  try {
    // Connect to the MongoDB cluster
    await client.connect();
    console.log('Connected successfully to server');

    const db = client.db(dbName);
    const collection = db.collection('users');

    // Perform operations on the database
    const result = await collection.find({}).toArray();
    console.log(result);
  } finally {
    // Close the connection
    await client.close();
  }
}

main().catch(console.error);
```

#### Explanation of the Connection String

The connection string `mongodb://root:rootpassword@localhost:27017` breaks down as follows:
- `mongodb`: Protocol used to communicate with MongoDB.
- `root:rootpassword`: Username and password for authentication.
- `localhost:27017`: Host and port where the MongoDB instance is running.

### Creating Collections and Performing Queries

In the MongoDB instance, we can create collections and perform queries. For example, we can create a collection named `users` and insert some documents.

Here is an example of inserting documents into the `users` collection:

```javascript
const { MongoClient } = require('mongodb');

async function main() {
  const client = new MongoClient('mongodb://root:rootpassword@localhost:27017');
  const dbName = 'useraccountdb';
  const collectionName = 'users';

  try {
    await client.connect();
    console.log('Connected successfully to server');

    const db = client.db(dbName);
    const collection = db.collection(collectionName);

    // Insert documents
    const docs = [
      { name: 'Alice', age: 30 },
      { name: 'Bob', age: 25 }
    ];
    const result = await collection.insertMany(docs);
    console.log(`Inserted ${result.insertedCount} documents`);
  } finally {
    await client.close();
  }
}

main().catch(console.error);
```

### Querying the Collection

To query the `users` collection, we can use the `find` method:

```javascript
const { MongoClient } = require('mongodb');

async function main() {
  const client = new MongoClient('mongodb://root:rootpassword@localhost:27017');
  const dbName = 'useraccountdb';
  const collectionName = 'users';

  try {
    await client.connect();
    console.log('Connected successfully to server');

    const db = client.db(dbName);
    const collection = db.collection(collectionName);

    // Query the collection
    const result = await collection.find({}).toArray();
    console.log(result);
  } finally {
    await client.close();
  }
}

main().catch(console.error);
```

### Security Considerations

#### Avoiding Hardcoding Credentials

Hardcoding credentials in your application is a significant security risk. Instead, use environment variables to store sensitive information. Here is an example of how to modify the connection string to use environment variables:

```javascript
const { MongoClient } = require('mongodb');

const url = `mongodb://${process.env.MONGO_USER}:${process.env.MONGO_PASSWORD}@localhost:27017`;
const dbName = process.env.MONGO_DB;

async function main() {
  const client = new MongoClient(url);

  try {
    await client.connect();
    console.log('Connected successfully to server');

    const db = client.db(dbName);
    const collection = db.collection('users');

    const result = await collection.find({}).toArray();
    console.log(result);
  } finally {
    await client.close();
  }
}

main().catch(console.error);
```

#### Setting Environment Variables

Set the environment variables in your `.env` file:

```
MONGO_USER=root
MONGO_PASSWORD=rootpassword
MONGO_DB=useraccountdb
```

And load them in your Node.js application using a library like `dotenv`:

```bash
npm install dotenv
```

Then, at the beginning of your script:

```javascript
require('dotenv').config();
```

### Real-World Examples and CVEs

#### CVE-2021-22830: MongoDB Authentication Bypass

CVE-2021-22830 is a critical vulnerability in MongoDB that allows attackers to bypass authentication and gain unauthorized access to the database. This vulnerability affects versions of MongoDB prior to 4.4.3 and 5.0.0.

**Impact**: An attacker could exploit this vulnerability to gain full access to the MongoDB instance, potentially leading to data theft or manipulation.

**Prevention**:
- Ensure that MongoDB is updated to the latest version.
- Use strong, unique passwords for database users.
- Enable authentication and restrict access to trusted IP addresses.

### How to Prevent / Defend

#### Secure Coding Practices

- **Use Environment Variables**: Store sensitive information like database credentials in environment variables.
- **Validate Inputs**: Always validate and sanitize inputs to prevent injection attacks.
- **Use Strong Authentication**: Implement strong authentication mechanisms and avoid using default or weak credentials.

#### Secure Configuration

- **Enable Authentication**: Ensure that MongoDB authentication is enabled.
- **Restrict Access**: Limit access to the MongoDB instance to trusted IP addresses.
- **Use TLS/SSL**: Enable TLS/SSL encryption for connections to the MongoDB instance.

#### Monitoring and Logging

- **Enable Auditing**: Enable auditing features in MongoDB to log all database activities.
- **Monitor Logs**: Regularly monitor logs for suspicious activities.

### Conclusion

By following the steps outlined above, you can effectively set up a development environment for a Node.js application that connects to a MongoDB database using Docker. Additionally, by adhering to secure coding practices and configuration guidelines, you can significantly reduce the risk of security vulnerabilities.

### Practice Labs

For hands-on practice, consider the following resources:
- **PortSwigger Web Security Academy**: Offers comprehensive labs on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

These resources provide practical experience in securing web applications and databases, including those using Docker and Node.js.

---
<!-- nav -->
[[04-Introduction to Dockerizing a Node.js and MongoDB Development Environment|Introduction to Dockerizing a Node.js and MongoDB Development Environment]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/17-Dockerizing Node.js and MongoDB Development Environment/00-Overview|Overview]] | [[06-Dockerizing Node.js and MongoDB Development Environment|Dockerizing Node.js and MongoDB Development Environment]]
