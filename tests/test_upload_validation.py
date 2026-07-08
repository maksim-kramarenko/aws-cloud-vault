from io import BytesIO

from app import create_app


def test_upload_requires_file():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/upload",
        data={},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "file is required"
    }


def test_upload_rejects_unsupported_extension():
    app = create_app()
    client = app.test_client()

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
    assert response.get_json()["error"] == (
        "file type is not allowed"
    )


def test_upload_accepts_allowed_extension():
    app = create_app()
    client = app.test_client()

    response = client.post(
        "/upload",
        data={
            "file": (
                BytesIO(b"example content"),
                "example.txt",
            )
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "file accepted",
        "filename": "example.txt",
    }
