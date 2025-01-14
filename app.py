from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS
import boto3
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# MongoDB URI (Replace with your actual credentials)
app.config["MONGO_URI"] = "mongodb+srv://praveenjayanth1111:D3NhzVGRqDuovgw8@vsarts.wspap.mongodb.net/vsarts?retryWrites=true&w=majority&tls=true"

# Initialize PyMongo
mongo = PyMongo(app)

# AWS S3 Configuration
S3_BUCKET = os.getenv("S3_BUCKET", "your-default-s3-bucket")
S3_REGION = os.getenv("S3_REGION", "your-default-region")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=S3_REGION
)

# Enable Flask Debugging
app.config["DEBUG"] = True

@app.route("/", methods=["GET"])
def index():
    try:
        # Test MongoDB connection and fetch collections
        collections = mongo.db.list_collection_names()
        return jsonify({"message": "Connected to MongoDB!", "collections": collections}), 200
    except Exception as e:
        app.logger.error(f"MongoDB Connection Error: {e}")
        return jsonify({"error": "Failed to connect to MongoDB", "details": str(e)}), 500

@app.route("/getJewellery", methods=["GET"])
def get_jewellery():
    try:
        collection = mongo.db['jewellery']
        # Fetch all documents from the 'jewellery' collection
        products = list(collection.find({}, {'_id': 0}))
        print(products)
        return jsonify(products), 200
    except Exception as e:
        app.logger.error(f"MongoDB Fetch Error: {e}")
        return jsonify({"error": "Failed to fetch documents", "details": str(e)}), 500

@app.route("/uploadJewellery", methods=["POST"])
def upload_jewellery():
    try:
        # Check if the request has a file part
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        name = request.form.get('name')  # Jewellery name
        category = request.form.get('category')  # Jewellery category

        if file.filename == '':
            return jsonify({"error": "No file selected for uploading"}), 400

        # Secure the filename
        filename = secure_filename(file.filename)


        # Generate a unique filename
        unique_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"

        # Upload to S3
        s3_client.upload_fileobj(
            file,
            S3_BUCKET,
            unique_filename,
            ExtraArgs={"ContentType": file.content_type}
        )

        # Generate the file URL
        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{unique_filename}"

        # Store metadata and URL in MongoDB
        jewellery_data = {
            "name": name,
            "category": category,
            "imageUrl": file_url,
            "uploadedAt": datetime.utcnow()
        }
        mongo.db['jewellery'].insert_one(jewellery_data)

        return jsonify({"message": "File uploaded successfully!", "file_url": file_url}), 201
    except Exception as e:
        app.logger.error(f"File Upload Error: {e}")
        return jsonify({"error": "File upload failed", "details": str(e)}), 500

# Start the Flask application
if __name__ == "__main__":
    app.run(debug=True)
