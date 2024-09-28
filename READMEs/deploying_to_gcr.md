# TLDR how to deploy a FastAPI as a Cloud Run Service

ToC

1. Create a repository in Google Artifact Registry
2. Add correct project id to cloudbuild.yaml
3. Upload entire project to Google Cloud Build and build an image
4. Check that the build was stored in Artifact Registry
5. Add correct project id to service.yaml
6. Create Cloud run service
7. Make service public

## 1 - Create a repository in Google Artifact Registry

- You have to create an image repository for storing your Docker images
  - https://console.cloud.google.com/artifacts/create-repo
  - call it `viti`
  - select `us-central1` as the region
  - leave everything else default

## 2 - Add correct project id to cloudbuild.yaml

```content of cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-f', 'Dockerfile', '-t', 'us-central1-docker.pkg.dev/<YOUR_GCP_PROJECT_ID>/viti/viti:latest', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/<YOUR_GCP_PROJECT_ID>/viti/viti:latest']
```

## 3 - Upload entire project to Google Cloud Build and build an image

- gcloud builds submit --region=us-central1 --config cloudbuild.yaml

## 4 - Check that the build was stored in Artifact Registry

https://console.cloud.google.com/artifacts/docker/<YOUR_GCP_PROJECT_ID>/us-central1/viti

## 5 - Add correct project id to service.yaml

```content of service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: viti-fastapi-service
spec:
  template:
    spec:
      containers:
        - image: us-central1-docker.pkg.dev/<YOUR_GCP_PROJECT_ID>/viti/viti
          ports:
            - containerPort: 8080
```

## 6 - Create Cloud run service

- gcloud run services replace service.yaml --region us-east1

## 7 - Make service public

gcloud run services set-iam-policy viti-fastapi-service service-policy.yaml --region us-east1