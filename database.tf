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

# Handle Database Instance
resource "google_sql_database_instance" "main" {
  count = var.database_type == "postgresql" ? 1 : 0

  name             = "sara-db-instance"
  database_version = "POSTGRES_15"
  region           = var.region
  project          = var.project_id

  timeouts {
    create = "30m"
    update = "30m"
  }

  settings {
    tier              = "db-custom-1-3840"
    disk_autoresize   = true
    disk_size         = 10
    disk_type         = "PD_SSD"
    user_labels       = var.labels
    ip_configuration {
      ipv4_enabled    = false
      # CORRECTED: Point to the actual network resource ID from network.tf
      private_network = google_compute_network.default.id
    }
    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "on"
    }
  }

  deletion_protection = var.deletion_protection
  # CORRECTED: Explicitly depend on the service networking connection being ready.
  depends_on = [google_service_networking_connection.private_service_access]
}

# Create Database
resource "google_sql_database" "database" {
  count = var.database_type == "postgresql" ? 1 : 0

  project         = var.project_id
  name            = var.db_name
  instance        = google_sql_database_instance.main[0].name
  deletion_policy = "ABANDON"
}

# Create Cloud SQL User
resource "google_sql_user" "service" {
  count = var.database_type == "postgresql" ? 1 : 0

  name            = var.db_user
  project         = var.project_id
  instance        = google_sql_database_instance.main[0].name
  password        = random_password.password.result
  deletion_policy = "ABANDON"
}

# Create SQL integration to Vertex AI
resource "google_project_iam_member" "vertex_integration" {
  count = var.database_type == "postgresql" ? 1 : 0

  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_sql_database_instance.main[0].service_account_email_address}"
}