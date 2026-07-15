output "pipeline_sa_key_base64" {
  description = "Base64-encoded service account key — decode into keys/car_pipeline_service_account.json, never commit it."
  value       = google_service_account_key.pipeline_sa_key.private_key
  sensitive   = true
}