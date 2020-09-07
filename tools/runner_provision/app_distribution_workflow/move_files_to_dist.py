"""
Script which prepares all files to upload to skydive
"""
import argparse
import shutil
from glob import glob
from pathlib import Path
import logging

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)


def _copy_aab_files_to_dist(build_dir: Path, dist_dir: Path, run_number: str) -> None:
    bundle_dir = (build_dir / "bundle").as_posix()
    aab_files = [
        Path(path) for path in glob(f"{bundle_dir}/**/*-release.aab", recursive=True)
    ]
    for aab_file in aab_files:
        dest_file = dist_dir / f"{aab_file.stem}-{run_number}.aab"
        logging.info("Copying %s to %s", aab_file, dest_file)
        shutil.copy2(aab_file, dest_file)


def _copy_apk_files_to_dist(build_dir: Path, dist_dir: Path, run_number: str) -> None:
    apk_dir = (build_dir / "apk").as_posix()
    apk_files = [
        Path(path) for path in glob(f"{apk_dir}/**/*-release.apk", recursive=True)
    ]
    for apk_file in apk_files:
        dest_file = dist_dir / f"{apk_file.stem}-{run_number}.apk"
        logging.info("Copying %s to %s", apk_file, dest_file)
        shutil.copy2(apk_file, dest_file)


def _create_clean_dist_dir(dist_dir: Path) -> None:
    if dist_dir.exists():
        logging.info("Removing dir %s", dist_dir)
        shutil.rmtree(dist_dir)
    logging.info("Creating dir %s", dist_dir)
    dist_dir.mkdir(parents=True)


def _create_zip_files(build_dir: Path, dist_dir: Path) -> None:
    for directory in ["logs", "mapping"]:
        dest_file = (dist_dir / directory).as_posix()
        source_dir = build_dir / directory
        logging.info("Creating archive %s from %s", dest_file, source_dir)
        shutil.make_archive(dest_file, "zip", source_dir)


def archive_files(base_dir: str, run_number: str) -> None:
    """
    Function which prepares all relevant files for uploading to skydive
    """
    build_dir = Path(base_dir, "build/outputs")
    dist_dir = Path(base_dir, "build/dist")
    _create_clean_dist_dir(dist_dir)
    _create_zip_files(build_dir=build_dir, dist_dir=dist_dir)

    _copy_aab_files_to_dist(
        build_dir=build_dir, dist_dir=dist_dir, run_number=run_number
    )
    _copy_apk_files_to_dist(
        build_dir=build_dir, dist_dir=dist_dir, run_number=run_number
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("app", help="The application we want to add to dist")
    parser.add_argument("run_number", help="The run number")
    args = parser.parse_args()
    archive_files(args.app, args.run_number)
