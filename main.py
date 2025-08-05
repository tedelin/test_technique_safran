import logging
import random
import time
from contextlib import asynccontextmanager

import numpy as np
import psycopg2
from fastapi import FastAPI, HTTPException
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

from prometheus_fastapi_instrumentator import Instrumentator
from os import getenv
from multiprocessing import Queue
from logging_loki import LokiQueueHandler

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.propagate import inject
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

Psycopg2Instrumentor().instrument()
loki_logs_handler = LokiQueueHandler(
    Queue(-1), url=getenv("LOKI_ENDPOINT"), tags={"application": "fastapi"}, version="1"
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(loki_logs_handler)

class Dataset(BaseModel):
    id: int
    name: str


def get_db_connection():
    conn = psycopg2.connect(host="db", database="postgres", user="postgres", password="postgres")
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS datasets (id SERIAL PRIMARY KEY, name TEXT)")
    conn.commit()
    cursor.close()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)
# Otel collector for traces
resource = Resource(attributes={"service.name": "fastapi"})
trace.set_tracer_provider(TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4317", insecure=True))
)
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()
# Prometheus Metrics
Instrumentator().instrument(app).expose(app)

@app.get("/datasets", response_model=list[Dataset])
async def get_datasets():
    logger.info("Fetching all datasets")
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM datasets")
    datasets = cursor.fetchall()
    cursor.close()
    conn.close()
    return datasets


@app.get("/datasets/{dataset_id}", response_model=Dataset)
async def get_dataset(dataset_id: int):
    logger.info(f"Fetching dataset with id {dataset_id}")
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM datasets WHERE id = %s", (dataset_id,))
    dataset = cursor.fetchone()
    cursor.close()
    conn.close()
    if dataset is None:
        logger.error(f"Dataset with id {dataset_id} not found")
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@app.post("/datasets", response_model=Dataset)
async def create_dataset(name: str):
    logger.info(f"Creating dataset with name {name}")
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("INSERT INTO datasets (name) VALUES (%s) RETURNING *", (name,))
    dataset = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return dataset


@app.post("/datasets/{dataset_id}/reticulate")
async def reticulate_dataset(dataset_id: int):
    logger.info(f"Reticulating dataset with id {dataset_id}")

    # Simulate CPU-intensive task
    start_time = time.time()
    while time.time() - start_time < 3:
        x = np.random.rand(1000, 1000)
        y = np.random.rand(1000, 1000)
        np.dot(x, y)

    # Simulate RAM usage
    large_list = [random.random() for _ in range(10_000_000)]
    time.sleep(2)

    logger.info(f"Finished reticulating dataset with id {dataset_id}")
    return {"status": "completed", "dataset_id": dataset_id}