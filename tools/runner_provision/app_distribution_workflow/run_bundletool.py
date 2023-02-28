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
from subprocess import run

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)


def _first_char_lowercase(text: str) -> str:
    if not text:
        return text
    return text[0].lower() + text[1:]


def _get_required_apk_dir(apk_base_dir: Path, flavor: str, build_type: str) -> Path:
    if flavor:
        segments = [flavor, build_type]
    else:
        segments = [build_type]
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


def _extract_apk(apks_file: Path, apk_file: Path) -> None:
    logging.info("Extracting apk %s from apks %s", apk_file, apks_file)
    with zipfile.ZipFile(apks_file) as apks_fh:
        with apks_fh.open("universal.apk") as universal_fh, open(
            apk_file, "wb"
        ) as apk_fh:
            shutil.copyfileobj(universal_fh, apk_fh)


def run_bundletool(base_dir: str, build_type: str, flavor: str) -> None:
    """
    Main function which runs the whole workflow
    """
    build_dir = Path(base_dir, "build/outputs")
    bundle_dir = build_dir / "bundle"
    apk_base_dir = build_dir / "apk"
    aab_file = _get_aab_file(bundle_dir)
    logging.info("bundle file is %s", aab_file)
    apk_dir = _get_required_apk_dir(
        apk_base_dir=apk_base_dir, flavor=flavor, build_type=build_type
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
    parser.add_argument(
        "build_type", help="The build type. For example release or debugMenu"
    )
    # pylint:disable=C0301
    parser.add_argument(
        "-f",
        "--flavor",
        nargs="?",
        const="",
        help="flavor of application. For example gms or china. If no flavor is used pass an empty string",
    )
    args = parser.parse_args()
    build_type_arg = _first_char_lowercase(args.build_type)
    flavor_arg = _first_char_lowercase(args.flavor)
    run_bundletool(args.app, build_type_arg, flavor_arg)
