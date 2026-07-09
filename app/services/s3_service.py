import boto3
from flask import current_app


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=current_app.config["AWS_REGION"],
    )


def get_bucket_name() -> str:
    bucket_name = current_app.config.get("S3_BUCKET_NAME")

    if not bucket_name:
        raise RuntimeError(
            "S3_BUCKET_NAME environment variable is not configured"
        )

    return bucket_name


def upload_file(
    file_object,
    object_key: str,
    content_type: str,
) -> None:
    client = get_s3_client()

    client.upload_fileobj(
        Fileobj=file_object,
        Bucket=get_bucket_name(),
        Key=object_key,
        ExtraArgs={"ContentType": content_type},
    )


def create_download_url(object_key: str) -> str:
    client = get_s3_client()

    return client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": get_bucket_name(),
            "Key": object_key,
        },
        ExpiresIn=current_app.config["S3_PRESIGNED_URL_TTL"],
    )


def delete_file(object_key: str) -> None:
    client = get_s3_client()

    client.delete_object(
        Bucket=get_bucket_name(),
        Key=object_key,
    )
