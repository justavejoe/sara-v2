# Filename: storage.tf

resource "google_storage_bucket" "sara_vault" {
  # Bucket names must be globally unique, so we use the project ID as a prefix.
  name          = "${var.project_id}-sara-documents-vault"
  location      = var.region
  project       = var.project_id
  
  # Enforces uniform access control, a security best practice.
  uniform_bucket_level_access = true

  # Deletes incomplete uploads after 1 day to keep the bucket clean.
  lifecycle_rule {
    action {
      type = "AbortIncompleteMultipartUpload"
    }
    condition {
      age = 1 # CORRECTED ARGUMENT NAME
    }
  }
}