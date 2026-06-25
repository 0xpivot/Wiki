---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Writing Useful Comments in Python Code

### Introduction to Comments in Python

Comments are an essential part of programming as they help developers understand the logic and purpose behind the code. In Python, comments are used to annotate the code and provide context, but they are not executed by the interpreter. There are two types of comments in Python:

1. **Single-line comments**: These start with the `#` symbol and continue until the end of the line.
2. **Multi-line comments**: These are created using triple quotes (`'''` or `"""`) and can span multiple lines.

### Single-line Comments

Single-line comments are straightforward and are used to annotate individual lines of code. They are denoted by the `#` symbol followed by the comment text.

#### Example of Single-line Comments

```python
# This is a single-line comment
print("Hello, World!")  # This comment explains the print statement
```

#### Why Use Single-line Comments?

Single-line comments are useful for providing quick explanations or reminders about specific lines of code. They can help other developers (or even yourself in the future) understand the purpose of a particular line of code.

#### Pitfalls of Overusing Single-line Comments

While single-line comments are helpful, overusing them can clutter the code and make it harder to read. For instance, commenting every line of code can be redundant and unnecessary.

#### Best Practices for Single-line Comments

- Use single-line comments sparingly and only when necessary.
- Provide meaningful information that adds value to the understanding of the code.
- Avoid trivial comments like `# increment i`.

### Multi-line Comments

Multi-line comments are created using triple quotes (`'''` or `"""`). They can span multiple lines and are often used for more detailed explanations or documentation within the code.

#### Syntax of Multi-line Comments

```python
'''
This is a multi-line comment.
It can span multiple lines and is useful for detailed explanations.
'''

"""
Another example of a multi-line comment.
These can also be used for documenting functions or classes.
"""
```

#### Why Use Multi-line Comments?

Multi-line comments are particularly useful for providing detailed explanations, such as documenting the purpose of a function, class, or complex logic. They can also be used for creating docstrings, which are strings used to document modules, functions, classes, and methods.

#### Pitfalls of Overusing Multi-line Comments

Similar to single-line comments, overusing multi-line comments can lead to cluttered code. It is important to strike a balance between providing enough context and keeping the code clean and readable.

#### Best Practices for Multi-line Comments

- Use multi-line comments for detailed explanations and documentation.
- Keep the comments concise and to the point.
- Use docstrings for documenting modules, functions, classes, and methods.

### Docstrings

Docstrings are a special type of multi-line comment used to document modules, functions, classes, and methods. They are enclosed in triple quotes and are placed immediately after the definition of the module, function, class, or method.

#### Example of Docstrings

```python
def greet(name):
    """
    This function greets the person passed in as a parameter.

    Parameters:
    name (str): The name of the person to greet.

    Returns:
    str: A greeting message.
    """
    return f"Hello, {name}!"
```

#### Why Use Docstrings?

Docstrings provide a standardized way to document code, making it easier for other developers to understand the purpose and usage of the code. They can be accessed programmatically using the `__doc__` attribute.

#### Pitfalls of Poorly Written Docstrings

Poorly written docstrings can be misleading and unhelpful. It is important to ensure that the docstrings accurately describe the functionality and parameters of the code.

#### Best Practices for Docstrings

- Follow the conventions specified in PEP 257 for writing docstrings.
- Include a brief description of the function, class, or method.
- Document the parameters and return values.
- Use consistent formatting and style.

### Real-world Examples and Best Practices

#### Example 1: Overuse of Comments

Consider the following code snippet with excessive comments:

```python
# Define a function to add two numbers
def add(a, b):
    # Add the two numbers
    result = a + b  # Store the result in a variable
    # Return the result
    return result  # Return the result of the addition
```

#### Improved Version

The improved version removes unnecessary comments and keeps the code clean and readable:

```python
def add(a, b):
    """Add two numbers and return the result."""
    return a + b
```

#### Example 2: Proper Use of Comments

Consider the following code snippet with proper use of comments:

```python
def calculate_discount(price, discount_rate):
    """
    Calculate the discounted price based on the given price and discount rate.

    Parameters:
    price (float): The original price.
    discount_rate (float): The discount rate as a percentage.

    Returns:
    float: The discounted price.
    """
    # Ensure the discount rate is within the valid range
    if discount_rate < 0 or discount_rate > 100:
        raise ValueError("Discount rate must be between 0 and 100.")

    # Calculate the discount amount
    discount_amount = price * (discount_rate / 100)

    # Subtract the discount amount from the original price
    discounted_price = price - discount_amount

    return discounted_price
```

#### Explanation

- The function `calculate_discount` is documented with a docstring that describes its purpose, parameters, and return value.
- Comments are used to explain the logic and validation steps within the function.

### How to Prevent / Defend Against Misuse of Comments

#### Detection

To detect misuse of comments, you can use static analysis tools like `flake8`, `pylint`, or `bandit`. These tools can help identify issues such as redundant comments, missing docstrings, and poorly formatted comments.

#### Prevention

- Follow coding standards and best practices for writing comments.
- Use automated tools to enforce coding standards and detect issues.
- Conduct code reviews to ensure that comments are meaningful and not redundant.

#### Secure Coding Fixes

Here is an example of a vulnerable code snippet with poor comments and the corresponding secure version:

**Vulnerable Code**

```python
# Define a function to add two numbers
def add(a, b):
    # Add the two numbers
    result = a + b  # Store the result in a variable
    # Return the result
    return result  # Return the result of the addition
```

**Secure Code**

```python
def add(a, b):
    """Add two numbers and return the result."""
    return a + b
```

### Conclusion

Writing useful comments in Python code is crucial for maintaining readability and understandability. By following best practices and avoiding common pitfalls, you can ensure that your code remains clean and maintainable. Use comments judiciously and focus on providing meaningful information that adds value to the understanding of the code.

### Practice Labs

For hands-on practice with writing useful comments in Python code, consider the following resources:

- **PortSwigger Web Security Academy**: Offers interactive labs for learning web security concepts, including secure coding practices.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including secure coding.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

By engaging with these resources, you can gain practical experience in writing clean and maintainable code with appropriate comments.

---
<!-- nav -->
[[01-Introduction to Comments in Python|Introduction to Comments in Python]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/25-Writing Useful Comments In Python Code/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/25-Writing Useful Comments In Python Code/03-Practice Questions & Answers|Practice Questions & Answers]]
