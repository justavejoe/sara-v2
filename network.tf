/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

# Configure PSC
# # Create VPC
resource "google_compute_network" "main" {
  name                    = "sara-vpc-main" # Static name for stability
  auto_create_subnetworks = false
  project                 = var.project_id
}

# # Create Subnet
resource "google_compute_subnetwork" "subnetwork" {
  name          = "sara-subnet-main" # Static name for stability
  ip_cidr_range = "10.2.0.0/16"
  region        = var.region
  network       = google_compute_network.main.id
  project       = var.project_id
}

# # Configure IP
resource "google_compute_address" "default" {
  project      = var.project_id
  name         = "psc-compute-address"
  region       = var.region
  address_type = "INTERNAL"
  subnetwork   = google_compute_subnetwork.subnetwork.id
  address      = "10.2.0.42"
}

# # Create VPC / PSC forwarding rule
resource "google_compute_forwarding_rule" "default" {
  # FINAL FIX: Make this resource conditional
  count = var.database_type == "postgresql" ? 1 : 0

  project               = var.project_id
  name                  = "psc-forwarding-rule-${google_sql_database_instance.main_configured[0].name}"
  region                = var.region
  network               = google_compute_network.main.id
  ip_address            = google_compute_address.default.self_link
  load_balancing_scheme = ""
  target                = google_sql_database_instance.main_configured[0].psc_service_attachment_link
}

# # Create DNS Zone for PSC
resource "google_dns_managed_zone" "psc" {
  # FINAL FIX: Make this resource conditional
  count = var.database_type == "postgresql" ? 1 : 0

  project     = var.project_id
  name        = "${google_sql_database_instance.main_configured[0].name}-${random_id.id.hex}-zone"
  dns_name    = "${google_sql_database_instance.main_configured[0].region}.sql.goog."
  description = "Regional zone for Cloud SQL PSC instances"
  visibility  = "private"
  private_visibility_config {
    networks {
      network_url = google_compute_network.main.id
    }
  }
}

# # Add SQL DNS record
resource "google_dns_record_set" "psc" {
  # FINAL FIX: Make this resource conditional
  count = var.database_type == "postgresql" ? 1 : 0

  project      = var.project_id
  name         = google_sql_database_instance.main_configured[0].dns_name
  type         = "A"
  ttl          = 300
  managed_zone = google_dns_managed_zone.psc[0].name
  rrdatas      = [google_compute_address.default.address]
}

resource "google_project_service" "service_networking" {
  project = var.project_id
  service = "servicenetworking.googleapis.com"
}

resource "google_compute_global_address" "private_ip_address" {
  project       = var.project_id
  name          = "private-ip-for-google-services"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
}

resource "google_service_networking_connection" "private_service_access" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]

  # Add a timeout to allow the peering operation more time to complete.
  timeouts {
    create = "15m"
  }

  depends_on = [google_project_service.service_networking]
}