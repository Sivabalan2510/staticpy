from flask import Flask, Response
from azure.storage.blob import BlobServiceClient
import os
import mimetypes

app = Flask(__name__)

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "$web"
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

@app.route('/<path:file_path>')
def serve_static(file_path):
    try:
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file_path)
        blob_data = blob_client.download_blob().readall()
        mime_type, _ = mimetypes.guess_type(file_path)
        return Response(blob_data, mimetype=mime_type or 'application/octet-stream')
    except Exception as e:
        return f"Error fetching file: {str(e)}", 404

if __name__ == '__main__':
    app.run()
