# Filename: storage.tf

# This tells Terraform to get data about an EXISTING bucket
# instead of trying to create a new one.
data "google_storage_bucket" "sara_vault" {
  name = "${var.project_id}-sara-documents-vault"
}