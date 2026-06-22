---
course: API Security
topic: SQL Injection
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain how you would identify if a JSON-based API endpoint is vulnerable to blind SQL injection.**

To identify if a JSON-based API endpoint is vulnerable to blind SQL injection, you need to test various inputs to see if they cause unexpected behavior or errors. Here’s how you can do it:

1. **Capture the Request**: Use a tool like Burp Suite to capture the request being sent to the API endpoint.
2. **Modify Parameters**: Inject payloads such as single quotes (`'`), backslashes (`\`), or SQL keywords like `ORDER BY`, `AND`, `OR`, etc., into the JSON payload.
3. **Observe Responses**: Look for differences in the responses. For example, if injecting a single quote causes a SQL syntax error, it indicates that the input is being used in a SQL query.
4. **Test with Conditional Statements**: Try using conditional statements like `AND 1=1` or `AND 1=2`. If the response changes based on the truth value of the condition, it suggests a vulnerability.

For instance, consider the following JSON payload:
```json
{
  "id": 95,
  "name": "test",
  "description": "test description",
  "price": 100
}
```
Inject a single quote into the `name` field:
```json
{
  "id": 95,
  "name": "test'",
  "description": "test description",
  "price": 100
}
```
If this results in an error message indicating a SQL syntax problem, the endpoint is likely vulnerable to SQL injection.

**Q2. How would you exploit a blind SQL injection vulnerability in an API endpoint that uses JSON payloads?**

Exploiting a blind SQL injection vulnerability in an API endpoint that uses JSON payloads involves crafting specific payloads to extract information from the database. Here’s a step-by-step process:

1. **Identify Vulnerable Parameters**: Determine which parameters in the JSON payload are vulnerable to SQL injection.
2. **Use Conditional Statements**: Craft payloads that leverage conditional statements to infer information. For example, use `AND` or `OR` conditions to check if certain conditions are met.

Example payload to check if the `id` is greater than 50:
```json
{
  "id": "95 AND 1=IF(ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1))>50,1,0)",
  "name": "test",
  "description": "test description",
  "price": 100
}
```

3. **Binary Search**: Use binary search techniques to narrow down the characters of the extracted data. For instance, check if the ASCII value of the first character is between 65 and 90 (uppercase letters).

Example payload to check if the first character is uppercase:
```json
{
  "id": "95 AND 1=IF(ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1)) BETWEEN 65 AND 90,1,0)",
  "name": "test",
  "description": "test description",
  "price": 100
}
```

4. **Iterate and Extract Data**: Continue this process iteratively to extract the entire string.

**Q3. What recent real-world examples or CVEs demonstrate the impact of blind SQL injection vulnerabilities in APIs?**

One notable example is the **CVE-2021-21972**, which affected the WordPress REST API. This vulnerability allowed attackers to inject malicious SQL queries through the API endpoints, potentially leading to unauthorized access to sensitive data.

In this case, the vulnerability was present in the `wp-json/wp/v2/posts` endpoint. Attackers could craft specific requests to inject SQL commands and manipulate the database.

Another example is the **CVE-2020-14882**, which affected the Magento e-commerce platform. This vulnerability allowed attackers to exploit SQL injection in the GraphQL API, potentially leading to data exfiltration and unauthorized actions.

These examples highlight the importance of securing API endpoints against SQL injection attacks, especially in JSON-based APIs where data structures can be complex and dynamic.

**Q4. How would you configure an API endpoint to prevent blind SQL injection attacks?**

To prevent blind SQL injection attacks on an API endpoint, follow these best practices:

1. **Input Validation**: Ensure that all input parameters are validated and sanitized. Use regular expressions or predefined patterns to validate input data.
2. **Parameterized Queries**: Use parameterized queries or prepared statements to separate SQL logic from user input. This ensures that user input is treated as data rather than executable code.
3. **Least Privilege Principle**: Run the database with the least privileges necessary. Avoid using administrative accounts for application-level database interactions.
4. **Error Handling**: Implement proper error handling to avoid leaking sensitive information through error messages. Return generic error messages to the client.
5. **Web Application Firewall (WAF)**: Deploy a WAF to filter out malicious requests before they reach the application. Configure the WAF to block known SQL injection patterns.
6. **Regular Audits and Testing**: Conduct regular security audits and penetration testing to identify and mitigate potential vulnerabilities.

By implementing these measures, you can significantly reduce the risk of blind SQL injection attacks on your API endpoints.

**Q5. How would you fix a blind SQL injection vulnerability in an API endpoint that uses JSON payloads?**

Fixing a blind SQL injection vulnerability in an API endpoint that uses JSON payloads involves several steps:

1. **Update Input Validation**: Ensure that all input fields in the JSON payload are properly validated and sanitized. Use libraries or frameworks that provide built-in validation mechanisms.
2. **Use Parameterized Queries**: Refactor the backend code to use parameterized queries or prepared statements. This ensures that user input is treated as data and not executable code.
3. **Implement Error Handling**: Modify error handling to return generic error messages to the client. Avoid exposing detailed error messages that could reveal underlying SQL structure.
4. **Review and Update Code**: Review the codebase to identify and fix similar vulnerabilities. Ensure that all database interactions are secure and follow best practices.
5. **Test the Fix**: After implementing the fixes, conduct thorough testing to ensure that the vulnerability has been resolved. Use automated tools and manual testing to verify the security of the API endpoint.

Example of refactoring code to use parameterized queries:
```python
import sqlite3

def get_product_info(product_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Use parameterized query
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    
    result = cursor.fetchone()
    conn.close()
    return result
```

By following these steps, you can effectively fix a blind SQL injection vulnerability in an API endpoint that uses JSON payloads.

---
<!-- nav -->
[[API Security/11-SQL Injection/03-Blind SQL Injection Part 2/07-Conclusion|Conclusion]] | [[API Security/11-SQL Injection/03-Blind SQL Injection Part 2/00-Overview|Overview]]
