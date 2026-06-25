---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Installing VirtualBox

### Downloading VirtualBox

To get started, visit the official VirtualBox website at [virtualbox.org](https://www.virtualbox.org/) and download the latest version of VirtualBox for your host operating system. Follow the installation instructions provided on the website.

### Configuring VirtualBox

Once installed, launch VirtualBox. The main window will display any existing VMs. To create a new VM, click on "New" in the top menu.

#### Creating a New VM

1. **Name and OS Type**:
    - Enter a name for your VM (e.g., `Ubuntu-Desktop`).
    - Select the type of operating system (`Linux`) and the version (`Ubuntu (64-bit)`).

2. **Memory Size**:
    - Allocate memory (RAM) to your VM. A minimum of 2048 MB is recommended for smooth operation.

3. **Hard Disk**:
    - Choose to create a new virtual hard disk now.
    - Select the type of hard disk (VDI is the default and recommended).
    - Choose the storage type (Dynamically allocated is recommended for flexibility).
    - Set the size of the virtual hard disk (at least 20 GB).

### Configuring Network Settings

By default, VirtualBox sets up a NAT network for the VM. This allows the VM to access the internet through the host's network connection. However, you may also configure a bridged network for direct access to the host's network.

#### Bridged Networking

1. **Select VM**: Click on the VM in the list and then click on "Settings".
2. **Network Tab**: Go to the "Network" tab.
3. **Adapter 1**: Enable the adapter and select "Bridged Adapter".
4. **Attached to**: Choose the appropriate network interface from the dropdown menu.

### Starting the VM

After configuring the VM, click on "Start" to boot it. The first time you start the VM, you will be prompted to select an installation media.

---
<!-- nav -->
[[10-Installing Oracle VirtualBox|Installing Oracle VirtualBox]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/11-Installing VirtualBox And Setting Up A Linux VM/00-Overview|Overview]] | [[12-Isolation Between Host and Guest Operating Systems|Isolation Between Host and Guest Operating Systems]]
