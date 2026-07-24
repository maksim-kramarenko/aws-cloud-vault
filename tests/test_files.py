from datetime import datetime, timezone

from app.extensions import db
from app.models import FileRecord


def test_list_files_returns_empty_list(client):
    response = client.get("/files")

    assert response.status_code == 200
    assert response.get_json() == {
        "count": 0,
        "files": [],
    }


def test_list_files_returns_database_records(client):
    older_file = FileRecord(
        original_filename="older.txt",
        object_key="uploads/older.txt",
        size_bytes=10,
        content_type="text/plain",
        created_at=datetime(
            2026,
            7,
            20,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    newer_file = FileRecord(
        original_filename="newer.pdf",
        object_key="uploads/newer.pdf",
        size_bytes=2048,
        content_type="application/pdf",
        created_at=datetime(
            2026,
            7,
            21,
            12,
            30,
            tzinfo=timezone.utc,
        ),
    )

    db.session.add_all([older_file, newer_file])
    db.session.commit()

    response = client.get("/files")

    assert response.status_code == 200

    response_data = response.get_json()

    assert response_data["count"] == 2
    assert len(response_data["files"]) == 2

    assert response_data["files"][0]["filename"] == (
        "newer.pdf"
    )
    assert response_data["files"][0]["size_bytes"] == 2048
    assert response_data["files"][0]["content_type"] == (
        "application/pdf"
    )

    assert response_data["files"][1]["filename"] == (
        "older.txt"
    )

    assert "object_key" not in response_data["files"][0]
