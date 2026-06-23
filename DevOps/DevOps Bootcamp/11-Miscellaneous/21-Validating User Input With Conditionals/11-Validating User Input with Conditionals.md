---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Validating User Input with Conditionals

### Introduction to User Input Validation

When developing applications, one of the most critical aspects is ensuring that the data provided by users is valid and safe to process. Invalid or malicious inputs can lead to various issues, including crashes, security vulnerabilities, and incorrect behavior. In this section, we will explore how to validate user input using conditionals, specifically focusing on numeric input validation.

### Understanding Conditionals

Conditionals are fundamental constructs in programming that allow the execution of different paths based on certain conditions. The most common form of conditional statements is the `if` statement, which checks whether a given condition is true and executes a block of code accordingly.

#### Syntax of the `if` Statement

The basic syntax of an `if` statement in Python looks like this:

```python
if condition:
    # Code to execute if the condition is true
```

For example, consider the following code snippet:

```python
number = 10

if number > 0:
    print("The number is positive.")
```

In this example, the condition `number > 0` is evaluated. Since `number` is indeed greater than 0, the code inside the `if` block is executed, printing "The number is positive."

### Using `else` for Alternative Paths

Sometimes, you might want to specify an alternative path if the initial condition is not met. This is where the `else` keyword comes into play. The `else` block is executed when the condition specified in the `if` statement is false.

#### Syntax of `if-else` Statements

The syntax of an `if-else` statement is as follows:

```python
if condition:
    # Code to execute if the condition is true
else:
    # Code to execute if the condition is false
```

For instance, consider the following code snippet:

```python
number = -5

if number > 0:
    print("The number is positive.")
else:
    print("The number is not positive.")
```

Here, since `number` is less than 0, the condition `number > 0` evaluates to false, and the code inside the `else` block is executed, printing "The number is not positive."

### Applying Conditionals to Validate User Input

Let's apply this knowledge to validate user input. Suppose we have a function that converts a given number of days into a specific unit (e.g., hours, minutes). We want to ensure that the input is a positive number; otherwise, we should provide an appropriate error message.

#### Example Function: Days to Units Conversion

Consider the following function that converts days to a specified unit:

```python
def days_to_units(days, conversion_unit):
    if days > 0:
        if conversion_unit == "hours":
            return days * 24
        elif conversion_unit == "minutes":
            return days * 24 * 60
        else:
            return "Invalid unit"
    else:
        return "You entered a negative value, so no conversion for you."
```

This function takes two parameters: `days` and `conversion_unit`. It first checks if `days` is greater than 0. If it is, it proceeds to perform the conversion based on the `conversion_unit`. If `days` is not greater than 0, it returns an error message indicating that a negative value was entered.

#### Full Example with User Input

Let's integrate this function with user input and handle the validation:

```python
def main():
    user_input = input("Enter the number of days: ")
    try:
        days = int(user_input)
        result = days_to_units(days, "hours")
        print(result)
    except ValueError:
        print("Please enter a valid number.")

if __name__ == "__main__":
    main()
```

In this example, the `main` function prompts the user to enter the number of days. It then attempts to convert the input to an integer and passes it to the `days_to_units` function. If the input cannot be converted to an integer, a `ValueError` is raised, and an appropriate error message is displayed.

### Comparison Operators

Comparison operators are used to compare two values and determine the relationship between them. The most common comparison operators are:

- `>` (greater than)
- `<` (less than)
- `==` (equal to)

These operators return a boolean value (`True` or `False`) based on the comparison.

#### Example Usage of Comparison Operators

Consider the following examples:

```python
a = 10
b = 5

print(a > b)  # Output: True
print(a < b)  # Output: False
print(a == b) # Output: False
```

In the above code, `a > b` evaluates to `True` because 10 is indeed greater than 5. Similarly, `a < b` evaluates to `False` because 10 is not less than 5, and `a == b` evaluates to `False` because 10 is not equal to 5.

### Real-World Examples and Security Implications

Invalid user input can lead to various security vulnerabilities, such as SQL injection, cross-site scripting (XSS), and buffer overflows. Ensuring that user input is validated and sanitized is crucial to preventing these attacks.

#### Example: SQL Injection

Consider a web application that allows users to search for products by name. If the input is not properly validated, an attacker could inject malicious SQL code to manipulate the database.

```sql
SELECT * FROM products WHERE name = 'user_input';
```

If `user_input` is not validated, an attacker could input something like `' OR '1'='1`, leading to the following SQL query:

```sql
SELECT * FROM products WHERE name = '' OR '1'='1';
```

This would return all records from the `products` table, bypassing the intended filter.

#### Secure Coding Practices

To prevent such attacks, always validate and sanitize user input. Use parameterized queries or prepared statements to ensure that user input is treated as data rather than executable code.

```python
import sqlite3

def search_products(product_name):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Parameterized query
    cursor.execute("SELECT * FROM products WHERE name = ?", (product_name,))
    results = cursor.fetchall()

    conn.close()
    return results
```

In this example, the `?` placeholder is used to safely insert the `product_name` into the SQL query, preventing SQL injection.

### How to Prevent / Defend Against Invalid Input

#### Detection

To detect invalid input, implement logging and monitoring mechanisms to track user input and system behavior. Regularly review logs to identify patterns of suspicious activity.

#### Prevention

1. **Input Validation**: Always validate user input to ensure it meets the expected format and constraints.
2. **Sanitization**: Sanitize input to remove any potentially harmful characters or scripts.
3. **Parameterized Queries**: Use parameterized queries or prepared statements to prevent SQL injection.
4. **Content Security Policies (CSP)**: Implement CSP to mitigate XSS attacks by specifying which sources of content are allowed to be executed within a document.

#### Secure Coding Fixes

Compare the vulnerable code with the secure code:

**Vulnerable Code:**

```python
def search_products(product_name):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Vulnerable query
    cursor.execute(f"SELECT * FROM products WHERE name = '{product_name}'")
    results = cursor.fetchall()

    conn.close()
    return results
```

**Secure Code:**

```python
def search_products(product_name):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Parameterized query
    cursor.execute("SELECT * FROM products WHERE name = ?", (product_name,))
    results = cursor.fetchall()

    conn.close()
    return results
```

### Conclusion

Validating user input is a critical aspect of building robust and secure applications. By using conditionals and comparison operators, you can ensure that your application handles invalid input gracefully and securely. Always follow secure coding practices to prevent common vulnerabilities such as SQL injection and XSS attacks.

### Practice Labs

For hands-on practice with validating user input and handling security vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on SQL injection, XSS, and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains numerous security vulnerabilities.

By completing these labs, you can gain practical experience in securing applications against various types of attacks.

---
<!-- nav -->
[[10-Validating User Input With Conditionals|Validating User Input With Conditionals]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/21-Validating User Input With Conditionals/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/21-Validating User Input With Conditionals/12-Practice Questions & Answers|Practice Questions & Answers]]
