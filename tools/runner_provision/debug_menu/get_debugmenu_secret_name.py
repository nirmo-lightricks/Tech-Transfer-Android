"""
Used for debugmenu builds in order to get dynamic secret
"""
import argparse


def get_secret_name(app: str) -> str:
    """
    gets the name of the firebase secret depending on the app
    """
    if app == "swish":
        secret_prefix = "VIDEOBOOST"
    else:
        secret_prefix = app.upper()
    return secret_prefix + "_FIREBASE_APP_DISTRIBUTION_SERVICE_ACCOUNT"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("app", help="The application we want to get secret")
    args = parser.parse_args()
    secret_name = get_secret_name(args.app)
    print(secret_name, end="")
