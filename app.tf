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

# Applies project-level permissions to the Cloud Run SA
resource "google_project_iam_member" "allrun" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/run.invoker",
    "roles/aiplatform.user",
    "roles/iam.serviceAccountTokenCreator",
    "roles/secretmanager.secretAccessor",
    "roles/storage.objectAdmin",
  ])

  project = module.project-services.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.runsa.email}"
}

# Deploys the retrieval-service backend
resource "google_cloud_run_v2_service" "retrieval_service" {
  name                = "retrieval-service"
  location            = var.region
  project             = module.project-services.project_id
  deletion_protection = var.deletion_protection

  template {
    annotations = {
      "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.main[0].connection_name
    }

    service_account = google_service_account.runsa.email
    labels          = var.labels

    containers {
      image = "us-central1-docker.pkg.dev/${var.project_id}/sara-repo/retrieval-service:latest"
      
      env {
        name  = "GCS_BUCKET_NAME"
        value = data.google_storage_bucket.sara_vault.name
      }
      env {
        name  = "DB_PROJECT"
        value = var.project_id
      }
      env {
        name  = "DB_REGION"
        value = var.region
      }
      env {
        name  = "DB_INSTANCE"
        value = google_sql_database_instance.main[0].name
      }
      env {
        name  = "DB_NAME"
        value = google_sql_database.main[0].name
      }
      env {
        name  = "DB_USER"
        value = google_sql_user.service[0].name
      }
      env {
        name = "DB_PASSWORD"
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
        tags       = ["direct-vpc-egress"]
      }
      egress = "PRIVATE_RANGES_ONLY"
    }
  }

  depends_on = [
    google_project_iam_member.allrun
  ]
}

# Deploys the frontend-service
resource "google_cloud_run_v2_service" "frontend_service" {
  name                = "frontend-service"
  location            = var.region
  project             = module.project-services.project_id
  deletion_protection = var.deletion_protection

  template {
    service_account = google_service_account.runsa.email
    labels          = var.labels

    containers {
      image = "us-central1-docker.pkg.dev/${var.project_id}/sara-repo/frontend-service:latest"
      env {
        name  = "SERVICE_URL"
        value = google_cloud_run_v2_service.retrieval_service.uri
      }
    }
  }

  depends_on = [
    google_project_iam_member.allrun
  ]
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