# Copyright (c) 2019 Lightricks. All rights reserved.
# Created by Noam Freeman.

def hidden_html_tag(metadata):
    return f"<p align='right' metadata='{metadata}'></p>\n"

def details_tag(summary, details):
    return f"<details><summary>{summary}</summary><p>\n\n{details}\n</p></details>"

def markdown_link(text, link):
    return f'<a src="{link}>{text}</a>'

new_paragraph = "\n\n"