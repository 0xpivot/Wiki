---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Displaying Hidden Files in the Terminal

Hidden files in Unix-based systems are files whose names start with a dot (`.`). These files are typically used for configuration purposes and are not displayed by default in the terminal.

### Command to Display Hidden Files

To display hidden files in the terminal, you can use the `-a` option with the `ls` command. For example:

```bash
ls -a
```

This will list all files, including hidden ones, in the current directory.

#### Example Usage

Suppose you are in your home directory and want to see all hidden files:

```bash
cd ~
ls -a
```

This will display all files, including those starting with a dot, such as `.bashrc`, `.ssh`, etc.

#### Underlying Mechanism

The `-a` option tells the `ls` command to display all files, including those that are hidden by default. Hidden files are typically used by various applications to store configuration data, binaries, or other important information.

#### Common Pitfalls

- **Accidental Deletion**: Be careful when manipulating hidden files, as they often contain important configuration data. Deleting or modifying these files can cause issues with the associated applications.

- **Security Risks**: Hidden files can sometimes contain sensitive information. Ensure that you do not inadvertently expose this information to unauthorized users.

### How to Prevent / Defend

- **Backup Configuration Files**: Before making changes to hidden configuration files, ensure that you have a backup of the original files.

- **Use Secure Permissions**: Set appropriate permissions on hidden files to prevent unauthorized access. For example, you can set the permissions on a hidden file using the `chmod` command:

    ```bash
    chmod 600 ~/.ssh/id_rsa
    ```

    This sets the permissions to read/write for the owner only, preventing other users from accessing the file.

---
<!-- nav -->
[[06-Copying and Pasting in the Terminal|Copying and Pasting in the Terminal]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/10-GUI vs CLI File Management Commands/00-Overview|Overview]] | [[08-Displaying Memory Information|Displaying Memory Information]]
