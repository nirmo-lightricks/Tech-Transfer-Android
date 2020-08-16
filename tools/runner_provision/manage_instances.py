import datetime
import logging
import time
from constants import GCP_PROJECT_ID, GCP_ZONE, GCP_IMAGE_NAME, GCP_NUMBER_OF_INSTANCES
from googleapiclient.discovery import build

MACHINE_PREFIX = "gh-runner"

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def get_old_instances(compute):
    instances_object = compute.instances()
    instance_response = instances_object.list(project=GCP_PROJECT_ID,
                                              zone=GCP_ZONE).execute()
    return [item for item in instance_response.get("items", []) if item["name"].startswith(MACHINE_PREFIX)]


def create_instance(compute, image_name):
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
            'email': 'default',
            'scopes': [
                "https://www.googleapis.com/auth/cloud-platform"
            ]
        }]
    }

    operation = compute.instances().insert(
        project=GCP_PROJECT_ID,
        zone=GCP_ZONE,
        body=config).execute()
    return operation


def wait_for_operation(compute, operation):
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
            return result

        time.sleep(1)


def create_instances(compute):
    operations = []
    today = datetime.date.today().isoformat()
    for image_num in range(GCP_NUMBER_OF_INSTANCES):
        image_name = f"{MACHINE_PREFIX}-{today}-{image_num}"
        logging.info("creating new instance %s", image_name)
        create_operation = create_instance(compute, image_name)
        operations.append(create_operation)
    return [wait_for_operation(compute, operation) for operation in operations]


def delete_old_instances(compute, old_instances):
    operations = []
    for instance in old_instances:
        logging.info("deleting instance %s", instance)
        delete_operation = compute.instances().delete(project=GCP_PROJECT_ID, zone=GCP_ZONE,
                                                      instance=instance["name"]).execute()
        operations.append(delete_operation)
    return [wait_for_operation(compute, operation) for operation in operations]


def manage_instances():
    compute = build('compute', 'v1', cache_discovery=False)
    old_instances = get_old_instances(compute)
    logging.info("old instances are %s", old_instances)
    instances_res = create_instances(compute)
    logging.info("creating instances resulted in %s", instances_res)
    deletion_res = delete_old_instances(compute, old_instances)
    logging.info("deleting instances resulted in %s", deletion_res)
    return {"creation_res": instances_res,
            "deletion_res": deletion_res}


if __name__ == "__main__":
    manage_instances()
