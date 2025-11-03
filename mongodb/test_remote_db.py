import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Use the same connection logic as your app
mongo_url = os.getenv("MONGODB_URL")
if not mongo_url:
    print("MONGODB_URL not set! Using local fallback.")
    mongo_url = "mongodb://localhost:27017/"

print(f"Connecting to: {mongo_url.split('@')[-1] if '@' in mongo_url else mongo_url}")

client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
db = client.get_database()  # or client["heart_disease_db"]

try:
    # This forces a real connection
    client.admin.command('ping')
    print("PING SUCCESS: Connected to MongoDB!")

    # Show server info
    info = client.server_info()
    print(f"Server Version: {info['version']}")
    print(f"Host: {client.address[0] if client.address else 'Unknown'}")

    # Count documents
    patients = db.patients.count_documents({})
    print(f"Patients in DB: {patients}")

except Exception as e:
    print("CONNECTION FAILED:", e)