---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Virtualization and Virtual Machines

Virtualization is a technology that allows multiple operating systems to run concurrently on a single physical hardware platform. This is achieved through the use of a hypervisor, which is a layer of software that creates and manages virtual machines (VMs). Each VM runs an independent operating system and applications, isolated from other VMs on the same physical host.

### Hypervisor Types

There are two main types of hypervisors:

1. **Type 1 (Bare-Metal Hypervisors)**: These run directly on the host's hardware and manage the underlying physical resources. Examples include VMware ESXi, Microsoft Hyper-V, and Xen.
   
2. **Type 2 (Hosted Hypervisors)**: These run on top of a host operating system, such as Oracle VirtualBox, VMware Workstation, and Parallels Desktop.

### Why Use Virtual Machines?

Virtual machines offer several benefits:

- **Resource Utilization**: Multiple VMs can share the same physical resources, leading to better utilization.
- **Isolation**: Each VM operates independently, ensuring that issues in one VM do not affect others.
- **Portability**: VMs can be easily moved between different physical hosts.
- **Testing and Development**: Developers can test applications in various environments without affecting the production setup.

### Installing VirtualBox

VirtualBox is a popular Type 2 hypervisor that is free and open-source. It supports a wide range of guest operating systems, including Windows, Linux, macOS, and Solaris.

#### Installation Steps

1. **Download VirtualBox**: Visit the official VirtualBox website and download the latest version for your operating system.
2. **Install VirtualBox**: Follow the installation wizard to install VirtualBox on your system.
3. **Verify Installation**: Once installed, launch VirtualBox to ensure it runs correctly.

### Setting Up a Linux VM

After installing VirtualBox, the next step is to set up a Linux virtual machine. This process involves creating a new VM and configuring its settings.

#### Creating a New VM

1. **Open VirtualBox**: Launch the VirtualBox application.
2. **Create a New VM**:
    - Click on "New" to start the VM creation wizard.
    - Enter a name for your VM (e.g., `LinuxUbuntu`).
    - Select the type of operating system (`Linux`) and the version (`Ubuntu`).

#### Configuring VM Settings

Once the VM is created, you need to configure its settings to ensure optimal performance and functionality.

##### Storage Configuration

One of the critical settings is the storage configuration. This determines how the VM's disk space is managed.

###### Disk Image Formats

VirtualBox supports different disk image formats:

- **VDI (VirtualBox Disk Image)**: This is the native format used by VirtualBox. It offers dynamic allocation and compression.
- **VMDK (Virtual Machine Disk)**: This format is used by VMware products.
- **VHD (Virtual Hard Disk)**: This format is used by Microsoft Virtual PC and Hyper-V.

For this example, we will use the VDI format.

```mermaid
graph TD;
    A[Disk Image Formats] --> B[VDI];
    A --> C[VMDK];
    A --> D[VHD];
```

###### Dynamic Allocation vs Fixed Size

When configuring the storage, you have two options:

- **Dynamically Allocated**: The hypervisor intelligently decides how much storage the VM needs and allocates it dynamically. This is efficient in terms of disk usage but may result in slightly slower performance due to the overhead of managing dynamic allocation.
  
- **Fixed Size**: The VM is allocated a fixed amount of storage upfront. This provides better performance but may lead to wasted disk space if the VM does not fully utilize the allocated storage.

For this example, we will choose dynamically allocated storage.

```mermaid
graph TD;
    A[Storage Options] --> B[Dynamically Allocated];
    A --> C[Fixed Size];
```

#### Adjusting Virtual Hard Disk Size

The next step is to adjust the virtual hard disk size. By default, VirtualBox sets the size to 10 GB. You can increase or decrease this based on your requirements.

```mermaid
graph TD;
    A[Adjust Virtual Hard Disk Size] --> B[Default: 10 GB];
    B --> C[Increase/Decrease Based on Requirements];
```

#### Setting Up the VirtualBox Folder

Finally, you need to specify the location where the VDI file will be stored. This is typically done by selecting a folder within the VirtualBox settings.

```mermaid
graph TD;
    A[VirtualBox Folder] --> B[Specify Location for VDI File];
```

### Complete Example

Here is a complete example of setting up a Linux VM using VirtualBox:

1. **Create a New VM**:
    - Name: `LinuxUbuntu`
    - Type: `Linux`
    - Version: `Ubuntu`

2. **Configure Storage**:
    - Disk Image Format: `VDI`
    - Storage Option: `Dynamically Allocated`
    - Virtual Hard Disk Size: `10 GB`

3. **Set Up VirtualBox Folder**:
    - Specify the location for the VDI file.

### Full Raw HTTP Message Example

While setting up a VM does not involve HTTP messages, it is important to understand the underlying communication protocols used by the hypervisor and the guest OS. Here is an example of a typical HTTP request and response that might occur during the boot process of a VM:

```http
GET /api/vm/status HTTP/1.1
Host: localhost:18083
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
Accept: application/json

HTTP/1.1 200 OK
Date: Mon, 20 Nov 2023 12:00:00 GMT
Content-Type: application/json
Content-Length: 123

{
    "status": "running",
    "vmName": "LinuxUbuntu",
    "storage": {
        "type": "dynamic",
        "size": "10GB"
    }
}
```

### Common Pitfalls and How to Prevent Them

#### Pitfall 1: Insufficient Disk Space

**Problem**: Allocating insufficient disk space can lead to performance issues and potential crashes.

**Prevention**:
- Always allocate enough disk space based on the expected usage.
- Monitor disk usage regularly and resize the disk if necessary.

#### Pitfall 2: Incompatible Disk Image Format

**Problem**: Using an incompatible disk image format can cause compatibility issues with other hypervisors.

**Prevention**:
- Choose a widely supported format like VDI or VMDK.
- Ensure the chosen format is compatible with all intended hypervisors.

#### Pitfall 3: Incorrect Storage Configuration

**Problem**: Incorrectly configuring storage can lead to inefficient resource utilization.

**Prevention**:
- Understand the differences between dynamic and fixed-size allocation.
- Choose the appropriate configuration based on the specific use case.

### Secure Coding Practices

#### Vulnerable Code Example

```python
# Vulnerable Code
def allocate_storage(size):
    if size < 10:
        return "Insufficient storage"
    else:
        return "Storage allocated successfully"

print(allocate_storage(5))
```

#### Secure Code Example

```python
# Secure Code
def allocate_storage(size):
    if size < 10:
        raise ValueError("Insufficient storage")
    else:
        return "Storage allocated successfully"

try:
    print(allocate_storage(5))
except ValueError as e:
    print(e)
```

### Real-World Examples and Breaches

#### Example 1: CVE-2021-3186

This vulnerability affected VMware ESXi and vCenter Server, allowing an attacker to execute arbitrary code on the host. Proper configuration and regular updates can mitigate such risks.

#### Example 2: Heartbleed Bug (CVE-2014-0160)

Although not directly related to virtualization, the Heartbleed bug demonstrated the importance of securing communication protocols. Ensuring secure communication between the hypervisor and guest OS is crucial.

### Hands-On Labs

To practice setting up a Linux VM using VirtualBox, consider the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs for web application security.
- **OWASP Juice Shop**: Provides a vulnerable web application for testing and learning.
- **DVWA (Damn Vulnerable Web Application)**: Another excellent resource for practicing web application security.

These labs provide practical experience in setting up and managing virtual machines, ensuring you gain a deep understanding of the concepts covered.

### Conclusion

Setting up a Linux VM using VirtualBox involves several steps, including choosing the appropriate disk image format, configuring storage, and specifying the location for the VDI file. Understanding these concepts and their implications is crucial for effective virtualization. By following best practices and secure coding techniques, you can ensure optimal performance and security for your virtual machines.

---
<!-- nav -->
[[05-Introduction to Virtualization and Hypervisors|Introduction to Virtualization and Hypervisors]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/11-Installing VirtualBox And Setting Up A Linux VM/00-Overview|Overview]] | [[07-Common Pitfalls and How to Prevent Them|Common Pitfalls and How to Prevent Them]]
