# Copyright (c) 2019 Lightricks. All rights reserved.
# Created by Noam Freeman.

import collections
from enum import Enum

import MarkdownUtils

SLACK_CHANNEL_URL = "https://lightricks.slack.com/app_redirect?team=T03V4THAJ&channel=help-android-ci"

SLACK_CHANNEL_LINK = MarkdownUtils.markdown_link("#help-android-ci", SLACK_CHANNEL_URL)

COMMENT_HEADER = f"""
## Lightricks CI status

Something looks wrong? Not sure why your build fails? Contact us at {SLACK_CHANNEL_LINK}
"""

COMMENT_FOOTER = """
    
<p align="right">
Generated by the Lightricks android jenkins team :hammer:
</p>
"""

NOTHING_TO_REPORT = """
### Nothing to report for this build!
"""

def report_markdown(entries):
    modules = collections.defaultdict(list)
    if not modules:
        return COMMENT_HEADER + NOTHING_TO_REPORT + COMMENT_FOOTER
    for entry in entries:
        modules[entry.module].append(entry)

    table = \
        '\n'.join(_report_module(module.capitalize(), modules[module]) for module in modules.keys())
    return COMMENT_HEADER +  "<table>\n" + table +  "\n</table>\n" + COMMENT_FOOTER

class Status(Enum):
    OK = "OK"
    WARNING = "WARNING"
    ERROR = "ERROR"

    def emoji(self):
        return {Status.OK: ":white_check_mark:",
                Status.WARNING: ":warning:",
                Status.ERROR: ":x:"}[self]

ReportEntry = collections.namedtuple("ReportEntry", 'module status stage info details')

def _report_entry_markdown(entry):
    details_markdown = f"{ MarkdownUtils.details_tag('Details', entry.details) }" if entry.details else ""
    return f" {entry.status.emoji()} {entry.stage}: {entry.info}<br/>{details_markdown}"

def _report_module(module_caption, module_entries):
    module_report = ''.join(_report_entry_markdown(entry) for entry in module_entries)
    return f"<tr><td><b> {module_caption} </b></td><td> {module_report} </td></tr>\n"
