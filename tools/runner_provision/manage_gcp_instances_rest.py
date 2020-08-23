"""
This module runs every night in google cloud run and creates the gcp instances.
It can be called with num_instances to change the number of instances
"""
import falcon  # type: ignore
from falcon import Request, Response
from constants import GCP_NUMBER_OF_INSTANCES
from manage_instances import manage_instances


class ManageInstancesResource:
    """
    Represents the main resource
    """

    # pylint: disable=R0201,R0903

    def on_get(self, req: Request, resp: Response) -> None:
        """
        Handles all get calls
        """
        num_instances = req.get_param_as_int(
            "num_instances", min_value=0, max_value=30, default=GCP_NUMBER_OF_INSTANCES
        )
        resp.media = manage_instances(num_instances)


api = falcon.API()
api.add_route("/", ManageInstancesResource())
