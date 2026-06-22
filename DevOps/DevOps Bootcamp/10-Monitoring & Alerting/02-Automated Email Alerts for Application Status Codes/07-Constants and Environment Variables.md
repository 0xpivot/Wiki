---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Constants and Environment Variables

### Understanding Constants

In programming, **constants** are variables whose values do not change throughout the execution of a program. They are used to store values that remain constant throughout the application, such as configuration settings, mathematical constants, or other fixed data points. 

#### Naming Conventions for Constants

One of the standard naming conventions for constants is to use **all uppercase letters**. This makes it visually distinct from regular variables, which typically use lowercase letters or camelCase. For example:

```python
MAX_CONNECTIONS = 10
```

This convention helps developers quickly identify which variables are intended to be constants and should not be modified during runtime.

#### Syntax for Constants in Different Languages

Some programming languages provide explicit support for constants through special keywords or constructs. For instance:

- **Python**: While Python does not have a built-in `const` keyword, the convention is to use all uppercase letters for constants.
- **JavaScript**: You can use the `const` keyword to declare constants.
- **Java**: You can use the `final` keyword to declare constants.

Here’s an example in JavaScript:

```javascript
const MAX_CONNECTIONS = 10;
```

And in Java:

```java
public final static int MAX_CONNECTIONS = 10;
```

### Environment Variables

Environment variables are dynamic named values that can affect the way running processes will behave on a computer. They are part of the environment in which a process runs. 

#### Setting Environment Variables

Environment variables can be set in various ways, including:

- **Terminal**: You can set environment variables directly in the terminal. For example, in a Unix-based system:

  ```sh
  export SOFTWARE_VERSION=18
  ```

  In Windows, you would use:

  ```cmd
  set SOFTWARE_VERSION=18
  ```

- **Operating System**: You can set environment variables persistently in your operating system. For example, in Linux, you can add the following line to your `.bashrc` or `.profile` file:

  ```sh
  export SOFTWARE_VERSION=18
  ```

  In Windows, you can set environment variables via the System Properties dialog.

### Persistent vs. Non-Persistent Environment Variables

When you set an environment variable in the terminal, it is only available within that specific terminal session. Once you close the terminal or start a new session, the environment variable is lost. This is non-persistent.

To make environment variables persistent, you need to set them in your operating system. Here’s how you can do it in different operating systems:

#### Linux

Add the environment variable to your `.bashrc` or `.profile` file:

```sh
export SOFTWARE_VERSION=18
```

Then, reload the profile:

```sh
source ~/.bashrc
```

#### Windows

Set the environment variable via the System Properties dialog:

1. Right-click on "Computer" or "This PC" and select "Properties".
2. Click on "Advanced system settings".
3. Click on the "Environment Variables" button.
4. Add a new environment variable with the desired name and value.

#### macOS

Add the environment variable to your `.bash_profile` or `.zshrc` file:

```sh
export SOFTWARE_VERSION=18
```

Then, reload the profile:

```sh
source ~/.bash_profile
```

### Accessing Environment Variables in a Program

Once you have set an environment variable, you can access it in your program. Here’s how you can do it in different programming languages:

#### Python

```python
import os

software_version = os.getenv('SOFTWARE_VERSION')
print(f"The software version is {software_version}")
```

#### JavaScript

```javascript
const softwareVersion = process.env.SOFTWARE_VERSION;
console.log(`The software version is ${softwareVersion}`);
```

#### Java

```java
public class Main {
    public static void main(String[] args) {
        String softwareVersion = System.getenv("SOFTWARE_VERSION");
        System.out.println("The software version is " + softwareVersion);
    }
}
```

### Real-World Examples and Security Implications

#### Example: Configuration Management

Imagine you have a web application that needs to connect to a database. The database connection details are stored in environment variables. If these variables are not set correctly, the application may fail to connect to the database.

#### Security Considerations

Environment variables can pose security risks if sensitive information, such as API keys or database passwords, is stored in them. If these variables are exposed, an attacker could gain unauthorized access to your systems.

#### How to Prevent / Defend

1. **Secure Environment Variables**: Ensure that sensitive environment variables are not exposed in your codebase or logs. Use tools like Docker secrets or Kubernetes secrets to manage sensitive data securely.
  
2. **Validation and Error Handling**: Always validate environment variables and handle errors gracefully. For example, if a required environment variable is missing, log an error and exit the program.

3. **Use Secure Coding Practices**: Follow secure coding practices to avoid exposing sensitive information. For example, avoid logging environment variables directly.

### Complete Example

Let’s walk through a complete example of setting up and accessing environment variables in a Python application.

#### Step 1: Set Environment Variable

In your `.bashrc` or `.profile` file:

```sh
export DATABASE_URL="postgresql://user:password@localhost/dbname"
```

Reload the profile:

```sh
source ~/.bashrc
```

#### Step 2: Access Environment Variable in Python

Create a Python script (`app.py`):

```python
import os

def get_database_url():
    return os.getenv('DATABASE_URL')

if __name__ == "__main__":
    db_url = get_database_url()
    print(f"Database URL: {db_url}")
```

Run the script:

```sh
python app.py
```

Output:

```
Database URL: postgresql://user:password@localhost/dbname
```

### Pitfalls and Common Mistakes

1. **Forgetting to Reload Profile**: After setting an environment variable in your `.bashrc` or `.profile`, remember to reload the profile using `source`.

2. **Incorrect Syntax**: Ensure you use the correct syntax for setting environment variables in your operating system.

3. **Exposing Sensitive Information**: Avoid exposing sensitive information in environment variables. Use secure methods to manage sensitive data.

### Conclusion

Understanding constants and environment variables is crucial for managing configurations and ensuring the security of your applications. By following best practices and using secure coding techniques, you can effectively manage environment variables and avoid common pitfalls.

### Practice Labs

For hands-on practice with environment variables and secure coding, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing web applications, including handling environment variables.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide practical experience in managing environment variables and securing your applications.

---
<!-- nav -->
[[06-Automated Email Alerts for Application Status Codes|Automated Email Alerts for Application Status Codes]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/02-Automated Email Alerts for Application Status Codes/00-Overview|Overview]] | [[08-Environment Variables and Automated Email Alerts for Application Status Codes|Environment Variables and Automated Email Alerts for Application Status Codes]]
