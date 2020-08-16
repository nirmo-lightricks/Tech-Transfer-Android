import falcon
from manage_instances import manage_instances


class ManageInstancesResource:
    def on_get(self, req, resp):
        resp.media = manage_instances()


api = falcon.API()
api.add_route('/', ManageInstancesResource())
