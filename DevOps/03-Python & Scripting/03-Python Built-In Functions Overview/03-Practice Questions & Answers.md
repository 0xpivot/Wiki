---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain what built-in functions are in Python and provide examples of how they are used.**

Built-in functions in Python are pre-defined functions that are always available for use. They are part of the Python language and do not require any external libraries to be imported. Examples include `print()`, `input()`, `set()`, and `int()`.

```python
# Example of using print()
print("Hello, World!")

# Example of using input()
user_input = input("Enter your name: ")

# Example of using set()
my_list = [1, 2, 3, 4, 4]
unique_elements = set(my_list)

# Example of using int()
number_str = "123"
number_int = int(number_str)
```

**Q2. How does the `input()` function work in Python? Provide an example and explain its usage.**

The `input()` function in Python reads a line from input, converts it to a string (stripping a trailing newline), and returns that. It can optionally take a prompt argument, which is a string that is printed to standard output without a newline before reading input.

```python
# Example of using input()
name = input("Please enter your name: ")
print(f"Hello, {name}!")
```

In this example, the user is prompted to enter their name, which is then stored in the variable `name` and used in a greeting message.

**Q3. What is the difference between built-in functions like `print()` and methods called on objects such as `split()`? Provide examples and explain the differences.**

Built-in functions like `print()` are standalone functions that operate independently of any particular object. They typically take arguments and return results.

Methods, on the other hand, are functions that are associated with a specific object. They are called on an instance of a class and often modify the state of the object or perform operations related to the object's data type.

```python
# Example of a built-in function
print("This is a built-in function.")

# Example of a method called on an object
text = "apple,banana,cherry"
words = text.split(",")
print(words)
```

In the above example, `print()` is a built-in function that outputs a string to the console. The `split()` method, however, is called on a string object (`text`) and splits the string into a list of substrings based on the delimiter provided.

**Q4. How would you use the `set()` function to convert a list into a set? Provide an example and explain the process.**

The `set()` function in Python can be used to convert a list into a set, which removes duplicate elements and ensures that each element is unique.

```python
# Example of converting a list to a set
my_list = [1, 2, 3, 4, 4, 5, 6, 6]
my_set = set(my_list)
print(my_set)
```

In this example, `my_list` contains some duplicate elements. When we pass `my_list` to the `set()` function, it creates a new set `my_set` that contains only the unique elements from `my_list`.

**Q5. Explain how the `int()` function works and provide an example of converting a string to an integer.**

The `int()` function in Python is used to convert a string or a number to an integer. If the argument is a string, it must contain a valid integer representation; otherwise, a `ValueError` will be raised.

```python
# Example of converting a string to an integer
number_str = "123"
number_int = int(number_str)
print(number_int)
```

In this example, `number_str` is a string containing the digits "123". By passing `number_str` to the `int()` function, it converts the string to an integer `123`, which is stored in `number_int`.

---
<!-- nav -->
[[02-Introduction to Python Built-in Functions|Introduction to Python Built-in Functions]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/03-Python Built-In Functions Overview/00-Overview|Overview]]
