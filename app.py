from flask import Flask, Response
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ClientAuthenticationError, ResourceNotFoundError
import os

app = Flask(__name__)

STORAGE_ACCOUNT_NAME = "staticciwebstg"  # <- Update if needed
CONTAINER_NAME = "$web"
BLOB_URL = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"

# Authenticate using Managed Identity
credential = ManagedIdentityCredential()

# OPTIONAL: Debug check to verify token acquisition
try:
    token = credential.get_token("https://storage.azure.com/.default")
    print("✅ Access token obtained")
except ClientAuthenticationError as e:
    print("❌ Token failure:", e)

# Create blob service client
blob_service_client = BlobServiceClient(account_url=BLOB_URL, credential=credential)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

@app.route('/<site>/', defaults={'path': 'index.html'})
@app.route('/<site>/<path:path>')
def serve_blob(site, path):
    blob_path = f"{site}/{path}"
    print(f"📦 Requesting blob: {blob_path}")
    try:
        blob_client = container_client.get_blob_client(blob_path)
        blob_data = blob_client.download_blob().readall()
        properties = blob_client.get_blob_properties()
        content_type = properties.content_settings.content_type or "application/octet-stream"
        return Response(blob_data, mimetype=content_type)
    except ResourceNotFoundError:
        print(f"⚠️ Blob not found: {blob_path}")
        return Response(f"404 - Not Found: {blob_path}", status=404)
    except Exception as e:
        print(f"❌ Error loading blob '{blob_path}': {e}")
        return Response(f"500 - Server Error", status=500)
