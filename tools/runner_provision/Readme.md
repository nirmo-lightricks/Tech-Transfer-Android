# Introduction

This folder contains all scripts to create and manage the android automation environment.

There are 2 flavors of the image:

* docker flavor

* gcp flavor 

Both images are created with the [packer program](https://www.packer.io/)

We use currently GCP but this could be changed in the future

There are different parts of the process

* Creation of the image

* Creation of the instances

* Startup script in the instance

# Prerequisites

* Need to have access to the R&D Android CI vault in 1password

* Install packer On mac packer can be installed with brew
> brew install packer

* Install gcloud commandline

* set default project as android-ci 
>gcloud config set project android-ci-286617

* Management of all python modules locally is done through pipenv. Howere it is installed through pip and requirements.txt. 
So whenever you install  a new python dependency with pipenv don't forget to run 
pipenv  lock -r > requirements.txt

# Upload github secret to secrets manager
This is needed for managing the github action runner
This needs to be done at first time

> gcloud services enable secretmanager.googleapis.com

create the secrets. Take the "Android Runner App Access Token" secret value from 1password 

> printf "value of secret"| gcloud secrets create GITHUB_RUNNER_APP_TOKEN --data-file=-

Take the "slack android ci notification webhook" secret value from 1password 

>printf "value of secret"| gcloud secrets create SLACK_ANDROID_CI_NOTIFICATION_WEBHOOK --data-file=-


# Creation of the image

## Creation of the secrets
This section should normally not be run but it may once break.

### Creation of GITHUB_RUNNER_APP_TOKEN
This command needs to be run: (It may need to be run by barak weiss or another github administrator)

> curl -X POST https://github.com/login/oauth/access_token?client_id=<app_client_id>&client_secret=<app_client_secret>&code=<your_code>

the access token is returned

the parameters are taken from : https://github.com/organizations/Lightricks/settings/apps/androidrunnermanager
* app_client_id is taken from Client ID field
* app_client_secret needs to be generated
* your_code is generated when uninstalling the app and installing again. then code is part of the url

### SLACK_ANDROID_CI_NOTIFICATION_WEBHOOK

It can be taken from https://api.slack.com/apps/A01DCJUBUA3/incoming-webhooks?
when creating a new web hook (which is unplausible) tthe changed web hook needs to be taken from here


## Creation of the GCP image

### Create the service account which runs the image
Needs just to be done in the first time
> gcloud iam service-accounts create gh-runner --display-name "Service account which runs the github actions"

Get the description of the secrets needed:

> gcloud secrets versions describe latest --secret=GITHUB_RUNNER_APP_TOKEN

Add permisssions to this secret:
> gcloud projects add-iam-policy-binding android-ci-286617 --member=serviceAccount:gh-runner@android-ci-286617.iam.gserviceaccount.com --role=roles/secretmanager.secretAccessor --condition="expression=resource.name=='projects/24917401109/secrets/GITHUB_RUNNER_APP_TOKEN/versions/latest',title=Restrict access to GITHUB_RUNNER_APP_TOKEN" 

just change version 1 to latest

> gcloud secrets versions describe latest --secret=SLACK_ANDROID_CI_NOTIFICATION_WEBHOOK

Add permisssions to this secret:

>gcloud projects add-iam-policy-binding android-ci-286617 --member=serviceAccount:gh-runner@android-ci-286617.iam.gserviceaccount.com --role=roles/secretmanager.secretAccessor --condition="expression=resource.name=='projects/24917401109/secrets/SLACK_ANDROID_CI_NOTIFICATION_WEBHOOK/versions/latest',title=Restrict access to SLACK_ANDROID_CI_NOTIFICATION_WEBHOOK"

Add permissions for sending logs to monitoring:

> gcloud projects add-iam-policy-binding android-ci-286617 --member=serviceAccount:gh-runner@android-ci-286617.iam.gserviceaccount.com --role=roles/monitoring.metricWriter --condition=None


### Creation of service acccount which runs packer

This has to be done first time

> gcloud iam service-accounts create packer --display-name "Packer creator of GCP VM images"

Now add permissions:

> gcloud projects add-iam-policy-binding android-ci-286617 --member=serviceAccount:packer@android-ci-286617.iam.gserviceaccount.com --role=roles/compute.instanceAdmin.v1 --condition=None

> gcloud projects add-iam-policy-binding android-ci-286617 --member=serviceAccount:packer@android-ci-286617.iam.gserviceaccount.com --role=roles/iam.serviceAccountUser --condition=None

Create json key file

> gcloud iam service-accounts keys create packer-credentials.json --iam-account=packer@android-ci-286617.iam.gserviceaccount.com

Store it in 1password as packer-credentials.json

### Enabling of the google compute api

This also has just to be done the first time. we need to enable google compute API

> gcloud services enable compute.googleapis.com

## Create the image 
Download the packer-gcp-credentials.json from the vault

>export GOOGLE_APPLICATION_CREDENTIALS=<path to the json file>

>packer build -force packer-gcp.json

-force means that the image will be replaced

This creates the image. The gcp instances are created every night at 0utc automatically through the runner admin explained below

## Creation of the docker image

The docker image is created with

>packer build  packer-docker.json

This way the docker image is pushed to a local repository. As the docker option is not used actively we have no workflow yet how to make all of this smooth

## Background

The interesting part of the image creation is done through the provisioners.

* install_os_dependencies.sh installs all apt dependencies and python dependencies

* setup_commands.py - installs android sdk and github action runner

# Creation of the instances 
The instances are created through the runner admin cloud scheduler. 

# Startup Script

The startup script is run through supervisord automatically. It registers a github runner. This is done through supervisord to enable  github action runner to update itself.


# Creation of the runner admin 
## Creation of gh-runner-admin user.
This is needed first time

> gcloud iam service-accounts create gh-runner-admin --display-name "Creates the gcp images through google cloud run"

Now add permissions:

> gcloud projects add-iam-policy-binding android-ci-286617 --member=serviceAccount:gh-runner-admin@android-ci-286617.iam.gserviceaccount.com --role=roles/compute.instanceAdmin.v1 --condition=None

> gcloud projects add-iam-policy-binding android-ci-286617 --member=serviceAccount:gh-runner-admin@android-ci-286617.iam.gserviceaccount.com --role=roles/iam.serviceAccountUser --condition=None

All the instance creation is done through github actions


# Add audit logs slacking
In order to get error messages from instance creation we need to do the following

Create a pubsub topic

> gcloud pubsub topics create audit-logging-error

Create a sink which catches these errors and publish them to the pubsub topic:

> gcloud logging sinks create audit_logs_error_sink pubsub.googleapis.com/projects/android-ci-286617/topics/audit-logging-error --log-filter='severity=(ERROR OR CRITICAL OR ALERT OR EMERGENCY) AND resource.type = "gce_instance"'

Give permissions to the logger account to be able to publish to the pubsub topic:

> gcloud beta pubsub topics add-iam-policy-binding audit-logging-error \
--member serviceAccount:p24917401109-567023@gcp-sa-logging.iam.gserviceaccount.com \
--role roles/pubsub.publisher

Give the service account of google cloud functions access to the webhook slack secret:
 
> gcloud projects add-iam-policy-binding android-ci-286617 --member=serviceAccount:android-ci-286617@appspot.gserviceaccount.com --role=roles/secretmanager.secretAccessor --condition="expression=resource.name=='projects/24917401109/secrets/SLACK_ANDROID_CI_NOTIFICATION_WEBHOOK/versions/latest',title=Restrict access to SLACK_ANDROID_CI_NOTIFICATION_WEBHOOK"

Finally deploy the google cloud function:
 
>cd tools/slack_cloud_function
>gcloud functions deploy slack_pubsub --runtime python39 --trigger-topic audit-logging-error
 
  


# Diagnosing issues with GCP:

The instances are at: https://console.cloud.google.com/compute/instances?project=android-ci-286617&instancessize=50
* Login into the problematic machine through ssh
* The interesting logs are /var/log/supervisor/ for supervisord and /actions_runner/_diag/ for github actions runner


# Upgrading 

## When to upgrade the image

All dependencies installed by install_os_dependencies.sh and setup_commands.py are hard coded into the image. If such 
a dependency needs to be updated the image needs to be created again.

## How the image is created

There is a job for it at: https://github.com/Lightricks/facetune-android/actions/workflows/packer_create_android_runner.yml

## Instructions on how to upgrade the image

* Make the dependency change

* Change the workflows which need to run the image by changing the label from android to android_staging and push

* Push the branch upstream. Github actions can only work on upstream images 

* Create a staging image

* Run the workflow

* Verify that the workflow runs well

* Change the workflow label back from android_staging to android 

* Get an approval

* Merge the PR

* Create the production image from develop

 
