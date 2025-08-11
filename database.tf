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

# This block is required to configure the PostgreSQL provider.
# It tells the provider how to connect to the Cloud SQL instance
# by using the Cloud SQL Auth Proxy. It depends on the service
# account that Terraform is running as having the 'Cloud SQL Client' role.
provider "postgresql" {
  host            = google_sql_database_instance.main[0].private_ip_address
  port            = 5432
  username        = var.db_user
  password        = var.db_pass
  sslmode         = "disable"
  connect_timeout = 15
}

# Handle Database Instance
resource "google_sql_database_instance" "main" {
  count = var.database_type == "postgresql" ? 1 : 0

  name             = "sara-db-instance"
  database_version = "POSTGRES_15"
  region           = var.region
  project          = var.project_id

  settings {
    tier              = "db-custom-1-3840" # 1 CPU, 3.75GB Memory
    disk_autoresize   = true
    disk_size         = 10
    disk_type         = "PD_SSD"
    user_labels       = var.labels
    ip_configuration {
      ipv4_enabled    = false
      private_network = module.project-services.service_networking_network # Connect to the private network
    }
    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "on"
    }
  }

  deletion_protection = var.deletion_protection
}

# Create Database
resource "google_sql_database" "database" {
  count = var.database_type == "postgresql" ? 1 : 0

  project         = var.project_id
  name            = var.db_name # Use the variable from Cloud Build
  instance        = google_sql_database_instance.main[0].name
  deletion_policy = "ABANDON"
}

# Create Cloud SQL User
resource "google_sql_user" "service" {
  count = var.database_type == "postgresql" ? 1 : 0

  name            = var.db_user # Use the variable from Cloud Build
  project         = var.project_id
  instance        = google_sql_database_instance.main[0].name
  password        = random_password.password.result # Correctly reference the password resource
  deletion_policy = "ABANDON"
}

# Create SQL integration to Vertex AI
resource "google_project_iam_member" "vertex_integration" {
  count = var.database_type == "postgresql" ? 1 : 0

  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_sql_database_instance.main[0].service_account_email_address}"
}

# Grant necessary permissions to the database user
resource "postgresql_grant" "sara_user_grant" {
  count = var.database_type == "postgresql" ? 1 : 0

  database    = google_sql_database.database[0].name # Correctly reference the database resource
  role        = google_sql_user.service[0].name      # Correctly reference the user resource
  schema      = "public"
  object_type = "schema"
  privileges  = ["CREATE", "USAGE"]
  
  # Ensure this runs after the user has been created
  depends_on = [google_sql_user.service]
}