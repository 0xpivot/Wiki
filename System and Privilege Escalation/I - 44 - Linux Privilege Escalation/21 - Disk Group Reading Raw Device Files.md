---
tags: [linux, privesc, pentesting, red-team]
difficulty: advanced
module: "44 - Linux Privilege Escalation"
topic: "44.21 Disk Group Abuse"
---

# 44.21 Disk Group Membership Abuse (Reading Raw Device Files)

## 1. Introduction

In Unix-like operating systems, "Everything is a file." This philosophy extends to physical hardware. Hard drives and partitions are represented as block device files in the `/dev` directory (e.g., `/dev/sda`, `/dev/nvme0n1p1`). 

By default, these raw block devices are owned by `root` and assigned to the `disk` group. If a system administrator inadvertently adds a standard user to the `disk` group—perhaps attempting to grant them permission to mount external drives or use specific backup software—they grant that user raw read and write access to the entire physical disk. This completely bypasses the filesystem permissions (UGO/ACLs), allowing the user to read arbitrary sensitive files (like `/etc/shadow` or SSH keys) by extracting them directly from the raw byte stream of the disk.

## 2. Core Concepts and Underlying Mechanisms

To understand this vulnerability, one must understand the difference between Filesystem Level Access and Block Level Access.

### 2.1 Filesystem Level Access
When a user types `cat /etc/shadow`, the kernel checks the filesystem permissions. Because `/etc/shadow` is `-rw-r-----` and owned by `root:shadow`, a standard user is denied access.

### 2.2 Block Level Access
The filesystem (ext4, xfs, etc.) is simply a data structure written onto a physical disk partition (e.g., `/dev/sda1`). 
If a user has read access to `/dev/sda1`, they can read the raw bytes of the disk directly, entirely ignoring the filesystem drivers and the permission checks they enforce. They can essentially run forensic tools against the live partition to extract any file.

## 3. Technical Breakdown and Architecture

The following ASCII diagram illustrates how block-level access circumvents filesystem security.

```text
+-------------------------------------------------------------------------+
|                      DISK GROUP ABUSE ARCHITECTURE                      |
|                                                                         |
|  [ User 'backup_admin' (Group: disk) ]                                  |
|         |                                                               |
|         +-- Attempts File Access -> [ ext4 Driver (Checks Perms) ]      |
|         |                            |                                  |
|         |                            v                                  |
|         |                  DENIED (/etc/shadow)                         |
|         |                                                               |
|         +-- Attempts Block Access -> [ /dev/sda1 (Group: disk) ]        |
|                                      |                                  |
|                                      v                                  |
|                                   GRANTED                               |
|                                      |                                  |
|  [ Attacker using debugfs ]          |                                  |
|  # debugfs /dev/sda1 <---------------+                                  |
|  debugfs: cat /etc/shadow                                               |
|  root:$6$xyz...:18000:0:99999:7:::                                      |
|                                                                         |
+-------------------------------------------------------------------------+
```

## 4. Enumeration Strategy

Enumeration is simple: check group memberships and device file permissions.

### 4.1 Checking Group Membership
Verify if the current user belongs to the `disk` group.
```bash
id
# Output: uid=1001(john) gid=1001(john) groups=1001(john),6(disk)
```

### 4.2 Enumerating Block Devices
List the block devices on the system to identify the partition holding the root filesystem.
```bash
lsblk
df -h
```
Determine which partition is mounted on `/` (e.g., `/dev/sda1` or `/dev/mapper/ubuntu--vg-ubuntu--lv`).

Check the permissions of the block device:
```bash
ls -la /dev/sda1
# Output: brw-rw---- 1 root disk 8, 1 Oct 10 10:00 /dev/sda1
```
The output confirms that the `disk` group has read and write (`rw`) access to the block device.

## 5. Exploitation Methodology

Exploitation involves using filesystem debugging and forensic tools to parse the raw block device and extract files. The `debugfs` utility (part of the `e2fsprogs` package) is perfectly suited for this on ext2/ext3/ext4 filesystems.

### 5.1 Using debugfs (Interactive Mode)
If the root filesystem is ext4, run `debugfs` directly against the block device.
```bash
debugfs /dev/sda1
```
This drops you into an interactive debugging prompt. From here, you can navigate the filesystem structure, completely ignoring standard permissions.
```bash
debugfs: cd /root/.ssh
debugfs: ls
debugfs: cat id_rsa
```
Copy the RSA private key output and save it locally to SSH into the machine as root.

Alternatively, extract the shadow hashes to crack offline:
```bash
debugfs: cat /etc/shadow
```

### 5.2 Extracting Files Directly
You can use `debugfs` non-interactively to dump a file to your current directory:
```bash
debugfs -R 'dump /etc/shadow /tmp/shadow.txt' /dev/sda1
```

### 5.3 Modifying Files (Write Access)
If you have write access to the block device, you can technically overwrite data. However, using `debugfs` to write to a *live, mounted* filesystem is extremely dangerous and can instantly corrupt the filesystem and crash the kernel (kernel panic). 
While it is possible to use `debugfs -w` to write files, it is highly discouraged during a red team engagement due to the high risk of catastrophic system failure. Extracting credentials or SSH keys (Read-Only) is the much safer and preferred route.

### 5.4 Exploiting XFS or other Filesystems
If the filesystem is not ext4 (e.g., XFS), `debugfs` will not work. You can use specialized forensic tools or simply `grep` the raw partition data, though this is messy.
```bash
strings /dev/sda1 | grep -C 5 "root:"
```
Or use tools like `xfs_db` if available, or copy the entire partition to an image file, mount it locally with loopback devices, and extract the data.

## 6. Edge Cases and Bypasses

- **LVM (Logical Volume Manager)**: Modern Linux systems often use LVM. The block device might be `/dev/mapper/vg-lv_root`. The permissions check is the same; check if the `disk` group owns the mapper device.
- **Encrypted Partitions (LUKS)**: If the underlying disk is encrypted with LUKS, the `/dev/sda` device is encrypted. However, the unlocked mapped device (e.g., `/dev/mapper/luks-uuid`) will be unencrypted. If the `disk` group has access to the mapped device, the exploit remains identical.
- **Kernel Panics**: As reiterated, do not attempt to write directly to a live mounted block device. Always opt for read-only extraction of credentials or keys.

## 7. Post-Exploitation & Persistence

After extracting the root SSH key or cracking the root password:
- SSH into the machine as root.
- Establish standard persistence.
- Do NOT alter block device permissions yourself, as it could cause system instability. Leave the misconfiguration as a finding for the final report.

## 8. Defense & Remediation

- **Strict Group Management**: Never add standard users to the `disk` group. If a user needs to mount USB drives, use `udisksctl` or configure specific `sudo` privileges for the `mount` command rather than granting raw device access.
- **Role-Based Access Control**: Utilize proper delegation and PolicyKit (polkit) rules for desktop environments to handle removable media safely without altering group memberships.
- **Auditing**: Regularly audit privileged groups (e.g., `root`, `sudo`, `wheel`, `disk`, `docker`, `lxd`, `shadow`) for unauthorized memberships.

## 9. Chaining Opportunities

Disk group abuse is an excellent escalation path when combined with:
- **Service Account Compromise**: A backup service (like Bacula or Amanda) might run as a non-root user but be placed in the `disk` group to allow block-level backups. Compromising the web interface of the backup software yields a shell in the `disk` group.
- **Information Disclosure**: Extracting `/etc/shadow` is only useful if you can crack the hashes. If the hashes are strong, you can use `debugfs` to extract application configuration files (e.g., database configs) from the `/opt` or `/var` directories, pivoting to application compromise.

## 10. Related Notes
- [[15 - Weak File Permissions on Sensitive Files]]
- [[17 - SSH Private Key Reuse]]
- [[19 - Docker Group Membership]]
- [[20 - LXC LXD Group Abuse]]
