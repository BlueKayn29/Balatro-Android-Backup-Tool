import io
import subprocess
import requests
import shutil
import os
import sys
import zipfile


package_keyword = "balatro"
package_keyword_to_name = {"balatro": "com.playstack.balatro.android"}
save_location = {"balatro": [f"extracted_backup/apps/com.playstack.balatro.android/f/1-meta.jkr",
                             f"extracted_backup/apps/com.playstack.balatro.android/f/1-profile.jkr"]}
save_location_pc = {"balatro": os.path.join(os.environ["APPDATA"], "Balatro")}
save_location_android = {"balatro": "files/"}
android_file_names = {"balatro": ["3-meta.jkr", "3-profile.jkr"]}
pc_file_names = {"balatro": ["meta.jkr", "profile.jkr"]}
adb_download_link = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
pkg_to_valid_pc_profiles = {"balatro": ["1", "2", "3"]}
pkg_to_valid_android_profiles = {"balatro": ["1", "2", "3"]}


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
        print(shutil.which("adb"))
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


def setup_device(adb_path):
    # Check for device
    execute_command(f"{adb_path} devices", commence_msg="Checking connected devices...", print_std=False,
                    callback=device_connection_check)


def list_packages(adb_path):
    execute_command(f"{adb_path} shell pm list packages",
                    commence_msg=f"Checking for package associated with {package_keyword} in device...",
                    callback=check_package)


def execute_command(command, verbose=True, commence_msg="Executing command", success_msg=None,
                    error_msg="Command failed", print_std=False, callback=None, print_cmd=False):
    if verbose:
        if commence_msg:
            print(commence_msg)
    if print_cmd:
        print("Command executed: ", command)
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
            print("STDERR: ", result.stderr)
    else:
        if verbose:
            print(error_msg)
        if print_std and verbose:
            print("STDOUT: ", result.stdout)
            print("STDERR: ", result.stderr)
    print()
