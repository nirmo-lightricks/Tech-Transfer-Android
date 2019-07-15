install via pipenv:
>pipenv install --dev

lint with
>mypy push_notification.py --strict --ignore-missing-imports
>pylint  push_notification.py 

Run:
export GOOGLE_APPLICATION_CREDENTIALS=<path to json>
To see all options:
python push_notification.py --help
