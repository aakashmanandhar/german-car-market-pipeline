terraform {
  required_version = ">= 1.7.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ---------------------------------------------------------------------------
# BRONZE — raw, per-source landing datasets. Three sources, three datasets,
# so a bad load from one source never touches another's raw data.
# ---------------------------------------------------------------------------
resource "google_bigquery_dataset" "bronze_postgres" {
  dataset_id  = "bronze_postgres_${var.environment}"
  location    = var.region
  description = "Raw data landed from the PostgreSQL operational database."
}

resource "google_bigquery_dataset" "bronze_api" {
  dataset_id  = "bronze_api_${var.environment}"
  location    = var.region
  description = "Raw data landed from the vehicle catalog API."
}

resource "google_bigquery_dataset" "bronze_mongo" {
  dataset_id  = "bronze_mongo_${var.environment}"
  location    = var.region
  description = "Raw data landed from MongoDB Atlas."
}

# ---------------------------------------------------------------------------
# SILVER — conformed, cleaned data. dbt owns the tables inside; Terraform
# only owns the dataset.
# ---------------------------------------------------------------------------
resource "google_bigquery_dataset" "silver" {
  dataset_id  = "silver_${var.environment}"
  location    = var.region
  description = "Cleaned, conformed data from all three sources — tables owned by dbt."
}

# ---------------------------------------------------------------------------
# GOLD — the star schema. Again, dbt owns the actual tables.
# ---------------------------------------------------------------------------
resource "google_bigquery_dataset" "gold" {
  dataset_id  = "gold_${var.environment}"
  location    = var.region
  description = "Star schema: fact_purchases and dimension tables — owned by dbt."
}

# ---------------------------------------------------------------------------
# BRONZE TABLES — PostgreSQL source
# ---------------------------------------------------------------------------
locals {
  postgres_tables = {
    regions          = "regions_bronze.json"
    financing_types  = "financing_types_bronze.json"
    sales_channels   = "sales_channels_bronze.json"
    customers        = "customers_bronze.json"
    stores           = "stores_bronze.json"
    purchases        = "purchases_bronze.json"
  }

  api_tables = {
    brands   = "brands_bronze.json"
    models   = "models_bronze.json"
    vehicles = "vehicles_bronze.json"
  }

  mongo_tables = {
    customer_reviews = "customer_reviews_bronze.json"
    dealer_notes     = "dealer_notes_bronze.json"
    market_events    = "market_events_bronze.json"
  }
}

resource "google_bigquery_table" "postgres_bronze_tables" {
  for_each            = local.postgres_tables
  dataset_id          = google_bigquery_dataset.bronze_postgres.dataset_id
  table_id            = each.key
  deletion_protection = false
  schema              = file("${path.module}/../schemas/${each.value}")
}

resource "google_bigquery_table" "api_bronze_tables" {
  for_each            = local.api_tables
  dataset_id          = google_bigquery_dataset.bronze_api.dataset_id
  table_id            = each.key
  deletion_protection = false
  schema              = file("${path.module}/../schemas/${each.value}")
}

resource "google_bigquery_table" "mongo_bronze_tables" {
  for_each            = local.mongo_tables
  dataset_id          = google_bigquery_dataset.bronze_mongo.dataset_id
  table_id            = each.key
  deletion_protection = false
  schema              = file("${path.module}/../schemas/${each.value}")
}

# ---------------------------------------------------------------------------
# SERVICE ACCOUNT — the identity all three extraction scripts run as
# ---------------------------------------------------------------------------
resource "google_service_account" "pipeline_sa" {
  account_id   = "car-pipeline-${var.environment}"
  display_name = "German car market pipeline service account (${var.environment})"
}

resource "google_project_iam_member" "pipeline_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

resource "google_project_iam_member" "pipeline_bq_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

resource "google_service_account_key" "pipeline_sa_key" {
  service_account_id = google_service_account.pipeline_sa.name
}

# ---------------------------------------------------------------------------
# STREAMING — Pub/Sub topic for real-time new purchase events
# ---------------------------------------------------------------------------
resource "google_pubsub_topic" "new_purchase" {
  name = "new-purchase-${var.environment}"
}

resource "google_project_iam_member" "pipeline_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}