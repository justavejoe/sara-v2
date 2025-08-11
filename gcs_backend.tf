# Filename: gcs_backend.tf

# This defines and creates the GCS bucket that will be used to store
# the Terraform state file itself. This must be a unique name.
resource "google_storage_bucket" "tfstate" {
  name          = "sara-v2-tf-state-1b431b9d" # Bucket from backend.tf
  location      = "US-CENTRAL1"
  force_destroy = true # Set to true for easier cleanup in non-production environments
  
  # Enable Uniform Bucket-Level Access for simpler IAM management
  uniform_bucket_level_access = true

  # Enable versioning to keep a history of your state files
  versioning {
    enabled = true
  }
}