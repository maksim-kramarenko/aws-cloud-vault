from pathlib import Path

from flask import Blueprint, current_app, jsonify, render_template, request


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


@main.post("/upload")
def upload():
    uploaded_file = request.files.get("file")

    if uploaded_file is None or uploaded_file.filename == "":
        return jsonify(error="file is required"), 400

    original_filename = uploaded_file.filename.strip()
    extension = get_extension(original_filename)

    if extension not in current_app.config["ALLOWED_EXTENSIONS"]:
        return jsonify(
            error="file type is not allowed",
            filename=original_filename,
        ), 415

    return jsonify(
        message="file accepted",
        filename=original_filename,
    ), 200
