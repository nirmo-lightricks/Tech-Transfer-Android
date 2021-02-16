"""
Runs packer of gcp.
* Creates specialized supervisord file for production vs staging
* Runs packer with production and staging parameter
"""

import argparse
import logging
from string import Template
from subprocess import run
from constants import GcpEnvironment


logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)


def _create_supervisord_file(github_runner_labels: str) -> None:
    template_file = "supervisord-gcp.conf.tmpl"
    out_file = "supervisord-gcp.conf"
    logging.info("Creating %s with label %s", out_file, github_runner_labels)
    with open(template_file, "r") as file:
        template_content = Template(file.read()).safe_substitute(
            {"labels": github_runner_labels}
        )

    with open(out_file, "w") as file:
        file.write(template_content)


def _run_packer(environment_label: str) -> None:
    environment = GcpEnvironment[environment_label.upper()]
    _create_supervisord_file(environment.github_runner_labels)
    packer_command = [
        "packer",
        "build",
        "-var",
        f"image_name={environment.image_name}",
        "-force",
        "packer-gcp.json",
    ]
    logging.info("run packer command %s", packer_command)
    run(packer_command, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("environment", choices=["production", "staging"])
    args = parser.parse_args()
    logging.info("working with environment %s", args.environment)
    _run_packer(args.environment)
