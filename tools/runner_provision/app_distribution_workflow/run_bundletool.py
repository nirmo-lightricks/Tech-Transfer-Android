"""
This scripit runs bundletool and puts the apk in the right location
"""
import argparse
import logging
import shutil
import zipfile
from glob import glob
from os import environ
from pathlib import Path
from re import finditer
from subprocess import run
from typing import List

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)


def _camel_case_split(identifier: str) -> List[str]:
    """
    split on camel case taken from brilliant answer: https://stackoverflow.com/a/29920015/2343743
    """
    matches = finditer(
        ".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", identifier
    )
    return [m.group(0) for m in matches]


def _get_required_apk_dir(bundle_dir: Path, apk_base_dir: Path, aab_file: Path) -> Path:
    aab_file_parts = aab_file.relative_to(bundle_dir).parts
    if len(aab_file_parts) != 2:
        raise Exception(
            "the assumed structure should be flavor/aabFile but is {aab_file_parts}"
        )
    segments = [
        name[0].lower() + name[1:] for name in _camel_case_split(aab_file_parts[0])
    ]
    return Path(apk_base_dir, *segments)


def _get_aab_file(bundle_dir: Path) -> Path:
    aab_files = glob(f"{bundle_dir.as_posix()}/**/*.aab")
    if len(aab_files) != 1:
        raise Exception("just exactly one aab is supported but got {aab_files}")
    return Path(aab_files[0])


def _run_bundle_command(aab_file: Path, apks_file: Path) -> None:
    command = [
        "java",
        "-jar",
        "/bundletool.jar",
        "build-apks",
        f"--bundle={aab_file.as_posix()}",
        f"--output={apks_file.as_posix()}",
        f"--ks={environ['KEYSTORE']}",
        f"--ks-pass=pass:{environ['KEYSTORE_PASSWORD']}",
        f"--key-pass=pass:{environ['KEY_PASSWORD']}",
        f"--ks-key-alias={environ['KEY']}",
        "--mode=universal",
    ]
    logging.info("bundletool command is %s", command)
    run(command, check=True)


# pylint:disable=C0330
def _extract_apk(apks_file: Path, apk_file: Path) -> None:
    logging.info("Extracting apk %s from apks %s", apk_file, apks_file)
    with zipfile.ZipFile(apks_file) as apks_fh:
        with apks_fh.open("universal.apk") as universal_fh, open(
            apk_file, "wb"
        ) as apk_fh:
            shutil.copyfileobj(universal_fh, apk_fh)


def run_bundletool(base_dir: str) -> None:
    """
    Main function which runs the whole workflow
    """
    build_dir = Path(base_dir, "build/outputs")
    bundle_dir = build_dir / "bundle"
    apk_base_dir = build_dir / "apk"
    aab_file = _get_aab_file(bundle_dir)
    logging.info("bundle file is %s", aab_file)
    apk_dir = _get_required_apk_dir(
        bundle_dir=bundle_dir, apk_base_dir=apk_base_dir, aab_file=aab_file
    )
    logging.info("apk dir is %s", apk_dir)
    apk_file_stem = apk_dir / f"{aab_file.stem}"
    logging.info("apk file stem is %s", apk_file_stem)
    apks_file = apk_file_stem.parent / (apk_file_stem.name + ".apks")
    apk_file = apk_file_stem.parent / (apk_file_stem.name + ".apk")
    _run_bundle_command(aab_file=aab_file, apks_file=apks_file)
    _extract_apk(apks_file=apks_file, apk_file=apk_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("app", help="The application we want to add to dist")
    args = parser.parse_args()
    run_bundletool(args.app)
