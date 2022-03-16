gcloud config set project android-ci-286617
bq --location=us-central1 mk --dataset android-ci-286617:build_analytics
bq mk --table android-ci-286617:build_analytics.performance_statistics gradle_analytics.json

 gcloud iam service-accounts create gradle-analytics-executor --description="runs google cloud function which inserts gradle analytics into bigquery" --display-name="gradle analytics executor"


export GOOGLE_APPLICATION_CREDENTIALS=~/Downloads/android-ci-286617-21c2508387e7.json

gcloud projects add-iam-policy-binding android-ci-286617 --member="serviceAccount:gradle-analytics-executor@android-ci-286617.iam.gserviceaccount.com"  --role="roles/bigquery.dataEditor"

When prompted select condition none

gcloud functions deploy gradle_analytics_backend --entry-point gradle_analytics_to_bigquery --runtime python39  --trigger-http --allow-unauthenticated --service-account=gradle-analytics-executor@android-ci-286617.iam.gserviceaccount.com --max-instances=10


functions_framework --target=gradle_analytics_to_bigquery

# Github Actions Connection

gcloud iam service-accounts create cloud-functions-deployer --description="deploys google cloud functions" --display-name="cloud functions deployer"

gcloud projects add-iam-policy-binding android-ci-286617 --member="serviceAccount:cloud-functions-deployer@android-ci-286617.iam.gserviceaccount.com"  --role="roles/cloudfunctions.admin"


 gcloud iam workload-identity-pools create ga-workpool --location="global" --display-name="Github Actions Pool" --description="Workload pool for facetune android github actions"

gcloud iam workload-identity-pools providers create-oidc "github-actions-provider" \
  --project="android-ci-286617" \
  --location="global" \
  --workload-identity-pool="ga-workpool" \
  --display-name="Github Actions Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.aud=assertion.aud" \
  --issuer-uri="https://token.actions.githubusercontent.com"


gcloud iam service-accounts add-iam-policy-binding "cloud-functions-deployer@android-ci-286617.iam.gserviceaccount.com" \
  --project="android-ci-286617" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/24917401109/locations/global/workloadIdentityPools/ga-workpool/attribute.repository/Lightricks/facetune-android"

