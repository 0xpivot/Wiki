---
tags: [cloud, advanced, container, kubernetes, vapt]
difficulty: advanced
module: "81 - Advanced Kubernetes and Container Breakouts"
topic: "81.06 Bypassing AppArmor and Seccomp in Containers"
---

# 81.06 Bypassing AppArmor and Seccomp in Containers

## 1. Introduction

When securing Linux containers (Docker, containerd, CRI-O), namespaces and cgroups provide isolation, but they do not provide a strong security boundary against root-level exploitation. A root user inside a container still shares the kernel with the host. To mitigate the risk of container breakouts, container runtimes employ Mandatory Access Control (MAC) systems like AppArmor and system call filters like Seccomp. 

In advanced container penetration testing, identifying weaknesses in custom or default profiles for AppArmor and Seccomp is a critical step towards achieving a full container escape. This document explores the deep technical details of both security mechanisms, how they are implemented in modern container runtimes, and the methodologies used by attackers to bypass them.

## 2. Understanding the Defensive Mechanisms

### 2.1 Seccomp (Secure Computing Mode)

Seccomp is a Linux kernel feature that restricts the system calls (syscalls) a process can make. In the context of containers, a seccomp profile is applied to the container's init process and inherited by all child processes. 

The default Docker seccomp profile blocks approximately 44 out of the 300+ available syscalls. The goal is to prevent the use of syscalls that are often abused for kernel exploitation or container escapes, such as:
- `ptrace`: Can be used to inject code into other processes.
- `kexec_load`: Used to load a new kernel.
- `unshare`, `clone` (with certain flags): Used to create new namespaces.
- `bpf`: Extended Berkeley Packet Filter operations.
- `userfaultfd`: Often abused in use-after-free kernel exploits.

Seccomp uses Berkeley Packet Filter (BPF) rules to evaluate syscalls. When a syscall is invoked, the kernel evaluates the BPF filter. If the filter denies the syscall, the kernel typically kills the process or returns an `EPERM` error.

### 2.2 AppArmor

AppArmor is a Linux kernel security module that allows the system administrator to restrict programs' capabilities with per-program profiles. Profiles can allow capabilities like network access, raw socket access, and permission to read, write, or execute files on matching paths.

In Docker, the default AppArmor profile (`docker-default`) is applied to all containers unless specifically overridden. It primarily restricts:
- Writing to certain sensitive paths like `/proc/sys/`, `/sys/`, and `/proc/bus/`.
- Mounting file systems (`mount`, `umount`).
- Accessing `ptrace`.

## 3. ASCII Diagram: The Syscall and MAC Boundary

```text
    User Space (Inside Container)
    +---------------------------------------------------+
    |                                                   |
    |  [ Malicious Process (uid=0) ]                    |
    |         |                                         |
    |         | 1. Executes Syscall (e.g., mount,       |
    |         |    ptrace, openat)                      |
    |         v                                         |
    +---------------------------------------------------+
              |
              v  (Syscall Exception / Context Switch)
    =====================================================  <-- Container Boundary
    Kernel Space (Host)
              |
              | 2. Seccomp-BPF Filter Check
              |    +----------------------------------+
              +--->| Is Syscall in Allowed List?      |
                   | Does it match argument filters?  |
                   +----------------------------------+
                            |
                     [Yes]  |   [No] -> SIGKILL or EPERM
                            v
              | 3. LSM Hook (AppArmor) Check
              |    +----------------------------------+
              +--->| Does AppArmor profile allow this |
                   | action on this specific object?  |
                   +----------------------------------+
                            |
                     [Yes]  |   [No] -> EACCES
                            v
              | 4. Kernel Function Execution (e.g., sys_mount)
              |    +----------------------------------+
              +--->| Standard DAC/Capabilities Check  |
                   | (Is user root? Has CAP_SYS_ADMIN?|
                   +----------------------------------+
                            |
                     [Yes]  |   [No] -> EPERM
                            v
              | 5. Action Performed (e.g., File system mounted)
              v
```

## 4. Bypassing Seccomp

Bypassing seccomp typically involves finding vulnerabilities in the kernel, exploiting a misconfigured profile, or utilizing architectural tricks.

### 4.1 Missing Syscall Restrictions

If a custom seccomp profile is used, developers often accidentally allow dangerous syscalls. 

#### The `ptrace` Bypass
If `ptrace` is allowed (perhaps for debugging purposes), an attacker who is root inside the container can attach to a process that is running in a different context or namespace, potentially allowing code execution outside the container if they share the PID namespace with the host, or manipulating processes to break out.

#### The `keyctl` Bypass
The `keyctl` syscall manages kernel keyrings. Historically, vulnerabilities like CVE-2016-0728 allowed local privilege escalation via `keyctl`. If this syscall is exposed, kernel exploits can be executed directly from the container.

### 4.2 Architecture Switching (The x32 ABI Trick)

Historically, seccomp filters often failed to account for different execution architectures on the same machine. For instance, on an x86_64 system, a process can make syscalls using the 32-bit (i386) ABI or the x32 ABI.

If the seccomp profile only filters x86_64 syscall numbers, an attacker can invoke the equivalent syscall using the x32 ABI. 
Syscall numbers differ between architectures. For example, `execve` is `59` on x86_64 but `520` on x32.

An attacker can use inline assembly to make an x32 syscall:

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/syscall.h>

#define __X32_SYSCALL_BIT 0x40000000

int main() {
    // Attempting to call an x32 syscall to bypass an x86_64 seccomp filter
    long syscall_num = 520 | __X32_SYSCALL_BIT; // execve in x32
    
    // Setup arguments for execve
    const char *path = "/bin/sh";
    char *const argv[] = { "sh", NULL };
    char *const envp[] = { NULL };

    long ret;
    asm volatile(
        "syscall"
        : "=a" (ret)
        : "0" (syscall_num), "D" (path), "S" (argv), "d" (envp)
        : "rcx", "r11", "memory"
    );

    return 0;
}
```
Modern Docker default seccomp profiles handle multi-architecture environments correctly by checking the `arch` field in the seccomp data, but custom profiles in Kubernetes environments frequently miss this.

### 4.3 Syscall Argument Filtering Weaknesses

Seccomp can filter based on syscall arguments, but it only checks the values of the registers at the time of the syscall. It cannot dereference pointers.

If a seccomp rule blocks `mount` based on the file system type (e.g., blocking `proc`), it only checks the memory address of the string, not the string itself. 

```json
{
  "names": [
    "mount"
  ],
  "action": "SCMP_ACT_ERRNO",
  "args": [
    {
      "index": 2,
      "value": 12345, 
      "op": "SCMP_CMP_EQ"
    }
  ]
}
```
Because seccomp-bpf cannot dereference pointers, filtering paths or string arguments in syscalls like `openat` or `mount` is impossible. Attackers can bypass intent-based restrictions if the profile designers mistakenly assume seccomp can filter by path.

## 5. Bypassing AppArmor

AppArmor bypasses generally rely on finding paths that are not restricted by the profile, or exploiting vulnerabilities where AppArmor enforcement is lacking.

### 5.1 The Unconfined Profile

The easiest bypass is when the container is run with `securityContext.appArmorProfile.type: Unconfined` in Kubernetes, or `--security-opt apparmor=unconfined` in Docker. 
In this state, AppArmor applies no restrictions. The attacker only has to bypass namespace and capability boundaries (which is easier if the container is also privileged).

### 5.2 The `docker-default` Weaknesses

The `docker-default` profile is robust but has limitations.
It primarily restricts writes to `/proc` and `/sys`, and prevents `mount`.

#### Overmounted `/proc` and `/sys`
If an attacker can mount a fresh `procfs` or `sysfs`, they can bypass the path-based restrictions of AppArmor. AppArmor restricts paths based on the mount tree it knows about at the time the profile is parsed.

If an attacker has the `CAP_SYS_ADMIN` capability but AppArmor is enforcing `docker-default`, the attacker cannot mount because `mount` is blocked by AppArmor. However, if the AppArmor profile allows `mount` but restricts paths, the attacker can mount a new `procfs` in `/tmp` and modify files like `/tmp/proc/sys/kernel/core_pattern` to achieve host code execution.

### 5.3 Shebang (`#!`) and Execution Contexts

AppArmor profiles often transition to different profiles upon executing certain binaries (`px` or `cx` rules). 
If a profile dictates that `/usr/sbin/nginx` runs under a strict profile, an attacker might try to run it via an interpreter or a different method to avoid the transition.

### 5.4 Exploiting Kernel Vulnerabilities to Disable AppArmor

AppArmor enforcement happens at the LSM (Linux Security Module) layer in the kernel. If an attacker has a kernel exploit that achieves arbitrary read/write, they can locate the `cred` structure of their process in kernel memory.

In kernel memory, the `cred` structure points to a `security` field (the LSM blob). By zeroing out or modifying the `task_struct->real_cred->security` pointer, the attacker can effectively detach the AppArmor profile from the running process, bypassing all restrictions instantly.

## 6. Identifying AppArmor and Seccomp Status

### Checking AppArmor
Inside a container, read `/proc/self/attr/current`.
```bash
cat /proc/self/attr/current
```
Output like `docker-default (enforce)` indicates AppArmor is active. An output of `unconfined` means no profile is applied.

### Checking Seccomp
Inside a container, read the `Seccomp` field in `/proc/self/status`.
```bash
grep Seccomp /proc/self/status
```
- `0`: Disabled (Unconfined)
- `1`: Strict mode (Only read, write, _exit, sigreturn allowed)
- `2`: Filter mode (Seccomp-BPF applied)

To see which syscalls are allowed, tools like `amicontained` or `seccomp-tools` can be used to dump and analyze the BPF filter.

## 7. Mitigation and Hardening

1. **Never use Unconfined Profiles**: Always enforce the default seccomp and AppArmor profiles unless there is a strict operational requirement.
2. **Custom Profiles**: When creating custom seccomp profiles, use a default-deny approach. Explicitly allow only the syscalls required by the application.
3. **Architecture Awareness**: Ensure seccomp profiles account for multiple architectures (e.g., filtering both `AUDIT_ARCH_X86_64` and `AUDIT_ARCH_X86`).
4. **Use Kubernetes Security Policies**: Enforce Pod Security Standards (Restricted) which inherently mandate baseline seccomp and AppArmor configurations.
5. **eBPF Monitoring**: Use tools like Tetragon, Falco, or Tracee to monitor container syscalls at the eBPF layer. These tools operate below Seccomp/AppArmor and can detect exploitation attempts in real-time.

## 8. Chaining Opportunities

- **Privileged Containers**: Bypassing Seccomp/AppArmor is often the prerequisite for exploiting [[10 - Escaping Privileged Containers Deep Dive]].
- **Kernel Exploitation**: A seccomp bypass that allows `userfaultfd` or `bpf` can be chained with a kernel CVE (e.g., Dirty Pipe) to escalate to host root.
- **Service Account Tokens**: After a container escape, use the techniques in [[09 - Secrets Extraction from etcd]] to pivot to the control plane.

## 9. Related Notes

- [[10 - Escaping Privileged Containers Deep Dive]]
- [[01 - Container Fundamentals and Namespaces]]
- [[02 - Linux Capabilities in Containers]]
- [[05 - Container Runtime Vulnerabilities]]
