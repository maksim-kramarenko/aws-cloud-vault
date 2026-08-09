from pathlib import Path
from uuid import uuid4

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
)
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import FileRecord
from app.services.s3_service import (
    create_download_url,
    delete_file,
    upload_file,
)


main = Blueprint("main", __name__)


def get_extension(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")


@main.get("/")
def index():
    return render_template(
        "index.html",
        version=current_app.config["APP_VERSION"],
        allowed_extensions=sorted(
            current_app.config["ALLOWED_EXTENSIONS"]
        ),
    )


@main.get("/health")
def health():
    return jsonify(status="healthy"), 200


@main.get("/files")
def list_files():
    records = (
        FileRecord.query
        .order_by(
            FileRecord.created_at.desc(),
            FileRecord.id.desc(),
        )
        .all()
    )

    files = [
        {
            "id": record.id,
            "filename": record.original_filename,
            "size_bytes": record.size_bytes,
            "content_type": record.content_type,
            "created_at": record.created_at.isoformat(),
        }
        for record in records
    ]

    return jsonify(
        count=len(files),
        files=files,
    ), 200


@main.get("/files/<int:file_id>/download")
def download_file(file_id: int):
    record = db.session.get(FileRecord, file_id)

    if record is None:
        return jsonify(error="file not found"), 404

    try:
        download_url = create_download_url(
            record.object_key
        )
    except Exception:
        current_app.logger.exception(
            "Failed to create presigned download URL"
        )
        return jsonify(
            error="storage operation failed"
        ), 502

    return jsonify(
        filename=record.original_filename,
        download_url=download_url,
        expires_in=current_app.config[
            "S3_PRESIGNED_URL_TTL"
        ],
    ), 200


@main.delete("/files/<int:file_id>")
def remove_file(file_id: int):
    record = db.session.get(FileRecord, file_id)

    if record is None:
        return jsonify(error="file not found"), 404

    try:
        delete_file(record.object_key)
    except Exception:
        current_app.logger.exception(
            "Failed to delete S3 object"
        )
        return jsonify(
            error="storage operation failed"
        ), 502

    try:
        db.session.delete(record)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception(
            "Failed to delete database record"
        )
        return jsonify(
            error="database operation failed"
        ), 500

    return jsonify(
        message="file deleted",
        file_id=file_id,
    ), 200


@main.post("/upload")
def upload():
    uploaded_file = request.files.get("file")

    if (
        uploaded_file is None
        or uploaded_file.filename == ""
    ):
        return jsonify(
            error="file is required"
        ), 400

    original_filename = uploaded_file.filename.strip()
    extension = get_extension(original_filename)

    if (
        extension
        not in current_app.config["ALLOWED_EXTENSIONS"]
    ):
        return jsonify(
            error="file type is not allowed",
            filename=original_filename,
        ), 415

    uploaded_file.stream.seek(0, 2)
    size_bytes = uploaded_file.stream.tell()
    uploaded_file.stream.seek(0)

    object_key = (
        f"uploads/{uuid4()}.{extension}"
    )

    content_type = (
        uploaded_file.mimetype
        or "application/octet-stream"
    )

    try:
        upload_file(
            file_object=uploaded_file.stream,
            object_key=object_key,
            content_type=content_type,
        )

        record = FileRecord(
            original_filename=original_filename,
            object_key=object_key,
            size_bytes=size_bytes,
            content_type=content_type,
        )

        db.session.add(record)
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()

        try:
            delete_file(object_key)
        except Exception:
            current_app.logger.exception(
                "Failed to remove orphaned S3 object"
            )

        return jsonify(
            error="database operation failed"
        ), 500

    except Exception:
        current_app.logger.exception(
            "File upload failed"
        )
        return jsonify(
            error="storage operation failed"
        ), 502

    return jsonify(
        message="file uploaded",
        file={
            "id": record.id,
            "filename": record.original_filename,
            "size_bytes": record.size_bytes,
            "content_type": record.content_type,
            "object_key": record.object_key,
        },
    ), 201
