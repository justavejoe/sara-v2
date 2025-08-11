# Filename: backend.tf

terraform {
  backend "gcs" {
    # This now correctly points to the dedicated Terraform state bucket
    # which is created in gcs_backend.tf
    bucket  = "sara-v2-tf-state-1b431b9d"
    prefix  = "terraform/state"
  }
}