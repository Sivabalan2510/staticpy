from flask import Flask, Response, abort
import requests
import mimetypes

app = Flask(__name__)

def hello():
    return "Hello from Flask!"
    
# Replace these with your actual storage details
STORAGE_ACCOUNT = "staticstgci"
CONTAINER_NAME = "$web"
SAS_TOKEN = "sp=rl&st=2025-07-08T12:04:59Z&se=2025-07-15T20:19:59Z&spr=https&sv=2024-11-04&sr=c&sig=NsrLETDg297yYhCZGhaEca1sfjN%2Fbxz2S94T1VBPcsg%3D"

@app.route('/<site>/')
@app.route('/<site>/<path:filename>')
def serve_site(site, filename="index.html"):
    blob_url = f"https://{STORAGE_ACCOUNT}.blob.core.windows.net/{CONTAINER_NAME}/{site}/{filename}?{SAS_TOKEN}"

    resp = requests.get(blob_url)
    if resp.status_code != 200:
        return abort(resp.status_code)

    mime_type, _ = mimetypes.guess_type(filename)
    return Response(resp.content, mimetype=mime_type or "application/octet-stream")

@app.route('/')
def root():
    return "Flask Proxy is running. Try /site1/"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
