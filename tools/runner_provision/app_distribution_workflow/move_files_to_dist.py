"""
Script which prepares all files to upload to skydive
"""
import argparse
import shutil
from glob import glob
from pathlib import Path


def archive_files(base_dir: str, run_number: int) -> None:
    """
    Function which prepares all relevant files for uploading to skydive
    """
    build_dir = Path(base_dir, "build/outputs")
    dist_dir = Path(base_dir, "build/dist")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True)

    for directory in ["logs", "mapping"]:
        shutil.make_archive(
            (dist_dir / directory).as_posix(), "zip", (build_dir / directory)
        )

    bundle_dir = (build_dir / "bundle").as_posix()
    aab_files = [Path(path) for path in glob(f"{bundle_dir}/**/*-release.aab")]
    for aab_file in aab_files:
        dest_file = dist_dir / f"{aab_file.stem}-{run_number}.aab"
        shutil.copy2(aab_file, dest_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("app", help="The application we want to add to dist")
    parser.add_argument("run_number", help="The run number")
    args = parser.parse_args()
    archive_files(args.app, args.run_number)
