import sys
import platform
import subprocess
import importlib.util


def get_option() -> int:
    while True:
        try:
            option = int(input("> "))
        except ValueError:
            print("Choose a valid option!")
        else:
            break
    return option


def get_info():
    return f"{platform.system()} {platform.release()}", platform.python_version()


def comp_ver():
    return sys.version_info >= (3, 11)


def install():
    print("\nChoose an installation method:")
    print("1. PyPI (Recommended)")
    print("2. GitHub (For contributors; requires Git)")
    installoption = get_option()
    if installoption not in [1, 2]:
        print("Please choose between 1 - 2!")
    if installoption == 1:
        pipinstall()
    elif installoption == 2:
        gitinstall()


def pipinstall():
    if not comp_ver():
        print("[!]Installation failed.")
        print(f"You're running Python {get_info()[1]}")
        return
    if importlib.util.find_spec("better_trace") is not None:
        print("better-trace is already installed!")
        return
    print("Installing better-trace...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "better-trace"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("✓ Installed successfully!")
    else:
        print("\n[!]Installation failed")
        print("Possible reasons:")
        print(
            "- No internet connection\n- pip is not working correctly\n- Permission denied\n- PyPI is temporarily unavailable"
        )
        print("\nFull output:")
        print(result.stderr)
    print("Returning to the menu...")
    return


def gitinstall():
    import shutil
    import pathlib

    if not comp_ver():
        print("[!]Installation failed.")
        print(f"You're running Python {get_info()[1]}")
        return

    if importlib.util.find_spec("better_trace") is not None:
        print("[!]Installation failed.")
        print("better-trace is already installed!")
        return
    if shutil.which("git") is None:
        print("[!]Installation failed.")
        print("Git is not installed or is not on PATH.")
        print("Please install Git and try again.")
        return
    folder = input("Clone directory (leave blank for current directory): ").strip()

    if not folder:
        folder = "."
    folder = pathlib.Path(folder)
    if not folder.exists():
        print("[!] Installation failed.")
        print("The specified directory does not exist.")
        return
    repo = folder / "better-trace"
    if repo.exists():
        print("[!]Installation failed.")
        print("Repo already exists! Please choose another folder")
        return
    result = subprocess.run(
        ["git", "clone", "https://github.com/8er8/better-trace.git"],
        cwd=folder,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("✓ Repository cloned!")
    else:
        print("[!]Installation failed.")
        print("\nPossible reasons:")
        print("- No internet connection")
        print("- GitHub is unavailable.")
        print("Output:")
        print(result.stderr)
        print("Returning to the menu...")
        return
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-e",
            ".",
        ],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("✓ Installed successfully!")
    else:
        print("\n[!]Installation failed")
        print("The repo was cloned successfully\nBut the installation failed.")
        print("Please check the output.")
        print("Output:")
        print(result.stderr)
    print("Returning to the menu...")
    return


print("╭─────────────────────────╮")
print("│    Better-Trace Setup   │")
print("╰─────────────────────────╯")
print("\nWelcome to better-trace! Please choose an option:")
print("1. Install")
print("2. Upgrade")
print("3. Uninstall")
print("4. Check compatibility")
print("5. Exit")
while True:
    option = get_option()
    if option not in [1, 2, 3, 4, 5]:
        print("Please choose between 1 - 5!")
    elif option == 1:
        install()
    elif option == 4:
        os_info, version = get_info()
        print(f" Operating System: {os_info}")
        print(f" Python version: {version}", end=" ")
        if comp_ver():
            print("— Supports better-trace!")
        else:
            print("— Doesn't support better-trace. (Requires Python 3.11 or above)")
    elif option == 5:
        print("Exiting...")
        break
