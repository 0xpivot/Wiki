---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## Improper Assets Management in API Security

### Introduction

Improper assets management is a critical issue in API security, often leading to significant vulnerabilities. Attackers frequently target non-production environments such as staging, testing, beta, or older versions of APIs that may not have the same level of protection as the production environment. These environments can provide a foothold for attackers to launch further attacks against the main system. In this section, we will delve into the details of improper assets management, its implications, and how to effectively manage and secure these assets.

### Understanding Non-Production Environments

Non-production environments are crucial for development, testing, and staging purposes. These environments allow developers and testers to work on new features, debug issues, and ensure that the final product is robust and secure. However, these environments often lack the same level of security controls as the production environment. This disparity can be exploited by attackers to gain unauthorized access to sensitive data or systems.

#### Examples of Non-Production Environments

- **Staging**: A replica of the production environment used for final testing before deployment.
- **Testing**: An environment used for unit testing, integration testing, and functional testing.
- **Beta**: A pre-release version of the application made available to a limited group of users for feedback.
- **Older Versions**: Previous versions of the API that are kept running for backward compatibility.

### Real-World Example: Just Dial

One notable example of improper assets management is the breach at Just Dial, an Indian local search service. When the company redesigned their APIs, the old API was left running unprotected and with access to the user database. This oversight allowed attackers to exploit the old API and gain unauthorized access to sensitive user data.

#### Background of the Incident

Just Dial is a popular local search service in India. When they decided to redesign their APIs, they focused on securing the new APIs but overlooked the old ones. The old API, which still had access to the user database, was left running without proper security measures. This oversight provided a window of opportunity for attackers to exploit the old API and gain unauthorized access to sensitive data.

### Implications of Improper Assets Management

Improper assets management can lead to several serious implications:

1. **Data Exposure**: Old or non-production APIs may have access to sensitive data, which can be exposed if not properly secured.
2. **Unauthorized Access**: Attackers can use non-production environments as a stepping stone to gain unauthorized access to the production environment.
3. **Reputation Damage**: Data breaches can severely damage a company's reputation and lead to loss of customer trust.
4. **Regulatory Compliance Issues**: Companies may face legal consequences if they fail to comply with data protection regulations due to improper asset management.

### How to Prevent / Defend Against Improper Assets Management

To effectively manage and secure API assets, companies should implement the following strategies:

#### Detection

1. **Regular Audits**: Conduct regular audits to identify and document all active and inactive APIs.
2. **Monitoring Tools**: Use monitoring tools to track API usage and detect any unusual activity.
3. **Security Scanning**: Perform regular security scans to identify vulnerabilities in both production and non-production environments.

#### Prevention

1. **Secure Configuration**: Ensure that all APIs, including non-production ones, are configured securely.
2. **Access Controls**: Implement strict access controls to limit access to sensitive data and systems.
3. **Deprecation Policies**: Establish clear policies for deprecating old APIs and ensure that they are properly decommissioned.

#### Secure Coding Fixes

Here is an example of how to secure an API endpoint using proper access controls and secure coding practices:

```python
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)

@app.route('/api/data', methods=['GET'])
@jwt_required()
def get_data():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"message": "Unauthorized"}), 403
    return jsonify({"data": "Sensitive information"})

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, the `@jwt_required()` decorator ensures that only authenticated users can access the `/api/data` endpoint. Additionally, the role-based access control checks if the user has the necessary permissions to access the sensitive data.

### Complete Example: Full HTTP Request and Response

Here is a complete example of a full HTTP request and response for accessing an API endpoint:

**HTTP Request:**

```http
GET /api/data HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**HTTP Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "data": "Sensitive information"
}
```

### Mermaid Diagrams

#### API Architecture Diagram

```mermaid
graph LR
  A[User] -->|HTTP Request| B[API Gateway]
  B -->|Authenticated Request| C[Backend Service]
  C -->|Database Query| D[Database]
  D -->|Response| C
  C -->|HTTP Response| B
  B -->|Response| A
```

#### Sequence Diagram

```mermaid
sequenceDiagram
  participant User
  participant APIGateway
  participant BackendService
  participant Database

  User->>APIGateway: GET /api/data
  APIGateway->>BackendService: Authenticated Request
  BackendService->>Database: Database Query
  Database-->>BackendService: Response
  BackendService-->>APIGateway: HTTP Response
  APIGateway-->>User: Response
```

### Common Pitfalls

1. **Ignoring Non-Production Environments**: Failing to secure non-production environments can lead to significant vulnerabilities.
2. **Lack of Regular Audits**: Not conducting regular audits to identify and document all active and inactive APIs can result in overlooked vulnerabilities.
3. **Insufficient Access Controls**: Failing to implement strict access controls can allow unauthorized access to sensitive data and systems.

### Hands-On Labs

For hands-on practice in managing and securing API assets, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on API security, including improper assets management.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security techniques, including API security.
- **DVWA (Damn Vulnerable Web Application)**: Another excellent resource for practicing web application security, including API security.

By following these strategies and practices, companies can effectively manage and secure their API assets, reducing the risk of unauthorized access and data exposure.

### Conclusion

Improper assets management is a critical issue in API security that can lead to significant vulnerabilities. By understanding the implications and implementing effective detection, prevention, and secure coding practices, companies can mitigate these risks and ensure the security of their API assets. Regular audits, strict access controls, and secure coding practices are essential components of a robust API security strategy.

---
<!-- nav -->
[[01-Improper Asset Management in APIs|Improper Asset Management in APIs]] | [[API Security/05-OWASP API TOP 10/10-API9 Improper assets management/00-Overview|Overview]] | [[03-Improper Assets Management in APIs|Improper Assets Management in APIs]]
