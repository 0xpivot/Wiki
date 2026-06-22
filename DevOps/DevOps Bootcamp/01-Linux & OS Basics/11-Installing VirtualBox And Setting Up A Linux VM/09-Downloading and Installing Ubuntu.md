---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Downloading and Installing Ubuntu

### Downloading Ubuntu ISO

To install Ubuntu, you need to download the ISO image from the official Ubuntu website at [ubuntu.com/download](https://ubuntu.com/download).

1. **Visit the Website**: Navigate to the Ubuntu download page.
2. **Select Version**: Choose the desired version of Ubuntu (e.g., the latest LTS release).
3. **Download ISO**: Click on the "Download" button to start the download.

### Mounting the ISO in VirtualBox

Once the ISO is downloaded, you need to mount it in VirtualBox.

1. **Select VM**: Click on the VM in the list and then click on "Settings".
2. **Storage Tab**: Go to the "Storage" tab.
3. **Controller**: Under the "Controller: IDE" section, click on the "Empty" slot.
4. **Add Optical Drive**: Click on the disc icon next to "Optical Drive" and select "Choose a disk file...".
5. **Select ISO**: Browse to the location where you saved the Ubuntu ISO and select it.

### Booting from the ISO

1. **Start VM**: Click on "Start" to boot the VM.
2. **Boot Menu**: During boot, you may see a boot menu. Select "Try Ubuntu without installing" to test the system or "Install Ubuntu" to proceed with installation.

### Installing Ubuntu

1. **Language Selection**: Choose your preferred language.
2. **Keyboard Layout**: Select the appropriate keyboard layout.
3. **Installation Type**: Choose "Erase disk and install Ubuntu" (since this is a virtual disk).
4. **Time Zone**: Select your time zone.
5. **User Setup**: Create a username and password for the new user account.
6. **Installation**: Wait for the installation to complete. This may take several minutes.

### Post-Installation Configuration

1. **Update System**: Open a terminal and run the following commands to update the system:
    ```sh
    sudo apt update
    sudo apt upgrade
    ```
2. **Install Additional Software**: Install any additional software you need using the package manager:
    ```sh
    sudo apt install <package-name>
    ```

---
<!-- nav -->
[[08-Detailed Steps for Setting Up a Linux VM|Detailed Steps for Setting Up a Linux VM]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/11-Installing VirtualBox And Setting Up A Linux VM/00-Overview|Overview]] | [[10-Installing Oracle VirtualBox|Installing Oracle VirtualBox]]
