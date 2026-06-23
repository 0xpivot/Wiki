---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Nested Function Calls and Type Checking in Python

### Nested Function Calls

In Python, functions can be called within other functions, creating a nested structure. This technique allows for more concise and sometimes more readable code, but it can also make the code harder to understand if overused.

#### Syntax and Example

Consider the following example where we have a function `days_to_units` that converts days to a specified unit (like hours or minutes):

```python
def days_to_units(days, conversion_unit):
    if conversion_unit == "hours":
        return days * 24
    elif conversion_unit == "minutes":
        return days * 24 * 60
    else:
        return "Invalid unit"

# Nested function call
print(days_to_units(2, "hours"))
```

Here, instead of assigning the result of `days_to_units` to a variable and then printing it, we directly pass the arguments to the function and print the result. This is a valid and often used approach in Python.

#### Benefits and Drawbacks

**Benefits:**
- **Conciseness:** Reduces the number of lines of code.
- **Readability:** Can make the code more readable if the nesting is not too deep.

**Drawbacks:**
- **Complexity:** Deeply nested function calls can make the code harder to read and debug.
- **Maintainability:** Overuse can lead to less maintainable code.

### Type Checking in Python

Type checking is crucial in Python, especially when dealing with user input or data from external sources. Python provides several ways to check the type of a variable, including the built-in `type()` function.

#### Using `type()` Function

The `type()` function returns the type of the object passed to it. Here’s how you can use it:

```python
# Check the type of a string
string_var = "Hello"
print(type(string_var))  # Output: <class 'str'>

# Check the type of an integer
int_var = 42
print(type(int_var))  # Output: <class 'int'>

# Check the type of a float
float_var = 3.14
print(type(float_var))  # Output: <class 'float'>
```

#### Practical Example: Validating User Input

When validating user input, it's important to ensure that the input matches the expected type. For instance, if you expect an integer, you should verify that the input is indeed an integer.

```python
def validate_input(user_input):
    try:
        int_value = int(user_input)
        print(f"Validated input: {int_value}")
    except ValueError:
        print("Invalid input! Please enter an integer.")

# Example usage
validate_input("42")  # Valid input
validate_input("hello")  # Invalid input
```

### Conditionals in Python

Conditionals are fundamental in programming and are used to control the flow of execution based on certain conditions. The most common conditional statements in Python are `if`, `elif`, and `else`.

#### Basic Structure

```python
if condition:
    # Code to execute if the condition is true
elif another_condition:
    # Code to execute if the previous condition is false and this one is true
else:
    # Code to execute if none of the above conditions are true
```

#### Example: Validating User Input with Conditionals

Let's extend the previous example to include type validation using conditionals:

```python
def validate_and_convert(user_input):
    if isinstance(user_input, str):
        try:
            int_value = int(user_input)
            print(f"Converted input: {int_value}")
        except ValueError:
            print("Invalid input! Please enter an integer.")
    else:
        print("Input must be a string.")

# Example usage
validate_and_convert("42")  # Valid input
validate_and_convert("hello")  4 # Invalid input
validate_and_convert(42)  # Input must be a string
```

### Real-World Examples and Security Implications

#### Recent CVEs and Breaches

One of the most common vulnerabilities related to user input validation is SQL Injection. For example, consider the following scenario where user input is directly used in a SQL query:

```sql
SELECT * FROM users WHERE username = '$username';
```

If `$username` is not properly validated, an attacker could inject malicious SQL code. For instance, if `$username` is set to `' OR '1'='1`, the query becomes:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1';
```

This would return all rows from the `users` table, potentially exposing sensitive data.

#### Secure Coding Practices

To prevent such vulnerabilities, always validate and sanitize user input. Use parameterized queries or prepared statements to safely handle user input in SQL queries.

```python
import sqlite3

def get_user(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# Example usage
get_user("john_doe")
```

### How to Prevent / Defend

#### Detection

- **Static Analysis Tools:** Use tools like PyLint, Bandit, or SonarQube to detect potential issues in your code.
- **Dynamic Analysis Tools:** Use tools like OWASP ZAP or Burp Suite to test your application for vulnerabilities.

#### Prevention

- **Input Validation:** Always validate user input to ensure it meets the expected format and type.
- **Sanitization:** Sanitize user input to remove any potentially harmful characters or patterns.
- **Parameterized Queries:** Use parameterized queries to safely handle user input in database operations.

#### Secure Coding Fixes

**Vulnerable Code:**

```python
def get_user(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
    user = cursor.fetchone()
    conn.close()
    return user
```

**Secure Code:**

```python
def get_user(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user
```

### Hands-On Practice

For hands-on practice with validating user input and handling conditionals, consider the following labs:

- **PortSwigger Web Security Academy:** Offers interactive labs on various web security topics, including input validation and SQL injection.
- **OWASP Juice Shop:** A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application):** Another intentionally vulnerable web application for learning web security.

These labs will help you apply the concepts learned in this chapter and gain practical experience in securing applications against common vulnerabilities.

### Conclusion

Understanding and effectively using nested function calls, type checking, and conditionals is essential for writing robust and secure Python applications. By following best practices and using secure coding techniques, you can prevent common vulnerabilities and ensure the reliability and security of your code.

---
<!-- nav -->
[[07-Introduction to User Input Validation|Introduction to User Input Validation]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/21-Validating User Input With Conditionals/00-Overview|Overview]] | [[09-Understanding Nested Conditional Statements|Understanding Nested Conditional Statements]]
