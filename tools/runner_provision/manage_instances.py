"""
Actual class which manages the gcp instances. It uses googleapiclient which is a
really horrible library but unfortunately it is the best library available
"""
import argparse
import datetime
import logging
import time
from itertools import zip_longest
from typing import List, Dict, cast
from googleapiclient.discovery import build, Resource  # type: ignore
from constants import GCP_PROJECT_ID, GCP_ZONE, GcpEnvironment

MACHINE_PREFIX = "gh-runner"

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)


def _get_old_instances(compute: Resource) -> List[Dict[str, str]]:
    instances_object = compute.instances()
    instance_response = instances_object.list(
        project=GCP_PROJECT_ID, zone=GCP_ZONE
    ).execute()
    return [
        item
        for item in instance_response.get("items", [])
        if item["name"].startswith(MACHINE_PREFIX)
    ]


def _create_instance_operation(
    compute: Resource, image_name: str, gcp_image_name: str
) -> Dict[str, str]:
    image_response = (
        compute.images().get(project=GCP_PROJECT_ID, image=gcp_image_name).execute()
    )
    source_disk_image = image_response["selfLink"]
    machine_type = f"zones/{GCP_ZONE}/machineTypes/n2-highmem-8"
    config = {
        "name": image_name,
        "machineType": machine_type,
        # Specify the boot disk and the image to use as a source.
        "disks": [
            {
                "boot": True,
                "autoDelete": True,
                "initializeParams": {
                    "sourceImage": source_disk_image,
                },
            },
            {
                "boot": False,
                "autoDelete": True,
                "type": "SCRATCH",
                "initializeParams": {
                    "disk_type": f"zones/{GCP_ZONE}/diskTypes/local-ssd"
                },
            },
        ],
        # Specify a network interface with NAT to access the public
        # internet.
        "networkInterfaces": [
            {
                "network": "global/networks/default",
                "accessConfigs": [{"type": "ONE_TO_ONE_NAT", "name": "External NAT"}],
            }
        ],
        # Allow the instance to access cloud storage and logging.
        "serviceAccounts": [
            {
                "email": "gh-runner@android-ci-286617.iam.gserviceaccount.com",
                "scopes": ["https://www.googleapis.com/auth/cloud-platform"],
            }
        ],
    }

    operation = (
        compute.instances()
        .insert(project=GCP_PROJECT_ID, zone=GCP_ZONE, body=config)
        .execute()
    )
    return cast(Dict[str, str], operation)


def _wait_for_operation(compute: Resource, operation: Dict[str, str]) -> Dict[str, str]:
    logging.info("Waiting for operation %s to finish...", operation)
    while True:
        result = (
            compute.zoneOperations()
            .get(project=GCP_PROJECT_ID, zone=GCP_ZONE, operation=operation["name"])
            .execute()
        )

        if result["status"] == "DONE":
            print("done.")
            if "error" in result:
                raise Exception(result["error"])
            return cast(Dict[str, str], result)

        time.sleep(1)


def _create_instance(
    compute: Resource, gcp_environment: GcpEnvironment, image_num: int
) -> Dict[str, str]:
    time_string = datetime.datetime.utcnow().strftime("%m-%d-%H-%M")
    image_name = (
        f"{MACHINE_PREFIX}-{time_string}-{gcp_environment.gcp_prefix}-{image_num}"
    )
    logging.info("creating new instance %s", image_name)
    create_operation = _create_instance_operation(
        compute, image_name, gcp_environment.image_name
    )

    return _wait_for_operation(compute, create_operation)


# pylint:disable=C0301
def _delete_old_instance(compute: Resource, instance: Dict[str, str]) -> Dict[str, str]:
    logging.info("deleting instance %s", instance)
    delete_operation = (
        compute.instances()
        .delete(project=GCP_PROJECT_ID, zone=GCP_ZONE, instance=instance["name"])
        .execute()
    )
    return _wait_for_operation(compute, delete_operation)


def manage_instances(
    num_instances: int, delete_old: bool, environment_label: str
) -> None:
    """
    main function which creates the new instances and deletes the old ones
    """
    environment = GcpEnvironment[environment_label.upper()]
    compute = build("compute", "v1", cache_discovery=False)
    old_instances = _get_old_instances(compute)
    logging.info("old instances are %s", old_instances)
    to_delete = old_instances if delete_old else []
    to_create_num = range(1, num_instances + 1)
    for instance_to_delete, instance_to_create_index in zip_longest(
        to_delete, to_create_num
    ):
        if instance_to_delete:
            deletion_res = _delete_old_instance(compute, instance_to_delete)
            logging.info("deleting instance resulted in %s", deletion_res)
        if instance_to_create_index:
            instance_res = _create_instance(
                compute, environment, instance_to_create_index
            )
            logging.info("creating instance resulted in %s", instance_res)

    if not delete_old:
        logging.info("Not deleting instances because flag was not set")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("instance_num", type=int, help="number of instances")
    parser.add_argument("delete_old", choices=["yes", "no"])
    parser.add_argument("environment", choices=["production", "staging"])
    args = parser.parse_args()
    manage_instances(args.instance_num, args.delete_old == "yes", args.environment)
