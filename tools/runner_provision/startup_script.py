#!/usr/bin/python3
"""
This script is used as startup script in the vm image
"""

import argparse
import datetime
import logging
import os
import signal
import socket
import traceback
from subprocess import run
from typing import cast
import requests

# pylint: disable=C0301
from google.cloud import secretmanager_v1  # type: ignore
from constants import (
    API_URL,
    CONFIG_COMMAND,
    GCP_PROJECT_ID,
    GH_RUNNER_PATH,
    MOUNT_DEVICE,
    MOUNT_PATH,
    RUNNER_WORKDIR,
    SHORT_URL,
    setup_environment,
)

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)


def _mount_device() -> None:
    logging.info("mounting device %s to %s", MOUNT_DEVICE, MOUNT_PATH)
    # pylint: disable=C0301
    run(
        [
            "mkfs.ext4",
            "-m",
            "0",
            "-E",
            "lazy_itable_init=0,lazy_journal_init=0,discard",
            MOUNT_DEVICE,
        ],
        check=True,
        input="\n",
        text=True,
    )
    MOUNT_PATH.mkdir(parents=True)
    run(
        ["mount", "-o", "discard,defaults", MOUNT_DEVICE, MOUNT_PATH.as_posix()],
        check=True,
    )
    run(
        f"echo UUID=`blkid -s UUID -o value {MOUNT_DEVICE}` {MOUNT_PATH.as_posix()} ext4 discard,defaults,nofail 0 2 | tee -a /etc/fstab",
        shell=True,
        check=True,
    )


def _get_secret_string(secret_name: str) -> str:
    client = secretmanager_v1.SecretManagerServiceClient()
    secret_version_path = (
        f"projects/{GCP_PROJECT_ID}/secrets/{secret_name}/versions/latest"
    )
    secret_value = client.access_secret_version(
        request={"name": secret_version_path}
    ).payload.data.decode("UTF-8")
    return cast(str, secret_value)


def _get_runner_token() -> str:
    access_token = _get_secret_string("GITHUB_RUNNER_APP_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {access_token}",
    }
    response = requests.post(API_URL, headers=headers)
    response.raise_for_status()
    return cast(str, response.json()["token"])


def _start_runner(runner_labels: str) -> None:
    hostname = socket.gethostname()
    today = datetime.date.today().isoformat()
    runner_name = f"{hostname}-{today}"
    runner_token = _get_runner_token()
    logging.info("starting runner")
    os.chdir(GH_RUNNER_PATH.as_posix())
    run(
        [
            CONFIG_COMMAND,
            "--url",
            SHORT_URL,
            "--token",
            runner_token,
            "--name",
            runner_name,
            "--work",
            RUNNER_WORKDIR.absolute(),
            "--labels",
            runner_labels,
            "--unattended",
            "--replace",
        ],
        check=True,
    )
    run("bin/runsvc.sh", check=True)


def _remove_runner(signal_num: int, stack_frame) -> None:  # type: ignore
    logging.info("got signal %s and stack frame %s", signal_num, stack_frame)
    runner_token = _get_runner_token()
    logging.info("remove runner")
    run([CONFIG_COMMAND, "remove", "--token", runner_token], check=True)


def _startup_script(runner_labels: str) -> None:
    setup_environment()
    signal.signal(signal.SIGINT, _remove_runner)
    signal.signal(signal.SIGTERM, _remove_runner)
    if MOUNT_PATH.exists():
        logging.info("machine already configured")
    else:
        _mount_device()
    _start_runner(runner_labels)


def _slack_exception(exception: Exception, stack_trace: str) -> None:
    webhook = _get_secret_string("SLACK_ANDROID_CI_NOTIFICATION_WEBHOOK")
    data = {
        "text": f"Could not create runner! Got exception {exception}. Stack trace is: {stack_trace} This needs to be fixed immediately"
    }
    response = requests.post(webhook, json=data)
    response.raise_for_status()


def run_startup_script(runner_labels: str) -> None:
    """
    main function which runs the startup sequence
    """
    try:
        _startup_script(runner_labels)
    # pylint: disable=W0703
    except Exception as exception:
        stack_trace = traceback.format_exc()
        _slack_exception(exception, stack_trace)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("runner_labels")
    args = parser.parse_args()
    run_startup_script(args.runner_labels)
