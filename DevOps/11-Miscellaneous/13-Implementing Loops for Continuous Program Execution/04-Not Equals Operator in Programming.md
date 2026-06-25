---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Not Equals Operator in Programming

In programming, the `not equals` operator is used to check whether two values are different. This operator is crucial for controlling the flow of a program based on conditions. The syntax for the `not equals` operator varies slightly across different programming languages, but the core functionality remains the same.

### Syntax Across Languages

- **Python**: `!=`
- **JavaScript**: `!=`
- **Java**: `!=`
- **C/C++**: `!=`

For instance, in Python, the expression `a != b` evaluates to `True` if `a` and `b` are not equal, and `False` otherwise.

### Example in Python

```python
a = 5
b = 10
if a != b:
    print("a is not equal to b")
```

This code snippet checks if `a` is not equal to `b`. Since `5` is indeed not equal to `10`, the output will be:

```
a is not equal to b
```

### Using `not equals` in Conditional Statements

The `not equals` operator is often used in conditional statements to control the execution flow of a program. One common use case is within loops, particularly `while` loops, which continue executing as long as a certain condition is true.

### Example: Loop Until User Enters "exit"

Consider a scenario where you want a program to continuously prompt the user for input until they enter the word "exit". Here’s how you can implement this using a `while` loop in Python:

```python
user_input = ""
while user_input != "exit":
    user_input = input("Enter something (type 'exit' to quit): ")
    print(f"You entered: {user_input}")
```

In this example, the `while` loop continues to execute as long as `user_input` is not equal to `"exit"`. Once the user types "exit", the loop breaks, and the program ends.

### Pitfalls and Warnings

When implementing such logic, it's important to handle potential issues that may arise. One common issue is the possibility of the `user_input` variable being undefined or not properly initialized. This can lead to runtime errors or unexpected behavior.

#### Example of Undefined Variable

If the `user_input` variable is not properly initialized before entering the loop, you might encounter an error. Consider the following incorrect implementation:

```python
# Incorrect implementation
while user_input != "exit":
    user_input = input("Enter something (type 'exit' to quit): ")
    print(f"You entered: {user_input}")
```

In this case, `user_input` is referenced before it is defined, leading to a `NameError`.

### Intelligent Code Editors and Warnings

Intelligent code editors like PyCharm can help catch these issues before they cause problems. PyCharm provides warnings and suggestions to ensure your code is robust and error-free.

#### Example Warning in PyCharm

When you hover over the `user_input` variable in PyCharm, you might see a warning message indicating that `user_input` can be undefined. This is because the variable is referenced before it is assigned a value.

### Correct Implementation

To avoid the undefined variable issue, ensure that `user_input` is properly initialized before entering the loop. Here’s the correct implementation:

```python
user_input = ""  # Initialize user_input
while user_input != "exit":
    user_input = input("Enter something (type 'exit' to quit): ")
    print(f"You entered: {user_input}")
```

### How to Prevent / Defend

#### Detection

To detect issues related to undefined variables, use static analysis tools and intelligent code editors. These tools can highlight potential issues before runtime.

#### Prevention

1. **Initialize Variables**: Always initialize variables before using them in conditions.
2. **Use Default Values**: Provide default values to ensure variables are always defined.
3. **Code Review**: Regularly review code to catch and fix potential issues.

#### Secure Coding Fixes

Here’s a comparison of the vulnerable and secure versions of the code:

**Vulnerable Code**

```python
# Vulnerable code
while user_input != "exit":
    user_input = input("Enter something (type 'exit' to quit): ")
    print(f"You entered: {user_input}")
```

**Secure Code**

```python
# Secure code
user_input = ""  # Initialize user_input
while user_input != "exit":
    user_input = input("Enter something (type 'exit' to quit): ")
    print(f"You entered: {user_input}")
```

### Real-World Examples and CVEs

While the example provided is relatively simple, similar issues can occur in more complex applications. For instance, consider a web application that relies on user input to control its flow. If the input is not properly validated or initialized, it could lead to unexpected behavior or even security vulnerabilities.

#### Example: CVE-2021-3116

CVE-2021-3116 is a vulnerability in the Apache Struts framework where improper validation of user input led to remote code execution. This highlights the importance of proper initialization and validation of variables.

### Conclusion

Using the `not equals` operator effectively in loops is crucial for controlling program flow. By ensuring proper initialization and handling potential issues, you can create robust and secure applications. Intelligent code editors like PyCharm can help catch and fix these issues early in the development process.

### Practice Labs

For hands-on practice with loops and conditional statements, consider the following resources:

- **PortSwigger Web Security Academy**: Offers interactive labs on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These resources provide practical experience in implementing and securing loops and conditional statements in real-world scenarios.

---
<!-- nav -->
[[03-Implementing Loops for Continuous Program Execution|Implementing Loops for Continuous Program Execution]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/13-Implementing Loops for Continuous Program Execution/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/13-Implementing Loops for Continuous Program Execution/05-Practice Questions & Answers|Practice Questions & Answers]]
