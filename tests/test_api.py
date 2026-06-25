import os
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

os.environ["ADMIN_USER"] = "admin"
os.environ["ADMIN_PASS"] = "admin"

from app.main import app  # noqa: E402

client = TestClient(app)


def make_row(data: dict):
    """Crée un mock qui se comporte comme un sqlite3.Row."""
    row = MagicMock()
    row.keys.return_value = list(data.keys())
    row.__getitem__ = lambda self, key: data[key]
    return row


FAKE_ASSET = {
    "id": 1,
    "name": "Test Server",
    "asset_type": "Server",
    "status": "active",
    "expiry_date": None,
    "created_at": "2026-06-24"
}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_assets_empty():
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchall.return_value = []
    with patch("app.main.get_connection", return_value=mock_conn):
        response = client.get("/assets")
    assert response.status_code == 200
    assert response.json() == []


def test_create_asset():
    mock_conn = MagicMock()
    mock_conn.execute.return_value.lastrowid = 1
    mock_conn.execute.return_value.fetchone.return_value = make_row(FAKE_ASSET)
    with patch("app.main.get_connection", return_value=mock_conn):
        response = client.post(
            "/assets",
            json={"name": "Test Server", "asset_type": "Server"},
            auth=("admin", "admin")
        )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Server"


def test_create_asset_unauthorized():
    response = client.post(
        "/assets",
        json={"name": "Test", "asset_type": "Server"},
    )
    assert response.status_code == 401


def test_create_asset_missing_fields():
    response = client.post(
        "/assets",
        json={"asset_type": "Server"},
        auth=("admin", "admin")
    )
    assert response.status_code == 422


def test_get_asset():
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchone.return_value = make_row(FAKE_ASSET)
    with patch("app.main.get_connection", return_value=mock_conn):
        response = client.get("/assets/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_asset_not_found():
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchone.return_value = None
    with patch("app.main.get_connection", return_value=mock_conn):
        response = client.get("/assets/99999")
    assert response.status_code == 404


def test_update_asset():
    mock_conn = MagicMock()
    updated = {**FAKE_ASSET, "name": "New Name"}
    mock_conn.execute.return_value.fetchone.return_value = make_row(updated)
    mock_conn.execute.return_value.rowcount = 1
    with patch("app.main.get_connection", return_value=mock_conn):
        response = client.put(
            "/assets/1",
            json={"name": "New Name"},
            auth=("admin", "admin")
        )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_delete_asset():
    mock_conn = MagicMock()
    mock_conn.execute.return_value.rowcount = 1
    with patch("app.main.get_connection", return_value=mock_conn):
        response = client.delete("/assets/1", auth=("admin", "admin"))
    assert response.status_code == 204


def test_delete_asset_unauthorized():
    response = client.delete("/assets/1")
    assert response.status_code == 401


def test_get_assets_list():
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchall.return_value = [make_row(FAKE_ASSET)]
    with patch("app.main.get_connection", return_value=mock_conn):
        response = client.get("/assets")
    assert response.status_code == 200
    assert len(response.json()) == 1