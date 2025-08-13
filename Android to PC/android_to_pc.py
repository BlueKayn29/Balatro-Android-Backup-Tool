import tarfile
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))  # for helper.py
from helper import *

backup_file_names = {"balatro": ["1-meta.jkr", "1-profile.jkr"]}
pc_file_names = {"balatro": ["meta.jkr", "profile.jkr"]}
abe_download_link = "https://github.com/nelenkov/android-backup-extractor/releases/download/latest/abe-e252b0b.jar"
# TODO: make dynamic ^^^
java_download_link = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.16%2B8/" \
                     "OpenJDK17U-jdk_x64_windows_hotspot_17.0.16_8.zip"


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


def copy_backup_to_pc_folder():
    # transfer save files to balatro pc save location
    make_pc_save = input(f"Do you want to copy the extracted save to the pc version of {package_keyword}?\n"
                         f"Type Y(Yes) or N(No)").strip().lower()
    if make_pc_save == "n":
        exit(0)
    if make_pc_save != "y":
        exit(1)

    main_location = save_location_pc[package_keyword]
    if not os.path.exists(main_location):
        print("Balatro not found on PC")
        print("You can manually copy save files from this directory")
        exit(1)

    valid_pc_profiles = pkg_to_valid_pc_profiles[package_keyword]
    pc_profile_no = input(
        f"Enter the PC PROFILE NUMBER to OVERWRITE (choose from {', '.join(valid_pc_profiles)}): ").strip().lower()
    if pc_profile_no not in valid_pc_profiles:
        print("Error: This PC profile does not exist.")
        exit(1)
    warning_check = input(f"WARNING: This will overwrite you PC profile {pc_profile_no}!!"
                          "Are you sure you want to proceed? Type Y (yes) or N (no): ").strip().lower()
    if warning_check not in ['y', 'yes']:
        print("Operation cancelled by user.")
        exit(1)

    full_location = os.path.join(main_location, pc_profile_no)
    source_file_names = backup_file_names[package_keyword]
    dest_file_names = pc_file_names[package_keyword]
    flag = True
    for (idx, file) in enumerate(source_file_names):
        source_path = os.path.join(os.getcwd(), file)
        os.makedirs(full_location, exist_ok=True)
        destination_path = os.path.join(full_location, dest_file_names[idx])
        try:
            shutil.copy2(source_path, destination_path)
        except Exception as e:
            flag = False
            break
    if not flag:
        print(f"ERROR converting to PC save. Manually copy the files to {package_keyword} pc save location")
    else:
        print("Successfully copied Android save files to PC")


def take_backup(adb_cmd):
    # take backup if backup doesn't exist
    backup_exists = check_existing_backup()
    if not backup_exists:
        execute_command(f"{adb_cmd} backup -apk -f backup.ab com.playstack.balatro.android",
                        commence_msg=f"Taking backup. Confirm on your android device to proceed.",
                        error_msg="Backup failed", callback=check_successful_backup)
    else:
        exit(1)


def process_backup_files(java_cmd):
    # use abe to convert to tar file
    execute_command(f"{java_cmd} -jar abe.jar unpack backup.ab backup.tar",
                    commence_msg="Unpacking backup to tar file", error_msg="Converting to tar failed",
                    callback=check_successful_ab2tar)

    # extract .tar file to 'extracted_backup' folder
    print("Extracting tar file")
    extract_to = 'extracted_backup'
    with tarfile.open("backup.tar", 'r') as tar:
        tar.extractall(path=extract_to)
    print(f"Successfully extracted tar files\n")


def finalize_android_backup():
    # copy save files to main folder
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
        exit(0)
    else:
        print("Backup successful. You can now disconnect your device.")
    print()


def android_to_pc_transfer():
    # Setup adb
    adb_cmd = setup_tool(
        tool_name="adb",
        exe_rel_path="adb.exe",
        download_url=adb_download_link,
        local_folder="platform-tools"
    )

    setup_device(adb_cmd)
    list_packages(adb_cmd)

    take_backup(adb_cmd)

    # Setup abe
    if not check_file_in_dir("abe.jar"):  # can create a function similar to setup_tools if needed but this works fine
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
        print()

    # Setup jdk
    java_cmd = setup_tool(
        tool_name="java",
        exe_rel_path=os.path.join("bin", "java.exe"),
        download_url=java_download_link,
        local_folder="jdk"
    )  # FIXME: Potential bug here (setup_tool tool path)

    process_backup_files(java_cmd)

    finalize_android_backup()


if __name__ == "__main__":
    android_to_pc_transfer()
    copy_backup_to_pc_folder()
