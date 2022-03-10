gcloud config set project android-ci-286617
bq --location=us-central1 mk --dataset android-ci-286617:build_analytics
bq mk --table android-ci-286617:build_analytics.performance_statistics gradle_analytics.json

 gcloud iam service-accounts create gradle-analytics-executor --description="runs google cloud function which inserts gradle analytics into bigquery" --display-name="gradle analytics executor"


export GOOGLE_APPLICATION_CREDENTIALS=~/Downloads/android-ci-286617-21c2508387e7.json

gcloud projects add-iam-policy-binding android-ci-286617 --member="serviceAccount:gradle-analytics-executor@android-ci-286617.iam.gserviceaccount.com"  --role="roles/bigquery.dataEditor"

When prompted select condition none

gcloud functions deploy gradle_analytics_backend --entry-point gradle_analytics_to_bigquery --runtime python39  --trigger-http --allow-unauthenticated --service-account=gradle-analytics-executor@android-ci-286617.iam.gserviceaccount.com --max-instances=10


functions_framework --target=gradle_analytics_to_bigquery