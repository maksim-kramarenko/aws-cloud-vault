from datetime import datetime, timezone

from app.extensions import db


class FileRecord(db.Model):
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True)

    original_filename = db.Column(
        db.String(255),
        nullable=False,
    )

    object_key = db.Column(
        db.String(512),
        nullable=False,
        unique=True,
    )

    size_bytes = db.Column(
        db.BigInteger,
        nullable=False,
    )

    content_type = db.Column(
        db.String(255),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
