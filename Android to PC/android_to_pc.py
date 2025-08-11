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
save_location_pc = {"balatro": os.path.join(os.environ["APPDATA"], "Balatro")}
backup_file_names = {"balatro": ["1-meta.jkr", "1-profile.jkr"]}
pc_file_names = {"balatro": ["meta.jkr", "profile.jkr"]}
abe_download_link = "https://github.com/nelenkov/android-backup-extractor/releases/download/latest/abe-e252b0b.jar"
# TODO: make dynamic ^^^
adb_download_link = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
java_download_link = "https://adoptium.net/en-GB/download?link=https%3A%2F%2Fgithub.com%2Fadoptium%2Ftemurin17-" \
                     "binaries%2Freleases%2Fdownload%2Fjdk-17.0.16%252B8%2FOpenJDK17U-jdk_x64_windows_hotspot" \
                     "_17.0.16_8.zip&vendor=Adoptium"


# TODO: fix this ^^^


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


def setup_tool(tool_name, exe_rel_path, download_url, local_folder):
    """
    Ensure a portable tool is available.
    :param tool_name: Name to check in system PATH (e.g., "java", "adb")
    :param exe_rel_path: Relative path inside extracted folder to the executable (e.g., "bin/java.exe")
    :param download_url: URL to download ZIP containing the tool
    :param local_folder: Folder name to extract to inside script directory
    :return: Full command path as string, quoted if needed
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tool_dir = os.path.join(script_dir, local_folder)
    tool_bin = os.path.join(tool_dir, exe_rel_path)

    # If tool is already in PATH
    if shutil.which(tool_name):
        print(f"{tool_name} is already installed.\n")
        return tool_name

    # If local copy exists
    if os.path.exists(tool_bin):
        print(f"Using local {tool_name} from script directory.\n")
        return f"\"{tool_bin}\""

    # Download tool
    print(f"{tool_name} not found. Downloading from {download_url}...")
    response = requests.get(download_url, stream=True)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(tool_dir)

    # If it extracted into a subfolder, adjust path
    extracted_folders = [f.path for f in os.scandir(tool_dir) if f.is_dir()]
    if extracted_folders:
        # In case the actual tool is inside the first extracted subfolder
        maybe_bin = os.path.join(extracted_folders[0], exe_rel_path)
        if os.path.exists(maybe_bin):
            tool_bin = maybe_bin

    if not os.path.exists(tool_bin):
        print(f"Failed to install {tool_name}")
        exit(1)

    print(f"{tool_name} installed locally at {tool_bin}\n")
    return f"\"{tool_bin}\""


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
        exit(1)
    print()


def copy_backup_to_pc_folder():
    # transfer save files to balatro pc save location
    make_pc_save = input(f"Do you want to copy the extracted save to the pc version of {package_keyword}?\n"
                         f"WARNING: This will replace your Profile 1 PC save!"
                         f" Type Y(Yes) or N(No)").strip().lower()
    if make_pc_save == "n":
        exit(0)
    if make_pc_save != "y":
        exit(1)
    main_location = save_location_pc[package_keyword]
    # TODO: replace_save = input(f"Do you want to replace existing profile 1 save?"
    #                      f" Type Y to replace or N to create a new profile").lower()
    full_location = os.path.join(main_location, "1")
    # TODO: Handle keeping save case
    # TODO: Ensure destination folder exists
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


def backup_tool():
    # Setup adb
    adb_cmd = setup_tool(
        tool_name="adb",
        exe_rel_path="adb.exe",
        download_url=adb_download_link,
        local_folder="platform-tools"
    )

    # Setup jdk
    java_cmd = setup_tool(
        tool_name="java",
        exe_rel_path=os.path.join("bin", "java.exe"),
        download_url=java_download_link,
        local_folder="jdk"
    )

    # Check for device
    execute_command(f"{adb_cmd} devices", commence_msg="Checking connected devices...", print_std=False,
                    callback=device_connection_check)

    # list all packages
    execute_command(f"{adb_cmd} shell pm list packages",
                    commence_msg=f"Checking for package associated with {package_keyword} in device...",
                    callback=check_package)

    # take backup if backup doesn't exist
    backup_exists = check_existing_backup()
    if not backup_exists:
        execute_command(f"{adb_cmd} backup -apk -f backup.ab com.playstack.balatro.android",
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
        print()

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
        exit(0)
    else:
        print("Backup successful. You can now disconnect your device.")
    print()


if __name__ == "__main__":
    backup_tool()
    copy_backup_to_pc_folder()
