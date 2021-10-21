#!/usr/bin/python3
"""
This script provisions the ubuntu image
"""
import argparse
import logging
import tarfile
import zipfile
from pathlib import Path
from subprocess import run
import requests
from constants import (
    ANDROID_SDK_ROOT,
    ANDROID_SDK_VERSION,
    BUNDLETOOL_VERSION,
    GH_RUNNER_VERSION,
    GH_RUNNER_PATH,
    MOUNT_PATH,
    setup_environment,
)

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)

DOCKER_TYPE = "docker"
GCP_TYPE = "gcp"


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
    with open(zip_file, "wb") as zip_fh:
        zip_fh.write(response.content)
    to_path = _cmdline_tools().absolute()
    logging.info("Extracting to %s", to_path)
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(to_path)
    # stupid workaround for python zipfile not preserving permissions
    run(["chmod", "-R", "777", _cmdline_tools().as_posix()], check=True)
    Path(zip_file).unlink()


def _install_android_sdk() -> None:
    sdk_components = [
        "build-tools;30.0.0",
        "build-tools;29.0.0",
        "build-tools;29.0.2",
        "build-tools;29.0.3",
        "build-tools;28.0.3",
        "cmake;3.10.2.4988404",
        "emulator",
        "ndk;21.4.7075529",
        "patcher;v4",
        "platforms;android-27",
        "platforms;android-28",
        "platforms;android-29",
        "platform-tools",
        "system-images;android-29;default;x86",
        "system-images;android-29;default;x86_64",
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
    with open(tgz_file, "wb") as tgz_fh:
        tgz_fh.write(response.content)
    to_path = GH_RUNNER_PATH.absolute()
    logging.info("Extracting to %s", to_path)
    tarfile.open(tgz_file, "r").extractall(to_path)
    Path(tgz_file).unlink()
    deps_command = GH_RUNNER_PATH / "bin/installdependencies.sh"
    run(deps_command.as_posix(), check=True)


def _download_bundle_tool() -> None:
    logging.info("Downloading bundle tool")
    # pylint: disable=C0301
    url = f"https://github.com/google/bundletool/releases/download/{BUNDLETOOL_VERSION}/bundletool-all-{BUNDLETOOL_VERSION}.jar"
    logging.info("Downloading url %s", url)
    response = requests.get(url)
    bundle_file = "/bundletool.jar"
    with open(bundle_file, "wb") as bundle_fh:
        bundle_fh.write(response.content)


def _create_dirs(machine_type: str) -> None:
    if machine_type == DOCKER_TYPE:
        MOUNT_PATH.mkdir(parents=True)


def _install_monitoring_agent() -> None:
    logging.info("Downloading monitoring agent")
    bash_file = "add-monitoring-agent-repo.sh"
    url = f"https://dl.google.com/cloudagents/{bash_file}"
    response = requests.get(url)
    response.raise_for_status()
    with open("add-monitoring-agent-repo.sh", "wb") as installation_file:
        installation_file.write(response.content)
    logging.info("running %s", bash_file)
    run(["bash", bash_file, "--also-install"], check=True)


def provision_machine(machine_type: str) -> None:
    """
    python script which provisions system
    """
    setup_environment()
    _setup_cmdline_tools()
    _install_android_sdk()
    _install_github_actions()
    _download_bundle_tool()
    _create_dirs(machine_type)
    _install_monitoring_agent()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("machine_type", choices=[DOCKER_TYPE, GCP_TYPE])
    args = parser.parse_args()
    provision_machine(args.machine_type)
