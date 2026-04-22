import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

import main
from main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_redis():
    """Patch main.r (the already-instantiated Redis client) for every test."""
    mock_r = MagicMock()
    with patch.object(main, "r", mock_r):
        yield mock_r


def test_create_job_returns_job_id(mock_redis):
    response = client.post("/jobs")

    assert response.status_code == 201
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) == 36

    mock_redis.lpush.assert_called_once()
    mock_redis.hset.assert_called_once()


def test_get_job_found(mock_redis):
    mock_redis.hget.return_value = b"queued"

    response = client.get("/jobs/some-job-id")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert data["job_id"] == "some-job-id"


def test_get_job_not_found(mock_redis):
    mock_redis.hget.return_value = None

    response = client.get("/jobs/nonexistent-id")

    assert response.status_code == 404
    assert "detail" in response.json()


def test_health_endpoint(mock_redis):
    mock_redis.ping.return_value = True

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_redis_mocked(mock_redis):
    """Verify Redis calls are mocked and not hitting a real server."""
    mock_redis.hget.return_value = b"queued"

    # create a job — should call lpush and hset on the mock
    create_resp = client.post("/jobs")
    assert create_resp.status_code == 201

    job_id = create_resp.json()["job_id"]

    mock_redis.lpush.assert_called_with("job", job_id)
    mock_redis.hset.assert_called_with(
        f"job:{job_id}", "status", "queued"
    )

    # fetch it — should call hget on the mock
    get_resp = client.get(f"/jobs/{job_id}")
    assert get_resp.status_code == 200

    mock_redis.hget.assert_called_with(
        f"job:{job_id}", "status"
    )


def test_create_multiple_jobs_unique_ids(mock_redis):
    """Each POST /jobs must return a distinct UUID."""
    ids = {
        client.post("/jobs").json()["job_id"]
        for _ in range(5)
    }
    assert len(ids) == 5


def test_health_calls_redis_ping(mock_redis):
    """Health endpoint must call redis ping."""
    mock_redis.ping.return_value = True

    client.get("/health")

    mock_redis.ping.assert_called_once()
    