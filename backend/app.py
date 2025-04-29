from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from core import *
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)

CORS(app)

# uploads folder
UPLOAD_FOLDER = "uploads/"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB limit

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# only .pdf extention allowed right now.
ALLOWED_EXTENSIONS = {"pdf"}


# Check if the file has a valid extension
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def base():
    return jsonify({"message": "All good ! "}), 200


@app.route("/upload/<path:filename>")
def serve_image(filename):
    """
    to serve the images of pdf to network so tha its accessibel for groq.
    """
    folder_name = filename.split("/")[0]  # Extract the first part as the subfolder
    image_name = filename.split("/")[1]  # Extract second part (image name)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], folder_name, image_name)

    # Check if the file exists
    if os.path.exists(file_path):
        return send_from_directory(
            os.path.join(app.config["UPLOAD_FOLDER"], folder_name), image_name
        )
    else:
        return jsonify({"message": "File not found", "filepath ": file_path}), 404


@app.route("/upload", methods=["POST"])
def upload_file():
    """
    endpoint for uploading pdf file.
    """
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # creating subfolder with name of pdf
        filename_without_extension = os.path.splitext(file.filename)[0]
        folder_path = os.path.join(
            app.config["UPLOAD_FOLDER"], filename_without_extension
        )

        # Create the subfolder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Save the file inside this subfolder
        file_path = os.path.join(folder_path, file.filename)
        file.save(file_path)

        return (
            jsonify({"message": "File successfully uploaded!", "file_path": file_path}),
            200,
        )
    else:
        return jsonify({"message": "Invalid file format"}), 400


@app.route("/start-process", methods=["POST"])
def start_process():
    """
    starts the pdf extraction process.
    """
    print("process started")
    file_name = request.json.get("fileName")

    if not file_name:
        return jsonify({"message": "No file name provided"}), 400

    # Call the actual processing function
    result = startprocess.initiate(file_name)

    return jsonify({"message": result}), 200


if __name__ == "__main__":
    app.run(debug=True)
