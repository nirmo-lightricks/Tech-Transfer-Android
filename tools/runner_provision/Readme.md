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
>gcloud config set-value project android-ci-286617

* Management of all python modules locally is done through pipenv. Howere it is installed through pip and requirements.txt. 
So whenever you install  a new python dependency with pipenv don't forget to run 
pipenv  lock -r > requirements.txt

# Upload github secret to secrets manager
This is needed for managing the github action runner
This needs to be done at first time

> gcloud services enable secretmanager.googleapis.com

create the secret. Take the "Android Runner App Access Token" secret value from 1password 

> printf "value of secret"| gcloud secrets create GITHUB_RUNNER_APP_TOKEN --data-file=-


# Creation of the image

## Creation of the GCP image

### Create the service account which runs the image
Needs just to be done in the first time
> gcloud iam service-accounts create gh-runner --display-name "Service account which runs the github actions"

Get the description of the secret needed:

> gcloud secrets versions describe latest --secret=GITHUB_RUNNER_APP_TOKEN

Add permisssions to this secret:
> gcloud projects add-iam-policy-binding android-ci-286617 --member=serviceAccount:gh-runner@android-ci-286617.iam.gserviceaccount.com --role=roles/secretmanager.secretAccessor --condition="expression=resource.name=='projects/24917401109/secrets/GITHUB_RUNNER_APP_TOKEN/versions/latest',title=Restrict access to GITHUB_RUNNER_APP_TOKEN" 

just change version 1 to latest

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
## Creation of the gcloud run image
> gcloud builds submit --tag gcr.io/android-ci-286617/gh-runner-admin

## Creation of the gcloud run service

> gcloud run deploy gh-runner-admin --image=gcr.io/android-ci-286617/gh-runner-admin --no-allow-unauthenticated --service-account=gh-runner-admin@android-ci-286617.iam.gserviceaccount.com --region=us-central1 --platform=managed

* --no-allow-unauthenticated means that just an authenticated user can run it It is very important to limit to a specific user because otherwise any person could run this cloud run through the http endpoint

The process will return a service url. In my case it was: https://gh-runner-admin-zwq4vjawda-uc.a.run.app 

## Create the user which invokes the cloud run

> gcloud iam service-accounts create gh-runner-admin-invoker --display-name "Invoker of cloud run gh-runner-admin"

## Giving it the right permissions
gcloud run services add-iam-policy-binding gh-runner-admin --member=serviceAccount:gh-runner-admin-invoker@android-ci-286617.iam.gserviceaccount.com --role=roles/run.invoker --region=us-central1 --platform=managed

## Creation of the google scheduler service

>  gcloud scheduler jobs create http gh-runner-admin-invoker --schedule "01 00 * * *" --http-method=GET --uri=https://gh-runner-admin-zwq4vjawda-uc.a.run.app  --oidc-service-account-email=gh-runner-admin-invoker@android-ci-286617.iam.gserviceaccount.com --oidc-token-audience=https://gh-runner-admin-zwq4vjawda-uc.a.run.app 

Unfortunately this created an app engine app (I hate app engine)
