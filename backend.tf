# Filename: backend.tf

terraform {
  backend "gcs" {
    # CORRECTED: This now points to the dedicated Terraform state bucket.
    bucket  = "sara-v2-tf-state-1b431b9d"
    prefix  = "terraform/state"
  }
}