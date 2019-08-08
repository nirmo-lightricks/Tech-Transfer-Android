# Copyright (c) 2019 Lightricks. All rights reserved.
# Created by Nir Moshe.
import os

from push_notification import send_push_messages, PushMessageConfiguration

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secret.json"

params = {
    "language_file": "translations.csv",
    "token_file": "token.csv",
    "title_key": "hi",
    "content_key": "how_are_you",
    "channel": "news",
    "name": "push3",
    "image_url": "https://assets.pixaloopapp.com/android/production/assets/3CC34ECC-65CA-4DDA-83FD-8D382F6B117F",
    "dry_run": True,

    "video_url": "",
    "time": ""
}

if __name__ == "__main__":
    send_push_messages(PushMessageConfiguration(**params))
