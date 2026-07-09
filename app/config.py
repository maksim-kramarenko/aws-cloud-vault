import os


class Config:
    MAX_CONTENT_LENGTH = int(
        os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)
    )

    ALLOWED_EXTENSIONS = {
        "txt",
        "pdf",
        "png",
        "jpg",
        "jpeg",
    }

    APP_VERSION = os.getenv("APP_VERSION", "0.1.0")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///:memory:",
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")

    S3_PRESIGNED_URL_TTL = int(
        os.getenv("S3_PRESIGNED_URL_TTL", "300")
    )
