---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Arithmetic Operations in Bash

### Background Theory

In Bash scripting, arithmetic operations can be performed using different syntaxes depending on the context and the desired outcome. One of the most common issues beginners face is treating numeric values as strings, leading to unexpected results. To ensure that arithmetic operations are correctly interpreted, Bash provides specific syntaxes such as double parentheses `(( ))` and double square brackets `[[ ]]`.

### Double Parentheses `(( ))`

The double parentheses `(( ))` are used for arithmetic evaluation in Bash. This syntax allows you to perform arithmetic operations on variables and constants. Here’s how it works:

```bash
# Example of arithmetic operation using double parentheses
a=5
b=3
result=$((a + b))
echo "Result: $result"
```

#### Explanation

- **Variables**: `a` and `b` are assigned integer values.
- **Arithmetic Operation**: `((a + b))` performs addition between `a` and `b`.
- **Result**: The result of the operation is stored in the variable `result`.

#### Why Use Double Parentheses?

Using double parentheses ensures that the expression inside is evaluated as an arithmetic operation rather than a string concatenation. Without this syntax, Bash would treat the variables as strings, leading to incorrect results.

#### Real-World Example

Consider a scenario where you are calculating the total score in a game. Each player enters their score, and the script should keep track of the total score.

```bash
#!/bin/bash

total_score=0

while true; do
    read -p "Enter your score (or 'Q' to quit): " score
    if [[ "$score" == "Q" ]]; then
        break
    fi
    total_score=$((total_score + score))
    echo "Total Score: $total_score"
done
```

#### Explanation

- **Loop**: The `while true` loop runs indefinitely until the user inputs 'Q'.
- **Input**: The `read` command captures the user's input.
- **Condition**: The `if` statement checks if the input is 'Q'. If true, the loop breaks.
- **Arithmetic Operation**: `total_score=$((total_score + score))` updates the total score by adding the current score.

#### Common Pitfalls

- **Type Conversion**: Ensure that the input is a valid number. If the user inputs a non-numeric value, the script may fail.
- **Edge Cases**: Handle scenarios where the user might input negative numbers or very large numbers.

### Double Square Brackets `[[ ]]`

Double square brackets `[[ ]]` are used for conditional expressions in Bash. They provide more features and flexibility compared to the single square brackets `[ ]`. Here’s how they work:

```bash
# Example of conditional expression using double square brackets
a=5
b=3
if [[ $a -gt $b ]]; then
    echo "a is greater than b"
else
    echo "a is not greater than b"
fi
```

#### Explanation

- **Variables**: `a` and `b` are assigned integer values.
- **Conditional Expression**: `[[ $a -gt $b ]]` checks if `a` is greater than `b`.
- **Output**: Depending on the condition, the appropriate message is printed.

#### Why Use Double Square Brackets?

Double square brackets offer more robust and flexible conditional checking. They handle spaces and special characters better than single square brackets.

#### Real-World Example

Consider a scenario where you are checking if a user's input is within a certain range.

```bash
#!/bin/bash

read -p "Enter a number between 1 and 10: " number

if [[ $number =~ ^[1-9]$|^10$ ]]; then
    echo "Number is within the range."
else
    echo "Number is out of range."
fi
```

#### Explanation

- **Input**: The `read` command captures the user's input.
- **Regular Expression**: `[[ $number =~ ^[1-9]$|^10$ ]]` checks if the input is a number between 1 and 10.
- **Output**: Depending on the condition, the appropriate message is printed.

#### Common Pitfalls

- **Regular Expressions**: Ensure that the regular expression is correctly formatted to match the desired input.
- **Edge Cases**: Handle scenarios where the user might input non-numeric values or values outside the specified range.

### How to Prevent / Defend

#### Detection

To detect potential issues with arithmetic operations and conditional expressions, you can use tools like `shellcheck`, which analyzes shell scripts and points out common errors and pitfalls.

```bash
shellcheck your_script.sh
```

#### Prevention

- **Use Double Parentheses for Arithmetic Operations**: Always use `(( ))` for arithmetic operations to ensure correct evaluation.
- **Use Double Square Brackets for Conditional Expressions**: Use `[[ ]]` for conditional expressions to handle spaces and special characters better.
- **Validate User Input**: Always validate user input to ensure it meets the expected format and range.

#### Secure Code Fix

Here’s an example of a vulnerable script and its secure version:

**Vulnerable Script**

```bash
#!/bin/bash

total_score=0

while true; do
    read -p "Enter your score (or 'Q' to quit): " score
    if [ "$score" == "Q" ]; then
        break
    fi
    total_score=$total_score + $score
    echo "Total Score: $total_score"
done
```

**Secure Script**

```bash
#!/bin/bash

total_score=0

while true; do
    read -p "Enter your score (or 'Q' to quit): " score
    if [[ "$score" == "Q" ]]; then
        break
    fi
    total_score=$((total_score + score))
    echo "Total Score: $total_score"
done
```

#### Explanation

- **Vulnerable Script**: Uses single square brackets `[ ]` and string concatenation for arithmetic operations.
- **Secure Script**: Uses double square brackets `[[ ]]` and double parentheses `(( ))` for arithmetic operations.

### Practice Labs

For hands-on practice with these concepts, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various aspects of web security, including scripting.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.

These labs provide practical experience in handling arithmetic operations and conditional expressions in Bash scripts.

### Conclusion

Understanding and correctly implementing arithmetic operations and conditional expressions in Bash scripts is crucial for writing robust and secure scripts. By using double parentheses `(( ))` for arithmetic operations and double square brackets `[[ ]]` for conditional expressions, you can avoid common pitfalls and ensure your scripts behave as expected.

---
<!-- nav -->
[[02-Introduction to Variable Usage and Command Output Capture in Scripting|Introduction to Variable Usage and Command Output Capture in Scripting]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/24-Variable Usage And Command Output Capture In Scripting/00-Overview|Overview]] | [[04-Variable Usage and Command Output Capture in Scripting|Variable Usage and Command Output Capture in Scripting]]
