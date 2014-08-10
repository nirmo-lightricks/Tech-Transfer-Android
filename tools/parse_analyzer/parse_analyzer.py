import json
import datetime

filename = "_Installation.json"
file = open(filename)

data = json.load(file)
file.close()

i = 1
for entry in data["results"]:
    if "advertisingId" not in entry:
        created = datetime.datetime.strptime(entry["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
        updated = datetime.datetime.strptime(entry["updatedAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
        if created != updated:
            print i, entry["objectId"], entry["appVersion"]
            i += 1
