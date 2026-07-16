import os
from django.conf import settings
from google.cloud import bigquery
from google.oauth2 import service_account

_client = None


def get_bigquery_client():
    """Returns a cached BigQuery client, reusing the same service account
    your extraction scripts and dbt already use."""
    global _client
    if _client is None:
        credentials = service_account.Credentials.from_service_account_file(
            os.path.join(os.path.dirname(__file__), "..", "..", "keys", "car_pipeline_service_account.json")
)
        _client = bigquery.Client(
            credentials=credentials,
            project=settings.GCP_PROJECT_ID
        )
    return _client