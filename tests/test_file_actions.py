from app.extensions import db
from app.models import FileRecord


def create_file_record():
    record = FileRecord(
        original_filename="example.txt",
        object_key="uploads/example.txt",
        size_bytes=15,
        content_type="text/plain",
    )

    db.session.add(record)
    db.session.commit()

    return record


def test_download_returns_presigned_url(client, monkeypatch):
    record = create_file_record()
    requested_keys = []

    def fake_create_download_url(object_key):
        requested_keys.append(object_key)
        return "https://example.com/presigned-download"

    monkeypatch.setattr(
        "app.routes.create_download_url",
        fake_create_download_url,
    )

    response = client.get(
        f"/files/{record.id}/download"
    )

    assert response.status_code == 200

    response_data = response.get_json()

    assert response_data["filename"] == "example.txt"
    assert response_data["download_url"] == (
        "https://example.com/presigned-download"
    )
    assert response_data["expires_in"] == 300

    assert requested_keys == ["uploads/example.txt"]


def test_download_returns_404_for_unknown_file(client):
    response = client.get("/files/999/download")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "file not found",
    }


def test_delete_removes_s3_object_and_database_record(
    client,
    monkeypatch,
):
    record = create_file_record()
    file_id = record.id
    deleted_keys = []

    def fake_delete_file(object_key):
        deleted_keys.append(object_key)

    monkeypatch.setattr(
        "app.routes.delete_file",
        fake_delete_file,
    )

    response = client.delete(
        f"/files/{file_id}"
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "file deleted",
        "file_id": file_id,
    }

    assert deleted_keys == ["uploads/example.txt"]

    assert db.session.get(
        FileRecord,
        file_id,
    ) is None


def test_delete_returns_404_for_unknown_file(client):
    response = client.delete("/files/999")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "file not found",
    }
