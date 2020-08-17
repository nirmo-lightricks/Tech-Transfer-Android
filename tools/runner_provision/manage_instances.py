'''
Actual class which manages the gcp instances. It uses googleapiclient which is a
really horrible library but unfortunately it is the best library available
'''
import datetime
import logging
import time
from constants import GCP_PROJECT_ID, GCP_ZONE, GCP_IMAGE_NAME, GCP_NUMBER_OF_INSTANCES
from googleapiclient.discovery import build, Resource  # type: ignore
from typing import List, Dict, cast

MACHINE_PREFIX = "gh-runner"

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def _get_old_instances(compute: Resource) -> List[Dict[str, str]]:
    instances_object = compute.instances()
    instance_response = instances_object.list(project=GCP_PROJECT_ID,
                                              zone=GCP_ZONE).execute()
    return [item for item in instance_response.get("items", [])
            if item["name"].startswith(MACHINE_PREFIX)]


def _create_instance(compute: Resource, image_name: str) -> Dict[str, str]:
    image_response = compute.images().get(project=GCP_PROJECT_ID,
                                          image=GCP_IMAGE_NAME).execute()
    source_disk_image = image_response['selfLink']
    machine_type = f"zones/{GCP_ZONE}/machineTypes/n2-standard-4"
    config = {
        'name': image_name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            },
            {
                'boot': False,
                'autoDelete': True,
                'initializeParams': {
                    'disk_type': 'local-ssd'
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'gh-runner@android-ci-286617.iam.gserviceaccount.com',
            'scopes': [
                "https://www.googleapis.com/auth/cloud-platform"
            ]
        }]
    }

    operation = compute.instances().insert(
        project=GCP_PROJECT_ID,
        zone=GCP_ZONE,
        body=config).execute()
    return cast(Dict[str, str], operation)


def _wait_for_operation(compute: Resource, operation: Dict[str, str]) -> Dict[str, str]:
    logging.info('Waiting for operation %s to finish...', operation)
    while True:
        result = compute.zoneOperations().get(
            project=GCP_PROJECT_ID,
            zone=GCP_ZONE,
            operation=operation["name"]).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return cast(Dict[str, str], result)

        time.sleep(1)


def _create_instances(compute: Resource, num_instances: int) -> List[Dict[str, str]]:
    operations = []
    today = datetime.date.today().isoformat()
    for image_num in range(num_instances):
        image_name = f"{MACHINE_PREFIX}-{today}-{image_num}"
        logging.info("creating new instance %s", image_name)
        create_operation = _create_instance(compute, image_name)
        operations.append(create_operation)
    return [_wait_for_operation(compute, operation) for operation in operations]


# pylint:disable=C0301


def _delete_old_instances(compute: Resource, old_instances: List[Dict[str, str]]) -> List[Dict[str, str]]:
    operations = []
    for instance in old_instances:
        logging.info("deleting instance %s", instance)
        delete_operation = compute.instances().delete(project=GCP_PROJECT_ID, zone=GCP_ZONE,
                                                      instance=instance["name"]).execute()
        operations.append(delete_operation)
    return [_wait_for_operation(compute, operation) for operation in operations]


def manage_instances(num_instances: int) -> Dict[str, List[Dict[str, str]]]:
    '''
    main function which creates the new instances and deletes the old ones
    '''
    compute = build('compute', 'v1', cache_discovery=False)
    old_instances = _get_old_instances(compute)
    logging.info("old instances are %s", old_instances)
    instances_res = _create_instances(compute, num_instances)
    logging.info("creating instances resulted in %s", instances_res)
    deletion_res = _delete_old_instances(compute, old_instances)
    logging.info("deleting instances resulted in %s", deletion_res)
    return {"creation_res": instances_res,
            "deletion_res": deletion_res}


if __name__ == "__main__":
    manage_instances(GCP_NUMBER_OF_INSTANCES)
