from flask import Flask, Response
from azure.storage.blob import BlobServiceClient
import os

app = Flask(__name__)

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "web"
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

@app.route('/<site>/<path:file_path>')
def serve_static(site, file_path):
    blob_path = f"{site}/{file_path}"
    try:
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_path)
        blob_data = blob_client.download_blob().readall()
        return Response(blob_data, mimetype='text/html')
    except Exception as e:
        return f"Error fetching file: {str(e)}", 404

if __name__ == '__main__':
    app.run()
