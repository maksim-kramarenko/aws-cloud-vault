from io import BytesIO

from app.models import FileRecord


def test_upload_requires_file(client):
    response = client.post(
        "/upload",
        data={},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "file is required",
    }


def test_upload_rejects_unsupported_extension(client):
    response = client.post(
        "/upload",
        data={
            "file": (
                BytesIO(b"example content"),
                "example.exe",
            )
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 415
    assert response.get_json() == {
        "error": "file type is not allowed",
        "filename": "example.exe",
    }


def test_upload_accepts_allowed_extension(
    client,
    monkeypatch,
):
    uploaded_to_s3 = {}

    def fake_upload_file(**kwargs):
        uploaded_to_s3.update(kwargs)

    monkeypatch.setattr(
        "app.routes.upload_file",
        fake_upload_file,
    )

    file_content = b"example content"

    response = client.post(
        "/upload",
        data={
            "file": (
                BytesIO(file_content),
                "example.txt",
            )
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 201

    response_data = response.get_json()
    uploaded_file = response_data["file"]

    assert response_data["message"] == "file uploaded"
    assert uploaded_file["id"] == 1
    assert uploaded_file["filename"] == "example.txt"
    assert uploaded_file["size_bytes"] == len(file_content)
    assert uploaded_file["content_type"] == "text/plain"

    assert uploaded_file["object_key"].startswith("uploads/")
    assert uploaded_file["object_key"].endswith(".txt")

    assert uploaded_to_s3["object_key"] == (
        uploaded_file["object_key"]
    )
    assert uploaded_to_s3["content_type"] == "text/plain"

    database_record = FileRecord.query.one()

    assert database_record.original_filename == "example.txt"
    assert database_record.object_key == (
        uploaded_file["object_key"]
    )
    assert database_record.size_bytes == len(file_content)
