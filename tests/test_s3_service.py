from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from app import create_app
from app.services.s3_service import (
    create_download_url,
    delete_file,
    get_bucket_name,
    upload_file,
)


def create_test_app():
    app = create_app()

    app.config.update(
        TESTING=True,
        S3_BUCKET_NAME="test-cloud-vault-bucket",
        AWS_REGION="us-east-1",
        S3_PRESIGNED_URL_TTL=300,
    )

    return app


def test_upload_file_calls_s3():
    app = create_test_app()
    client = MagicMock()
    file_object = BytesIO(b"test file content")

    with app.app_context():
        with patch(
            "app.services.s3_service.get_s3_client",
            return_value=client,
        ):
            upload_file(
                file_object=file_object,
                object_key="uploads/example.txt",
                content_type="text/plain",
            )

    client.upload_fileobj.assert_called_once_with(
        Fileobj=file_object,
        Bucket="test-cloud-vault-bucket",
        Key="uploads/example.txt",
        ExtraArgs={
            "ContentType": "text/plain",
        },
    )


def test_create_download_url():
    app = create_test_app()
    client = MagicMock()

    client.generate_presigned_url.return_value = (
        "https://example.com/download"
    )

    with app.app_context():
        with patch(
            "app.services.s3_service.get_s3_client",
            return_value=client,
        ):
            url = create_download_url(
                "uploads/example.txt"
            )

    assert url == "https://example.com/download"

    client.generate_presigned_url.assert_called_once_with(
        ClientMethod="get_object",
        Params={
            "Bucket": "test-cloud-vault-bucket",
            "Key": "uploads/example.txt",
        },
        ExpiresIn=300,
    )


def test_delete_file_calls_s3():
    app = create_test_app()
    client = MagicMock()

    with app.app_context():
        with patch(
            "app.services.s3_service.get_s3_client",
            return_value=client,
        ):
            delete_file("uploads/example.txt")

    client.delete_object.assert_called_once_with(
        Bucket="test-cloud-vault-bucket",
        Key="uploads/example.txt",
    )


def test_bucket_name_is_required():
    app = create_app()
    app.config["S3_BUCKET_NAME"] = ""

    with app.app_context():
        with pytest.raises(
            RuntimeError,
            match="S3_BUCKET_NAME",
        ):
            get_bucket_name()
