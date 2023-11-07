from flask import send_from_directory, abort
from headbook import app

# by default, path parameters (filename, ext) match any string not including a '/'


@app.get("/<filename>.<ext>")
def serve_static(filename, ext):
    """Serve files from the static/ subdirectory"""

    # browsers can be really picky about file types, so it's important
    # to set this correctly, particularly for JS and CSS
    file_types = {
        "js": "application/javascript",
        "ico": "image/vnd.microsoft.icon",
        "png": "image/png",
        "html": "text/html",
        "css": "text/css",
    }

    if ext in file_types:
        return send_from_directory(
            app.static_folder, f"{filename}.{ext}", mimetype=file_types[ext]
        )
    else:
        abort(404)
