# BALATRO SAVE TRANSFER TOOL

A Python-based utility to transfer Balatro save files between Android and PC in both directions.

---

## Requirements
- **Python installed and added to PATH**  
  [How to install Python and add to PATH](https://www.howtogeek.com/197947/how-to-install-python-on-windows/)  
- **USB debugging enabled** on your Android device  
- **Internet connection** (to install Python dependencies automatically)  

### Additional requirement for **PC → Android**:
- The **Android Balatro APK must be debuggable**  
  [How to make an app debuggable](https://gist.github.com/amahdy/87041554f62e384bee5766a958fd4f9a)

---

## Android → PC Transfer

### Steps:
1. Connect your Android device to your PC/laptop and run the provided `.bat` file.  
2. When prompted, grant backup permission on your Android device.  
3. Ensure you have an internet connection so dependencies can be installed automatically.  
4. If successful, the script will create two backup files in the same directory:  
   - `1-meta.jkr`  
   - `1-profile.jkr`  
   If the files are missing, check the newly created **extracted backup** folder.

---

## PC → Android Transfer

**WARNING**:  
You will be asked to:
- Select a PC profile to copy  
- Select an Android profile to overwrite  

This will replace the selected Android profile with the chosen PC profile.  
It is highly recommended to backup your Android profile first.

### Steps:
1. Connect your Android device to your PC/laptop and run the provided `.bat` file.  
2. Ensure USB debugging is enabled.  
3. Maintain an internet connection to install any dependencies.  
4. Read the warnings carefully — overwriting cannot be undone without a backup.
