---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Python Lists for Multiple Input Calculations

In this section, we will delve into the intricacies of handling multiple inputs in Python using lists. Specifically, we will focus on validating and processing these inputs to ensure our application functions correctly. This is a fundamental skill in DevOps, particularly when dealing with user inputs in scripts and applications.

### Understanding User Input in Python

When working with user input in Python, it is crucial to understand that `input()` always returns a string. This means that even if the user enters a number or a list of numbers, the input will be treated as a string unless explicitly converted.

#### Example of User Input as String

```python
user_input = input("Enter a list of numbers separated by spaces: ")
print(type(user_input))  # <class 'str'>
```

### Converting User Input to a List

To handle multiple inputs effectively, we often need to convert the user input into a list of elements. This can be achieved using the `split()` method, which splits a string into a list based on a specified delimiter.

#### Using `split()` Method

The `split()` method takes an optional argument that specifies the delimiter. By default, it splits the string at whitespace characters.

```python
user_input = input("Enter a list of numbers separated by spaces: ")
numbers_list = user_input.split()
print(numbers_list)
```

For example, if the user enters `"1 2 3 4"`, the output will be:

```python
['1', '2', '3', '4']
```

### Handling Individual Elements in the List

Once we have the list of numbers, we can iterate through it to process each element individually. This is particularly useful when performing calculations or validations on each number.

#### Iterating Through the List

```python
user_input = input("Enter a list of numbers separated by spaces: ")
numbers_list = user_input.split()

for num in numbers_list:
    print(num)
```

### Type Conversion of List Elements

Since the `split()` method returns a list of strings, we need to convert these strings to integers or floats depending on our requirements.

#### Converting Strings to Integers

```python
user_input = input("Enter a list of numbers separated by spaces: ")
numbers_list = user_input.split()

# Convert each element to an integer
numbers_list = [int(num) for num in numbers_list]
print(numbers_list)
```

### Example Application: Validating and Executing Function

Let's consider an application where we need to validate and process a list of numbers entered by the user.

#### Initial Code Structure

```python
def validate_and_execute(numbers_list):
    for num in numbers_list:
        if num > 0:
            print(f"Positive number: {num}")
        else:
            print(f"Non-positive number: {num}")

user_input = input("Enter a list of numbers separated by spaces: ")
numbers_list = user_input.split()
numbers_list = [int(num) for num in numbers_list]

validate_and_execute(numbers_list)
```

### Handling Edge Cases and Errors

It is essential to handle potential errors such as invalid input formats or non-numeric values.

#### Error Handling with Try-Except

```python
def validate_and_execute(numbers_list):
    for num in numbers_list:
        if num > 0:
            print(f"Positive number: {num}")
        else:
            print(f"Non-positive number: {num}")

user_input = input("Enter a list of numbers separated by spaces: ")
numbers_list = user_input.split()

try:
    numbers_list = [int(num) for num in numbers_list]
    validate_and_execute(numbers_list)
except ValueError:
    print("Invalid input! Please enter numeric values only.")
```

### Real-World Examples and Security Implications

Handling user input securely is critical to prevent vulnerabilities such as injection attacks. For instance, if the input is used in SQL queries or shell commands, it could lead to SQL injection or command injection.

#### Example: SQL Injection

Consider a scenario where user input is used in a SQL query:

```python
import sqlite3

user_input = input("Enter a list of numbers separated by spaces: ")
numbers_list = user_input.split()
numbers_list = [int(num) for num in numbers_list]

conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# Vulnerable code
query = f"SELECT * FROM numbers WHERE value IN ({', '.join(map(str, numbers_list))})"
cursor.execute(query)

# Secure code
placeholders = ', '.join(['?'] * len(numbers_list))
query = f"SELECT * FROM numbers WHERE value IN ({placeholders})"
cursor.execute(query, numbers_list)
```

### How to Prevent / Defend

#### Detection and Prevention

1. **Input Validation**: Always validate user input to ensure it meets the expected format.
2. **Type Conversion**: Explicitly convert input to the required data type.
3. **Error Handling**: Implement robust error handling to manage unexpected inputs.
4. **Secure Coding Practices**: Use parameterized queries or prepared statements to prevent injection attacks.

#### Secure Code Fix

**Vulnerable Code**

```python
user_input = input("Enter a list of numbers separated by spaces: ")
numbers_list = user_input.split()
numbers_list = [int(num) for num in numbers_list]

query = f"SELECT * FROM numbers WHERE value IN ({', '.join(map(str, numbers_list))})"
cursor.execute(query)
```

**Secure Code**

```python
user_input = input("Enter a list of numbers separated by spaces: ")
numbers_list = user_input.split()
numbers_list = [int(num) for num in numbers_list]

placeholders = ', '.join(['?'] * len(numbers_list))
query = f"SELECT * FROM numbers WHERE value IN ({placeholders})"
cursor.execute(query, numbers_list)
```

### Hands-On Practice

To solidify your understanding, practice with real-world scenarios and tools:

- **PortSwigger Web Security Academy**: Focus on input validation and SQL injection labs.
- **OWASP Juice Shop**: Explore various security vulnerabilities related to user input.
- **DVWA**: Practice with different levels of difficulty to understand input handling.

By following these steps and practicing diligently, you will gain a comprehensive understanding of handling multiple inputs in Python and ensure your applications are secure and robust.

---
<!-- nav -->
[[03-Introduction to Python Lists and User Input Handling|Introduction to Python Lists and User Input Handling]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/16-Python Lists for Multiple Input Calculations/00-Overview|Overview]] | [[05-Introduction to Python Lists|Introduction to Python Lists]]
