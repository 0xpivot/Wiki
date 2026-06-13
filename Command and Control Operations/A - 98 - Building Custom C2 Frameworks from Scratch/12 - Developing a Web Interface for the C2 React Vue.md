---
tags: [c2, malware-dev, red-team, custom, vapt]
difficulty: advanced
module: "98 - Building Custom C2 Frameworks from Scratch"
topic: "98.12 Developing a Web Interface for the C2 React Vue"
---

# 98.12 Developing a Web Interface for the C2 React Vue

## The Role of the Web Interface in Modern C2 Frameworks
A Command and Control (C2) framework is only as effective as its operator's ability to manage it. While terminal-based interfaces (like Metasploit's `msfconsole` or Empire's legacy CLI) are functional, modern Red Team operations involving multiple operators, hundreds of agents, and complex lateral movement paths require a robust, graphical Web Interface.

Developing a C2 interface using modern frontend frameworks like React or Vue.js allows for real-time state management, modular component design, and rich visualization of target networks. This document explores the architectural decisions, state management patterns, and UI/UX considerations for building a custom C2 frontend.

## Architectural Design

The C2 Web Interface acts as the client-side presentation layer, interacting strictly with the Teamserver via REST APIs and WebSockets. It should never communicate directly with the infected endpoints (agents).

### Standard Three-Tier Architecture
1.  **Frontend (React/Vue):** Handles the UI, state management (Redux/Vuex), and real-time DOM updates.
2.  **Backend/Teamserver (Golang/Python/Rust):** Handles agent check-ins, database management, operator authentication, and exposes the API for the frontend.
3.  **Agents (C/C++/Rust):** The malicious payloads running on target infrastructure.

### Key Functional Requirements
- **Real-Time Tasking & Polling:** Operators must see agent check-ins and task execution results instantly.
- **Multi-Player Support:** Multiple operators must be able to log in, interact with the same agents, and see each other's commands in real-time.
- **Visual Network Graphing:** Rendering the relational paths of agents (e.g., Agent A -> SMB Pipe -> Agent B -> TCP -> Teamserver).
- **Extensibility:** An architecture that allows easy integration of new modules, exploit panels, and payload generators.

## System Architecture ASCII Diagram

```text
    +-------------------------------------------------------+
    |                  C2 Web Interface                     |
    |                 (React.js / Vue.js)                   |
    |                                                       |
    |  +--------------+  +---------------+  +------------+  |
    |  | Agent Viewer |  | Terminal UI   |  | Graph Node |  |
    |  | (DataGrid)   |  | (Xterm.js)    |  | (D3.js)    |  |
    |  +--------------+  +---------------+  +------------+  |
    |          |                 |                 |        |
    |          +-----------------+-----------------+        |
    |                            |                          |
    |                   State Management                    |
    |                   (Redux / Pinia)                     |
    +-------------------------------------------------------+
                |                                ^
           REST API (JWT Auth)             WebSocket (WSS)
           (Create Tasks, Generate)        (Real-time logs)
                |                                |
                v                                |
    +-------------------------------------------------------+
    |                   Teamserver Backend                  |
    |               (Golang / Gin / Gorilla WS)             |
    +-------------------------------------------------------+
                |                                ^
           HTTP/S, DNS, TCP                HTTP/S, DNS, TCP
           (Tasking Queue)                 (Check-in & Data)
                |                                |
                v                                |
    +-------------------------------------------------------+
    |                    Target Network                     |
    |  [Agent 1 (HTTP)] <---SMB---> [Agent 2 (Peer)]        |
    +-------------------------------------------------------+
```

## State Management and Real-Time Communication

In a React or Vue application, maintaining the state of hundreds of agents is computationally expensive. Using a state manager like Redux (React) or Vuex/Pinia (Vue) is critical.

### WebSockets for Real-Time Telemetry
Instead of aggressively polling the REST API every second, the frontend establishes a secure WebSocket (WSS) connection to the Teamserver. The Teamserver pushes events (e.g., `AGENT_CHECKIN`, `TASK_COMPLETE`, `NEW_LOOT`) to the frontend.

#### Educational Snippet: React WebSocket Integration
```typescript
// Abstracted concept of a React Hook for C2 WebSocket communication
import { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import { updateAgentStatus, appendTerminalLog } from './store/c2Slice';

export const useC2WebSocket = (wsUrl: string, token: string) => {
    const dispatch = useDispatch();
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        const ws = new WebSocket(`${wsUrl}?auth=${token}`);

        ws.onopen = () => setIsConnected(true);
        ws.onclose = () => setIsConnected(false);

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            switch (data.eventType) {
                case 'AGENT_CHECKIN':
                    // Update the agent's last seen timestamp and active IP
                    dispatch(updateAgentStatus(data.payload));
                    break;
                case 'TASK_OUTPUT':
                    // Route the command output to the correct terminal emulator window
                    dispatch(appendTerminalLog({
                        agentId: data.payload.agentId,
                        output: data.payload.outputString
                    }));
                    break;
                case 'LOOT_ACQUIRED':
                    // Notify the operator via a UI toast notification
                    showToast(`New loot from ${data.payload.agentId}: ${data.payload.lootType}`);
                    break;
                default:
                    console.warn('Unknown event type', data);
            }
        };

        return () => ws.close(); // Cleanup on unmount
    }, [wsUrl, token, dispatch]);

    return isConnected;
};
```

## UI/UX Considerations for Red Teams

A poorly designed C2 interface can lead to operator fatigue and critical OPSEC mistakes (e.g., executing the wrong command on the wrong endpoint).

1.  **Terminal Emulation:** Operators are accustomed to CLIs. Integrating libraries like `Xterm.js` allows the web interface to provide a genuine terminal feel, complete with bash-like autocomplete, history, and color coding for different output streams (stdout vs stderr).
2.  **Visual Graphing:** Utilizing libraries like `D3.js` or `React Flow` to map the network dynamically. When an agent moves laterally via an SMB named pipe, the UI should automatically draw a connecting line between the parent and child node, instantly showing the operator the network topology.
3.  **Payload Generation Wizard:** A step-by-step UI for building payloads. Selecting the architecture (x64/x86), format (EXE, DLL, shellcode), and evasion profiles (sleep time, jitter, obfuscation level) through intuitive dropdowns reduces human error.
4.  **Role-Based Access Control (RBAC):** Implementing views based on operator roles. A "Junior Operator" might only see the terminal and execution results, while the "Team Lead" has access to the infrastructure management and payload generation tabs.

## Real-World Attack Scenario

### Operation "Glass Pane"
A Red Team was tasked with simulating an APT group infiltrating a large healthcare provider. The team consisted of five operators working simultaneously from different geographical locations.
1.  **Deployment:** They utilized a custom C2 framework with a React.js frontend hosted behind a reverse proxy on heavily restricted infrastructure.
2.  **Collaboration:** Operator A secured initial access via a Phishing payload and obtained a beacon. The React UI instantly updated via WebSockets, notifying all 5 operators via a UI toast: `New Agent [BONE-THUG] checked in from 10.0.5.21`.
3.  **Parallel Operations:** Operator B opened a dedicated `Xterm.js` terminal tab in the web UI for `BONE-THUG` and began running local reconnaissance commands (`whoami /priv`, `seatbelt`). Simultaneously, Operator C used the C2's built-in file browser UI component to quietly download the user's `chrome_data.sqlite` without interrupting Operator B's terminal session.
4.  **Visual Lateral Movement:** As Operator A pivoted to a domain controller using WMI, the React frontend's D3.js graph automatically drew a link showing the new lateral connection, providing the entire team with immediate situational awareness of their expanding footprint.

## Chaining Opportunities

- The Web UI's Payload Wizard can be integrated with the Teamserver's **Dynamic Compilation Engine** (compiling C/C++ agents on the fly with randomized variables) to serve uniquely obfuscated binaries straight to the operator's browser.
- Integrating external APIs into the frontend. For example, piping BloodHound data directly into the C2's D3.js graph to overlay the compromised agents onto the Active Directory attack path.
- Integrating Webhooks for external notifications (e.g., sending a Slack/Discord message when a high-value target checks in).

## Related Notes

- [[14 - Adding Lateral Movement Modules to Custom C2]]
- [[21 - Designing a Robust Teamserver Architecture in Golang]]
- [[25 - Multi-Player OPSEC and Operator RBAC]]
- [[38 - Dynamic Payload Generation and Compilation via API]]
- [[06 - Integrating BloodHound and Graph Theory into C2]]
