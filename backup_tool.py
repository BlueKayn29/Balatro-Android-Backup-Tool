import io
import subprocess
import requests
import tarfile
import shutil
import os
import sys
import zipfile

package_keyword = "balatro"
save_location = {"balatro": [f"extracted_backup/apps/com.playstack.balatro.android/f/1-meta.jkr",
                             f"extracted_backup/apps/com.playstack.balatro.android/f/1-profile.jkr"]}
backup_file_names = {"balatro": ["1-meta.jkr", "1-profile.jkr"]}
abe_download_link = "https://github.com/nelenkov/android-backup-extractor/releases/download/latest/abe-62310d4.jar"
adb_download_link = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"


def check_package(stdout):
    if package_keyword not in stdout:
        print("Package not found in device")
        return False
    print("Package found in device")
    return True


def device_connection_check(stdout):
    lines = stdout.strip().split("\n")
    for line in lines[1:]:
        if 'device' in line and not 'offline' in line:
            return True
    print("Device not found. Please connect your device and enable USB debugging.")
    return False


def check_successful_backup(stdout):
    flag = check_file_in_dir("backup.ab")
    if not flag:
        print("Error: ADB executed backup but file was not created")
    return flag


def check_successful_ab2tar(stdout):
    flag = check_file_in_dir("backup.tar")
    if not flag:
        print("Backup.tar file creation failed")
    return flag


def check_file_in_dir(filename):
    return os.path.isfile(filename)


def check_existing_backup():
    flag = False
    for file in backup_file_names[package_keyword]:
        if os.path.isfile(file):
            print(f"Backup file \"{file}\" already exists in current directory")
            flag = True
    if flag:
        print("One or more backup files already exist. Delete or move them before continuing.")
    return flag


def execute_command(command, verbose=True, commence_msg="Executing command", success_msg=None,
                    error_msg="Command failed", print_std=False, callback=None):
    if verbose:
        if commence_msg:
            print(commence_msg)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        if success_msg and verbose:
            print(success_msg)
        if callback:
            status = callback(result.stdout)
            if not status:
                sys.exit(1)
        if print_std and verbose:
            print("STDOUT: ", result.stdout)
    else:
        if verbose:
            print(error_msg)
        if print_std and verbose:
            print("STDERR: ", result.stderr)
    print()


# TODO: Add check for adb in path
# Download adb
if not check_file_in_dir("adb.exe"):
    print("Downloading Android Debugger Bridge (adb)...")
    response = requests.get(adb_download_link)
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            adb_files = [f for f in z.namelist() if f.endswith("adb.exe")]
            if adb_files:
                adb_path_in_zip = adb_files[0]
                # print(f"Extracting {adb_path_in_zip}...")
                z.extract(adb_path_in_zip, ".")
                extracted_path = os.path.join(".", adb_path_in_zip)
                final_path = os.path.join(".", "adb.exe")
                os.replace(extracted_path, final_path)
                # print("adb.exe extracted successfully.")
            else:
                print("adb.exe not found in ZIP.")
    else:
        print(f"Download failed: {response.status_code}")
    print()

# Check for device
execute_command("adb devices", commence_msg="Checking connected devices...", print_std=False,
                callback=device_connection_check)

# list all packages
execute_command("adb shell pm list packages",
                commence_msg=f"Checking for package associated with {package_keyword} in device...",
                callback=check_package)

# take backup if backup doesn't exist
backup_exists = check_existing_backup()
if not backup_exists:
    execute_command("adb backup -apk -f backup.ab com.playstack.balatro.android",
                    commence_msg=f"Taking backup. Confirm on your android device to proceed.",
                    error_msg="Backup failed", callback=check_successful_backup)
else:
    exit(1)

# download abe if it doesn't exist
if not check_file_in_dir("abe.jar"):
    print("Downloading Android Backup Extractor...")
    response = requests.get(abe_download_link)
    if response.status_code == 200:
        with open("abe.jar", "wb") as f:
            f.write(response.content)
    else:
        print(f"Download failed Status code: {response.status_code}")
        exit(1)
        print("\n")

    if check_file_in_dir("abe.jar"):
        print("Downloaded ABE successfully")
    else:
        print("ABE download finished but couldn't find \"abe.jar\" file")
    print("\n")

# use abe to convert to tar file
execute_command("java -jar abe.jar unpack backup.ab backup.tar",
                commence_msg="Unpacking backup to tar file", error_msg="Converting to tar failed",
                callback=check_successful_ab2tar)

# extract .tar file to 'extracted_backup' folder
print("Extracting tar file")
extract_to = 'extracted_backup'
with tarfile.open("backup.tar", 'r') as tar:
    tar.extractall(path=extract_to)
print(f"Successfully extracted tar files\n")

# copy save files to main folder
# TODO: add for more apps
backup_file_paths = save_location["balatro"]
flag = True
for path in backup_file_paths:
    destination_path = os.path.join(os.getcwd(), os.path.basename(path))
    try:
        shutil.copy2(path, destination_path)
    except FileNotFoundError:
        flag = False
if not flag:
    print("Backup was successful but backup files were not found in their usual location\nSearch the"
          " \"extracted backup\" folder manually for the files.")
else:
    print("Backup successful. You can now disconnect your device.")
