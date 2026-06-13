---
tags: [vapt, injection, advanced]
difficulty: advanced
module: "10 - Injection Attacks"
topic: "10.15 gRPC Injection"
---

# 10.15 — gRPC Injection

## What is gRPC?

gRPC is a modern RPC (Remote Procedure Call) framework using HTTP/2 and Protocol Buffers (protobuf). It's commonly used for microservices communication. gRPC endpoints are harder to test than REST APIs but still vulnerable to injection.

```
GRPC VS REST:
  REST:  HTTP/1.1, JSON, text-based
  gRPC:  HTTP/2, Protocol Buffers (binary), strongly typed
  
TESTING CHALLENGE:
  Binary protocol → can't just modify text in Burp
  Need to decode/encode protobuf messages
  But: the underlying data still flows to DB queries!
  → SQLi, NoSQLi, command injection all still possible
```

---

## gRPC Interception with Burp Suite

```bash
# BURP SUPPORTS gRPC (Burp Suite Pro 2022.9+):
# 1. Configure Burp as proxy
# 2. Enable HTTP/2 support in Burp
# 3. gRPC messages appear as readable text in Burp!
#    (Burp decodes protobuf automatically in some cases)

# GRPC-WEB PROXY (makes gRPC testable with any HTTP tool):
# Many apps expose gRPC-Web which is HTTP/1.1-compatible
# Test like a normal HTTP request!

# CURL FOR gRPC-WEB:
curl -X POST https://target.com/api.UserService/GetUser \
  -H "Content-Type: application/grpc-web+proto" \
  --data-binary @message.bin

# GRPCURL (tool for testing gRPC):
grpcurl -plaintext target.com:50051 list
grpcurl -plaintext -d '{"user_id": "1"}' target.com:50051 api.UserService/GetUser
```

---

## Protobuf Injection Techniques

```bash
# PROTOBUF FIELD INJECTION:
# Fields are typed, but string fields can contain injection payloads!

# USING GRPCURL:
grpcurl -plaintext \
  -d '{"username": "admin'\''", "password": "test"}' \
  target.com:50051 auth.AuthService/Login
# → SQL injection in username field!

# PROTOBUF MANUAL CRAFTING:
# protoc compiler + custom .proto file to craft messages

# GRPC REFLECTION (discover methods):
grpcurl -plaintext target.com:50051 list
grpcurl -plaintext target.com:50051 describe api.UserService
grpcurl -plaintext target.com:50051 describe api.UserService.GetUser
```

---

## Common gRPC Vulnerabilities

```
1. SQL/NoSQL INJECTION IN STRING FIELDS:
   Same as REST API — string field → DB query → inject!
   
2. MISSING AUTHENTICATION:
   gRPC metadata = HTTP headers
   Check if Bearer token is required on each method
   grpcurl -plaintext -d '{}' target.com:50051 admin.AdminService/ListUsers
   → Returns data without auth? → Missing authentication!
   
3. GRPC REFLECTION ENABLED IN PRODUCTION:
   Reflection allows discovering all services/methods
   Should be disabled in production
   
4. INSECURE DESERIALIZATION:
   Protobuf parsing of malformed messages
   
5. RATE LIMIT BYPASS:
   gRPC streaming allows sending many messages in one connection
   May bypass rate limits applied per-connection
```

---

## Testing Tools

```bash
# GRPCURL:
brew install grpcurl
# OR:
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# EVANS (interactive gRPC client):
go install github.com/ktr0731/evans@latest
evans --host target.com --port 50051 --reflection repl

# BLOOM RPC (GUI gRPC client):
# Download from GitHub: FullyRiped/BloomRPC

# POSTMAN (supports gRPC):
# Import .proto file → test methods

# BURP EXTENSION (grpc-scanner):
# Community extensions for gRPC testing in Burp
```

---

## Defense

```
PROTECTION:
  1. Validate all incoming protobuf field values (same as REST)
  2. Use parameterized queries in resolvers
  3. Disable gRPC server reflection in production
  4. Implement authentication via gRPC metadata (Bearer token)
  5. Use TLS for all gRPC connections
  6. Implement per-method authorization
```

---

## Related Notes
- [[Module 07 - API Security]] — API security testing module
- [[Module 06 - SQL Injection]] — injection in backends
- [[13 - GraphQL Injection]] — similar modern API injection
