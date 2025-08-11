# Filename: storage.tf

# This now correctly defines the application's data vault as a
# resource that Terraform will create and manage. This is separate
# from the Terraform state bucket.
resource "google_storage_bucket" "sara_vault" {
  name          = "${var.project_id}-sara-documents-vault"
  location      = var.region
  force_destroy = true # Set to true for easier cleanup in non-production environments
  uniform_bucket_level_access = true
}