/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

# Creates a single Service Account to be used by both Cloud Run services
resource "google_service_account" "runsa" {
  project      = module.project-services.project_id
  account_id   = "sara-run-sa"
  display_name = "SARA Cloud Run Service Account"
}

# Grant the service account access to the SQL password secret
resource "google_secret_manager_secret_iam_member" "password_accessor" {
  project   = google_secret_manager_secret.cloud_sql_password.project
  secret_id = google_secret_manager_secret.cloud_sql_password.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runsa.email}"
}

# Grant the service account access to the Cloud SQL instance
resource "google_project_iam_member" "sql_client" {
  project = module.project-services.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.runsa.email}"
}

# Grant the service account access to Vertex AI
resource "google_project_iam_member" "ai_user" {
  project = module.project-services.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.runsa.email}"
}

# Deploys the retrieval-service backend
resource "google_cloud_run_v2_service" "retrieval_service" {
  name     = "retrieval-service"
  location = var.region
  project  = module.project-services.project_id

  template {
    annotations = {
      "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.main[0].connection_name
    }
    service_account = google_service_account.runsa.email
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/sara-repo/sara-retrieval-service:latest"
      env {
        name  = "GCS_BUCKET_NAME"
        value = google_storage_bucket.sara_vault.name
      }
      env {
        name  = "DB_NAME"
        value = google_sql_database.database[0].name
      }
      env {
        name  = "DB_USER"
        value = google_sql_user.service[0].name
      }
      env {
        name = "DB_PASSWORD_SECRET"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.cloud_sql_password.secret_id
            version = "latest"
          }
        }
      }
    }
    vpc_access {
      network_interfaces {
        network    = google_compute_network.main.id
        subnetwork = google_compute_subnetwork.subnetwork.id
      }
      egress = "ALL_TRAFFIC"
    }
  }
}

# Deploys the frontend-service
resource "google_cloud_run_v2_service" "frontend_service" {
  name     = "frontend-service"
  location = var.region
  project  = module.project-services.project_id

  template {
    service_account = google_service_account.runsa.email
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/sara-repo/sara-frontend-service:latest"
      env {
        name  = "SERVICE_URL"
        value = google_cloud_run_v2_service.retrieval_service.uri
      }
    }
  }
}

# Allows the frontend service to securely call the backend retrieval service.
resource "google_cloud_run_v2_service_iam_member" "retrieval_service_invoker" {
  project  = google_cloud_run_v2_service.retrieval_service.project
  location = google_cloud_run_v2_service.retrieval_service.location
  name     = google_cloud_run_v2_service.retrieval_service.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.runsa.email}"
}

# Sets the frontend service to be publicly accessible
resource "google_cloud_run_v2_service_iam_member" "noauth_frontend" {
  project  = google_cloud_run_v2_service.frontend_service.project
  location = google_cloud_run_v2_service.frontend_service.location
  name     = google_cloud_run_v2_service.frontend_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}