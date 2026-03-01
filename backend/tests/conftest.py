import importlib
import sys
import time
from collections.abc import Generator
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import boto3  # type: ignore[import-not-found]
import pytest
from fastapi.testclient import TestClient


def _wait_until_table_active(
    dynamodb_client: Any, table_name: str, timeout_s: float = 30.0
) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        resp = dynamodb_client.describe_table(TableName=table_name)
        if resp["Table"]["TableStatus"] == "ACTIVE":
            return
        time.sleep(0.25)
    raise RuntimeError(f"Timed out waiting for DynamoDB table to become ACTIVE: {table_name}")


@pytest.fixture
def temp_dynamodb_table(monkeypatch: pytest.MonkeyPatch) -> Generator[str, None, None]:
    """
    Create a temporary DynamoDB table for tests and expose it via env vars.
    """
    table_name = f"ccbda-crud-test-{uuid4().hex}"

    boto3_any = cast(Any, boto3)
    client: Any = boto3_any.client("dynamodb")

    client.create_table(
        TableName=table_name,
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "N"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
    )
    _wait_until_table_active(client, table_name)
    monkeypatch.setenv("STORAGE_TABLE", table_name)

    try:
        yield table_name
    finally:
        # Best-effort cleanup
        try:
            client.delete_table(TableName=table_name)
        except Exception:
            pass


@pytest.fixture
def client(temp_dynamodb_table: str, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Create a test client wired to a temporary DynamoDB table."""
    monkeypatch.setenv("FRONTEND_URLS", "http://localhost:3000,http://127.0.0.1:3000")

    backend_dir = Path(__file__).resolve().parents[1]  # .../backend
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    import src.main as main_module

    importlib.reload(main_module)
    return TestClient(main_module.app)
