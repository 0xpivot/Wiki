---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Python Lists and User Input Handling

In this section, we will delve into the intricacies of handling user input in Python using lists. Specifically, we will explore how to take multiple inputs from users, convert them into a list, and perform calculations on these inputs. This process involves understanding how to use the `split` function effectively and handling various types of input data.

### Background Theory

Python lists are one of the most versatile data structures available in Python. They allow you to store multiple items in a single variable. Lists are ordered, changeable, and allow duplicate values. Each item in a list is identified by an index, which starts at 0 for the first item.

When dealing with user input, it is often necessary to take multiple values and process them together. One common approach is to ask the user to input a series of values separated by a delimiter (such as a space or a comma). These values can then be converted into a list using the `split` function.

### Understanding the `split` Function

The `split` function in Python is used to break a string into a list of substrings based on a specified delimiter. By default, the `split` function uses whitespace as the delimiter. However, you can specify a different delimiter if needed.

#### Default Behavior of `split`

By default, the `split` function splits the string on whitespace:

```python
input_string = "40 55 60"
values_list = input_string.split()
print(values_list)
```

Output:
```python
['40', '55', '60']
```

Here, the `split` function splits the string `"40 55 60"` into a list of strings `['40', '55', '60']`.

#### Specifying a Different Delimiter

You can also specify a different delimiter, such as a comma:

```python
input_string = "40,55,60"
values_list = input_string.split(',')
print(values_list)
```

Output:
```python
['40', '55', '60']
```

In this case, the `split` function splits the string `"40,55,60"` into a list of strings `['40', '55', '60']`.

### Handling User Input

Let's consider a scenario where we want to take multiple inputs from the user and perform calculations on them. We will use the `split` function to convert the input string into a list of values.

#### Example Code

```python
def calculate_values(input_string):
    values_list = input_string.split()
    results = []
    for value in values_list:
        try:
            num_value = int(value)
            result = num_value * 2  # Example calculation
            results.append(result)
        except ValueError:
            print(f"{value} is not a valid number.")
    return results

input_string = input("Enter a list of numbers separated by spaces: ")
results = calculate_values(input_string)
print(results)
```

### Handling Different Types of Input

In real-world scenarios, users might input values that are not strictly numbers. For instance, they might include text or floating-point numbers. We need to handle these cases gracefully.

#### Example with Mixed Input

```python
def calculate_values(input_string):
    values_list = input_string.split()
    results = []
    for value in values_list:
        try:
            num_value = float(value)  # Convert to float to handle both integers and floats
            result = num_value * 2  # Example calculation
            results.append(result)
        except ValueError:
            print(f"{value} is not a valid number.")
    return results

input_string = input("Enter a list of numbers separated by spaces: ")
results = calculate_values(input_string)
print(results)
```

### Real-World Examples and Security Considerations

Handling user input securely is crucial to prevent potential vulnerabilities. For example, if the input is used in a way that could be exploited (e.g., SQL injection), it is essential to validate and sanitize the input.

#### Example of Vulnerability

Consider a scenario where user input is used in a database query:

```python
import sqlite3

def get_user_data(user_input):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{user_input}'"
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

user_input = input("Enter a username: ")
data = get_user_data(user_input)
print(data)
```

This code is vulnerable to SQL injection attacks. If the user inputs something like `' OR '1'='1`, the query becomes:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1'
```

This would return all rows from the `users` table.

#### Secure Coding Practices

To prevent SQL injection, use parameterized queries:

```python
import sqlite3

def get_user_data(user_input):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (user_input,))
    results = cursor.fetchall()
    conn.close()
    return results

user_input = input("Enter a username: ")
data = get_user_data(user_input)
print(data)
```

### How to Prevent / Defend

#### Detection

To detect potential issues with user input, you can use static analysis tools like Bandit or PyLint. These tools can help identify insecure coding practices.

#### Prevention

1. **Input Validation**: Always validate user input to ensure it meets the expected format.
2. **Sanitization**: Sanitize input to remove any potentially harmful characters.
3. **Parameterized Queries**: Use parameterized queries to prevent SQL injection.
4. **Error Handling**: Implement robust error handling to manage unexpected input gracefully.

### Complete Example with Error Handling

```python
def calculate_values(input_string):
    values_list = input_string.split()
    results = []
    for value in values_list:
        try:
            num_value = float(value)  # Convert to float to handle both integers and floats
            result = num_value * 2  # Example calculation
            results.append(result)
        except ValueError:
            print(f"{value} is not a valid number.")
    return results

input_string = input("Enter a list of numbers separated by spaces: ")
results = calculate_values(input_string)
print(results)
```

### Conclusion

Handling user input in Python using lists and the `split` function is a powerful technique for processing multiple values. By understanding the default behavior and how to specify different delimiters, you can create flexible and robust applications. Additionally, by implementing secure coding practices, you can protect your applications from potential vulnerabilities.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice web security concepts.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning web security.

These labs provide practical experience in handling user input securely and detecting potential vulnerabilities.

---
<!-- nav -->
[[02-Introduction to Python Lists and Loops|Introduction to Python Lists and Loops]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/16-Python Lists for Multiple Input Calculations/00-Overview|Overview]] | [[04-Introduction to Python Lists for Multiple Input Calculations|Introduction to Python Lists for Multiple Input Calculations]]
