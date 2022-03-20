"""
This is a google cloud function which pushes gradle analytics to bigquery
"""

import logging
from datetime import datetime
from typing import Any, cast, Dict, List, Optional, TypedDict
import functions_framework  # type: ignore
import flask
from google.cloud import bigquery  # type: ignore

BuildStep = TypedDict(
    "BuildStep",
    {
        "name": str,
        "status": str,
        "startTime": int,
        "endTime": int,
        "runningTime": int,
        "freshRun": bool,
    },
)

GithubActionsInfo = TypedDict(
    "GithubActionsInfo",
    {"workflowName": str, "runId": str, "branch": str, "owner": str},
)


GeneralParameters = TypedDict(
    "GeneralParameters",
    {
        "gitRepo": str,
        "hostname": str,
        "platform": str,
        "cores": int,
        "architecture": str,
        "xmx": int,
        "isCi": bool,
        "javaVersion": str,
        "gradleVersion": str,
        "agpVersion": str,
        "kotlinVersion": str,
        "androidStudioVersion": Optional[str],
        "githubActionsInfo": Optional[GithubActionsInfo],
        "hasGitChanged": bool,
        "taskNames": List[str],
    },
)

BuildAnalytics = TypedDict(
    "BuildAnalytics",
    {
        "id": str,
        "generalParameters": GeneralParameters,
        "buildSteps": List[BuildStep],
        "status": str,
        "startTime": int,
        "endTime": int,
        "runningTime": int,
    },
)


def _ms_to_datetime(time_in_ms: int) -> datetime:
    return datetime.fromtimestamp(time_in_ms / 1000)


def _json_to_bigquery_row(analytics: BuildAnalytics) -> Dict[str, Any]:
    general_parameters = analytics["generalParameters"]
    github_action_info = None
    github_action_info_obj = general_parameters.get("githubActionsInfo")
    if github_action_info_obj:
        github_action_info = {
            "workflow_name": github_action_info_obj["workflowName"],
            "run_id": github_action_info_obj["runId"],
            "branch": github_action_info_obj["branch"],
            "owner": github_action_info_obj["owner"],
        }
    build_steps = [
        {
            "name": step["name"],
            "status": step["status"],
            "start_time": _ms_to_datetime(step["startTime"]),
            "end_time": _ms_to_datetime(step["endTime"]),
            "running_time": step["runningTime"],
            "is_fresh_run": step["freshRun"],
        }
        for step in analytics["buildSteps"]
    ]

    return {
        "id": analytics["id"],
        "architecture": general_parameters["architecture"],
        "platform": general_parameters["platform"],
        "hostname": general_parameters["hostname"],
        "cores": general_parameters["cores"],
        "java_version": general_parameters["javaVersion"],
        "gradle_version": general_parameters["gradleVersion"],
        "kotlin_version": general_parameters["kotlinVersion"],
        "agp_version": general_parameters["agpVersion"],
        "android_studio_version": general_parameters.get("androidStudioVersion"),
        "javaXmx": general_parameters["xmx"],
        "is_ci": general_parameters["isCi"],
        "status": analytics["status"],
        "start_time": _ms_to_datetime(analytics["startTime"]),
        "end_time": _ms_to_datetime(analytics["endTime"]),
        "running_time": analytics["runningTime"],
        "git_repo": general_parameters["gitRepo"],
        "github_actions_info": github_action_info,
        "has_git_changed": general_parameters["hasGitChanged"],
        "root_task_names": general_parameters["taskNames"],
        "build_steps": build_steps,
    }


@functions_framework.http  # type: ignore
def gradle_analytics_to_bigquery(request: flask.Request) -> Any:
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    client = bigquery.Client()
    table_ref = client.dataset("build_analytics").table("performance_statistics")
    table = client.get_table(table_ref)
    row = _json_to_bigquery_row(cast(BuildAnalytics, request.get_json()))
    errors = client.insert_rows(table, [row])
    if errors:
        logging.error("got following error when inserting %s: %s", row, errors)
        return "developer error!", 400
    client.close()
    return "ok"
