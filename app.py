from flask import Flask, Response, abort
from azure.storage.blob import BlobServiceClient
import os
import mimetypes

app = Flask(__name__)

# Get the full SAS URL to the storage account (including SAS token)
AZURE_STORAGE_SAS_URL = os.getenv("AZURE_STORAGE_SAS_URL")
CONTAINER_NAME = "$web"

if not AZURE_STORAGE_SAS_URL:
    raise RuntimeError("AZURE_STORAGE_SAS_URL environment variable is not set")

# Initialize BlobServiceClient using the SAS URL
blob_service_client = BlobServiceClient(account_url=AZURE_STORAGE_SAS_URL)

@app.route('/')
def home():
    return "🚀 Welcome! Use /site_name/ or /site_name/path/to/file to fetch files."

@app.route('/<site>/', defaults={'filename': 'index.html'})
@app.route('/<site>/<path:filename>')
def serve_file(site, filename):
    blob_path = f"{site}/{filename}"

    try:
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_path)
        blob_data = blob_client.download_blob().readall()

        mime_type, _ = mimetypes.guess_type(filename)
        mime_type = mime_type or 'application/octet-stream'

        return Response(blob_data, mimetype=mime_type)

    except Exception as e:
        app.logger.error(f"Failed to fetch blob '{blob_path}': {e}")
        abort(404)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
