from flask import Flask, Response, abort
from azure.storage.blob import BlobServiceClient
import os
import mimetypes

app = Flask(__name__)

# Get SAS URL for container (including container path and SAS token)
AZURE_STORAGE_SAS_URL = os.getenv("AZURE_STORAGE_SAS_URL")

if not AZURE_STORAGE_SAS_URL:
    print("❌ ERROR: AZURE_STORAGE_SAS_URL is not set.")
    exit(1)

# Initialize BlobServiceClient with the SAS URL
blob_service_client = BlobServiceClient(account_url=AZURE_STORAGE_SAS_URL)
container_name = "$web"

@app.route('/')
def index():
    return "🚀 Welcome! Use /site_name/path/to/file to fetch files."

@app.route('/<site>/', defaults={'filename': 'index.html'})
@app.route('/<site>/<path:filename>')
def serve_static_site(site, filename):
    blob_path = f"{site}/{filename}"
    print(f"📦 Fetching blob: {blob_path}")

    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
        stream = blob_client.download_blob()
        content = stream.readall()

        mime_type, _ = mimetypes.guess_type(filename)
        mime_type = mime_type or "application/octet-stream"

        return Response(content, mimetype=mime_type)

    except Exception as e:
        print(f"❌ Error fetching blob: {e}")
        abort(404)
