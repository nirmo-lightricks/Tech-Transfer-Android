## Slack bot posting

All slack bot posting is made through the CI Notifications app.

You can add web hooks at https://api.slack.com/apps/A01DCJUBUA3/incoming-webhooks

The procedure is the following:

* Add a channel in the slack desktop app

* Add a webhook with the added channel

* save the webhook in 1password in the R&D-Android-CI vault

* tell barak weiss to add this as github actions secret

* Use it from github actions


