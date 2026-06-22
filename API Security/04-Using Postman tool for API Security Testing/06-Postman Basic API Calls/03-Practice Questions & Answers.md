---
course: API Security
topic: Using Postman tool for API Security Testing
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain how to create a GET request in Postman and describe its purpose.**

To create a GET request in Postman, follow these steps:

1. Open Postman.
2. Click on the "New" button to create a new request.
3. Enter the URL of the endpoint you want to access, e.g., `https://www.google.com`.
4. Ensure the HTTP method is set to `GET`.
5. Click the "Send" button to execute the request.

The purpose of a GET request is to retrieve information from a server without causing any changes to the server's state. It is commonly used for fetching data such as web pages, API responses, etc.

**Q2. How do you add query parameters to a GET request in Postman? Provide an example.**

To add query parameters to a GET request in Postman:

1. After entering the base URL, click on the "Params" tab.
2. Add a key-value pair for each query parameter. For example, if you want to search for "Hackers Era" on Google, you might add a key `q` with the value `Hackers Era`.

Example:
- Key: `q`
- Value: `Hackers Era`

This would result in a URL like `https://www.google.com/search?q=Hackers+Era`.

**Q3. Describe the differences between GET and POST requests in terms of their usage and impact on server state.**

GET and POST requests differ in their usage and impact on server state:

- **GET Request**: Used to retrieve information from a server. It does not cause any changes to the server's state. Data is sent via the URL, which can be bookmarked or shared easily. Example: Fetching a webpage or API data.

- **POST Request**: Used to submit data to be processed by the server. It can modify the server's state by creating, updating, or deleting resources. Data is sent in the body of the request, which is not visible in the URL. Example: Submitting a form, uploading files, or creating a new user account.

**Q4. How do you construct a POST request in Postman to send JSON data to a server? Provide an example.**

To construct a POST request in Postman to send JSON data:

1. Enter the URL of the endpoint you want to send data to, e.g., `https://jsonplaceholder.typicode.com/posts`.
2. Set the HTTP method to `POST`.
3. Go to the "Body" tab and select "raw".
4. Choose "JSON" from the dropdown menu.
5. Enter the JSON data you want to send. For example:

```json
{
  "title": "foo",
  "body": "bar",
  "userId": 1
}
```

6. Click the "Send" button to execute the request.

**Q5. What is the significance of the response status codes 200 and 201 in the context of GET and POST requests?**

- **200 OK**: Indicates that the request has succeeded and the server has returned the requested data. Commonly seen in GET requests.
  
- **201 Created**: Indicates that the request has been fulfilled and has resulted in the creation of a new resource. Typically seen in POST requests where a new resource is created on the server.

**Q6. How can you validate the JSON payload sent in a POST request using a JSON formatter tool?**

To validate the JSON payload:

1. Use a JSON formatter tool like `jsonformatter.org` or `jsonlint.com`.
2. Copy the JSON payload you want to send.
3. Paste the JSON into the formatter tool.
4. The tool will highlight any syntax errors or issues with the JSON structure.
5. Correct the JSON payload based on the feedback from the tool before sending it in the POST request.

**Q7. Discuss a recent real-world example where improper handling of API requests led to security vulnerabilities.**

A notable example is the Capital One data breach in 2019 (CVE-2019-11216). The breach occurred due to misconfigured API endpoints that allowed unauthorized access to sensitive customer data. The attacker exploited a vulnerability in the WAF (Web Application Firewall) configuration, which failed to properly restrict access to certain API endpoints. This highlights the importance of securing API endpoints and validating input to prevent unauthorized access and data breaches.

---
<!-- nav -->
[[API Security/04-Using Postman tool for API Security Testing/06-Postman Basic API Calls/02-Introduction to Postman for API Security Testing|Introduction to Postman for API Security Testing]] | [[API Security/04-Using Postman tool for API Security Testing/06-Postman Basic API Calls/00-Overview|Overview]]
