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

# Creates a secure, random password for the database user.
resource "random_password" "cloud_sql_password" {
  length  = 16
  special = true
}

# Creates a secret in Google Secret Manager to store the password.
resource "google_secret_manager_secret" "cloud_sql_password" {
  project   = module.project-services.project_id
  secret_id = "sara-cloud-sql-password-${random_id.id.hex}"

  # FINAL, DEFINITIVE FIX: This restores the correct user_managed replication
  # block, ensuring the secret is created in the same region as the app.
  # This syntax is required by your specific provider versions.
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }

  labels     = var.labels
  depends_on = [module.project-services]
}

# Creates a new version of the secret with the generated password.
resource "google_secret_manager_secret_version" "cloud_sql_password" {
  secret      = google_secret_manager_secret.cloud_sql_password.id
  secret_data = random_password.cloud_sql_password.result
}