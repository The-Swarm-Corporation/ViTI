provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "cloud_run_api" {
  service = "run.googleapis.com"
  project = var.project_id
}

resource "google_project_service" "artifact_registry_api" {
  service = "artifactregistry.googleapis.com"
  project = var.project_id
}

resource "google_project_service" "iam_api" {
  service = "iam.googleapis.com"
  project = var.project_id
}

resource "google_project_service" "cloud_build_api" {
  service = "cloudbuild.googleapis.com"
  project = var.project_id
}

# Create a service account for Cloud Run deployment
resource "google_service_account" "cloud_run_sa" {
  account_id   = "cloud-run-deployer"
  display_name = "Cloud Run Deployer Service Account"
  project      = var.project_id
}

# Grant necessary roles to the service account
resource "google_project_iam_binding" "run_admin" {
  role    = "roles/run.admin"
  members = ["serviceAccount:${google_service_account.cloud_run_sa.email}"]
  project = var.project_id
}

resource "google_project_iam_binding" "artifact_registry_admin" {
  role    = "roles/artifactregistry.admin"
  members = ["serviceAccount:${google_service_account.cloud_run_sa.email}"]
  project = var.project_id
}

resource "google_project_iam_binding" "storage_admin" {
  role    = "roles/storage.admin"
  members = ["serviceAccount:${google_service_account.cloud_run_sa.email}"]
  project = var.project_id
}

# Create an Artifact Registry repository to store Docker images
resource "google_artifact_registry_repository" "docker_repo" {
  provider = google
  location = var.region
  repository_id = "docker-repo"
  format = "DOCKER"
  description = "Docker repository for Cloud Run"
  project = var.project_id
}

# Deploy the Cloud Run service
resource "google_cloud_run_service" "viti_inference_service" {
  name     = "viti-inference"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/viti:latest"
        resources {
          limits = {
            memory = "512Mi"
            cpu    = "1"
          }
        }
      }
      service_account_name = google_service_account.cloud_run_sa.email
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  autogenerate_revision_name = true
  project = var.project_id
}

# Allow unauthenticated access to Cloud Run
resource "google_cloud_run_service_iam_member" "noauth" {
  location    = google_cloud_run_service.viti_inference_service.location
  project     = google_cloud_run_service.viti_inference_service.project
  service     = google_cloud_run_service.viti_inference_service.name
  role        = "roles/run.invoker"
  member      = "allUsers"
}

# Outputs for Service URL and Service Account details
output "cloud_run_url" {
  value = google_cloud_run_service.viti_inference_service.status[0].url
}

output "service_account_email" {
  value = google_service_account.cloud_run_sa.email
}