from flask import Flask, Response, abort
from azure.storage.blob import BlobServiceClient
import os

app = Flask(__name__)

# Load connection string from environment variable
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_name = "web"

@app.route('/<site>/<path:filename>')
def serve_static_site(site, filename):
    blob_path = f"{site}/{filename}"
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
        stream = blob_client.download_blob()
        content = stream.readall()
        # You can improve MIME type detection here if needed
        return Response(content, mimetype='text/html')
    except Exception as e:
        print(f"Error fetching blob: {e}")
        abort(404)

@app.route('/')
def index():
    return "Welcome to the Static Site Router!"

