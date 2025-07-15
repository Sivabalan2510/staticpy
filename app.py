from flask import Flask, Response
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import os

app = Flask(__name__)

# Replace this with your actual storage account name
STORAGE_ACCOUNT_URL = "https://staticciwebstg.blob.core.windows.net"
CONTAINER_NAME = "$web"

# Authenticate using Managed Identity
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

@app.route('/<site>/', defaults={'path': 'index.html'})
@app.route('/<site>/<path:path>')
def proxy(site, path):
    blob_path = f"{site}/{path}"
    try:
        blob_client = container_client.get_blob_client(blob_path)
        downloader = blob_client.download_blob()
        data = downloader.readall()
        content_type = blob_client.get_blob_properties().content_settings.content_type
        return Response(data, mimetype=content_type or 'application/octet-stream')
    except Exception as e:
        print(f"Blob not found: {blob_path} - {e}")
        return Response(f"404 - Not Found: {blob_path}", status=404)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
