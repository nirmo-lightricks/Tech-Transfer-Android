## Installation
1. install via pip:
    `pip install -r requirements.txt`

2. `export GOOGLE_APPLICATION_CREDENTIALS=<path to json>`


## Contribute
### lint
>mypy push_notification.py --strict --ignore-missing-imports
>pylint .

## Run

To see all options:
python push_notification.py --help

__Example:__
See `example/example.py`


## Find your device token

Write the following code in your `MainActivity`:
```
        FirebaseInstanceId.getInstance().getInstanceId().addOnSuccessListener(this, instanceIdResult -> {
            String newToken = instanceIdResult.getToken();
            Log.e("newToken", newToken);
            getPreferences(Context.MODE_PRIVATE).edit().putString("fb", newToken).apply();
        });
```
