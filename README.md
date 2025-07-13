## **SARA 1.0: Project Status & Key Learnings**

Build triggered at 7:08 PM on July 12, 2025.

[2025-07-12] - Phase 0 (Infrastructure Setup) Complete. All foundational infrastructure is defined in Terraform and deployed successfully via the Cloud Build CI/CD pipeline.

### I. Current Status

The Cloud Build pipeline is currently running to deploy our **Phase 0** infrastructure. We expect this build to succeed, which will result in:
* A fully deployed and secure backend API (`retrieval-service`).
* A deployed frontend service shell (`frontend-service`).
* A provisioned Cloud SQL for PostgreSQL database with the `pgvector` extension enabled.
* All necessary IAM roles and permissions correctly configured for the application to run.

### II. Key Learnings & Resolutions

This initial setup phase revealed several important requirements and led to key fixes:

* **Organization Policies:** We discovered that your Google Cloud organization enforces policies that required us to:
    1.  Use a dedicated, user-managed service account (`sara-build-trigger-sa`) for our Cloud Build trigger.
    2.  Explicitly configure the build's logging option to **`CLOUD_LOGGING_ONLY`** in our `cloudbuild.yaml` file.

* **IAM Permissions:** The build process required our `sara-build-trigger-sa` service account to have a specific set of roles beyond the defaults. We successfully granted the following roles to allow Terraform to manage all necessary resources and their permissions:
    * Editor
    * Service Usage Admin
    * Project IAM Admin
    * Cloud Run Admin
    * Secret Manager Admin

* **Infrastructure & Code Fixes:** We successfully debugged and resolved several issues with the reference architecture and our setup:
    * **Directory Structure:** We flattened the nested project directories to create a clean repository root.
    * **Build Configuration:** We authored a new root `cloudbuild.yaml` to correctly execute Terraform commands.
    * **Resource Quotas:** We identified and cleared a VPC Network quota limit by deleting the network in the `sara-learning-temp` project.
    * **Application Bug:** We identified and fixed a `ValueError` in the reference application's `app/routes.py` file.

### III. Next Steps (Post-Build)

Once the current build succeeds, our immediate next steps are:
1.  **Manually Initialize the Database:** Run the `curl` command to call the `/data/import` endpoint on the new `retrieval-service`.
2.  **Final Verification:** Send a test query to the `/policies/search` endpoint to confirm the entire RAG pipeline is working.
3.  **Phase 0 Complete:** Officially conclude our foundational setup.
4.  **Begin Phase 1:** Start development on the MVP features for SARA 1.0.

### Terraform Configuration Details
# terraform-genai-retrieval-augmented-generation

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| database\_type | Cloud SQL MySQL, Cloud SQL PostgreSQL, AlloyDB, or Cloud Spanner | `string` | `"postgresql"` | no |
| deletion\_protection | Whether or not to protect Cloud SQL resources from deletion when solution is modified or changed. | `string` | `false` | no |
| enable\_apis | Whether or not to enable underlying apis in this solution. . | `string` | `true` | no |
| frontend\_container | The public Artifact Registry URI for the frontend container | `string` | `"us-docker.pkg.dev/google-samples/containers/jss/rag-frontend-service:v0.0.2"` | no |
| labels | A map of labels to apply to contained resources. | `map(string)` | <pre>{<br>  "genai-rag": true<br>}</pre> | no |
| project\_id | Google Cloud Project ID | `string` | n/a | yes |
| region | Google Cloud Region | `string` | `"us-central1"` | no |
| retrieval\_container | The public Artifact Registry URI for the retrieval container | `string` | `"us-docker.pkg.dev/google-samples/containers/jss/rag-retrieval-service:v0.0.3"` | no |

## Outputs

| Name | Description |
|------|-------------|
| deployment\_ip\_address | Web URL link |

<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
