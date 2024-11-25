from flask import Flask, request, send_from_directory
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 确保上传文件夹存在

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return {"error": "No file provided"}, 400
    file = request.files["file"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    public_url = f"http://14.136.11.131:5000/{UPLOAD_FOLDER}/{file.filename}"  # 替换 <your_public_ip> 为实际的公网 IP
    return {"url": public_url}

@app.route(f"/{UPLOAD_FOLDER}/<filename>")
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
