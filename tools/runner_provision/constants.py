"""
these are the constants controlling the proviision and startup script
"""
from os import environ
from pathlib import Path

ANDROID_SDK_ROOT = "/android-sdk"
ANDROID_SDK_VERSION = "6514223"
BUNDLETOOL_VERSION = "1.1.0"
GH_RUNNER_VERSION = "2.273.4"
GH_RUNNER_PATH = Path("/actions_runner")
CONFIG_COMMAND = GH_RUNNER_PATH / "config.sh"

MOUNT_PATH = Path("/mnt/disks/sdb")
MOUNT_DEVICE = "/dev/sdb"
RUNNER_WORKDIR = MOUNT_PATH / "runner_workspace"
LABELS = "android,gcloud"
SHORT_URL = "https://github.com/Lightricks"

API_URL = "https://api.github.com/orgs/Lightricks/actions/runners/registration-token"

GCP_PROJECT_ID = "android-ci-286617"
GCP_ZONE = "us-central1-a"
GCP_IMAGE_NAME = "github-action-runner-v1"
GCP_NUMBER_OF_INSTANCES = 2


def setup_environment() -> None:
    """
    sets all environment variables wich are needed for shell scripts run from here
    """
    env_variables = {
        "ANDROID_SDK_ROOT": ANDROID_SDK_ROOT,
        "ANDROID_HOME": ANDROID_SDK_ROOT,
        "ANDROID_SDK_VERSION": ANDROID_SDK_VERSION,
        "JAVA_HOME": "/usr/lib/jvm/java-8-openjdk-amd64",
        # pylint: disable=C0301
        "PATH": f"{environ['PATH']}:/snap/bin:{ANDROID_SDK_ROOT}/cmdline-tools/tools/bin:{ANDROID_SDK_ROOT}/platform-tools:{ANDROID_SDK_ROOT}/emulator",
        "GRADLE_USER_HOME": (MOUNT_PATH / "gradle_cache").as_posix(),
        "RUNNER_ALLOW_RUNASROOT": "1",
    }
    environ.update(env_variables)
