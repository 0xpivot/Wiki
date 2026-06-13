---
tags: [vapt, graphql, subscriptions, websockets, authorization]
difficulty: intermediate
module: "30 - GraphQL Security"
topic: "30.10 GraphQL Subscriptions Abuse"
---

# 30.10 — GraphQL Subscriptions Abuse

## What is it?
GraphQL **Subscriptions** are the third core operation type (alongside Queries and Mutations). While Queries fetch data once, and Mutations modify data, Subscriptions allow clients to maintain an active connection to the server to listen for real-time updates.

Because HTTP is stateless and unidirectional, Subscriptions are almost always implemented over **WebSockets** (or sometimes Server-Sent Events). When an event occurs on the server (e.g., a new message is inserted into the database), the server pushes a GraphQL payload down the WebSocket connection to all subscribed clients.

Securing Subscriptions is notoriously difficult because authorization must happen at two distinct phases:
1. **Connection Phase:** Can this user open a WebSocket to the server?
2. **Subscription Phase:** Is this user authorized to listen to this *specific* event stream (e.g., `chatId: 123`)?

Failure to secure the second phase leads to massive real-time data leaks.

## Attack Vectors in Subscriptions

### 1. Subscription IDOR (Eavesdropping)
The most common vulnerability is a failure to authorize the subscription arguments. An attacker subscribes to an event stream that belongs to another user.

**Vulnerable Subscription Request:**
```graphql
subscription {
  onNewMessage(chatRoomId: "PUBLIC_ROOM_1") {
    sender
    text
    timestamp
  }
}
```

**The Attack:** 
The attacker intercepts the WebSocket setup message and changes the argument from `"PUBLIC_ROOM_1"` to `"PRIVATE_ADMIN_CHAT"`. 

If the backend resolver does not verify that the user associated with the WebSocket session has permission to view `"PRIVATE_ADMIN_CHAT"`, the server will establish the subscription. The attacker will sit silently, and whenever an admin sends a message, a copy is routed directly to the attacker's WebSocket in real-time.

### 2. WebSocket Connection Spoofing (Missing Auth Phase 1)
Because WebSockets are a different protocol (`ws://` or `wss://`), traditional HTTP session cookies or HTTP Authorization headers are sometimes lost or difficult to attach during the initial WebSocket handshake in certain frontend frameworks.

To bypass this, developers often pass authentication tokens inside the initial WebSocket payload (a protocol specific to GraphQL-WS, usually the `connection_init` message).

**Vulnerable Setup:**
```json
// Sent via WebSocket immediately after connection opens
{
  "type": "connection_init",
  "payload": {
    "Authorization": "Bearer JWT_TOKEN"
  }
}
```

**The Attack:** 
If the server relies entirely on the client providing a token in the payload but fails to disconnect the socket if the token is missing or invalid, an unauthenticated attacker can establish an anonymous WebSocket. They can then fire subscriptions that assume the user is trusted, bypassing the entire authentication layer.

### 3. Denial of Service (DoS) via Subscription Exhaustion
WebSockets consume persistent server resources (memory and open file descriptors/sockets). GraphQL Subscriptions exacerbate this because the server must evaluate the subscription resolver logic for *every* connected client whenever a relevant mutation fires.

**The Attack:**
An attacker writes a script to open 10,000 concurrent WebSockets to the `/graphql` endpoint and fires a complex subscription on every single socket.
When the triggering event occurs (e.g., a new user registers), the GraphQL engine attempts to fan out the payload, executing the complex resolver 10,000 times simultaneously, instantly exhausting the server's CPU and crashing the node.

## Visualizing Subscription Eavesdropping

```text
========================================================================================
                          SUBSCRIPTION IDOR (REAL-TIME EAVESDROPPING)
========================================================================================

  [ Attacker ]                                            [ GraphQL Server ]
       |                                                         |
       |--- 1. Opens WebSocket (wss://api.target.com/graphql) -->|
       |                                                         |
       |--- 2. Sends: {"type":"connection_init"} --------------->|
       |<-- 3. Replies: {"type":"connection_ack"} ---------------|
       |                                                         |
       |--- 4. Sends Malicious Subscription -------------------->|
       |   {                                                     |
       |     "type": "start",                                    |
       |     "payload": {                                        |
       |       "query": "subscription { onDirectMessage(userId: 1) { text } }"
       |     }                                                   |
       |   }                                                     |
       |                                                         | (Fails to check if)
       |                                                         | (Attacker == userId 1)
       |<-- 5. Subscribed successfully. Waiting... --------------|
       |                                                         |
       |                                                         |
       |                                        [ Admin User ]---| (Sends DM to User 1)
       |                                                         |
       |<-- 6. PUSH: {"data": {"onDirectMessage": {"text": "Secret"}}}
       |
  [ Eavesdrops on private conversation in real-time ]

========================================================================================
```

## How to Test for Subscription Vulnerabilities
1. **Identify Subscriptions:** Check the schema via Introspection (`subscriptionType { name }`) to see if subscriptions are supported.
2. **Intercept the WebSocket:** In Burp Suite, open the `WebSockets history` tab. Look for JSON payloads containing `"type": "start"` or `"query": "subscription..."`.
3. **Test for IDOR:** Modify the arguments in the subscription payload. Change `userId`, `organizationId`, or `channelId` to targets you do not own.
4. **Trigger the Event:** You must force the server to fire the event. Log into a second account and perform an action that triggers the subscription (e.g., send a message to the target `channelId`). If your attacker account receives the WebSocket frame containing the message, you have confirmed an IDOR.
5. **Test Auth Bypasses:** Attempt to send a `start` payload *without* sending a `connection_init` payload first. Attempt to send an invalid JWT in the connection payload.

## Real-World Example
A pentester found a GraphQL endpoint for a financial trading application. The application used subscriptions to stream live stock prices to users based on their portfolio.
The subscription looked like this: `subscription { portfolioUpdates(accountId: "555") { stock, currentPrice } }`.

The pentester connected a WebSocket and requested `accountId: "001"`, belonging to the CEO. The server accepted the subscription. However, the pentester noticed that the `portfolioUpdates` object also included a `totalAccountValue` and `pendingTrades` field in the schema.
By changing their subscription query to:
`subscription { portfolioUpdates(accountId: "001") { pendingTrades { ticker, amount } } }`
The pentester was able to watch the CEO's massive insider trades execute in real-time, long before the data was public. The developers secured the queries, but completely forgot to secure the WebSockets.

## How to Fix It
- **Context Verification on `subscribe()`:** In the resolver configuration for a subscription, there is a `subscribe` function that fires when the client initially requests the stream. This function MUST verify that `context.user` has authorization to listen to the specific arguments requested. If unauthorized, throw an error and refuse the connection.
- **Payload Filtering on `resolve()`:** Even if the user is authorized to listen to the stream, ensure that the actual data being pushed down the pipe is filtered based on the user's role.
- **WebSocket Rate Limiting:** Enforce strict limits on the number of active WebSockets per IP address, and limit the number of active subscriptions a single WebSocket connection can maintain to prevent DoS attacks.

## Chaining Opportunities
- This vuln + [[29 - WebSockets Security]] → The fundamental transport mechanism is WebSockets. Understanding raw WebSocket manipulation in Burp Suite is mandatory to exploit GraphQL subscriptions.
- This vuln + [[08 - GraphQL IDOR]] → Eavesdropping on a subscription is essentially an IDOR applied to a continuous stream of data rather than a single database lookup.

## Related Notes
- [[29.01 - What are WebSockets]]
- [[29.04 - WebSocket Message Manipulation]]
- [[08 - GraphQL IDOR]]
