# Filename: backend.tf

terraform {
  backend "gcs" {
    bucket  = "sara-project-v2-sara-documents-vault" # Use the exact name of your GCS bucket
    prefix  = "terraform/state"
  }
}