---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of using functions in programming.**

Functions serve several purposes in programming:
1. **Avoiding Code Duplication:** By encapsulating repeated code into a function, you can reuse the function across your program without rewriting the same logic multiple times.
2. **Improving Readability:** Functions allow you to break down complex programs into smaller, manageable parts. This makes the code easier to read and understand.
3. **Maintaining Code:** When changes are needed, modifying a single function is often easier than searching through and updating multiple instances of the same code.
4. **Reusability:** Functions can be reused in different parts of the program or even in different programs, promoting code reusability.

**Q2. How do you define a function in Python, and what is the syntax?**

In Python, you define a function using the `def` keyword followed by the function name and parentheses. The syntax is as follows:

```python
def function_name(parameters):
    # Function body
    # Statements to be executed
```

For example, to define a function that converts days to hours:

```python
def days_to_units(num_of_days):
    hours = num_of_days * 24
    print(f"{num_of_days} days are {hours} hours")
```

**Q3. Why is it important to provide parameters to a function? Provide an example.**

Parameters are important because they allow functions to operate on different data without needing to hardcode values. This makes functions more flexible and reusable. For instance, consider the `days_to_units` function:

```python
def days_to_units(num_of_days):
    hours = num_of_days * 24
    print(f"{num_of_days} days are {hours} hours")

# Calling the function with different parameters
days_to_units(20)
days_to_units(35)
```

By passing different values (`20`, `35`) to the `num_of_days` parameter, the function can handle various inputs dynamically.

**Q4. What is the difference between global and local variables in the context of functions?**

Global variables are defined outside of any function and can be accessed by any function in the program. Local variables are defined within a function and are only accessible within that function. 

Example:

```python
name_of_units = "hours"  # Global variable

def days_to_units(num_of_days):
    hours = num_of_days * 24  # Local variable
    print(f"{num_of_days} days are {hours} {name_of_units}")

days_to_units(20)
```

In this example, `name_of_units` is a global variable accessible within the `days_to_units` function, while `hours` is a local variable that exists only within the function.

**Q5. How can you handle errors when a function is called without the required parameters?**

When a function is called without the required parameters, Python raises a `TypeError`. To handle this, ensure that the function is called with the correct number of arguments. For example:

```python
def days_to_units(num_of_days):
    hours = num_of_days * 24
    print(f"{num_of_days} days are {hours} hours")

# Correct call
days_to_units(20)

# Incorrect call (will raise TypeError)
# days_to_units()
```

To prevent such errors, always check that the function is called with the necessary parameters.

**Q6. Can a function have multiple parameters? If yes, provide an example.**

Yes, a function can have multiple parameters. Parameters are separated by commas within the parentheses. Here’s an example:

```python
def days_to_units(num_of_days, custom_message):
    hours = num_of_days * 24
    print(f"{custom_message}: {num_of_days} days are {hours} hours")

# Calling the function with multiple parameters
days_to_units(20, "Awesome")
days_to_units(35, "Looks good")
```

In this example, `num_of_days` and `custom_message` are both parameters of the `days_to_units` function.

---
<!-- nav -->
[[06-Variable Scope in Functions|Variable Scope in Functions]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/02-Avoiding Code Duplication With Functions/00-Overview|Overview]]
