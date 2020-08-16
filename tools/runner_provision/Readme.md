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

* set default project as videoboost 
>gcloud config set-value project videoboost-32071

* Management of all python modules locally is done through pipenv. Howere it is installed through pip and requirements.txt. 
So whenever you install  a new python dependency with pipenv don't forget to run 
pipenv  lock -r > requirements.txt


# Creation of the image

## Creation of the GCP image

Download the packer_gcp_credentials.json from the vault

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
## Creation of the gcloud run image
> gcloud builds submit --tag gcr.io/videoboost-32071/gh-runner-admin

## Creation of the gcloud run service

> gcloud run deploy gh-runner-admin --image=gcr.io/videoboost-32071/gh-runner-admin --no-allow-unauthenticated --service-account=gh-runner-admin@videoboost-32071.iam.gserviceaccount.com --region=us-central1 --platform=managed

* The service account gh-runner-admin@videoboost-32071.iam.gserviceaccount.com comes already with the roles :Compute instance Admin and Service account user

* --no-allow-unauthenticated means that just an authenticated user can run it It is very important to limit to a specific user because otherwise any person could run thia cloud run through the http endpoint

The process will return a service url. In my case it was: https://gh-runner-admin-p3k6w4he2a-uc.a.run.app

## Create the user which invokes the cloud run

> gcloud iam service-accounts create gh-runner-admin-invoker --display-name "Invoker of cloud run gh-runner-admin"

## Giving it the right permissions
gcloud run services add-iam-policy-binding gh-runner-admin --member=serviceAccount:gh-runner-admin-invoker@videoboost-32071.iam.gserviceaccount.com --role=roles/run.invoker --region=us-central1 --platform=managed

## Creation of the google scheduler service

>  gcloud scheduler jobs create http gh-runner-admin-invoker --schedule "01 00 * * *" --http-method=GET --uri=https://gh-runner-admin-p3k6w4he2a-uc.a.run.app --oidc-service-account-email=gh-runner-admin-invoker@videoboost-32071.iam.gserviceaccount.com --oidc-token-audience=https://gh-runner-admin-p3k6w4he2a-uc.a.run.app

Unfortunately this created an app engine app (I hate app engine)
