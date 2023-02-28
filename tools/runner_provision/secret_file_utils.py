"""
Unfortunately github actions do not have secret files as in jenkins, so i need to workaround here.
In order to get a binary secret file we have to do the following:
1. Encode it to base64 and ask a github administrator to set it as secret BIN_TO_TEXT
2. In the runner return it to binary and write it to a file TEXT_TO_BIN

For a normal text file it is easier because we have just to write it to a file ENV_TO_TEXT
"""
import base64
import argparse
import os
from tempfile import mkstemp

BIN_TO_TEXT = "bin2text"
TEXT_TO_BIN = "text2bin"
ENV_TO_TEXT = "env2text"


def encode_file(file_path: str) -> str:
    """
    takes a binary file and encodes it to base64
    """
    with open(file_path, "rb") as fh:
        binary = fh.read()
        return base64.b64encode(binary).decode()


def decode_file(env_variable: str) -> str:
    """
    takes an env file with the base64 content, writes its binary content to
    a temp file and returns it's path
    """
    base64_content = os.environ[env_variable]
    if not base64_content.strip():
        raise AssertionError(f"{env_variable} is empty")
    binary_content = base64.b64decode(base64_content)
    fd, filepath = mkstemp()
    with open(fd, "wb") as fh:
        fh.write(binary_content)
    return filepath


def env_variable_to_file(env_variable: str) -> str:
    """
    takes an env file with text content, writes its binary content to a
    temp file and returns it's path
    """
    content = os.environ[env_variable]
    if not content.strip():
        raise AssertionError(f"{env_variable} is empty")
    fd, filepath = mkstemp()
    with open(fd, "w") as fh:
        fh.write(content)
    return filepath


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=[BIN_TO_TEXT, ENV_TO_TEXT, TEXT_TO_BIN])
    parser.add_argument("data")
    args = parser.parse_args()
    if args.task == BIN_TO_TEXT:
        print(encode_file(args.data), end="")
    elif args.task == ENV_TO_TEXT:
        print(env_variable_to_file(args.data), end="")
    else:
        print(decode_file(args.data), end="")
