---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Setting Up VirtualBox

### Installing VirtualBox

Before setting up a Linux VM, you need to install VirtualBox. Follow these steps:

1. Visit the [VirtualBox website](https://www.virtualbox.org/wiki/Downloads).
2. Download the appropriate version for your operating system.
3. Run the installer and follow the prompts to complete the installation.

### Creating a New Virtual Machine

Once VirtualBox is installed, you can create a new virtual machine:

1. Open VirtualBox.
2. Click on "New" to create a new VM.
3. Enter a name for the VM (e.g., "Ubuntu 20.04 LTS").
4. Choose the type (Linux) and version (Ubuntu 64-bit).
5. Allocate memory (RAM) to the VM. A minimum of 2 GB is recommended for smooth operation.
6. Create a virtual hard disk. Choose "VDI" as the file type and "Dynamically allocated" for the storage type.
7. Set the size of the virtual hard disk (e.g., 20 GB).

### Configuring the Virtual Machine

After creating the VM, you need to configure it:

1. Select the newly created VM and click on "Settings".
2. Under "System", set the number of processors and enable PAE/NX if necessary.
3. Under "Display", allocate video memory (e.g., 128 MB).
4. Under "Storage", click on the controller icon and then "Add Hard Disk". Select the ISO image you downloaded earlier.

### Starting the Virtual Machine

Now you can start the virtual machine:

1. Select the VM and click on "Start".
2. In the boot menu, select the ISO image you added.
3. Follow the installation prompts to install Ubuntu on the virtual machine.

---
<!-- nav -->
[[13-Practice Labs|Practice Labs]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/11-Installing VirtualBox And Setting Up A Linux VM/00-Overview|Overview]] | [[15-Setting Up a Linux Ubuntu Virtual Machine|Setting Up a Linux Ubuntu Virtual Machine]]
