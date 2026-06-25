---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain how to assign and reference a variable in a Bash script.**

To assign a value to a variable in a Bash script, you use the assignment operator `=`. For example:

```bash
file_name="config.yml"
```

To reference the value of a variable, you use the `$` symbol followed by the variable name. For example:

```bash
echo $file_name
```

This will output `config.yml`.

**Q2. How can you capture the output of a command and store it in a variable? Provide an example.**

You can capture the output of a command and store it in a variable by using the following syntax:

```bash
variable=$(command)
```

For example, to capture the output of the `ls` command listing the contents of a directory:

```bash
dir_contents=$(ls /path/to/directory)
echo $dir_contents
```

This will store the output of the `ls` command in the `dir_contents` variable and then print it.

**Q3. Describe how to use conditionals (if-else statements) in a Bash script. Provide an example.**

Conditionals in Bash scripts are used to check conditions and execute different blocks of code based on the outcome. The syntax is:

```bash
if [ condition ]; then
    # Code to execute if condition is true
else
    # Code to execute if condition is false
fi
```

For example, to check if a directory exists and create it if it doesn't:

```bash
if [ -d "/path/to/directory" ]; then
    echo "Directory exists."
else
    mkdir /path/to/directory
    echo "Directory created."
fi
```

**Q4. How can you pass parameters to a Bash script and use them within the script? Provide an example.**

Parameters can be passed to a Bash script when it is executed. Inside the script, you can access these parameters using positional variables (`$1`, `$2`, etc.). For example:

```bash
#!/bin/bash
echo "First parameter: $1"
echo "Second parameter: $2"
```

If you run the script with parameters:

```bash
./script.sh param1 param2
```

It will output:

```
First parameter: param1
Second parameter: param2
```

**Q5. Explain how to use loops in Bash scripts. Provide an example using a `for` loop.**

Loops in Bash scripts are used to iterate over a sequence of items. A `for` loop can be used to iterate over a list of items. The syntax is:

```bash
for variable in list; do
    # Code to execute for each item in the list
done
```

For example, to iterate over a list of directories and print their contents:

```bash
directories=("dir1" "dir2" "dir3")
for dir in "${directories[@]}"; do
    echo "Contents of $dir:"
    ls "$dir"
done
```

This will print the contents of each directory listed in the `directories` array.

**Q6. How can you use a `while` loop in a Bash script? Provide an example.**

A `while` loop is used to repeatedly execute a block of code as long as a specified condition is true. The syntax is:

```bash
while [ condition ]; do
    # Code to execute while condition is true
done
```

For example, to continuously prompt the user for input until they enter 'quit':

```bash
while true; do
    read -p "Enter a word (type 'quit' to exit): " word
    if [ "$word" = "quit" ]; then
        break
    fi
    echo "You entered: $word"
done
```

This will keep prompting the user until they enter 'quit', at which point the loop will terminate.

**Q7. What is the difference between using single square brackets `[ ]` and double square brackets `[[ ]]` in Bash conditionals?**

Single square brackets `[ ]` are the traditional way to perform tests in Bash. They are part of the shell syntax and require spaces around the brackets and the operators. For example:

```bash
if [ -f "$filename" ]; then
    echo "File exists."
fi
```

Double square brackets `[[ ]]` are a more modern feature introduced in Bash. They offer more features and flexibility, such as pattern matching and regular expressions. They also do not require spaces around the brackets and operators. For example:

```bash
if [[ -f "$filename" ]]; then
    echo "File exists."
fi
```

Additionally, double square brackets support logical operators like `&&` and `||` directly, making the syntax cleaner and more intuitive.

**Q8. How can you use a `for` loop to iterate over all command-line arguments passed to a Bash script? Provide an example.**

To iterate over all command-line arguments passed to a Bash script, you can use a `for` loop with the special variable `$@`. For example:

```bash
#!/bin/bash
for arg in "$@"; do
    echo "Argument: $arg"
done
```

If you run the script with multiple arguments:

```bash
./script.sh arg1 arg2 arg3
```

It will output:

```
Argument: arg1
Argument: arg2
Argument: arg3
```

This demonstrates how to process each argument passed to the script individually.

---
<!-- nav -->
[[05-Variables in Scripting|Variables in Scripting]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/24-Variable Usage And Command Output Capture In Scripting/00-Overview|Overview]]
