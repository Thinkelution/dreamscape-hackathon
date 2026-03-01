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

# Create production .env with backend URL
cat > .env.production <<EOF
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyD6qfA1PfrF5PZx7qSS0k00PYnn9vll034
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=dreamscape-hackathon.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=dreamscape-hackathon
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=dreamscape-hackathon.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=411432678431
NEXT_PUBLIC_FIREBASE_APP_ID=1:411432678431:web:15a0c7d640aa7fcf97d12a
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-JXMQE6ZBVY
EOF

npm run build

echo "--- Deploying to Firebase Hosting ---"
npx firebase deploy --only hosting --project "$PROJECT_ID"

cd ..

echo ""
echo "=== Deployment Complete ==="
echo "Backend: $BACKEND_URL"
echo "Frontend: https://${PROJECT_ID}.web.app"
