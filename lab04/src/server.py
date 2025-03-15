from flask import Flask, request, Response
import requests, os, hashlib, json
from urllib.parse import urlparse

app = Flask(__name__)
LOG_FILE = "proxy.log"
CACHE_DIR = "cache"
CONFIG_FILE = "config.json"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
else:
    config = {"blacklist": []}

def log_request(url, code):
    with open(LOG_FILE, "a") as f:
        f.write(f"{url} {code}\n")

def get_cache_filename(url):
    fname = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, fname), os.path.join(CACHE_DIR, fname + ".meta")

def is_blocked(url):
    parsed = urlparse(url if "://" in url else "http://" + url)
    domain = parsed.netloc
    for blocked in config.get("blacklist", []):
        if blocked in domain:
            return True
    return False

def filter_headers(headers, content):
    excluded = ['transfer-encoding', 'content-encoding', 'content-length', 'connection']
    filtered = {k: v for k, v in headers.items() if k.lower() not in excluded}
    filtered["Content-Length"] = str(len(content))
    return filtered

@app.route('/', defaults={'target': ''}, methods=["GET", "POST"])
@app.route('/<path:target>', methods=["GET", "POST"])
def proxy(target):
    target_url = target
    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        target_url = "http://" + target_url
    parsed = urlparse(target_url)
    if not parsed.netloc or '.' not in parsed.netloc:
        log_request(target_url, 400)
        return Response("Invalid target URL.", status=400)
    if is_blocked(target_url):
        log_request(target_url, 403)
        return Response("This page is blocked by the proxy.", status=403)
    method = request.method
    headers = {}
    for h in ["User-Agent", "Accept", "Content-Type"]:
        if h in request.headers:
            headers[h] = request.headers[h]
    try:
        if method == "GET":
            cache_file, meta_file = get_cache_filename(target_url)
            if os.path.exists(cache_file) and os.path.exists(meta_file):
                with open(meta_file, "r") as f:
                    meta = json.load(f)
                # If conditional headers exist, perform conditional GET
                if "Last-Modified" in meta or "ETag" in meta:
                    if "Last-Modified" in meta:
                        headers["If-Modified-Since"] = meta["Last-Modified"]
                    if "ETag" in meta:
                        headers["If-None-Match"] = meta["ETag"]
                    resp = requests.get(target_url, headers=headers, timeout=5)
                    if resp.status_code == 304:
                        with open(cache_file, "rb") as f:
                            content = f.read()
                        log_request(target_url, 304)
                        return Response(content, status=304, headers=filter_headers(resp.headers, content))
                    else:
                        content = resp.content
                        if resp.status_code == 200:
                            new_meta = {}
                            if "Last-Modified" in resp.headers:
                                new_meta["Last-Modified"] = resp.headers["Last-Modified"]
                            if "ETag" in resp.headers:
                                new_meta["ETag"] = resp.headers["ETag"]
                            with open(cache_file, "wb") as f:
                                f.write(content)
                            with open(meta_file, "w") as f:
                                json.dump(new_meta, f)
                        log_request(target_url, resp.status_code)
                        return Response(content, status=resp.status_code, headers=filter_headers(resp.headers, content))
                else:
                    # No conditional info, serve cache directly
                    with open(cache_file, "rb") as f:
                        content = f.read()
                    log_request(target_url, 200)
                    return Response(content, status=200, headers={"Content-Length": str(len(content))})
            else:
                resp = requests.get(target_url, headers=headers, timeout=5)
                content = resp.content
                if resp.status_code == 200:
                    meta = {}
                    if "Last-Modified" in resp.headers:
                        meta["Last-Modified"] = resp.headers["Last-Modified"]
                    if "ETag" in resp.headers:
                        meta["ETag"] = resp.headers["ETag"]
                    with open(cache_file, "wb") as f:
                        f.write(content)
                    with open(meta_file, "w") as f:
                        json.dump(meta, f)
                log_request(target_url, resp.status_code)
                return Response(content, status=resp.status_code, headers=filter_headers(resp.headers, content))
        elif method == "POST":
            data = request.get_data()
            resp = requests.post(target_url, headers=headers, data=data, timeout=5)
            if resp.status_code == 405:
                resp = requests.get(target_url, headers=headers, timeout=5)
            content = resp.content
            log_request(target_url, resp.status_code)
            return Response(content, status=resp.status_code, headers=filter_headers(resp.headers, content))
        else:
            return Response("Method Not Allowed", status=405)
    except Exception as e:
        log_request(target_url, 500)
        return Response("Error occurred: " + str(e), status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)
