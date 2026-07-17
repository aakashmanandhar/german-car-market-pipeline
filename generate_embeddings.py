import os
import time
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account
from vertexai.language_models import TextEmbeddingModel
import vertexai
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

PROJECT_ID = "german-car-pipeline"
LOCATION = "europe-west3"

vertexai.init(project=PROJECT_ID, location=LOCATION)
embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-005")

credentials = service_account.Credentials.from_service_account_file(
    "keys/car_pipeline_service_account.json"
)
bq_client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

TABLE_ID = f"{PROJECT_ID}.gold_dev.embedded_documents"

SCHEMA = [
    bigquery.SchemaField("source_table", "STRING"),
    bigquery.SchemaField("source_id", "STRING"),
    bigquery.SchemaField("content", "STRING"),
    bigquery.SchemaField("embedding", "FLOAT64", mode="REPEATED"),
]


@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=2, min=2, max=30))
def get_embeddings_with_retry(texts):
    return embedding_model.get_embeddings(texts)


def embed_source(source_table, id_column, text_column, query, write_disposition):
    rows = list(bq_client.query(query).result())
    print(f"Embedding {len(rows)} rows from {source_table}...")

    documents_to_insert = []
    for i in range(0, len(rows), 5):
        batch = rows[i:i + 5]
        texts = [str(row[text_column]) for row in batch]
        embeddings = get_embeddings_with_retry(texts)

        for row, embedding in zip(batch, embeddings):
            documents_to_insert.append({
                "source_table": source_table,
                "source_id": str(row[id_column]),
                "content": row[text_column],
                "embedding": list(embedding.values),
            })
        time.sleep(0.1)

    # Batch load, not streaming insert — avoids the streaming buffer entirely,
    # the correct tool for a full backfill like this rather than real-time inserts.
    job_config = bigquery.LoadJobConfig(
        schema=SCHEMA,
        write_disposition=write_disposition,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    load_job = bq_client.load_table_from_json(
        documents_to_insert, TABLE_ID, job_config=job_config
    )
    load_job.result()  # waits for the load to finish, raises if it failed

    print(f"Loaded {len(documents_to_insert)} embedded rows from {source_table}.")


# First source truncates and recreates the table cleanly; the rest append to it.
embed_source(
    "customer_reviews", "review_id", "review_text",
    f"SELECT review_id, review_text FROM `{PROJECT_ID}.silver_dev.silver_customer_reviews` WHERE review_text IS NOT NULL",
    write_disposition="WRITE_TRUNCATE"
)

embed_source(
    "dealer_notes", "note_id", "note_text",
    f"SELECT note_id, note_text FROM `{PROJECT_ID}.silver_dev.silver_dealer_notes` WHERE note_text IS NOT NULL",
    write_disposition="WRITE_APPEND"
)

embed_source(
    "market_events", "event_id", "event_description",
    f"SELECT event_id, event_description FROM `{PROJECT_ID}.silver_dev.silver_market_events`",
    write_disposition="WRITE_APPEND"
)

print("Done.")