---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Variable Scope in Functions

In programming, especially in languages like Python, the concept of variable scope is crucial for managing data and ensuring that functions operate correctly and securely. Variable scope defines where a variable can be accessed within a program. Understanding variable scope helps avoid issues such as code duplication, unintended side effects, and security vulnerabilities.

### Global Variables

Global variables are defined outside of any function and are accessible throughout the entire program. This includes all functions and modules that import the global variable. Here’s an example:

```python
# Define a global variable
num_of_units = 10

def display_units():
    print(f"The number of units is {num_of_units}")

display_units()  # Output: The number of units is 10
```

#### Why Use Global Variables?

Global variables are useful when you need to share data across multiple functions or modules. They simplify the management of shared data and can make the code more readable and maintainable.

#### Pitfalls of Global Variables

While global variables can be convenient, they also introduce several risks:

1. **Unintended Side Effects**: Any function can modify a global variable, leading to unexpected behavior.
2. **Debugging Difficulties**: Tracking changes to global variables can be challenging, especially in large programs.
3. **Security Risks**: Global variables can be modified by malicious code, leading to potential security vulnerabilities.

#### Real-World Example: CVE-2021-3186

CVE-2021-3186 is a security vulnerability in the Apache Struts framework. One of the issues was related to the improper handling of global variables, which allowed attackers to inject arbitrary commands. This highlights the importance of carefully managing global variables to prevent unauthorized modifications.

### Local Variables

Local variables are defined within a function and are only accessible within that function. They are created when the function is called and destroyed when the function exits. Here’s an example:

```python
def calculate_days():
    number_of_days = 30
    print(f"The number of days is {number_of_days}")

calculate_days()  # Output: The number of days is 30
```

#### Why Use Local Variables?

Local variables help encapsulate data within a function, making the code more modular and easier to understand. They also reduce the risk of unintended side effects and improve security by limiting the scope of data.

#### Pitfalls of Local Variables

While local variables are generally safer than global variables, they can still lead to issues if not managed properly:

1. **Data Leakage**: If a local variable is accidentally returned or passed to another function, it can leak sensitive data.
2. **Scope Confusion**: Developers might mistakenly assume a variable is global when it is actually local, leading to errors.

### Testing Variable Scope

To demonstrate the difference between global and local variables, let’s create a function `scope_check` that tests the accessibility of both types of variables.

```python
# Define a global variable
num_of_units = 10

def scope_check():
    try:
        print(f"The number of units is {num_of_units}")
    except NameError:
        print("num_of_units is not defined")

    try:
        print(f"The number of days is {number_of_days}")
    except NameError:
        print("number_of_days is not defined")

scope_check()
```

#### Expected Output

```
The number of units is 10
number_of_days is not defined
```

This output confirms that the global variable `num_of_units` is accessible within the function, while the local variable `number_of_days` is not.

### How to Prevent / Defend Against Scope Issues

#### Detection

To detect issues related to variable scope, you can use static analysis tools like PyLint, which can identify unused variables, undefined variables, and other scope-related issues.

#### Prevention

1. **Minimize Global Variables**: Use global variables sparingly and only when necessary. Consider using constants instead.
2. **Encapsulation**: Encapsulate data within functions or classes to limit their scope.
3. **Code Reviews**: Regular code reviews can help catch scope-related issues early.

#### Secure Coding Fixes

Here’s an example of how to refactor code to avoid global variables and ensure proper scoping:

**Vulnerable Code**

```python
# Vulnerable code with global variables
num_of_units = 10

def calculate_days():
    number_of_days = 30
    print(f"The number of days is {number_of_days}")

calculate_days()
print(f"The number of units is {num_of_units}")
```

**Secure Code**

```python
# Secure code with local variables
def calculate_days(num_of_units):
    number_of_days = 30
    print(f"The number of days is {number_of_days}")
    return num_of_units

num_of_units = 10
num_of_units = calculate_days(num_of_units)
print(f"The number of units is {num_of_units}")
```

### Conclusion

Understanding variable scope is essential for writing clean, efficient, and secure code. By carefully managing the scope of variables, you can avoid common pitfalls and ensure that your functions operate as intended. Static analysis tools and regular code reviews can help detect and prevent scope-related issues.

### Practice Labs

For hands-on practice with variable scope and function management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web application security, including topics related to variable scope and function management.
- **OWASP Juice Shop**: A deliberately insecure web application for security training, which can help you understand the practical implications of variable scope in web applications.

By engaging with these resources, you can deepen your understanding of variable scope and apply it effectively in your DevOps practices.

---
<!-- nav -->
[[05-Understanding Scope in Programming|Understanding Scope in Programming]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/02-Avoiding Code Duplication With Functions/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/02-Avoiding Code Duplication With Functions/07-Practice Questions & Answers|Practice Questions & Answers]]
