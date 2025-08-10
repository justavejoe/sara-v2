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
      
      # --- START: Environment Variables ---
      env {
        name  = "GCS_BUCKET_NAME"
        value = data.google_storage_bucket.sara_vault.name
      }

      # --- FIX: Added these blocks for the new db.py ---
      env {
        name  = "DB_PROJECT"
        value