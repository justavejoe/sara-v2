# Filename: backend.tf

terraform {
  backend "gcs" {
    # CORRECTED: This now points to the dedicated Terraform state bucket
    # that was being used in your Cloud Build environment.
    bucket  = "sara-v2-tf-state-1b431b9d" 
    prefix  = "terraform/state"
  }
}