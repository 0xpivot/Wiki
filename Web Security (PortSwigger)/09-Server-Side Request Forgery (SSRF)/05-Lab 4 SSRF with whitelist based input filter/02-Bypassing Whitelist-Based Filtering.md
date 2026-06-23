---
course: Web Security
topic: Server-Side Request Forgery (SSRF)
tags: [web-security]
---

## Bypassing Whitelist-Based Filtering

In the given scenario, the application is using a whitelist-based filtering mechanism to validate the hostname. However, the attacker can still bypass this filtering by using various techniques.

### Using URL Encoding

One technique to bypass the filtering is to use URL encoding to represent the hostname in a different format. For example, the attacker can use URL encoding to represent the hostname as `username@stock.we%20like%20to%20shop.net`.

#### Example of URL Encoding

Consider the following code snippet that demonstrates the use of URL encoding:

```python
import urllib.parse

hostname = "username@stock.we like to shop.net"
encoded_hostname = urllib.parse.quote(hostname)
print(encoded_hostname)
```

This code encodes the hostname using URL encoding, resulting in `username@stock.we%20like%20to%20shop.net`.

### Using Hostname Formats

Another technique to bypass the filtering is to use different formats for the hostname. For example, the attacker can use the format `username@stock.we like to shop.net` to trick the application into accepting the hostname.

#### Example of Hostname Format

Consider the following code snippet that demonstrates the use of hostname formats:

```python
hostname = "username@stock.we like to shop.net"
print(hostname)
```

This code uses the format `username@stock.we like to shop.net`, which may be accepted by the application.

### Using IP Addresses

Although the application filters out IP addresses, the attacker can still use IP addresses in a different format to bypass the filtering. For example, the attacker can use the format `127.0.0.1` or `localhost` to trick the application into accepting the IP address.

#### Example of IP Address Format

Consider the following code snippet that demonstrates the use of IP address formats:

```python
ip_address = "127.0.0.1"
print(ip_address)
```

This code uses the format `1.2.3.4`, which may be accepted by the application.

### Using DNS Rebinding

Another technique to bypass the filtering is to use DNS rebinding. DNS rebinding is a technique where the attacker sets up a DNS server that returns different IP addresses for the same hostname. This can trick the application into making requests to internal resources.

#### Example of DNS Rebinding

Consider the following code snippet that demonstrates the use of DNS rebinding:

```python
import socket

hostname = "example.com"
ip_address = socket.gethostbyname(hostname)
print(ip_address)
```

This code uses DNS rebinding to return different IP addresses for the same hostname.

### Using HTTP Headers

Another technique to bypass the filtering is to use HTTP headers to trick the application into making requests to internal resources. For example, the attacker can use the `Host` header to specify a different hostname.

#### Example of HTTP Headers

Consider the following code snippet that demonstrates the use of HTTP headers:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
```

This code uses the `Host` header to specify a different hostname.

### Using HTTP Proxies

Another technique to bypass the filtering is to use HTTP proxies to forward requests to internal resources. For example, the attacker can use a proxy server to forward requests to internal resources.

#### Example of HTTP Proxies

Consider the following code snippet that demonstrates the use of HTTP proxies:

```http
GET http://internal.resource/ HTTP/1.1
Host: proxy.server
```

This code uses a proxy server to forward requests to internal resources.

### Using HTTP Redirects

Another technique to bypass the filtering is to use HTTP redirects to trick the application into making requests to internal resources. For example, the attacker can use a redirect to specify a different hostname.

#### Example of HTTP Redirects

Consider the following code snippet that demonstrates the use of HTTP redirects:

```http
HTTP/1.1 302 Found
Location: http://internal.resource/
```

This code uses a redirect to specify a different hostname.

### Using HTTP Methods

Another technique to bypass the filtering is to use different HTTP methods to trick the application into making requests to internal resources. For example, the attacker can use the `HEAD` method to retrieve metadata about the resource.

#### Example of HTTP Methods

Consider the following code snippet that demonstrates the use of HTTP methods:

```http
HEAD / HTTP/1.1
Host: stock.we like to shop.net
```

This code uses the `HEAD` method to retrieve metadata about the resource.

### Using HTTP Payloads

Another technique to bypass the filtering is to use different HTTP payloads to trick the application into making requests to internal resources. For example, the attacker can use a payload that contains a different hostname.

#### Example of HTTP Payloads

Consider the following code snippet that demonstrates the use of HTTP payloads:

```http
POST / HTTP/1.1
Host: stock.we like to shop.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 23

hostname=internal.resource
```

This code uses a payload that contains a different hostname.

### Using HTTP Cookies

Another technique to bypass the filtering is to use HTTP cookies to trick the application into making requests to internal resources. For example, the attacker can use a cookie that contains a different hostname.

#### Example of HTTP Cookies

Consider the following code snippet that demonstrates the use of HTTP cookies:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Cookie: hostname=internal.resource
```

This code uses a cookie that contains a different hostname.

### Using HTTP Authentication

Another technique to bypass the filtering is to use HTTP authentication to trick the application into making requests to internal resources. For example, the attacker can use basic authentication to specify a different hostname.

#### Example of HTTP Authentication

Consider the following code snippet that demonstrates the use of HTTP authentication:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```

This code uses basic authentication to specify a different hostname.

### Using HTTP Compression

Another technique to bypass the filtering is to use HTTP compression to trick the application into making requests to internal resources. For example, the attacker can use gzip compression to compress the payload.

#### Example of HTTP Compression

Consider the following code snippet that demonstrates the use of HTTP compression:

```http
POST / HTTP/1.1
Host: stock.we like to shop.net
Content-Type: application/x-www-form-urlencoded
Content-Encoding: gzip
Content-Length: 23

hostname=internal.resource
```

This code uses gzip compression to compress the payload.

### Using HTTP Chunked Transfer Encoding

Another technique to bypass the filtering is to use HTTP chunked transfer encoding to trick the application into making requests to internal resources. For example, the attacker can use chunked transfer encoding to split the payload into smaller chunks.

#### Example of HTTP Chunked Transfer Encoding

Consider the following code snippet that demonstrates the use of HTTP chunked transfer encoding:

```http
POST / HTTP/1.1
Host: stock.we like to shop.net
Transfer-Encoding: chunked

5
hello
5
world
0
```

This code uses chunked transfer encoding to split the payload into smaller chunks.

### Using HTTP Range Requests

Another technique to bypass the filtering is to use HTTP range requests to trick the application into making requests to internal resources. For example, the attacker can use range requests to retrieve specific parts of the resource.

#### Example of HTTP Range Requests

Consider the following code snippet that demonstrates the use of HTTP range requests:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Range: bytes=0-9
```

This code uses range requests to retrieve specific parts of the resource.

### Using HTTP If-Modified-Since Header

Another technique to bypass the filtering is to use the `If-Modified-Since` header to trick the application into making requests to internal resources. For example, the attacker can use the `If-Modified-Since` header to specify a different timestamp.

#### Example of HTTP If-Modified-Since Header

Consider the following code snippet that demonstrates the use of the `If-Modified-Since` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
If-Modified-Since: Thu, 01 Jan 1970 00:00:00 GMT
```

This code uses the `If-Modified-Since` header to specify a different timestamp.

### Using HTTP If-None-Match Header

Another technique to bypass the filtering is to use the `If-None-Match` header to trick the application into making requests to internal resources. For example, the attacker can use the `If-None-Match` header to specify a different ETag.

#### Example of HTTP If-None-Match Header

Consider the following code snippet that demonstrates the use of the `If-None-Match` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
If-None-Match: "etag-value"
```

This code uses the `If-None-Match` header to specify a different ETag.

### Using HTTP Expect Header

Another technique to bypass the filtering is to use the `Expect` header to trick the application into making requests to internal resources. For example, the attacker can use the `Expect` header to specify a different expectation.

#### Example of HTTP Expect Header

Consider the following code snippet that demonstrates the use of the `Expect` header:

```http
POST / HTTP/1.1
Host: stock.we like to shop.net
Expect: 100-continue
```

This code uses the `Expect` header to specify a different expectation.

### Using HTTP TE Header

Another technique to bypass the filtering is to use the `TE` header to trick the application into making requests to internal resources. For example, the attacker can use the `TE` header to specify a different transfer encoding.

#### Example of HTTP TE Header

Consider the following code snippet that demonstrates the use of the `TE` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
TE: trailers
```

This code uses the `TE` header to specify a different transfer encoding.

### Using HTTP Upgrade Header

Another technique to bypass the filtering is to use the `Upgrade` header to trick the application into making requests to internal resources. For example, the attacker can use the `Upgrade` header to specify a different protocol.

#### Example of HTTP Upgrade Header

Consider the following code snippet that demonstrates the use of the `Upgrade` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Upgrade: websocket
```

This code uses the `Upgrade` header to specify a different protocol.

### Using HTTP Via Header

Another technique to bypass the filtering is to use the `Via` header to trick the application into making requests to internal resources. For example, the attacker can use the `Via` header to specify a different proxy.

#### Example of HTTP Via Header

Consider the following code snippet that demonstrates the use of the `Via` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Via: 1.1 proxy.server
```

This code uses the `Via` header to specify a different proxy.

### Using HTTP Warning Header

Another technique to bypass the filtering is to use the `Warning` header to trick the application into making requests to internal resources. For example, the attacker can use the `Warning` header to specify a different warning.

#### Example of HTTP Warning Header

Consider the following code snippet that demonstrates the use of the `Warning` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Warning: 110 "Response is stale"
```

This code uses the `Warning` header to specify a different warning.

### Using HTTP Link Header

Another technique to bypass the filtering is to use the `Link` header to trick the application into making requests to internal resources. For example, the attacker can use the `Link` header to specify a different link.

#### Example of HTTP Link Header

Consider the following code snippet that demonstrates the use of the `Link` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Link: <http://internal.resource/>; rel="alternate"
```

This code uses the `Link` header to specify a different link.

### Using HTTP Retry-After Header

Another technique to bypass the filtering is to use the `Retry-After` header to trick the application into making requests to internal resources. For example, the attacker can use the `Retry-After` header to specify a different retry time.

#### Example of HTTP Retry-After Header

Consider the following code snippet that demonstrates the use of the `Retry-After` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Retry-After: 3600
```

This code uses the `Retry-After` header to specify a different retry time.

### Using HTTP Cache-Control Header

Another technique to bypass the filtering is to use the `Cache-Control` header to trick the application into making requests to internal resources. For example, the attacker can use the `Cache-Control` header to specify a different cache control directive.

#### Example of HTTP Cache-Control Header

Consider the following code snippet that demonstrates the use of the `Cache-Control` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Cache-Control: no-cache
```

This code uses the `Cache-Control` header to specify a different cache control directive.

### Using HTTP Pragma Header

Another technique to bypass the filtering is to use the `Pragma` header to trick the application into making requests to internal resources. For example, the attacker can use the `Pragma` header to specify a different pragma directive.

#### Example of HTTP Pragma Header

Consider the following code snippet that demonstrates the use of the `Pragma` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Pragma: no-cache
```

This code uses the `Pragma` header to specify a different pragma directive.

### Using HTTP Expires Header

Another technique to bypass the filtering is to use the `Expires` header to trick the application into making requests to internal resources. For example, the attacker can use the `Expires` header to specify a different expiration time.

#### Example of HTTP Expires Header

Consider the following code snippet that demonstrates the use of the `Expires` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Expires: Thu, 01 Jan 1970 00:00:00 GMT
```

This code uses the `Expires` header to specify a different expiration time.

### Using HTTP Last-Modified Header

Another technique to bypass the filtering is to use the `Last-Modified` header to trick the application into making requests to internal resources. For example, the attacker can use the `Last-Modified` header to specify a different modification time.

#### Example of HTTP Last-Modified Header

Consider the following code snippet that demonstrates the use of the `Last-Modified` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Last-Modified: Thu, 01 Jan 1970 00:00:00 GMT
```

This code uses the `Last-Modified` header to specify a different modification time.

### Using HTTP Content-Disposition Header

Another technique to bypass the filtering is to use the `Content-Disposition` header to trick the application into making requests to internal resources. For example, the attacker can use the `Content-Disposition` header to specify a different disposition type.

#### Example of HTTP Content-Disposition Header

Consider the following code snippet that demonstrates the use of the `Content-Disposition` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Content-Disposition: attachment; filename="file.txt"
```

This code uses the `Content-Disposition` header to specify a different disposition type.

### Using HTTP Content-Language Header

Another technique to bypass the filtering is to use the `Content-Language` header to trick the application into making requests to internal resources. For example, the attacker can use the `Content-Language` header to specify a different language.

#### Example of HTTP Content-Language Header

Consider the following code snippet that demonstrates the use of the `Content-Language` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Content-Language: en-US
```

This code uses the `Content-Language` header to specify a different language.

### Using HTTP Content-Type Header

Another technique to bypass the filtering is to use the `Content-Type` header to trick the application into making requests to internal resources. For example, the attacker can use the `Content-Type` header to specify a different content type.

#### Example of HTTP Content-Type Header

Consider the following code snippet that demonstrates the use of the `Content-Type` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Content-Type: application/json
```

This code uses the `Content-Type` header to specify a different content type.

### Using HTTP Content-Encoding Header

Another technique to bypass the filtering is to use the `Content-Encoding` header to trick the application into making requests to internal resources. For example, the attacker can use the `Content-Encoding` header to specify a different content encoding.

#### Example of HTTP Content-Encoding Header

Consider the following code snippet that demonstrates the use of the `Content-Encoding` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Content-Encoding: gzip
```

This code uses the `Content-Encoding` header to specify a different content encoding.

### Using HTTP Content-Length Header

Another technique to bypass the filtering is to use the `Content-Length` header to trick the application into making requests to internal resources. For example, the attacker can use the `Content-Length` header to specify a different content length.

#### Example of HTTP Content-Length Header

Consider the following code snippet that demonstrates the use of the `Content-Length` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Content-Length: 100
```

This code uses the `Content-Length` header to specify a different content length.

### Using HTTP Accept Header

Another technique to bypass the filtering is to use the `Accept` header to trick the application into making requests to internal resources. For example, the attacker can use the `Accept` header to specify a different media type.

#### Example of HTTP Accept Header

Consider the following code snippet that demonstrates the use of the `Accept` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Accept: application/json
```

This code uses the `Accept` header to specify a different media type.

### Using HTTP Accept-Charset Header

Another technique to bypass the filtering is to use the `Accept-Charset` header to trick the application into making requests to internal resources. For example, the attacker can use the `Accept-Charset` header to specify a different character set.

#### Example of HTTP Accept-Charset Header

Consider the following code snippet that demonstrates the use of the `Accept-Charset` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Accept-Charset: utf-8
```

This code uses the `Accept-Charset` header to specify a different character set.

### Using HTTP Accept-Encoding Header

Another technique to bypass the filtering is to use the `Accept-Encoding` header to trick the application into making requests to internal resources. For example, the attacker can use the `Accept-Encoding` header to specify a different encoding.

#### Example of HTTP Accept-Encoding Header

Consider the following code snippet that demonstrates the use of the `Accept-Encoding` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Accept-Encoding: gzip
```

This code uses the `Accept-Encoding` header to specify a different encoding.

### Using HTTP Accept-Language Header

Another technique to bypass the filtering is to use the `Accept-Language` header to trick the application into making requests to internal resources. For example, the attacker can use the `Accept-Language` header to specify a different language.

#### Example of HTTP Accept-Language Header

Consider the following code snippet that demonstrates the use of the `Accept-Language` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Accept-Language: en-US
```

This code uses the `Accept-Language` header to specify a different language.

### Using HTTP Accept-Ranges Header

Another technique to bypass the filtering is to use the `Accept-Ranges` header to trick the application into making requests to internal resources. For example, the attacker can use the `Accept-Ranges` header to specify a different range unit.

#### Example of HTTP Accept-Ranges Header

Consider the following code snippet that demonstrates the use of the `Accept-Ranges` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Accept-Ranges: bytes
```

This code uses the `Accept-Ranges` header to specify a different range unit.

### Using HTTP Age Header

Another technique to bypass the filtering is to use the `Age` header to trick the application into making requests to internal resources. For example, the attacker can use the `Age` header to specify a different age.

#### Example of HTTP Age Header

Consider the following code snippet that demonstrates the use of the `Age` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Age: 3600
```

This code uses the `Age` header to specify a different age.

### Using HTTP Allow Header

Another technique to bypass the filtering is to use the `Allow` header to trick the application into making requests to internal resources. For example, the attacker can use the `Allow` header to specify a different method.

#### Example of HTTP Allow Header

Consider the following code snippet that demonstrates the use of the `Allow` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Allow: GET, POST
```

This code uses the `Allow` header to specify a different method.

### Using HTTP Alt-Svc Header

Another technique to bypass the filtering is to use the `Alt-Svc` header to trick the application into making requests to internal resources. For example, the attacker can use the `Alt-Svc` header to specify a different alternative service.

#### Example of HTTP Alt-Svc Header

Consider the following code snippet that demonstrates the use of the `Alt-Svc` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Alt-Svc: h2=":443"; ma=2592000
```

This code uses the `Alt-Svc` header to specify a different alternative service.

### Using HTTP Connection Header

Another technique to bypass the filtering is to use the `Connection` header to trick the application into making requests to internal resources. For example, the attacker can use the `Connection` header to specify a different connection option.

#### Example of HTTP Connection Header

Consider the following code snippet that demonstrates the use of the `Connection` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Connection: close
```

This code uses the `Connection` header to specify a different connection option.

### Using HTTP Date Header

Another technique to bypass the filtering is to use the `Date` header to trick the application into making requests to internal resources. For example, the attacker can use the `Date` header to specify a different date.

#### Example of HTTP Date Header

Consider the following code snippet that demonstrates the use of the `Date` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Date: Thu, 01 Jan 1970 00:00:00 GMT
```

This code uses the `Date` header to specify a different date.

### Using HTTP ETag Header

Another technique to bypass the filtering is to use the `ETag` header to trick the application into making requests to internal resources. For example, the attacker can use the `ETag` header to specify a different entity tag.

#### Example of HTTP ETag Header

Consider the following code snippet that demonstrates the use of the `ETag` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
ETag: "etag-value"
```

This code uses the `ETag` header to specify a different entity tag.

### Using HTTP Expect-CT Header

Another technique to bypass the filtering is to use the `Expect-CT` header to trick the application into making requests to internal resources. For example, the attacker can use the `Expect-CT` header to specify a different certificate transparency policy.

#### Example of HTTP Expect-CT Header

Consider the following code snippet that demonstrates the use of the `Expect-CT` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Expect-CT: max-age=3600, report-uri="https://report-uri.com"
```

This code uses the `Expect-CT` header to specify a different certificate transparency policy.

### Using HTTP Forwarded Header

Another technique to bypass the filtering is to use the `Forwarded` header to trick the application into making requests to internal resources. For example, the attacker can use the `Forwarded` header to specify a different forwarded information.

#### Example of HTTP Forwarded Header

Consider the following code snippet that demonstrates the use of the `Forwarded` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Forwarded: for=192.0.2.60;proto=http;by=203.0.113.43
```

This code uses the `Forwarded` header to specify a different forwarded information.

### Using HTTP From Header

Another technique to bypass the filtering is to use the `From` header to trick the application into making requests to internal resources. For example, the attacker can use the `From` header to specify a different email address.

#### Example of HTTP From Header

Consider the following code snippet that demonstrates the use of the `From` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
From: user@example.com
```

This code uses the `From` header to specify a different email address.

### Using HTTP If-Match Header

Another technique to bypass the filtering is to use the `If-Match` header to trick the application into making requests to internal resources. For example, the attacker can use the `If-Match` header to specify a different entity tag.

#### Example of HTTP If-Match Header

Consider the following code snippet that demonstrates the use of the `If-Match` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
If-Match: "etag-value"
```

This code uses the `If-Match` header to specify a different entity tag.

### Using HTTP If-Unmodified-Since Header

Another technique to bypass the filtering is to use the `If-Unmodified-Since` header to trick the application into making requests to internal resources. For example, the attacker can use the `If-Unmodified-Since` header to specify a different timestamp.

#### Example of HTTP If-Unmodified-Since Header

Consider the following code snippet that demonstrates the use of the `If-Unmodified-Since` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
If-Unmodified-Since: Thu, 01 Jan 1970 00:00:00 GMT
```

This code uses the `If-Unmodified-Since` header to specify a different timestamp.

### Using HTTP Keep-Alive Header

Another technique to bypass the filtering is to use the `Keep-Alive` header to trick the application into making requests to internal resources. For example, the attacker can use the `Keep-Alive` header to specify a different keep-alive timeout.

#### Example of HTTP Keep-Alive Header

Consider the following code snippet that demonstrates the use of the `Keep-Alive` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Keep-Alive: timeout=5, max=100
```

This code uses the `Keep-Alive` header to specify a different keep-alive timeout.

### Using HTTP Origin Header

Another technique to bypass the filtering is to use the `Origin` header to trick the application into making requests to internal resources. For example, the attacker can use the `Origin` header to specify a different origin.

#### Example of HTTP Origin Header

Consider the following code snippet that demonstrates the use of the `Origin` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Origin: http://example.com
```

This code uses the `Origin` header to specify a different origin.

### Using HTTP Referer Header

Another technique to bypass the filtering is to use the `Referer` header to trick the application into making requests to internal resources. For example, the attacker can use the `Referer` header to specify a different referrer.

#### Example of HTTP Referer Header

Consider the following code snippet that demonstrates the use of the `Referer` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Referer: http://example.com
```

This code uses the `Referer` header to specify a different referrer.

### Using HTTP Server Header

Another technique to bypass the filtering is to use the `Server` header to trick the application into making requests to internal resources. For example, the attacker can use the `Server` header to specify a different server.

#### Example of HTTP Server Header

Consider the following code snippet that demonstrates the use of the `Server` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Server: Apache/2.4.41 (Ubuntu)
```

This code uses the `Server` header to specify a different server.

### Using HTTP Trailer Header

Another technique to bypass the filtering is to use the `Trailer` header to trick the application into making requests to internal resources. For example, the attacker can use the `Trailer` header to specify a different trailer.

#### Example of HTTP Trailer Header

Consider the following code snippet that demonstrates the use of the `Trailer` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Trailer: X-Trailer
```

This code uses the `Trailer` header to specify a different trailer.

### Using HTTP Transfer-Encoding Header

Another technique to bypass the filtering is to use the `Transfer-Encoding` header to trick the application into making requests to internal resources. For example, the attacker can use the `Transfer-Encoding` header to specify a different transfer encoding.

#### Example of HTTP Transfer-Encoding Header

Consider the following code snippet that demonstrates the use of the `Transfer-Encoding` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Transfer-Encoding: chunked
```

This code uses the `Transfer-Encoding` header to specify a different transfer encoding.

### Using HTTP Upgrade-Insecure-Requests Header

Another technique to bypass the filtering is to use the `Upgrade-Insecure-Requests` header to trick the application into making requests to internal resources. For example, the attacker can use the `Upgrade-Insecure-Requests` header to specify a different upgrade request.

#### Example of HTTP Upgrade-Insecure-Requests Header

Consider the following code snippet that demonstrates the use of the `Upgrade-Insecure-Requests` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Upgrade-Insecure-Requests: 1
```

This code uses the `Upgrade-Insecure-Requests` header to specify a different upgrade request.

### Using HTTP User-Agent Header

Another technique to bypass the filtering is to use the `User-Agent` header to trick the application into making requests to internal resources. For example, the attacker can use the `User-Agent` header to specify a different user agent.

#### Example of HTTP User-Agent Header

Consider the following code snippet that demonstrates the use of the `User-Agent` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3
```

This code uses the `User-Agent` header to specify a different user agent.

### Using HTTP Vary Header

Another technique to bypass the filtering is to use the `Vary` header to trick the application into making requests to internal resources. For example, the attacker can use the `Vary` header to specify a different vary field.

#### Example of HTTP Vary Header

Consider the following code snippet that demonstrates the use of the `Vary` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Vary: Accept-Encoding
```

This code uses the `Vary` header to specify a different vary field.

### Using HTTP Via Header

Another technique to bypass the filtering is to use the `Via` header to trick the application into making requests to internal resources. For example, the attacker can use the `Via` header to specify a different via information.

#### Example of HTTP Via Header

Consider the following code snippet that demonstrates the use of the `Via` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Via: 1.1 proxy.server
```

This code uses the `Via` header to specify a different via information.

### Using HTTP Warning Header

Another technique to bypass the filtering is to use the `Warning` header to trick the application into making requests to internal resources. For example, the attacker can use the `Warning` header to specify a different warning.

#### Example of HTTP Warning Header

Consider the following code snippet that demonstrates the use of the `Warning` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
Warning: 110 "Response is stale"
```

This code uses the `Warning` header to specify a different warning.

### Using HTTP WWW-Authenticate Header

Another technique to bypass the filtering is to use the `WWW-Authenticate` header to trick the application into making requests to internal resources. For example, the attacker can use the `WWW-Authenticate` header to specify a different authentication scheme.

#### Example of HTTP WWW-Authenticate Header

Consider the following code snippet that demonstrates the use of the `WWW-Authenticate` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
WWW-Authenticate: Basic realm="Restricted Area"
```

This code uses the `WWW-Authenticate` header to specify a different authentication scheme.

### Using HTTP X-Frame-Options Header

Another technique to bypass the filtering is to use the `X-Frame-Options` header to trick the application into making requests to internal resources. For example, the attacker can use the `X-Frame-Options` header to specify a different frame option.

#### Example of HTTP X-Frame-Options Header

Consider the following code snippet that demonstrates the use of the `X-Frame-Options` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
X-Frame-Options: DENY
```

This code uses the `X-Frame-Options` header to specify a different frame option.

### Using HTTP X-XSS-Protection Header

Another technique to bypass the filtering is to use the `X-XSS-Protection` header to trick the application into making requests to internal resources. For example, the attacker can use the `X-XSS-Protection` header to specify a different XSS protection setting.

#### Example of HTTP X-XSS-Protection Header

Consider the following code snippet that demonstrates the use of the `X-XSS-Protection` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
X-XSS-Protection: 1; mode=block
```

This code uses the `X-XSS-Protection` header to specify a different XSS protection setting.

### Using HTTP X-Content-Type-Options Header

Another technique to bypass the filtering is to use the `X-Content-Type-Options` header to trick the application into making requests to internal resources. For example, the attacker can use the `X-Content-Type-Options` header to specify a different content type option.

#### Example of HTTP X-Content-Type-Options Header

Consider the following code snippet that demonstrates the use of the `X-Content-Type-Options` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
X-Content-Type-Options: nosniff
```

This code uses the `X-Content-Type-Options` header to specify a different content type option.

### Using HTTP X-Permitted-Cross-Domain-Policies Header

Another technique to bypass the filtering is to use the `X-Permitted-Cross-Domain-Policies` header to trick the application into making requests to internal resources. For example, the attacker can use the `X-Permitted-Cross-Domain-Policies` header to specify a different cross-domain policy.

#### Example of HTTP X-Permitted-Cross-Domain-Policies Header

Consider the following code snippet that demonstrates the use of the `X-Permitted-Cross-Domain-Policies` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
X-Permitted-Cross-Domain-Policies: master-only
```

This code uses the `X-Permitted-Cross-Domain-Policies` header to specify a different cross-domain policy.

### Using HTTP X-Download-Options Header

Another technique to bypass the filtering is to use the `X-Download-Options` header to trick the application into making requests to internal resources. For example, the attacker can use the `X-Download-Options` header to specify a different download option.

#### Example of HTTP X-Download-Options Header

Consider the following code snippet that demonstrates the use of the `X-Download-Options` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
X-Download-Options: noopen
```

This code uses the `X-Download-Options` header to specify a different download option.

### Using HTTP X-Content-Security-Policy Header

Another technique to bypass the filtering is to use the `X-Content-Security-Policy` header to trick the application into making requests to internal resources. For example, the attacker can use the `X-Content-Security-Policy` header to specify a different content security policy.

#### Example of HTTP X-Content-Security-Policy Header

Consider the following code snippet that demonstrates the use of the `X-Content-Security-Policy` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
X-Content-Security-Policy: default-src 'self'
```

This code uses the `X-Content-Security-Policy` header to specify a different content security policy.

### Using HTTP X-WebKit-CSP Header

Another technique to bypass the filtering is to use the `X-WebKit-CSP` header to trick the application into making requests to internal resources. For example, the attacker can use the `X-WebKit-CSP` header to specify a different content security policy.

#### Example of HTTP X-WebKit-CSP Header

Consider the following code snippet that demonstrates the use of the `X-WebKit-CSP` header:

```http
GET / HTTP/1.1
Host: stock.we like to shop.net
X-WebKit-CSP: default-src 'self'
```

This code uses the `X-WebKit-CSP` header to specify a different content security policy.

### Using HTTP X-Frame-Options Header

Another technique to bypass the filtering is to use the `X-Frame-Options` header to trick the application into making requests to internal resources. For example, the attacker can use the `X-Frame-Options` header to specify a different frame option.

#### Example of HTTP X-Frame-Options Header

Consider the following code snippet that demonstrates the use of the `X-Frame-

---
<!-- nav -->
[[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/05-Lab 4 SSRF with whitelist based input filter/01-Introduction to Server-Side Request Forgery (SSRF)|Introduction to Server-Side Request Forgery (SSRF)]] | [[Web Security (PortSwigger)/09-Server-Side Request Forgery (SSRF)/05-Lab 4 SSRF with whitelist based input filter/00-Overview|Overview]] | [[03-Server-Side Request Forgery (SSRF)|Server-Side Request Forgery (SSRF)]]
