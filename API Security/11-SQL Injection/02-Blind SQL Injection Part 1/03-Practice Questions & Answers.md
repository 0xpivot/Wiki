---
course: API Security
topic: SQL Injection
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of blind SQL injection and how it differs from standard SQL injection.**

Blind SQL injection is a type of SQL injection where the attacker cannot see the direct output of the injected SQL query. Instead, the attacker infers the success or failure of the injection by observing changes in the application's behavior or timing. This contrasts with standard SQL injection, where the attacker can directly observe the results of the injected SQL query, often through error messages or altered data displayed on the web page.

**Q2. How can you detect a blind SQL injection vulnerability in an API endpoint?**

To detect a blind SQL injection vulnerability in an API endpoint, you can follow these steps:

1. **Identify Potential Parameters:** Look for parameters that interact with the database, such as `username`, `id`, or `email`.
   
2. **Inject Test Payloads:** Try injecting payloads like single quotes (`'`), double quotes (`"`), or special characters like `--` (commenting out the rest of the query).

3. **Observe Responses:** Check for differences in the responses. For example, if the response changes or an error occurs when you inject a single quote, it might indicate a vulnerability.

4. **Use Time-Based Techniques:** Inject payloads that cause a delay, such as `sleep(10)`. If the response takes longer than expected, it could indicate a successful injection.

For example, if you inject a single quote into the `username` parameter and receive an error message, it suggests that the input is being used in a SQL query without proper sanitization.

**Q3. How would you exploit a blind SQL injection vulnerability to extract data from a database?**

To exploit a blind SQL injection vulnerability and extract data from a database, you can use techniques like boolean-based or time-based injection. Here’s an example using boolean-based injection:

1. **Determine Database Structure:** Use payloads to determine the structure of the database, such as the number of columns and the names of tables.

   Example payload:
   ```sql
   ' OR 1=1 --
   ```
   This payload checks if the query returns true, indicating a potential vulnerability.

2. **Extract Data:** Once you know the structure, you can extract data by crafting payloads that return true or false based on the presence of specific data.

   Example payload to extract the length of a column:
   ```sql
   ' AND (SELECT LENGTH(column_name) FROM table_name WHERE id = 1) > 5 --
   ```

3. **Iterate and Refine:** Continue refining your payloads to extract specific data by incrementally checking values.

For instance, if you are trying to extract the length of a username, you can use:
```sql
' AND (SELECT LENGTH(username) FROM users WHERE id = 1) > 5 --
```
By iterating and adjusting the length, you can eventually determine the exact length and content of the username.

**Q4. How can you use SQLMap to automate the process of detecting and exploiting blind SQL injection vulnerabilities?**

SQLMap is a powerful tool for automating the detection and exploitation of SQL injection vulnerabilities, including blind SQL injection. Here’s how you can use it:

1. **Capture the Request:** Use a tool like Burp Suite to capture the HTTP request to the vulnerable API endpoint.

2. **Save the Request:** Save the captured request to a file, e.g., `request.txt`.

3. **Run SQLMap:** Use SQLMap to analyze the request and attempt to exploit the vulnerability.

   Example command:
   ```bash
   sqlmap -r request.txt --batch --level 5 --risk 3 --technique=B
   ```
   - `-r request.txt`: Specifies the file containing the HTTP request.
   - `--batch`: Runs SQLMap in batch mode without prompting for user input.
   - `--level 5`: Sets the level of tests to a higher value to detect more complex vulnerabilities.
   - `--risk 3`: Sets the risk level to a higher value to perform more aggressive tests.
   - `--technique=B`: Specifies the use of boolean-based blind SQL injection techniques.

4. **Review Results:** SQLMap will attempt to exploit the vulnerability and provide detailed information about the database structure and extracted data.

For example, if you run SQLMap against an endpoint and it detects a blind SQL injection vulnerability, SQLMap will automatically attempt to extract data from the database.

**Q5. Describe a recent real-world example of a blind SQL injection vulnerability and explain how it was exploited.**

One notable example of a blind SQL injection vulnerability is the breach of the Capital One data in 2019. The attacker exploited a misconfigured server that exposed sensitive data due to a vulnerability in the WAF (Web Application Firewall) configuration.

The attacker used a combination of SQL injection and other techniques to access the data. Specifically, the attacker exploited a blind SQL injection vulnerability in the WAF configuration to bypass security controls and gain unauthorized access to the database.

Here’s a simplified explanation of how the attack might have been carried out:

1. **Identify Vulnerability:** The attacker identified a misconfigured WAF rule that allowed certain SQL injection payloads to pass through.

2. **Exploit Vulnerability:** Using a combination of boolean-based and time-based SQL injection techniques, the attacker crafted payloads to extract data from the database.

3. **Data Extraction:** By iteratively querying the database and observing the responses, the attacker was able to extract sensitive information such as Social Security numbers and bank account details.

This example highlights the importance of properly configuring security controls and regularly testing for vulnerabilities to prevent such breaches.

---
<!-- nav -->
[[API Security/11-SQL Injection/02-Blind SQL Injection Part 1/02-Introduction to SQL Injection|Introduction to SQL Injection]] | [[API Security/11-SQL Injection/02-Blind SQL Injection Part 1/00-Overview|Overview]]
