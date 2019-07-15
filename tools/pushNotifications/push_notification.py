# Copyright (c) 2019 Lightricks. All rights reserved.
'''
Module which makes push notifications.
The project is governed by GOGGLE_APPLICATION_CREDENTIALS environment variable.
This makes the module independent of the project and reusable.
'''
import argparse
import csv
import json
import logging
import re
import os.path
from collections import defaultdict
from typing import Dict, List
from dataclasses import dataclass
import firebase_admin
from firebase_admin import messaging
import requests
from more_itertools import chunked




logging.basicConfig(level=logging.INFO)

TOKENS_PER_FCM_CALL = 100
# valid datetime regexp: 10:20 and 8:15 is valid but 10:0 is not valid
TIME_REGEXP = r'\d{1,2}:\d{2}'
ALL_CHANNELS = {'news', 'promotions'}
DEFAULT_TRANSLATION = 'en'


@dataclass
class PushMessageConfiguration():
    '''
    Describes the input of the program.
    This makes the module agnostic of it's execution environment.
    '''
    language_file: str
    token_file: str
    title_key: str
    content_key: str
    channel: str
    image_url: str
    time: str
    video_url: str
    dry_run: bool = False

    def __post_init__(self) -> None:
        if not os.path.isfile(self.language_file):
            raise Exception(
                f'language_file {self.language_file} does not exist')
        if not os.path.isfile(self.token_file):
            raise Exception(f'token_file {self.token_file} does not exist')
        if not self.title_key:
            raise Exception('title_key missing')
        if not self.content_key:
            raise Exception('content_key missing')
        if  not  self.channel:
            raise Exception('channel is missing')
        if not self.channel in ALL_CHANNELS:
            raise Exception(f' channel should be one of {ALL_CHANNELS} but is {self.channel}')
        if not re.match(TIME_REGEXP, self.time):
            raise Exception(
                f'time expression should be of format:{TIME_REGEXP} but is {self.time}')
        if self.video_url and not requests.head(self.video_url).ok:
            raise Exception(f'video url {self.video_url} is incorrect')
        if self.video_url and not requests.head(self.image_url).ok:
            raise Exception(f'video url {self.image_url} is incorrect')

def _parse_language_file(language_file: str) -> Dict[str, Dict[str, str]]:
    translations: Dict[str, Dict[str, str]] = defaultdict(dict)
    with open(language_file, newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            key = row.pop('key')
            translations[key] = row
    return translations

def _get_tokens(token_file: str) -> List[str]:
    with open(token_file) as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)
        return [row[0] for row in csv_reader]

def _get_translation_with_fallback_to_en(translations: Dict[str, Dict[str, str]], title_key: str,
                                         content_key: str, lang: str) -> List[str]:
    return [
        translations[title_key].get(
            lang) or translations[title_key][DEFAULT_TRANSLATION],
        translations[content_key].get(
            lang) or translations[content_key][DEFAULT_TRANSLATION]
    ]

def _create_data_dict(push_message_configuration: PushMessageConfiguration) -> Dict[str, str]:
    language_db = _parse_language_file(push_message_configuration.language_file)
    all_languages = filter(None, language_db[push_message_configuration.title_key].keys())
    translation_dict = {
        language: _get_translation_with_fallback_to_en(
            language_db, push_message_configuration.title_key,
            push_message_configuration.content_key, language)
        for language in all_languages
    }
    data_dict = {
        'translations': json.dumps(translation_dict),
        'time': push_message_configuration.time,
        'channel': push_message_configuration.channel
    }
    if push_message_configuration.image_url:
        data_dict['image_url'] = push_message_configuration.image_url
    if push_message_configuration.image_url:
        data_dict['video_url'] = push_message_configuration.video_url

    return data_dict

def _send_multicast(token_chunk: List[str], data_dict: Dict[str, str]) -> None:
    message = messaging.MulticastMessage(tokens=token_chunk, data=data_dict)
    logging.info(f'Sending message for tokens:{token_chunk}')
    response = messaging.send_multicast(message)
    logging.info(
        f'success count: {response.success_count}, failure count: {response.failure_count}')
    for i, api_response in enumerate(response.responses):
        if api_response.success:
            logging.info(
                f'token: {token_chunk[i]}, message id: {api_response.message_id}, succcess')
        else:
            logging.info(
                f'token: {token_chunk[i]}, message id: {api_response.message_id} failed,  '
                + f'Exception: {api_response.exception}')

def send_push_messages(push_message_configuration: PushMessageConfiguration) -> None:
    '''
    main function of the module. Sens push messages according to PushMessageConfiguration
    '''
    firebase_admin.initialize_app()
    tokens = _get_tokens(push_message_configuration.token_file)
    data_dict = _create_data_dict(push_message_configuration)
    for token_chunk in chunked(tokens, TOKENS_PER_FCM_CALL):
        if push_message_configuration.dry_run:
            logging.info(f'Would have sent {data_dict} to {token_chunk}')
        else:
            try:
                _send_multicast(token_chunk, data_dict)
            except (messaging.ApiCallError, ValueError) as exception:
                logging.warning(f'Catched exception:{exception}')

def _create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('language_file')
    parser.add_argument('token_file')
    parser.add_argument('title_key')
    parser.add_argument('content_key')
    parser.add_argument('channel')
    parser.add_argument(
        '--time', help="when to run push notification locally. In format hh:mm")
    parser.add_argument('--image_url')
    parser.add_argument('--video_url')
    parser.add_argument('--dry_run', action='store_true', default=False)
    return parser

def _run_program() -> None:
    parser = _create_argument_parser()
    args = parser.parse_args()
    push_message_configuration = PushMessageConfiguration(language_file=args.language_file,
                                 token_file=args.token_file, channel=args.channel,
                                 title_key=args.title_key, content_key=args.content_key,
                                 image_url=args.image_url, time=args.time,
                                 video_url=args.video_url, dry_run=args.dry_run)
    send_push_messages(push_message_configuration)

if __name__ == '__main__':
    _run_program()
