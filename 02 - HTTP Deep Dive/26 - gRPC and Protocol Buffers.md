---
tags: [vapt, http, api, web, intermediate]
difficulty: intermediate
module: "02 - HTTP Deep Dive"
topic: "02.26 gRPC and Protocol Buffers"
---

# 02.26 — gRPC and Protocol Buffers

## What is it?

**gRPC** (Google Remote Procedure Call) is a high-performance RPC framework that uses **Protocol Buffers (protobuf)** for serialization and **HTTP/2** for transport. Common in microservices architectures, mobile-to-server communication, and internal service-to-service calls.

---

## gRPC vs REST vs SOAP

```
                REST          SOAP          gRPC
Transport:      HTTP/1.1      HTTP/1.1      HTTP/2
Format:         JSON/XML      XML           Protocol Buffers (binary)
Schema:         OpenAPI       WSDL          .proto file
Streaming:      No            No            Yes (bidirectional!)
Performance:    Medium        Low           High
Human readable: Yes           Yes           No (binary)
Browser support: Yes          Yes           Limited (gRPC-web needed)
```

---

## Protocol Buffers (Protobuf)

```
1. Define schema in .proto file:
   syntax = "proto3";
   
   service UserService {
     rpc GetUser (GetUserRequest) returns (UserResponse);
     rpc CreateUser (CreateUserRequest) returns (UserResponse);
   }
   
   message GetUserRequest {
     int32 user_id = 1;
   }
   
   message UserResponse {
     int32 id = 1;
     string username = 2;
     string email = 3;
     string role = 4;
   }

2. Generate code from .proto:
   protoc --go_out=. service.proto
   protoc --python_out=. service.proto

3. Binary serialization:
   UserResponse{id: 1, username: "alice", role: "admin"}
   → Compact binary: 08 01 12 05 61 6c 69 63 65 ...
   (NOT human readable — requires proto schema to decode!)
```

---

## Security Context — gRPC in VAPT

### 1. Finding gRPC Services

```bash
# gRPC uses HTTP/2 with specific content-type:
# Content-Type: application/grpc

# Nmap detection:
nmap -sV -p 50051,50052,9090,9091 target.com
# 50051 = default gRPC port (but can be any port)

# Test if gRPC port exists:
curl -v --http2 https://target.com:50051 2>&1 | head -20
# If "application/grpc" in content-type → gRPC!

# grpcurl (curl for gRPC):
grpcurl -plaintext target.com:50051 list
# Lists all services (like OPTIONS for REST)

grpcurl -plaintext target.com:50051 list UserService
# Lists all methods in UserService

grpcurl -plaintext target.com:50051 describe UserService.GetUser
# Shows request/response types
```

### 2. gRPC Reflection — API Discovery

```bash
# If reflection is enabled → get full schema without .proto file!
grpcurl -plaintext target.com:50051 list
# UserService
# ProductService
# AdminService   ← found admin service!

grpcurl -plaintext target.com:50051 list AdminService
# AdminService.DeleteAllUsers
# AdminService.GetAllSecrets

# Try calling admin method without auth:
grpcurl -plaintext target.com:50051 AdminService.GetAllSecrets '{}'

# If reflection disabled:
# Try to find .proto files in:
# - JavaScript bundle (grpc-web)
# - Mobile app decompilation
# - GitHub repos
# - /proto/ or /protos/ endpoint on web server
```

### 3. gRPC Injection

```bash
# JSON-transcoded gRPC (common with gRPC-gateway):
# gRPC calls mapped to REST endpoints
# All REST injection attacks apply to transcoded parameters

# Direct gRPC injection via grpcurl:
# SQLi in string field:
grpcurl -d '{"username":"admin'"'"' OR '"'"'1'"'"'='"'"'1"}' \
  -plaintext target.com:50051 \
  UserService.GetUserByName

# Path traversal:
grpcurl -d '{"filename":"../../../etc/passwd"}' \
  -plaintext target.com:50051 \
  FileService.GetFile

# SSRF via URL field:
grpcurl -d '{"url":"http://169.254.169.254/latest/meta-data/"}' \
  -plaintext target.com:50051 \
  ProxyService.FetchURL
```

### 4. Burp Suite with gRPC

```
Burp Suite 2023+ supports gRPC with HTTP/2:

1. Set browser/client proxy to Burp (127.0.0.1:8080)
2. Enable HTTP/2 in Burp (default on)
3. gRPC traffic appears in HTTP history as binary content
4. Burp can decode protobuf if you provide .proto file

EXTENSION: "Protobuf Decoder" Burp extension
- Automatically detects and decodes protobuf messages
- Allows modification of decoded JSON → re-encode as protobuf → send

ALTERNATIVE: grpc-proxy
# Use mitmproxy with gRPC addon:
pip install mitmproxy-grpc
mitmweb --mode upstream --upstream-cert --ssl-insecure
```

### 5. gRPC Authentication Testing

```bash
# gRPC auth via metadata (headers):
grpcurl -H "Authorization: Bearer TOKEN" \
  -plaintext target.com:50051 \
  UserService.GetUser '{}'

# Test without auth:
grpcurl -plaintext target.com:50051 UserService.GetAllUsers '{}'
# If no auth required → unauthorized access!

# Test with invalid token:
grpcurl -H "Authorization: Bearer invalid" \
  -plaintext target.com:50051 \
  UserService.GetAllUsers '{}'
# Should return Unauthenticated, not 200 with data
```

---

## Hands-On: gRPC Testing Toolkit

```bash
# Install grpcurl
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest
# or: brew install grpcurl (macOS)

# List services (requires reflection)
grpcurl -plaintext target.com:50051 list

# Describe a method
grpcurl -plaintext target.com:50051 describe UserService.GetUser

# Call a method
grpcurl -d '{"user_id": 1}' -plaintext target.com:50051 UserService.GetUser

# With TLS
grpcurl -d '{"user_id": 1}' target.com:443 UserService.GetUser

# With authentication
grpcurl -H "Authorization: Bearer TOKEN" \
  -d '{"user_id": 1}' \
  target.com:443 UserService.GetUser

# IDOR test — change user_id to other users:
for id in 1 2 3 4 5 100 999; do
  echo "--- User $id ---"
  grpcurl -d "{\"user_id\": $id}" \
    -H "Authorization: Bearer MY_TOKEN" \
    target.com:443 UserService.GetUser
done

# grpcui — web UI for gRPC testing (like Postman for gRPC)
grpcui -plaintext target.com:50051
# Opens browser UI at http://localhost:8080
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| gRPC reflection enabled in production | Disable reflection service in production |
| No auth on gRPC methods | Implement server interceptor for auth on all methods |
| Injection via protobuf fields | Validate all input fields regardless of serialization format |
| Plaintext gRPC (no TLS) | Always use TLS for gRPC in production |
| Admin methods exposed via reflection | Use method-level authorization |

---

## Related Notes
- [[23 - REST API Architecture]] — REST alternative
- [[20 - HTTP2 Multiplexing HPACK Server Push]] — gRPC uses HTTP/2
- [[Module 07 - API Security]] — API security principles
- [[Module 14 - XXE]] — protobuf alternatives to XML injection
