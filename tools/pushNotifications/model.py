
# Copyright (c) 2019 Lightricks. All rights reserved.
import json
import os
import re
from typing import Dict, List
import requests
from dataclasses import dataclass, asdict

# valid datetime regexp: 10:20 and 8:15 is valid but 10:0 is not valid
TIME_REGEXP = r'\d{1,2}:\d{2}'
ALL_CHANNELS = {'news', 'promotions'}

@dataclass
class PushMessageConfiguration():
    '''
    Describes the input of the program.
    This makes the module agnostic of it's execution environment.
    '''
    name: str
    language_file: str
    token_file: str
    title_key: str
    content_key: str
    channel: str
    image_url: str
    time: str
    video_url: str
    active_feature_id: str
    visible_feature_item_id: str
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
        if self.time and not re.match(TIME_REGEXP, self.time):
            raise Exception(
                f'time expression should be of format:{TIME_REGEXP} but is {self.time}')
        if self.video_url and not requests.head(self.video_url).ok:
            raise Exception(f'video url {self.video_url} is incorrect')
        if self.video_url and not requests.head(self.image_url).ok:
            raise Exception(f'video url {self.image_url} is incorrect')

@dataclass
class PushMessage:
    translations: Dict[str, List[str]]
    time: str
    channel: str
    name: str
    image_url: str
    video_url: str
    active_feature_id: str
    visible_feature_item_id: str
    def to_json(self)->str:
        return json.dumps(asdict(self))
