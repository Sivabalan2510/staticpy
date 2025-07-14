from flask import Flask, Response, abort
from azure.storage.blob import BlobServiceClient
import os
import mimetypes

app = Flask(__name__)

# Get and validate the connection string
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

if not AZURE_STORAGE_CONNECTION_STRING:
    print("❌ ERROR: AZURE_STORAGE_CONNECTION_STRING is not set.")
    exit(1)

# Optional: partially mask the connection string for log visibility
masked = AZURE_STORAGE_CONNECTION_STRING[:30] + "..." if AZURE_STORAGE_CONNECTION_STRING else "None"
print(f"✅ AZURE_STORAGE_CONNECTION_STRING loaded: {masked}")

# Set up Blob service
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
container_name = "$web"

# ✅ Keep just ONE root route
@app.route('/')
def index():
    return "🚀 Welcome to the Static Site Router! Use /site_name/path/to/file to fetch files."

# Route to serve static site files
@app.route('/<site>/<path:filename>')
def serve_static_site(site, filename):
    blob_path = f"{site}/{filename}"
    print(f"📦 Fetching blob: {blob_path}")

    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
        stream = blob_client.download_blob()
        content = stream.readall()

        # Guess the correct MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        mime_type = mime_type or "application/octet-stream"

        return Response(content, mimetype=mime_type)

    except Exception as e:
        print(f"❌ Error fetching blob: {e}")
        abort(404)
