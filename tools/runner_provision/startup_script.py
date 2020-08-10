#!/usr/bin/python3
'''
This script is used as startup script in the vm image
'''

import datetime
import logging
import os
import requests
import signal
import socket
# pylint: disable=C0301
from constants import API_URL, CONFIG_COMMAND, GH_RUNNER_PATH, LABELS, MOUNT_DEVICE, MOUNT_PATH, RUNNER_WORKDIR, \
    SHORT_URL, setup_environment
from google.cloud import secretmanager_v1  # type: ignore
from subprocess import run
from typing import cast

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def _mount_device() -> None:
    logging.info("mounting device %s to %s", MOUNT_DEVICE, MOUNT_PATH)
    # pylint: disable=C0301
    run(["mkfs.ext4", "-m", "0", "-E", "lazy_itable_init=0,lazy_journal_init=0,discard", MOUNT_DEVICE], check=True,
        input="\n", text=True)
    MOUNT_PATH.mkdir(parents=True)
    run(["mount", "-o", "discard,defaults",
         MOUNT_DEVICE, MOUNT_PATH.as_posix()], check=True)
    run(
        f"echo UUID=`blkid -s UUID -o value {MOUNT_DEVICE}` {MOUNT_PATH.as_posix()} ext4 discard,defaults,nofail 0 2 | tee -a /etc/fstab",
        shell=True, check=True)


def _get_runner_token() -> str:
    client = secretmanager_v1.SecretManagerServiceClient()
    name = client.secret_version_path(
        "711876413525", "GITHUB_RUNNER_APP_TOKEN", "latest")
    access_token = client.access_secret_version(
        name).payload.data.decode('UTF-8')
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {access_token}"
    }
    response = requests.post(API_URL, headers=headers)
    return cast(str, response.json()["token"])


def _start_runner() -> None:
    hostname = socket.gethostname()
    today = datetime.date.today().isoformat()
    runner_name = f"{hostname}-{today}"
    runner_token = _get_runner_token()
    logging.info("starting runner")
    run(
        [CONFIG_COMMAND,
         "--url", SHORT_URL,
         "--token", runner_token,
         "--name", runner_name,
         "--work", RUNNER_WORKDIR.absolute(),
         "--labels", LABELS,
         "--unattended",
         "--replace"
         ],
        check=True
    )
    os.chdir(GH_RUNNER_PATH.as_posix())
    run("bin/runsvc.sh", check=True)


def _remove_runner(signal_num: int, stack_frame) -> None:  # type: ignore
    logging.info("got signal %s and stack frame %s", signal_num, stack_frame)
    runner_token = _get_runner_token()
    logging.info("remove runner")
    run([CONFIG_COMMAND, "remove", "--token", runner_token], check=True)


def startup_script() -> None:
    '''
    main function which runs the startup seequence
    '''
    setup_environment()
    signal.signal(signal.SIGINT, _remove_runner)
    signal.signal(signal.SIGTERM, _remove_runner)
    if MOUNT_PATH.exists():
        logging.info("machine already configured")
    else:
        _mount_device()
    _start_runner()


if __name__ == "__main__":
    startup_script()
