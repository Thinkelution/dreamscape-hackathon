#!/bin/bash
set -euo pipefail

PROJECT_ID="dreamscape-hackathon"
REGION="us-central1"
REPO="dreamscape-repo"
SA="backend@${PROJECT_ID}.iam.gserviceaccount.com"

echo "=== Dreamscape Deployment ==="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Ensure gcloud is pointing to the right project
gcloud config set project "$PROJECT_ID"

# ---- Backend ----
echo "--- Building backend Docker image ---"
cd backend
gcloud builds submit \
  --tag "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/dreamscape-backend:latest" \
  --project "$PROJECT_ID"

echo "--- Deploying backend to Cloud Run ---"
gcloud run deploy dreamscape-backend \
  --image "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/dreamscape-backend:latest" \
  --service-account "$SA" \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_API_KEY=$(gcloud secrets versions access latest --secret=gemini-api-key --project=$PROJECT_ID 2>/dev/null || echo $GOOGLE_API_KEY)" \
  --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID" \
  --set-env-vars "GCS_BUCKET_NAME=dreamscape-media" \
  --memory 1Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 3

BACKEND_URL=$(gcloud run services describe dreamscape-backend --region "$REGION" --project "$PROJECT_ID" --format 'value(status.url)')
echo "Backend deployed at: $BACKEND_URL"

cd ..

# ---- Frontend ----
echo "--- Building and deploying frontend ---"
cd frontend

# Ensure .env.local exists with Firebase config (not committed to repo)
if [ ! -f .env.local ]; then
  echo "ERROR: frontend/.env.local not found. Copy from .env.example and fill in your Firebase config."
  exit 1
fi

npm run build

echo "--- Deploying to Firebase Hosting ---"
npx firebase deploy --only hosting --project "$PROJECT_ID"

cd ..

echo ""
echo "=== Deployment Complete ==="
echo "Backend: $BACKEND_URL"
echo "Frontend: https://${PROJECT_ID}.web.app"
