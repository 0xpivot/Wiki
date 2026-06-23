---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## Introduction to API1 Broken Object Level Authorization

API1 Broken Object Level Authorization is one of the critical vulnerabilities listed in the OWASP API Security Top 10. This vulnerability occurs when an application fails to properly restrict access to resources based on the user's identity or role. In other words, an attacker can manipulate identifiers to gain unauthorized access to sensitive data or perform actions they should not be allowed to perform.

### What is Object Level Authorization?

Object Level Authorization (OLA) refers to the practice of ensuring that users can only access specific objects or resources that they are authorized to interact with. This is different from Role-Based Access Control (RBAC), which grants permissions based on roles assigned to users. OLA ensures that even if a user is authenticated and has certain permissions, they cannot access objects that do not belong to them.

#### Why Does Object Level Authorization Matter?

Without proper OLA, an attacker can exploit the system by manipulating identifiers such as IDs, GUIDs, or other unique keys. This can lead to unauthorized access to sensitive data, modification of critical information, or even deletion of important records. For instance, consider a scenario where a user can view their own profile by accessing `/api/users/{userId}`. If the application does not enforce OLA, an attacker could simply change `userId` to another user's ID and gain access to their profile.

### How Does Broken Object Level Authorization Work?

Broken Object Level Authorization typically arises due to insufficient validation of object identifiers. Here’s a step-by-step breakdown of how this vulnerability can be exploited:

1. **Identify the Identifier**: Attackers look for identifiers in URLs, request bodies, or headers. These identifiers are often used to reference specific objects or resources within the application.

2. **Manipulate the Identifier**: Once an identifier is found, attackers attempt to modify it to point to a different resource. For example, changing `userId=123` to `userId=456`.

3. **Access Unauthorized Resources**: If the application does not validate the identifier against the user's permissions, the attacker gains access to resources they should not have access to.

### Real-World Examples

Several high-profile breaches have been attributed to broken object level authorization:

- **CVE-2021-3129**: A vulnerability in the Microsoft Exchange Server allowed attackers to manipulate object identifiers and gain unauthorized access to email messages and attachments.
- **CVE-2020-1472**: Known as “Zerologon,” this vulnerability in the Netlogon Remote Protocol allowed attackers to manipulate identifiers and gain administrative privileges on Windows servers.

### Detection and Exploitation Techniques

To detect and exploit broken object level authorization, attackers often follow these steps:

1. **Create Multiple Accounts**: By creating multiple accounts, attackers can test the application's behavior when different users attempt to access the same resource.

2. **Capture Requests**: Using tools like Burp Suite, Wireshark, or browser developer tools, attackers capture HTTP requests containing object identifiers.

3. **Modify Identifiers**: Attackers then modify the captured identifiers and send the modified requests to the server to see if they can access unauthorized resources.

#### Example Scenario

Consider a web application that allows users to view their own orders using the endpoint `/api/orders/{orderId}`. An attacker might follow these steps:

1. **Capture Request**:
    ```http
    GET /api/orders/123 HTTP/1.1
    Host: example.com
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```

2. **Modify Identifier**:
    ```http
    GET /api/orders/456 HTTP/1.1
    Host: example.com
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```

3. **Send Modified Request**:
    ```http
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
        "orderId": 456,
        "items": [
            {"productId": 1, "quantity": 2},
            {"productId": 2, "quantity": 1}
        ],
        "total": 150.00
    }
    ```

If the application returns the order details for `orderId=456`, it indicates a broken object level authorization vulnerability.

### How to Prevent / Defend Against Broken Object Level Authorization

#### Secure Coding Practices

1. **Validate Identifiers**: Always validate object identifiers against the user's permissions. Ensure that the user is authorized to access the specific resource referenced by the identifier.

2. **Use Unique Identifiers**: Use GUIDs or other unique identifiers that are difficult to guess or predict. However, ensure that these identifiers are still validated against the user's permissions.

3. **Role-Based Access Control (RBAC)**: Implement RBAC to ensure that users can only access resources that match their roles and permissions.

#### Example Secure Code

Here’s an example of how to implement secure validation in a Node.js application:

```javascript
// Vulnerable code
app.get('/api/orders/:orderId', (req, res) => {
    const orderId = req.params.orderId;
    const order = getOrderByID(orderId);
    res.json(order);
});

// Secure code
app.get('/api/orders/:orderId', (req, res) => {
    const userId = req.user.id; // Assuming user is authenticated
    const orderId = req.params.orderId;
    const order = getOrderByID(orderId);

    if (order.userId === userId) {
        res.json(order);
    } else {
        res.status(403).json({ error: 'Forbidden' });
    }
});
```

#### Configuration Hardening

1. **Enable Strict Transport Security (HSTS)**: Ensure that all communication between the client and server is encrypted using HTTPS.

2. **Use Content Security Policy (CSP)**: Implement CSP to prevent cross-site scripting (XSS) attacks that could be used to manipulate identifiers.

3. **Regular Audits and Penetration Testing**: Conduct regular security audits and penetration testing to identify and mitigate vulnerabilities.

### Mermaid Diagrams

#### Sequence Diagram for Exploitation

```mermaid
sequenceDiagram
    participant User as U
    participant Attacker as A
    participant Server as S

    U->>S: GET /api/orders/123
    S-->>U: Order details for 123

    A->>S: GET /api/orders/456
    S-->>A: Order details for 456
```

#### Sequence Diagram for Secure Implementation

```mermaid
sequenceDiagram
    participant User as U
    participant Attacker as A
    participant Server as S

    U->>S: GET /api/orders/123
    S-->>U: Order details for 123

    A->>S: GET /api/orders/456
    S-->>A: Forbidden
```

### Practice Labs

For hands-on experience with detecting and exploiting broken object level authorization, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a module on broken object level authorization where you can practice identifying and exploiting this vulnerability.
- **OWASP Juice Shop**: A deliberately insecure web application that includes several broken object level authorization challenges.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of web application vulnerabilities, including broken object level authorization, for educational purposes.

By thoroughly understanding and implementing the preventive measures discussed, developers can significantly reduce the risk of broken object level authorization vulnerabilities in their applications.

---
<!-- nav -->
[[API Security/05-OWASP API TOP 10/01-API1 Broken Object Level Authorization/00-Overview|Overview]] | [[02-Introduction to Broken Object Level Authorization|Introduction to Broken Object Level Authorization]]
