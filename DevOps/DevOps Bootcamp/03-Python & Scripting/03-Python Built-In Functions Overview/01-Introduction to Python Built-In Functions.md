---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Python Built-In Functions

In this section, we will delve deeply into the concept of Python built-in functions. These are functions provided by Python itself, which you can use directly in your code without needing to define them. They are essential tools for performing various operations efficiently and effectively. Understanding these functions thoroughly will enhance your ability to write robust and maintainable Python programs.

### What Are Built-In Functions?

Built-in functions are pre-defined functions that come with Python. They are part of the Python Standard Library and are ready to use without importing any additional modules. These functions perform specific tasks and are designed to simplify common programming tasks.

#### Example: `print()`

The `print()` function is one of the most commonly used built-in functions. It outputs the specified value(s) to the standard output device (usually the screen).

```python
print("Hello, World!")
```

This code snippet will display "Hello, World!" on the console.

#### Example: `input()`

The `input()` function is used to get user input from the console. It waits for the user to type something and press Enter.

```python
user_input = input("Enter your name: ")
print(f"Hello, {user_input}!")
```

This code will prompt the user to enter their name and then greet them.

### Why Use Built-In Functions?

Using built-in functions offers several advantages:

1. **Efficiency**: Built-in functions are optimized for performance. They are written in C and compiled, making them faster than custom-written Python functions.
2. **Consistency**: Using built-in functions ensures consistency across different parts of your codebase and aligns with Python's idiomatic style.
3. **Reduced Errors**: Since these functions are extensively tested and widely used, they are less likely to contain bugs compared to custom functions.
4. **Ease of Use**: Built-in functions are straightforward to use and require minimal setup, reducing the learning curve for new developers.

### How Built-In Functions Work Under the Hood

To understand how built-in functions work, let's look at the `print()` function in more detail. When you call `print()`, Python internally performs the following steps:

1. **Argument Parsing**: Python parses the arguments passed to the function.
2. **Output Formatting**: The arguments are formatted according to the rules defined by the `print()` function.
3. **Output Writing**: The formatted output is written to the standard output stream, typically the console.

Here is a simplified representation of the `print()` function's internal workings using a mermaid diagram:

```mermaid
graph TD
    A[User calls print()] --> B[Parse arguments]
    B --> C[Format output]
    C --> D[Write to stdout]
    D --> E[Output displayed on console]
```

### Common Built-In Functions

Let's explore some of the most commonly used built-in functions in Python:

#### `print()`

The `print()` function is used to display output on the console. It can take multiple arguments separated by commas.

```python
print("Hello", "World", sep=" ", end="\n")
```

- **`sep`**: Specifies the separator between the arguments. Default is a space.
- **`end`**: Specifies the string appended after the last value. Default is a newline (`\n`).

#### `input()`

The `input()` function reads a line from input (usually the user) and returns it as a string.

```python
name = input("Enter your name: ")
print(f"Hello, {name}!")
```

#### `set()`

The `set()` function converts an iterable (like a list) into a set, removing duplicates.

```python
my_list = [1, 2, 2, 3, 4, 4]
my_set = set(my_list)
print(my_set)  # Output: {1, 2, 3, 4}
```

#### `int()`

The `int()` function converts a string or number to an integer.

```python
num_str = "123"
num_int = int(num_str)
print(num_int)  # Output: 123
```

### Real-World Examples and Recent CVEs

While built-in functions themselves are generally safe, improper usage can lead to vulnerabilities. For instance, using `eval()` with untrusted input can result in arbitrary code execution.

#### CVE-2021-3186: Flask `eval()` Vulnerability

In 2021, a vulnerability was discovered in the Flask web framework where the `eval()` function was used with untrusted input. This allowed attackers to execute arbitrary code.

**Vulnerable Code:**

```python
@app.route('/evaluate')
def evaluate():
    expression = request.args.get('expr', '')
    result = eval(expression)
    return str(result)
```

**Secure Code:**

```python
@app.route('/evaluate')
def evaluate():
    expression = request.args.get('expr', '')
    # Use a safer alternative like `ast.literal_eval`
    try:
        result = ast.literal_eval(expression)
    except Exception as e:
        return f"Error: {str(e)}"
    return str(result)
```

### How to Prevent / Defend

#### Detection

To detect potential misuse of built-in functions, you can use static analysis tools like Bandit or PyLint. These tools can identify insecure usage patterns and suggest improvements.

#### Prevention

1. **Avoid `eval()` with Untrusted Input**: Always validate and sanitize inputs before passing them to functions like `eval()`.
2. **Use Safer Alternatives**: For evaluating expressions, consider using `ast.literal_eval()` instead of `eval()`.
3. **Input Validation**: Validate all user inputs to ensure they meet expected formats and constraints.

### Complete Examples

#### Example: Using `print()` and `input()`

```python
# Prompt user for input
name = input("Enter your name: ")

# Print greeting
print(f"Hello, {name}!")

# Full HTTP request and response (hypothetical scenario)
http_request = """
POST /greet HTTP/1.1
Host: example.com
Content-Type: application/json
Content-Length: 23

{"name": "Alice"}
"""

http_response = """
HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: 12

Hello, Alice!
"""

print(http_request)
print(http_response)
```

#### Example: Using `set()` and `int()`

```python
# Convert list to set
my_list = [1, 2, 2, 3, 4, 4]
my_set = set(my_list)
print(my_set)  # Output: {1, 2, 3, 4}

# Convert string to integer
num_str = "123"
num_int = int(num_str)
print(num_int)  # Output: 123
```

### Pitfalls and Common Mistakes

1. **Incorrect Argument Types**: Ensure that the arguments passed to built-in functions match the expected types. For example, `int()` expects a string or number, not a list.
2. **Ignoring Exceptions**: Always handle exceptions that may be raised by built-in functions. For example, `int()` raises a `ValueError` if the argument cannot be converted to an integer.
3. **Overusing `eval()`**: Avoid using `eval()` with untrusted input, as it can lead to security vulnerabilities.

### Conclusion

Understanding and effectively using Python built-in functions is crucial for writing efficient and secure code. By leveraging these functions correctly, you can simplify your code and reduce the likelihood of errors and security issues. Always validate and sanitize inputs, and use safer alternatives when necessary.

### Practice Labs

For hands-on practice with Python built-in functions, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes exercises that involve Python scripting.
- **OWASP Juice Shop**: A deliberately vulnerable web application for practicing web security skills, including Python-based attacks and defenses.

These labs provide practical scenarios where you can apply your knowledge of Python built-in functions in a real-world context.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/03-Python & Scripting/03-Python Built-In Functions Overview/00-Overview|Overview]] | [[02-Introduction to Python Built-in Functions|Introduction to Python Built-in Functions]]
