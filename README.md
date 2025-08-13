# **BALATRO SAVE & BACKUP TOOL**

A set of tools to transfer, backup, and restore Balatro save files between **Android** and **PC**.

---

## **Requirements**
- Ensure Python is installed and added to your system PATH.  
  [How to install Python and add it to PATH](https://www.howtogeek.com/197947/how-to-install-python-on-windows/)

- Ensure you have an active internet connection (for installing dependencies automatically when running the tool).

- **For PC → Android transfer only**:  
  - The Android Balatro APK must be **debuggable**.  
    [How to make an app debuggable](https://gist.github.com/amahdy/87041554f62e384bee5766a958fd4f9a)

- **For all Android-related operations**:  
  - Enable **USB debugging** on your Android device.
  - Connect your Android device to your PC via USB.

---

## **Tools Overview**

### 1. **Android → PC (Save Transfer Tool)**
Transfers your Balatro saves from an Android device to your PC.

**Usage:**
1. Connect your Android device to your PC and run the corresponding `.bat` file.
2. Grant **backup permission** on your Android device when prompted.
3. Follow the on-screen instructions and warnings carefully to avoid losing important saves.

---

### 2. **PC → Android (Save Transfer Tool)**
Transfers your Balatro saves from your PC to your Android device.

**WARNING:**  
This will **replace** the selected Android profile with the selected PC profile.  
It is **highly recommended** to backup your Android profile before proceeding.

**Usage:**
1. Connect your Android device to your PC and run the corresponding `.bat` file.
2. Follow the on-screen instructions to select a PC profile to copy and an Android profile to overwrite.
3. Read all warnings carefully before confirming the operation.

---

### 3. **Backup/Restore Tool**
Allows you to backup or restore Balatro save files.

**Restore Usage:**
1. Connect your Android device to your PC.
2. Run `balatro_restore_saves.bat`.
3. Place your backup files (`meta.jkr` and `profile.jkr`) in the `to_restore` folder.  
   - Ensure **only one** `meta.jkr` and one `profile.jkr` file are present.
4. Follow on-screen instructions to restore your saves.

**Backup Usage:**
For now, use Android → PC (Save Transfer Tool) to Backup. PC Balatro is not required for this.
---

## **Important Notes**
- Always read the warnings carefully before proceeding with any transfer or restore.
- Making backups before overwriting saves is strongly advised.
