---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Objects and Classes in Python

In Python, the concept of **objects** and **classes** is fundamental to object-oriented programming (OOP). This paradigm allows developers to model real-world entities and their interactions in a structured manner. Let's delve into the details of how classes and objects work in Python, including the special methods and attributes that make OOP powerful and flexible.

### Classes in Python

A **class** is a blueprint for creating objects. It defines the structure and behavior of an object. In Python, a class is defined using the `class` keyword followed by the name of the class. Here’s a simple example:

```python
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email
```

#### Understanding the `__init__` Method

The `__init__` method is a special method in Python classes. It is called automatically when an instance of the class is created. This method is often referred to as the **constructor** because it constructs the initial state of the object.

- **Purpose**: The `__init__` method initializes the attributes of the object.
- **Syntax**: The method signature includes `self` as the first parameter, followed by other parameters that define the attributes of the object.

Here’s a detailed breakdown of the `__init__` method:

```python
def __init__(self, username, email):
    self.username = username
    self.email = email
```

- **`self`**: This is a reference to the instance of the class. It is used to access variables that belong to the class. The `self` parameter is a convention; you could technically name it anything, but `self` is widely accepted and understood.
- **`username` and `email`**: These are the parameters passed to the `__init__` method. They are used to initialize the attributes of the object.

#### Creating Instances of a Class

Once a class is defined, you can create instances of that class. Each instance is a separate object with its own set of attributes.

```python
user1 = User("john_doe", "john@example.com")
user2 = User("jane_doe", "jane@example.com")
```

- **`user1` and `user2`**: These are instances of the `User` class. Each instance has its own `username` and `email` attributes.

### Attributes in Classes

Attributes are variables that belong to a class. They can be initialized in the `__init__` method or defined directly within the class.

#### Instance Attributes

Instance attributes are specific to each instance of the class. They are defined within the `__init__` method and accessed using the `self` keyword.

```python
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email
```

- **`self.username` and `self.email`**: These are instance attributes. Each instance of the `User` class will have its own `username` and `email`.

#### Class Attributes

Class attributes are shared among all instances of the class. They are defined outside the `__init__` method and are accessible using the class name.

```python
class User:
    default_email_domain = "example.com"

    def __init__(self, username, email):
        self.username = username
        self.email = email
```

- **`default_email_domain`**: This is a class attribute. It is shared among all instances of the `User` class.

### Methods in Classes

Methods are functions defined within a class. They operate on the data contained within the class and can modify the state of the object.

#### Instance Methods

Instance methods are methods that operate on an instance of the class. They are defined within the class and take `self` as the first parameter.

```python
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def get_full_name(self):
        return f"{self.username} ({self.email})"
```

- **`get_full_name`**: This is an instance method. It takes `self` as the first parameter and returns the full name of the user.

#### Class Methods

Class methods are methods that operate on the class itself rather than an instance of the class. They are defined using the `@classmethod` decorator.

```python
class User:
    default_email_domain = "example.com"

    def __init__(self, username, email):
        self.username = username
        self.email = email

    @classmethod
    def create_user_with_default_domain(cls, username):
        email = f"{username}@{cls.default_email_domain}"
        return cls(username, email)
```

- **`create_user_with_default_domain`**: This is a class method. It takes `cls` as the first parameter and creates a new instance of the `User` class with the default email domain.

### Special Methods in Python

Python provides several special methods that allow you to customize the behavior of your classes. These methods are prefixed and suffixed with double underscores (`__`).

#### `__str__` and `__repr__` Methods

These methods are used to provide string representations of objects.

- **`__str__`**: This method returns a string representation of the object that is readable by humans.
- **`__repr__`: This method returns a string representation of the object that can be used to recreate the object.

```python
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __str__(self):
        return f"User({self.username}, {self.email})"

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
```

- **`__str__`**: Returns a human-readable string representation of the object.
- **`__repr__`: Returns a string representation of the object that can be used to recreate the object.

### Inheritance in Python

Inheritance is a key feature of OOP that allows you to create a new class based on an existing class. The new class inherits the attributes and methods of the existing class and can also add new attributes and methods or override existing ones.

```python
class Admin(User):
    def __init__(self, username, email, admin_level):
        super().__init__(username, email)
        self.admin_level = admin_level
```

- **`Admin`**: This is a subclass of the `User` class. It inherits the `username` and `email` attributes from the `User` class and adds a new attribute `admin_level`.
- **`super()`**: This is a built-in function that allows you to call methods from the parent class.

### Encapsulation in Python

Encapsulation is the practice of hiding the internal details of an object and providing access to them through methods. This helps to protect the integrity of the object and prevents unauthorized access to its attributes.

#### Private Attributes

Private attributes are attributes that are intended to be accessed only within the class. They are denoted by a single leading underscore (`_`).

```python
class User:
    def __init__(self, username, email):
        self._username = username
        self._email = email

    def get_username(self):
        return self._username

    def set_username(self, username):
        self._username = username
```

- **`_username` and `_email`**: These are private attributes. They are intended to be accessed only within the class.
- **`get_username` and `set_username`**: These are methods that provide controlled access to the private attributes.

### Polymorphism in Python

Polymorphism is the ability of different classes to be used interchangeably. This is achieved through method overriding and method overloading.

#### Method Overriding

Method overriding is the practice of redefining a method in a subclass that is already defined in the parent class.

```python
class User:
    def send_email(self):
        print(f"Sending email to {self.email}")

class Admin(User):
    def send_email(self):
        print(f"Sending email to {self.email} with admin privileges")
```

- **`send_email`**: This method is overridden in the `Admin` class. It provides a different implementation of the method.

### Real-World Examples and Security Considerations

#### Example: User Management System

Consider a user management system where users can be created, updated, and deleted. The system should ensure that sensitive information such as passwords is not exposed.

```python
import hashlib

class User:
    def __init__(self, username, password):
        self.username = username
        self.password_hash = self.hash_password(password)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        return self.password_hash == self.hash_password(password)
```

- **`hash_password`**: This method hashes the password using SHA-256.
- **`check_password`**: This method checks if the provided password matches the hashed password.

#### Security Considerations

When working with user data, it is important to ensure that sensitive information is protected. Here are some best practices:

- **Hash Passwords**: Always hash passwords before storing them in the database.
- **Use HTTPS**: Ensure that all communication between the client and server is encrypted using HTTPS.
- **Input Validation**: Validate all input to prevent injection attacks.
- **Access Control**: Implement proper access control to ensure that only authorized users can access sensitive information.

### How to Prevent / Defend

#### Detection

To detect potential vulnerabilities in your code, you can use static analysis tools such as PyLint, Bandit, and PySec. These tools can help identify common security issues such as SQL injection, cross-site scripting (XSS), and insecure deserialization.

#### Prevention

To prevent security vulnerabilities, follow these best practices:

- **Secure Coding Practices**: Follow secure coding practices such as input validation, output encoding, and error handling.
- **Use Secure Libraries**: Use secure libraries and frameworks that have been audited for security vulnerabilities.
- **Regular Audits**: Regularly audit your code for security vulnerabilities using static analysis tools and manual code reviews.

#### Secure Code Fix

Here is an example of a vulnerable code and its secure version:

**Vulnerable Code**

```python
import sqlite3

def login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
    result = cursor.fetchone()
    conn.close()
    return result is not None
```

**Secure Code**

```python
import sqlite3

def login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None
```

- **Vulnerable Code**: Uses string interpolation, which can lead to SQL injection.
- **Secure Code**: Uses parameterized queries to prevent SQL injection.

### Hands-On Practice

To gain practical experience with objects and classes in Python, you can use the following resources:

- **PortSwigger Web Security Academy**: Offers interactive labs on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

By practicing with these resources, you can gain a deeper understanding of how to implement and secure objects and classes in Python.

### Conclusion

Understanding objects and classes in Python is crucial for building robust and secure applications. By following best practices and using secure coding techniques, you can ensure that your applications are resilient to common security threats.

---
<!-- nav -->
[[04-Introduction to Objects and Classes in Python|Introduction to Objects and Classes in Python]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/10-Objects and Classes in Python/00-Overview|Overview]] | [[06-Understanding Data Types and Variables in Python|Understanding Data Types and Variables in Python]]
