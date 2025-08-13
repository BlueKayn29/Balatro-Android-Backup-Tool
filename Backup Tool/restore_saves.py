import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'PC to Android'))  # for pc_to_android.py
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))  # for helper.py

from pc_to_android import *


def prepare_restore(android_profile_no):
    restorable_folder = "to_restore"
    base_names = pc_file_names[package_keyword]
    checklist = set()
    for file_name in os.listdir(restorable_folder):
        src = os.path.join(restorable_folder, file_name)
        dst = None
        for b in base_names:
            if file_name == b:
                dst = android_profile_no + "-" + b
                checklist.add(b)
                break
            elif file_name[2:] == b:
                dst = android_profile_no + "-" + file_name[2:]
                checklist.add(b)
                break
        if os.path.isfile(src) and dst:
            shutil.copy2(src, dst)
    if checklist != set(base_names):
        print("Couldn't find the files to be restored")
        exit(1)


if __name__ == "__main__":
    print("RESTORE BALATRO SAVE FILES TO ANDROID\n")
    print("Put your save files in current directory. The tool will otherwise fail")
    valid_android_profiles = pkg_to_valid_android_profiles[package_keyword]
    android_profile_no = input(f"Enter the ANDROID PROFILE NUMBER to restore to "
                               f"(choose from {', '.join(valid_android_profiles)}): ").strip()
    if android_profile_no not in valid_android_profiles:
        print("Error: This PC profile does not exist.")
        exit(1)
    print("WARNING: This will REPLACE the selected Android profile save with the backup save.")
    print("It is HIGHLY RECOMMENDED to BACKUP your Android profile before proceeding.\n")
    warning_check = input("Are you sure you want to proceed"
                          "? Type Y (yes) or N (no): ").strip().lower()
    if warning_check not in ['y', 'yes']:
        print("Operation cancelled by user.")
        exit(1)

    prepare_restore(android_profile_no)
    pc_to_android_transfer(android_profile_no)
