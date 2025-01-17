import uuid
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
        collection = mongo.db['jewellery_data']
        count = collection.count_documents({})
        print(f"Number of documents in collection: {count}")
        # Fetch all documents from the 'jewellery_data' collection
        products = list(collection.find({}))
        print(products)
        for product in products:
            product['_id'] = str(product['_id'])        
        return jsonify(products), 200
    except Exception as e:
        app.logger.error(f"MongoDB Fetch Error: {e}")
        return jsonify({"error": "Failed to fetch documents", "details": str(e)}), 500

@app.route("/deleteJewellery",methods=["POST"])
def delete_jewellery():
    try:
        collection = mongo.db['jewellery_data']
        # Get the product ID from the request
        product_id = request.json.get('id')
        if not product_id:
            return jsonify({"error": "Product ID is required"}), 400

        # Delete the product from the collection
        result = collection.delete_one({"_id": product_id})
        if result.deleted_count == 0:
            return jsonify({"error": "Product not found"}), 404

        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        app.logger.error(f"MongoDB Delete Error: {e}")
        return jsonify({"error": "Failed to delete product", "details": str(e)}), 500

@app.route("/uploadJewellery", methods=["POST"])
def upload_jewellery():
    try:
        # Check if the request has a file part
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        name = request.form.get('name')  # Jewellery name
        description=request.form.get('description')
        category = request.form.get('category')  # Jewellery category
        material = request.form.get('material')  # Jewellery material
        stock = request.form.get('stock')  # Jewellery stock
        price = request.form.get('price')  # Jewellery price
        discountedPrice = request.form.get('discountedPrice')  # Jewellery discounted price
        weight=request.form.get('weight')
    #     formData.append("name", jewelleryName);
    # formData.append("description", jewelleryDescription);
    # formData.append("category", jewelleryCategoryData?.value as string);
    # formData.append("material", material?.value as string);
    # formData.append("stock", stock);
    # formData.append("price", price);
    # formData.append("discountedPrice", discountedPrice);
    # formData.append("weight", weight);
    # formData.append("file", productImageUrl[0]);


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
            "productId":123,
            "name": name,
            "description":description,
            "material":material,
            "stock":stock,
            "price":price,
            "discountedPrice":discountedPrice,
            "weight":weight,
            "category": category,
            "imageUrl": file_url,
            "uploadedAt": datetime.utcnow()
        }
        mongo.db['jewellery_data'].insert_one(jewellery_data)

        return jsonify({"message": "File uploaded successfully!", "file_url": file_url}), 201
    except Exception as e:
        app.logger.error(f"File Upload Error: {e}")
        return jsonify({"error": "File upload failed", "details": str(e)}), 500

# Start the Flask application
if __name__ == "__main__":
    app.run(debug=True)
