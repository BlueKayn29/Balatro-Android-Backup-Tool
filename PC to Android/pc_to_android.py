import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))  # for helper.py
from helper import *


def pc_to_working_dir(pc_profile_no, android_profile_no):
    # transfer save files from balatro pc save location to current working dir
    main_location = save_location_pc[package_keyword]
    full_location = os.path.join(main_location, pc_profile_no)
    source_file_names = pc_file_names[package_keyword]
    dest_file_names = android_profile_to_file_name(android_profile_no)
    # dest_file_names = android_file_names[package_keyword]
    flag = True
    for (idx, file) in enumerate(source_file_names):
        source_path = os.path.join(full_location, file)
        destination_path = os.path.join(os.getcwd(), dest_file_names[idx])
        try:
            shutil.copy2(source_path, destination_path)
        except Exception as e:
            flag = False
            break
    if not flag:
        print(f"ERROR copying files from pc save location to current directory.")
        exit(1)
    print()


def push_save(adb_cmd, android_profile_no=3):
    print("Transferring save files...")
    dest = save_location_android[package_keyword]
    package_name = package_keyword_to_name[package_keyword]
    android_file_names = android_profile_to_file_name(android_profile_no)

    for file_name in android_file_names:
        # (potential adb bug: adb push may fail or truncate the filename if the target filename is omitted)
        execute_command(f"{adb_cmd} push {file_name} /data/local/tmp/{file_name}", commence_msg=None)
        execute_command(f"{adb_cmd} shell run-as {package_name} cp /data/local/tmp/{file_name} {dest}",
                        commence_msg=".")
    print()


def pc_to_android_transfer(android_profile_no):
    # transfer save files from current dir to android save location via adb (debuggable app required?)

    adb_cmd = setup_tool(
        tool_name="adb",
        exe_rel_path="adb.exe",
        download_url=adb_download_link,
        local_folder="platform-tools"
    )
    setup_device(adb_cmd)
    list_packages(adb_cmd)
    push_save(adb_cmd, android_profile_no)


if __name__ == "__main__":
    print("Initiating file transfer to Android device.\n")
    print("You will be asked to select a PC profile to copy and an Android profile to overwrite.")
    print("WARNING: This will REPLACE the selected Android profile with the PC profile.")
    print("It is HIGHLY RECOMMENDED to BACKUP your Android profile before proceeding.\n")

    valid_pc_profiles = pkg_to_valid_pc_profiles[package_keyword]
    valid_android_profiles = pkg_to_valid_android_profiles[package_keyword]
    pc_profile_no = input(f"Enter the PC PROFILE NUMBER to copy "
                          f"(choose from {', '.join(valid_pc_profiles)}): ").strip()
    if pc_profile_no not in valid_pc_profiles:
        print("Error: This PC profile does not exist.")
        exit(1)

    android_profile_no = input(
        f"Enter the ANDROID PROFILE NUMBER to overwrite (choose from {', '.join(valid_android_profiles)}): ").strip()
    if android_profile_no not in valid_android_profiles:
        print("Error: This Android profile does not exist.")
        exit(1)

    warning_check = input("Are you sure you want to proceed"
                          "(Read the above warning)? Type Y (yes) or N (no): ").strip().lower()
    if warning_check not in ['y', 'yes']:
        print("Operation cancelled by user.")
        exit(1)

    pc_to_working_dir(pc_profile_no, android_profile_no)
    pc_to_android_transfer(android_profile_no)
    print("Successfully transferred save files to android. You can now disconnect your device")