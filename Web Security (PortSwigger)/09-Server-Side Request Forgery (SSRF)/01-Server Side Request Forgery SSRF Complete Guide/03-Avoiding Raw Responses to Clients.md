---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Avoiding Raw Responses to Clients

### What is a Raw Response?

A raw response occurs when an application directly returns the content of a requested resource to the client without any processing or validation. This can expose sensitive information or allow unauthorized access to internal resources.

### Why Avoid Raw Responses?

Returning raw responses can lead to SSRF attacks where an attacker tricks the application into accessing internal resources and displaying their contents to the client. This can result in unauthorized access to sensitive data.

#### Example of a Raw Response

Consider a scenario where a user requests `http://localhost/admin`. If the application returns the raw content of this page, it exposes sensitive administrative functionality to the client.

### How to Implement Custom Responses

To avoid raw responses, implement custom responses that process and validate the requested content before returning it to the client.

#### Code Example

Here’s an example of how to handle a request and return a custom response in Python:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/proxy', methods=['GET'])
def proxy_request():
    url = request.args.get('url')
    
    if is_allowed_url(url):
        # Simulate fetching the content from the URL
        content = fetch_content_from_url(url)
        
        # Process and validate the content
        processed_content = process_content(content)
        
        # Return a custom response
        return jsonify({"content": processed_content})
    else:
        return jsonify({"error": "URL not allowed"}), 403

def fetch_content_from_url(url):
    # Simulate fetching content from the URL
    return f"Content from {url}"

def process_content(content):
    # Simulate processing the content
    return f"Processed: {content}"

# Example usage
if __name__ == '__main__':
    app.run(debug=True)
```

### Real-World Examples

The CVE-2021-21972 vulnerability in Jenkins again highlights the importance of avoiding raw responses. This vulnerability allowed attackers to bypass input validation and execute arbitrary commands, demonstrating the need for proper handling of responses.

### Pitfalls and Common Mistakes

- **Direct Access**: Allowing direct access to internal resources without proper validation can expose sensitive data.
- **Inconsistent Processing**: Failing to consistently process and validate responses can leave gaps in security.
- **Error Handling**: Improper error handling can reveal sensitive information about the application’s internal workings.

### How to Prevent / Defend

1. **Consistent Processing**: Ensure that all responses are processed and validated before being returned to the client.
2. **Error Handling**: Implement proper error handling to avoid revealing sensitive information.
3. **Logging and Monitoring**: Log and monitor access attempts to detect and respond to suspicious activity.

---
<!-- nav -->
[[02-What is an SSRF Vulnerability|What is an SSRF Vulnerability]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/01-Server Side Request Forgery SSRF Complete Guide/00-Overview|Overview]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/01-Server Side Request Forgery SSRF Complete Guide/04-Background Theory|Background Theory]]
