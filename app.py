from flask import Flask, Response
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ClientAuthenticationError, ResourceNotFoundError
import time

app = Flask(__name__)

# Configuration
STORAGE_ACCOUNT_NAME = "staticciwebstg"  # Replace with your storage account name
CONTAINER_NAME = "$web"
MAX_RETRIES = 3
RETRY_DELAY = 3  # seconds

# Construct blob service client using Managed Identity
BLOB_URL = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
credential = ManagedIdentityCredential()
blob_service_client = BlobServiceClient(account_url=BLOB_URL, credential=credential)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)


@app.route('/<site>/', defaults={'path': 'index.html'})
@app.route('/<site>/<path:path>')
def serve_blob(site, path):
    blob_path = f"{site}/{path}"
    print(f"📦 Requesting blob: {blob_path}")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            blob_client = container_client.get_blob_client(blob_path)

            # Download blob content
            blob_data = blob_client.download_blob().readall()

            # Try to detect MIME type
            props = blob_client.get_blob_properties()
            content_type = props.content_settings.content_type or "application/octet-stream"

            return Response(blob_data, mimetype=content_type)

        except ClientAuthenticationError as e:
            print(f"⚠️ Attempt {attempt} - Authorization error: {e}")
            if attempt == MAX_RETRIES:
                return Response("403 - Unauthorized", status=403)
            time.sleep(RETRY_DELAY)

        except ResourceNotFoundError:
            print(f"❌ Blob not found: {blob_path}")
            return Response(f"404 - Not Found: {blob_path}", status=404)

        except Exception as e:
            print(f"❌ Unexpected error on attempt {attempt}: {e}")
            return Response(f"500 - Server Error: {blob_path}", status=500)

    return Response("500 - Retry Failed", status=500)


# Optional: health check
@app.route("/health")
def health():
    return "OK", 200
