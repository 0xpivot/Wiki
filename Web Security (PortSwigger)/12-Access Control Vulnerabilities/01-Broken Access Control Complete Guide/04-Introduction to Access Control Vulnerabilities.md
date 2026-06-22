---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Introduction to Access Control Vulnerabilities

Access control vulnerabilities are among the most critical issues in web security. These vulnerabilities occur when users can perform actions outside of their intended permissions, leading to severe consequences such as unauthorized access, data modification, or even destruction of data. In this chapter, we will delve deep into the concept of broken access control vulnerabilities, their types, impacts, and how to prevent them.

### What is Access Control?

Access control is a fundamental security mechanism that ensures that users can only access resources and perform actions that they are authorized to do. This is typically achieved through a combination of authentication (verifying the identity of the user) and authorization (granting or denying access based on the user's role).

#### Types of Access Control

There are three primary types of access control:

1. **Discretionary Access Control (DAC)**: Users have the ability to grant or revoke access to other users based on their discretion.
2. **Mandatory Access Control (MAC)**: Access is controlled by a central authority, and users cannot change the access rules.
3. **Role-Based Access Control (RBAC)**: Access is granted based on the roles assigned to users. Each role has specific permissions associated with it.

### Broken Access Control Vulnerabilities

Broken access control vulnerabilities arise when users can act outside of their intended permissions. This can happen due to flaws in the implementation of access control mechanisms, leading to various types of vulnerabilities such as horizontal privilege escalation, vertical privilege escalation, and insecure direct object references.

#### Impact of Broken Access Control Vulnerabilities

The impact of broken access control vulnerabilities can vary widely depending on the type of vulnerability found. Here are some common impacts:

- **Sensitive Information Disclosure**: Unauthorized access to sensitive data such as personal information, financial details, or confidential business data.
- **Unauthorized Access**: Users gaining access to resources or functionalities that they should not have access to.
- **Data Modification or Destruction**: Unauthorized users modifying or deleting data, leading to potential loss of business continuity.

### Real-World Examples

Let's look at some recent real-world examples of broken access control vulnerabilities:

#### Example 1: CVE-2021-21972

In 2021, a critical vulnerability was discovered in the popular open-source project Apache Struts. The vulnerability allowed attackers to bypass access controls and execute arbitrary code on the server. This led to unauthorized access and potential data theft.

```markdown
**CVE-2021-21972**
- **Description**: A vulnerability in Apache Struts allowed attackers to bypass access controls and execute arbitrary code.
- **Impact**: Unauthorized access and potential data theft.
```

#### Example 2: Equifax Data Breach (2017)

In 2017, Equifax suffered a massive data breach due to a vulnerability in their web application framework. The vulnerability allowed attackers to access sensitive personal information of millions of customers. This breach highlighted the importance of robust access control mechanisms.

```markdown
**Equifax Data Breach (2017)**
- **Description**: A vulnerability in Equifax's web application framework allowed attackers to access sensitive personal information.
- **Impact**: Exposure of sensitive personal information of millions of customers.
```

### Horizontal Privilege Escalation

Horizontal privilege escalation occurs when a user with normal privileges gains access to resources or performs actions that are intended for other users within the same permission level. This can lead to sensitive information disclosure or unauthorized access to other users' data.

#### Example Scenario

Consider a web application where users can view their own orders. However, due to a flaw in the access control mechanism, a user can modify the URL to view other users' orders. This is an example of horizontal privilege escalation.

```http
GET /orders?userId=123 HTTP/1.1
Host: example.com
Authorization: Bearer <token>
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "orderId": 123,
  "items": [
    {
      "name": "Product A",
      "quantity": 2,
      "price": 100
    }
  ],
  "total": 200
}
```

#### How to Prevent Horizontal Privilege Escalation

To prevent horizontal privilege escalation, ensure that the access control mechanism properly validates the user's permissions before granting access to resources. Here are some steps to follow:

1. **Validate User Permissions**: Ensure that the user's permissions are checked before accessing any resource.
2. **Use Role-Based Access Control (RBAC)**: Implement RBAC to manage user permissions based on roles.
3. **Audit Logs**: Maintain audit logs to track user activities and detect any unauthorized access attempts.

```python
# Vulnerable Code
def get_order(user_id):
    order = db.get_order(user_id)
    return order

# Secure Code
def get_order(user_id):
    if current_user.id == user_id:
        order = db.get_order(user_id)
        return order
    else:
        raise PermissionError("Access denied")
```

### Vertical Privilege Escalation

Vertical privilege escalation occurs when a user with lower privileges gains access to resources or performs actions that are intended for users with higher privileges. This can lead to unauthorized access to administrative functions or sensitive data.

#### Example Scenario

Consider a web application where users can view their own orders, but administrators can view all orders. Due to a flaw in the access control mechanism, a regular user can modify the URL to access administrative functions. This is an example of vertical privilege escalation.

```http
GET /admin/orders HTTP/1.1
Host: example.com
Authorization: Bearer <token>
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "orderId": 123,
    "items": [
      {
        "name": "Product A",
        "quantity": 2,
        "price": 100
      }
    ],
    "total": 200
  },
  {
    "orderId": 456,
    "items": [
      {
        "name": "Product B",
        "quantity": 1,
        "price": 150
      }
    ],
    "total": 150
  }
]
```

#### How to Prevent Vertical Privilege Escalation

To prevent vertical privilege escalation, ensure that the access control mechanism properly validates the user's role before granting access to administrative functions. Here are some steps to follow:

1. **Role-Based Access Control (RBAC)**: Implement RBAC to manage user permissions based on roles.
2. **Separation of Duties**: Ensure that users with lower privileges cannot access administrative functions.
3. **Audit Logs**: Maintain audit logs to track user activities and detect any unauthorized access attempts.

```python
# Vulnerable Code
def get_admin_orders():
    orders = db.get_all_orders()
    return orders

# Secure Code
def get_admin_orders():
    if current_user.is_admin:
        orders = db.get_all_orders()
        return orders
    else:
        raise PermissionError("Access denied")
```

### Insecure Direct Object References

Insecure direct object references occur when a user can manipulate the input to access resources that they should not have access to. This can lead to unauthorized access to sensitive data or administrative functions.

#### Example Scenario

Consider a web application where users can view their own orders using a URL parameter. Due to a flaw in the access control mechanism, a user can modify the URL parameter to access other users' orders. This is an example of insecure direct object references.

```http
GET /orders?orderId=123 HTTP/1.1
Host: example.com
Authorization: Bearer <token>
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "orderId": 123,
  "items": [
    {
      "name": "Product A",
      "quantity": 2,
      "price": 100
    }
  ],
  "total": 200
}
```

#### How to Prevent Insecure Direct Object References

To prevent insecure direct object references, ensure that the access control mechanism properly validates the user's permissions before granting access to resources. Here are some steps to follow:

1. **Validate User Permissions**: Ensure that the user's permissions are checked before accessing any resource.
2. **Use Role-Based Access Control (RBAC)**: Implement RBAC to manage user permissions based on roles.
3. **Audit Logs**: Maintain audit logs to track user activities and detect any unauthorized access attempts.

```python
# Vulnerable Code
def get_order(order_id):
    order = db.get_order(order_id)
    return order

# Secure Code
def get_order(order_id):
    if current_user.id == order.user_id:
        order = db.get_order(order_id)
        return order
    else:
        raise PermissionError("Access denied")
```

### Conclusion

Broken access control vulnerabilities are a serious threat to web applications. They can lead to unauthorized access, data modification, or even destruction of data. To prevent these vulnerabilities, it is essential to implement robust access control mechanisms, validate user permissions, and maintain audit logs. By following these best practices, you can ensure that your web application is secure and protected against access control vulnerabilities.

### Practice Labs

For hands-on practice with access control vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including access control vulnerabilities.
- **OWASP Juice Shop**: An intentionally vulnerable web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is deliberately vulnerable for educational purposes.

By completing these labs, you can gain practical experience in identifying and preventing access control vulnerabilities in web applications.

---
<!-- nav -->
[[03-Fundamentals of Access Control|Fundamentals of Access Control]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/01-Broken Access Control Complete Guide/00-Overview|Overview]] | [[05-What is a Broken Access Control Vulnerability|What is a Broken Access Control Vulnerability]]
