---
course: API Security
topic: SQL Injection
tags: [api-security]
---

## Understanding the Attack Vector

### User Input Validation

The primary cause of SQL Injection is the failure to properly validate user input. Applications should ensure that all user-provided data is sanitized and validated before being used in SQL queries.

### Example Attack

Let's consider the scenario described in the lecture. Suppose we have an API endpoint that accepts a `post_id` and `user_id` as parameters. The application constructs an SQL query based on these parameters:

```http
GET /api/posts?post_id=1&user_id=1
```

The corresponding SQL query might look like this:

```sql
SELECT * FROM posts WHERE post_id = 1 AND user_id = 1;
```

An attacker could attempt to inject SQL commands by modifying the `post_id` parameter:

```http
GET /api/posts?post_id=1' OR '1'='1&user_id=1
```

This would result in the following SQL query:

```sql
SELECT * FROM posts WHERE post_id = 1' OR '1'='1 AND user_id = 1;
```

The condition `'1'='1'` is always true, which could allow the attacker to bypass authentication or retrieve unauthorized data.

### Single Quotes and Comments

In the lecture, the instructor mentions using single quotes (`'`) and comments (`--`). These are common techniques used in SQL Injection attacks.

- **Single Quotes**: Used to terminate a string in SQL. For example, `' OR '1'='1` terminates the original string and introduces a new condition.
- **Comments**: Used to ignore the rest of the SQL statement. For example, `--` starts a comment, effectively ignoring any remaining SQL code.

### Full HTTP Request and Response

Here is a complete example of an HTTP request and response for a SQL Injection attack:

```http
GET /api/posts?post_id=1' OR '1'='1&user_id=1 HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: */*
```

Response:

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: application/json
Content-Length: 1234

{
  "posts": [
    {
      "id": 1,
      "title": "Example Post",
      "content": "This is an example post."
    },
    {
      "id": 2,
      "title": "Another Post",
      "content": "This is another example post."
    }
  ]
}
```

### Common Pitfalls

- **Improper Input Validation**: Failing to validate user input can lead to SQL Injection.
- **Concatenating Strings**: Directly concatenating user input into SQL queries is a common mistake.
- **Using Deprecated Functions**: Using deprecated functions like `mysql_query()` instead of prepared statements can increase vulnerability.

---
<!-- nav -->
[[API Security/11-SQL Injection/04-SQL Injection/03-How to Prevent  Defend Against SQL Injection|How to Prevent  Defend Against SQL Injection]] | [[API Security/11-SQL Injection/04-SQL Injection/00-Overview|Overview]] | [[API Security/11-SQL Injection/04-SQL Injection/05-Conclusion|Conclusion]]
