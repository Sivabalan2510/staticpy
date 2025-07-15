from flask import Flask, Response, abort
import requests
import mimetypes

app = Flask(__name__)

# Replace these with your actual storage details
STORAGE_ACCOUNT = "staticstgci"
CONTAINER_NAME = "$web"
SAS_TOKEN = "sv=2024-11-04&ss=b&srt=sco&sp=rltfx&se=2025-07-15T19:22:02Z&st=2025-07-11T11:07:02Z&spr=https&sig=BiJU%2F23C47MWXiQgWpEcHVld%2BKUPh7G664C9xXPByXg%3D"

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
