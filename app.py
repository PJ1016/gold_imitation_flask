from flask import Flask, jsonify
from flask_pymongo import PyMongo
from datetime import datetime
from flask_cors import CORS  # Import CORS

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# MongoDB URI (Replace with your actual credentials)
app.config["MONGO_URI"] = "mongodb+srv://praveenjayanth1111:D3NhzVGRqDuovgw8@vsarts.wspap.mongodb.net/vsarts?retryWrites=true&w=majority&tls=true"

# Initialize PyMongo
mongo = PyMongo(app)

# Enable Flask Debugging
app.config["DEBUG"] = True

# Create a route to test MongoDB connection
@app.route("/", methods=["GET"])
def index():
    try:
        # Test MongoDB connection and fetch collections
        collections = mongo.db.list_collection_names()
        return jsonify({"message": "Connected to MongoDB!", "collections": collections}), 200
    except Exception as e:
        app.logger.error(f"MongoDB Connection Error: {e}")
        return jsonify({"error": "Failed to connect to MongoDB", "details": str(e)}), 500

@app.route("/getJewelley", methods=["GET"])
def get_jewelley():
    try:
        collection = mongo.db['jewellery']
        # Fetch all documents from the 'jewellery' collection
        products = list(collection.find({}, {'_id': 0}))
        return jsonify(products), 200
    except Exception as e:
        app.logger.error(f"MongoDB Fetch Error: {e}")
        return jsonify({"error": "Failed to fetch documents", "details": str(e)}), 500

# Start the Flask application
if __name__ == "__main__":
    app.run(debug=True)
