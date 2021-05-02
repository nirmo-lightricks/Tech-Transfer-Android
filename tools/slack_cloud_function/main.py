"""
google cloud function to send audit log to slack
"""
import base64
import json
from typing import Any, cast, Dict
import requests
from google.cloud import secretmanager_v1  # type: ignore


def _get_slack_webhook() -> str:
    client = secretmanager_v1.SecretManagerServiceClient()
    path = secretmanager_v1.SecretManagerServiceClient.secret_version_path(
        "android-ci-286617", "SLACK_ANDROID_CI_NOTIFICATION_WEBHOOK", "latest"
    )

    secret_value = client.access_secret_version(
        request={"name": path}
    ).payload.data.decode("UTF-8")
    return cast(str, secret_value)


def _slack_message(text: str, webhook: str) -> None:
    """
    sends text to webhook
    """
    response = requests.post(webhook, json={"text": text})
    response.raise_for_status()


def slack_pubsub(event: Dict[str, str], context: Any) -> None:
    """
    main function which is run by google cloud function
    """
    pubsub_message = base64.b64decode(event["data"]).decode("utf-8")
    pubsub_object = json.loads(pubsub_message)
    error_message = json.dumps(pubsub_object["protoPayload"], indent=4, sort_keys=True)
    message = f"got error message from audit log: {error_message}"
    webhook = _get_slack_webhook()
    _slack_message(message, webhook)
