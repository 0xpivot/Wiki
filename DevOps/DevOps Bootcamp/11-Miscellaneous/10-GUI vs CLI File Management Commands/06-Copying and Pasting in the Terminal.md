---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Copying and Pasting in the Terminal

Another useful feature in the terminal is the ability to copy and paste text. This can be particularly handy when dealing with long commands or configurations that you want to execute.

### Key Combination for Copying and Pasting

In many terminal emulators, you can use `Ctrl+Shift+V` to paste text that was previously copied from another source, such as a web browser.

#### Example Usage

Suppose you want to display the last 20 commands executed in your terminal history. You can find the appropriate command on a website like Stack Exchange and copy it. Then, in your terminal, you can paste the command using `Ctrl+Shift+V`.

For example, the command to display the last 20 commands in your history is:

```bash
history | tail -n 20
```

You can copy this command from a website and paste it into your terminal using `Ctrl+Shift+V`.

#### Underlying Mechanism

The `Ctrl+Shift+V` key combination allows you to paste text from the clipboard into the terminal. This is particularly useful when dealing with long commands or configurations that you do not want to retype manually.

#### Common Pitfalls

- **Clipboard Interference**: Ensure that the text you are pasting does not contain any unintended characters or formatting that could interfere with the command execution.

- **Security Risks**: Be cautious about pasting commands from untrusted sources, as they could potentially execute malicious code.

### How to Prevent / Defend

- **Review Commands Before Execution**: Always review the command you are pasting before executing it. Ensure that it does not contain any unexpected or harmful elements.

- **Use Secure Sources**: Only copy commands from trusted sources. Avoid pasting commands from unverified websites or forums.

---
<!-- nav -->
[[05-Command Line Interface (CLI) vs Graphical User Interface (GUI)|Command Line Interface (CLI) vs Graphical User Interface (GUI)]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/10-GUI vs CLI File Management Commands/00-Overview|Overview]] | [[07-Displaying Hidden Files in the Terminal|Displaying Hidden Files in the Terminal]]
