---
tags: [threat-hunting, forensics, memory, rootkits, vapt]
difficulty: advanced
module: "92 - Advanced Memory Forensics and Rootkit Detection"
topic: "92.03 Detecting Hidden and Unlinked Processes"
---

# Rootkit Techniques: Detecting Hidden and Unlinked Processes

## Direct Kernel Object Manipulation (DKOM) - Unlinking
One of the most persistent and dangerous ways attackers maintain stealth on a compromised system is through Direct Kernel Object Manipulation (DKOM). DKOM involves a kernel-level driver (a rootkit) modifying OS-critical memory structures directly. The most famous DKOM technique is process unlinking, designed to hide a malicious process from the operating system's built-in monitoring tools and API calls.

As discussed in process internals, the Windows kernel maintains a doubly linked list of all active processes via the `ActiveProcessLinks` field within the `EPROCESS` block. Utilities like Task Manager, Process Explorer, and the `EnumProcesses` API traverse this linked list to generate the list of running applications.

If a rootkit alters the pointers in this linked list, it can completely bypass standard detection mechanisms. 

### The Mechanics of Unlinking
To hide "Process B" (the malware) operating between "Process A" and "Process C":
1. The rootkit modifies the `FLINK` of Process A to skip Process B and point directly to Process C.
2. The rootkit modifies the `BLINK` of Process C to skip Process B and point directly to Process A.
3. Process B is now severed from the `ActiveProcessLinks` list.
4. Process B continues to run flawlessly. Why? Because the Windows CPU scheduler (the Dispatcher) schedules threads (`ETHREAD`), not processes. As long as the threads are still linked to the dispatcher database, the CPU will grant the hidden process execution time.

## Cross-View Validation Techniques
Detecting DKOM requires cross-view validation. Cross-view validation operates on a simple principle: if you ask for the same information using two entirely different mechanisms, any discrepancy between the two answers points to tampering.

In memory forensics, if we use one method to find processes (walking the linked list) and another method (scanning raw memory for structure headers), any process found in the second method but missing in the first is highly suspicious and likely hidden.

## Volatility 3 Plugins for Hidden Process Detection

### 1. `windows.pslist` (The Linked List View)
`windows.pslist` faithfully follows the `ActiveProcessLinks` exactly like the OS APIs. If a process is unlinked via DKOM, `pslist` will *not* show it. This acts as our "baseline" view.

### 2. `windows.psscan` (The Pool Tag Scanning View)
`windows.psscan` does not care about the linked list. Instead, it performs "pool tag scanning". When Windows allocates memory for an `EPROCESS` block, it uses the Non-Paged Pool and tags the memory allocation with a specific 4-byte signature (often `Proc` or similar, depending on OS version). 
`psscan` sequentially scans physical memory byte-by-byte looking for this signature and validating the structure behind it.

**Cross-View Validation Execution:**
By comparing the output of `pslist` vs `psscan`, an analyst can spot hidden processes. Volatility 3 handles this correlation via other plugins or manual comparison. If PID 1337 shows up in `psscan` but not in `pslist`, it has been unlinked.

### 3. Thread Scanning (`windows.thrdscan`)
Since a process must have executing threads to be malicious, scanning for `ETHREAD` objects is highly effective. Even if an `EPROCESS` block is heavily corrupted or unlinked, the `ETHREAD` objects must remain intact for the malware to function. `windows.thrdscan` finds these threads and can link them back to their parent process.

### 4. Handle Scanning (`windows.handles`)
Every process interacts with system resources (Files, Mutexes, Registry keys) via Handles. The kernel maintains a Handle Table. By scanning memory for handle tables (`_HANDLE_TABLE`), analysts can identify rogue handle tables that do not correspond to any known, linked process in the `ActiveProcessLinks`.

```text
=============================================================================
                  ASCII Diagram: DKOM Unlinking Process
=============================================================================

Normal State (Visible to Task Manager):

[ Process A ] <===========> [ Process B ] <===========> [ Process C ]
   PID: 100                 PID: 666 (Malware)             PID: 200
  FLINK ->                  FLINK ->                       FLINK ->
  <- BLINK                  <- BLINK                       <- BLINK

-----------------------------------------------------------------------------
DKOM Unlinked State (Hidden):

[ Process A ] ========================================> [ Process C ]
   PID: 100         +-------------------------------+      PID: 200
  FLINK -----------/                                 \---> FLINK ->
  <- BLINK <---------------------------------------------- BLINK
                    |                               |
                    |         [ Process B ]         |
                    |         PID: 666 (Hidden)     |
                    |        FLINK -> (Points to C) |
                    |        <- BLINK (Points to A) |
                    +-------------------------------+
=============================================================================
```

## Real-World Attack Scenario
**Scenario:** An advanced threat actor has breached a domain controller. They have deployed a kernel-mode rootkit known as `FUTo` or a modern equivalent like `Turla Driver`. The SOC team sees outbound beacons in network logs, but the endpoint's antivirus and EDR report a perfectly clean machine. 

**Incident Response Steps:**
1. The IR team acquires a physical memory dump of the Domain Controller.
2. The analyst executes `vol -f dc_mem.raw windows.pslist`. The output shows 85 normal Windows processes.
3. The analyst executes `vol -f dc_mem.raw windows.psscan`. The output shows 86 processes.
4. A differential comparison reveals a process named `svchost.exe` (PID 4052) present in `psscan` but entirely missing from `pslist`.
5. The analyst attempts to use standard API hooks to dump the memory of PID 4052, but it fails because the OS APIs cannot "find" the process.
6. Using Volatility's direct memory translation, the analyst targets the process using `vol -f dc_mem.raw windows.procdump --pid 4052` which relies on the `psscan` offsets rather than the linked list.
7. The extracted process is analyzed and confirmed to be a custom C2 agent deployed by the APT group, completely masked from EDR by the rootkit's DKOM unlinking mechanism.

## Chaining Opportunities
- If you find a hidden process, the next immediate step is to extract its payload. Refer to [[05 - Extracting Malware Payloads from Memory Dumps]].
- Hidden processes often use sophisticated memory structures. Understanding `EPROCESS` is required, review [[02 - Analyzing Windows Process Structures EPROCESS]].
- Sometimes attackers don't hide the process, they hide inside a legitimate one. See [[04 - Hunting for Injected Threads and Hollowed Processes]].

## Related Notes
- [[Rootkit Architecture and Kernel Mode Drivers]]
- [[Bypassing Endpoint Detection and Response (EDR)]]
- [[Windows Pool Memory Allocation (Paged vs Non-Paged)]]
- [[Advanced Persistent Threat (APT) Tradecraft]]
