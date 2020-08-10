#!/usr/bin/python3
'''
This script provisions the ubuntu image
'''
import logging
import requests
import tarfile
import zipfile
# pylint: disable=C0301
from constants import ANDROID_SDK_ROOT, ANDROID_SDK_VERSION, GH_RUNNER_VERSION, GH_RUNNER_PATH, setup_environment
from pathlib import Path
from subprocess import run

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def _cmdline_tools() -> Path:
    return Path(ANDROID_SDK_ROOT, "cmdline-tools")


def _setup_cmdline_tools() -> None:
    logging.info("creating dir %s", _cmdline_tools())
    _cmdline_tools().mkdir(parents=True)
    # pylint: disable=C0301
    url = f"https://dl.google.com/android/repository/commandlinetools-linux-{ANDROID_SDK_VERSION}_latest.zip"
    logging.info("Downloading %s", url)
    response = requests.get(url)
    zip_file = "android_sdk_11111.zip"
    with open(zip_file, 'wb') as zip_fh:
        zip_fh.write(response.content)
    to_path = _cmdline_tools().absolute()
    logging.info("Extracting to %s", to_path)
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(to_path)
    # stupid workaround for python zipfile not preserving permissions
    run(["chmod", "-R", "777", _cmdline_tools().as_posix()], check=True)
    Path(zip_file).unlink()


def _install_android_sdk() -> None:
    sdk_components = [
        "build-tools;30.0.0", "build-tools;29.0.0", "build-tools;29.0.3", "build-tools;28.0.3",
        "cmake;3.10.2.4988404", "emulator", "ndk;21.0.6113669", "patcher;v4",
        "platforms;android-27", "platforms;android-28", "platforms;android-29",
        "platform-tools", "system-images;android-28;default;x86",
    ]
    logging.info("installing android sdk parts %s", sdk_components)
    sdkmanager_command = (_cmdline_tools() / "tools/bin/sdkmanager").absolute()
    run("yes | sdkmanager --licenses", shell=True, check=True)
    run([sdkmanager_command.as_posix()] + sdk_components, check=True)
    # this line should not exist. need to think why we need it
    run(["chmod", "-R", "777", ANDROID_SDK_ROOT], check=True)


def _install_github_actions() -> None:
    logging.info("installing github actions")
    # pylint: disable=C0301
    url = f"https://github.com/actions/runner/releases/download/v{GH_RUNNER_VERSION}/actions-runner-linux-x64-{GH_RUNNER_VERSION}.tar.gz"
    logging.info("Downloading url %s", url)
    response = requests.get(url)
    tgz_file = "actions.tgz"
    with open(tgz_file, 'wb') as tgz_fh:
        tgz_fh.write(response.content)
    to_path = GH_RUNNER_PATH.absolute()
    logging.info("Extracting to %s", to_path)
    tarfile.open(tgz_file, "r").extractall(to_path)
    Path(tgz_file).unlink()
    deps_command = GH_RUNNER_PATH / "bin/installdependencies.sh"
    run(deps_command.as_posix(), check=True)


def provision_machine() -> None:
    '''
    python script which provisions system
    '''
    setup_environment()
    _setup_cmdline_tools()
    _install_android_sdk()
    _install_github_actions()


if __name__ == "__main__":
    provision_machine()
