'''
utility for sending slack messages without getting into problems of escaping
'''
from os import environ
import requests


def slack_message(text: str, webhook: str) -> None:
    '''
    sends text to webhook
    '''
    response = requests.post(webhook, json={"text": text})
    response.raise_for_status()


if __name__ == "__main__":
    slack_message(environ["text"], environ["webhook"])
