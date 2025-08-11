# ... (all previous content in app.tf is correct)

# Deploys the retrieval-service backend
resource "google_cloud_run_v2_service" "retrieval_service" {
  name     = "retrieval-service"
  location = var.region
  project  = module.project-services.project_id

  template {
    annotations = {
      # CORRECTED: Now references the fully configured database instance
      "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.main_configured[0].connection_name
    }
    service_account = google_service_account.runsa.email
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/sara-repo/sara-retrieval-service:latest"
      env {
        name  = "GCS_BUCKET_NAME"
        # CORRECTED: This now correctly references the resource, not a data source.
        value = google_storage_bucket.sara_vault.name
      }
      # ... (the rest of the file is correct)