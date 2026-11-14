"""AppEEARS point-sample request for HLS red/NIR/Fmask over the demo parcel (T-013). PREPARATION ONLY.

`build_request()` and `main()` are offline: they only build / print the JSON body and the manual steps.
`submit()`, `get_status()` and `download_bundle()` talk to the network, need NASA Earthdata credentials from
environment variables, and are NEVER called by the tests or by main().

Official documentation used (read 2026-11-14):
  * AppEEARS API, base URL, login, task, status, bundle: https://appeears.earthdatacloud.nasa.gov/api/
      POST /login        HTTP Basic (Earthdata username:password) -> {"token_type":"Bearer","token":...,"expiration":...}
                         the token "will expire approximately 48 hours after being acquired"; on HTTP 403 get a new one
      POST /task         Authorization: Bearer <token>, JSON body, HTTP 202 + {"task_id":..., "status":"pending"}
      GET  /status/{id}  states pending | processing | done | error (HTTP 303 -> /api/task/{id} when done)
      GET  /bundle/{id}  list of files {file_id, file_name, file_size, file_type, sha256}
      GET  /bundle/{id}/{file_id}  HTTP 302 to a presigned S3 URL (valid 48 h); the client must follow the redirect
    Point task schema from the same page: task_type "point"; params.dates[] {startDate,endDate} as MM-DD-YYYY;
    params.layers[] {product, layer}; params.coordinates[] {latitude, longitude, id, category}.
  * Product ids and layer names, from the public product catalogue (no login needed):
      https://appeears.earthdatacloud.nasa.gov/api/product                      -> HLSL30.020, HLSS30.020, HLSL30_VI.020, HLSS30_VI.020
      https://appeears.earthdatacloud.nasa.gov/api/product/HLSL30.020           -> layers B04, B05, Fmask (uint8, fill 255) ...
      https://appeears.earthdatacloud.nasa.gov/api/product/HLSS30.020           -> layers B04, B8A, Fmask (uint8, fill 255) ...
      https://appeears.earthdatacloud.nasa.gov/api/product/HLSS30_VI.020        -> NDVI layer (int16, scale 0.0001, fill -19999), NO quality layer
      https://appeears.earthdatacloud.nasa.gov/api/quality/HLSS30.020/Fmask     -> decoded Fmask fields (cloud, adjacent, shadow, snow/ice, water, aerosol)
NOTE: the task brief said 'HLSL30.002 / HLSS30.002'. AppEEARS lists them as version '.020' (the HLS 2.0 collection);
'.002' returned HTTP 404 on the product endpoint. We use the *_30.020 reflectance products (not *_VI.020) on purpose:
the VI products carry no Fmask in AppEEARS (IsQA false, empty QualityLayers), so clouds could not be masked.
"""
import base64
import json
import math
import os
import urllib.error
import urllib.request

API = "https://appeears.earthdatacloud.nasa.gov/api"

# Demo parcel: Torre-Pacheco, SIGPAC 18/426/1, ~4.1 ha (centre coordinate given by the team).
PARCEL_LAT, PARCEL_LON = 37.73830, -0.98838

# One AppEEARS point = the 30 m pixel under it. A small grid around the centre approximates a parcel mean
# (bare_soil.parcel_mean_ndvi). 3 x 3 points at 30 m spacing covers 60 x 60 m: ASSUMPTION that this stays inside the
# 4.1 ha parcel; check against the SIGPAC polygon before trusting edge points (not verified).
GRID_N = 3
GRID_SPACING_M = 30.0

# (product, layers). NIR is B05 on Landsat OLI and B8A on Sentinel-2 (HLS V2.0 User Guide, section 6.2 / Table 7).
LAYERS = [
    ("HLSL30.020", ["B04", "B05", "Fmask"]),
    ("HLSS30.020", ["B04", "B8A", "Fmask"]),
]

# Two winters (Oct-Mar) plus the summer between them. HLS has data from 2013 (L30) / 2015 (S30) onwards.
DEFAULT_START, DEFAULT_END = "2024-09-01", "2026-10-31"


def _mmddyyyy(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{m}-{d}-{y}"


def grid_points(lat=PARCEL_LAT, lon=PARCEL_LON, n=GRID_N, spacing_m=GRID_SPACING_M):
    """n x n coordinates centred on (lat, lon), `spacing_m` apart (flat-earth approximation, fine at 30 m)."""
    dlat = spacing_m / 111_320.0
    dlon = spacing_m / (111_320.0 * math.cos(math.radians(lat)))
    half = (n - 1) / 2.0
    pts = []
    for i in range(n):
        for j in range(n):
            pts.append({"latitude": round(lat + (i - half) * dlat, 6), "longitude": round(lon + (j - half) * dlon, 6),
                        "id": f"p{i}{j}", "category": "parcel_18_426_1"})
    return pts


def build_request(start=DEFAULT_START, end=DEFAULT_END, n=GRID_N, spacing_m=GRID_SPACING_M,
                  task_name="agrockham-t013-hls-torre-pacheco-18-426-1") -> dict:
    """JSON body for POST {API}/task (task_type 'point'). Offline, no credentials."""
    return {
        "task_type": "point",
        "task_name": task_name,
        "params": {
            "dates": [{"startDate": _mmddyyyy(start), "endDate": _mmddyyyy(end)}],
            "layers": [{"product": p, "layer": l} for p, ls in LAYERS for l in ls],
            "coordinates": grid_points(n=n, spacing_m=spacing_m),
        },
    }


MANUAL_STEPS = """\
MANUAL STEPS (the human does these; nothing here was executed):
 1. Create a free NASA Earthdata Login account: https://urs.earthdata.nasa.gov/users/new  (confirm the e-mail).
 2. Log in once at https://appeears.earthdatacloud.nasa.gov/ ; accept the AppEEARS terms / authorise the app if asked.
 3. Option A (browser, no code): Extract > Point Samples > Start a new request. Paste the coordinates (id, category,
    latitude, longitude), set the date range, add the layers listed in the body above, format CSV, Submit.
    Option B (script): export EARTHDATA_USER=... EARTHDATA_PASS=...  (never write them in a file), then
    `python3 -c "from app.backend.ndvi import appeears_request as r; print(r.submit())"`.
 4. Wait for status 'done' (minutes to a few hours: queues are unpredictable). Download the CSV bundle(s) into
    app/data/cache/ndvi/ (one CSV per product).
 5. Tell the agent: the CSVs are there, and it runs appeears_csv + bare_soil to produce the `ndvi` block.
"""


def main():
    """Print the request body and the manual steps. No network, no credentials."""
    print(json.dumps(build_request(), indent=2))
    print()
    print(MANUAL_STEPS)


# ----------------------------------------------------------------------------------------------------------------------
# Everything below needs the network and credentials. NOT called by main() or by any test.
# ----------------------------------------------------------------------------------------------------------------------
def _token_from_env() -> str:
    """Bearer token from env. EARTHDATA_TOKEN = an AppEEARS bearer token (as returned by POST /login). Whether an
    Earthdata-Login user token is also accepted was NOT verified. Otherwise EARTHDATA_USER/EARTHDATA_PASS -> POST /login.
    Credentials are never printed or written to disk."""
    tok = os.environ.get("EARTHDATA_TOKEN")
    if tok:
        return tok
    user, pw = os.environ.get("EARTHDATA_USER"), os.environ.get("EARTHDATA_PASS")
    if not user or not pw:
        raise RuntimeError("Set EARTHDATA_USER and EARTHDATA_PASS (or EARTHDATA_TOKEN) in the environment.")
    basic = base64.b64encode(f"{user}:{pw}".encode()).decode()
    req = urllib.request.Request(f"{API}/login", method="POST", data=b"",
                                 headers={"Authorization": f"Basic {basic}", "Content-Length": "0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["token"]


def _call(method, path, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Authorization": f"Bearer {token}"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{API}{path}", method=method, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def submit(body=None) -> str:
    """POST /task. Returns the task_id. Needs credentials (see _token_from_env)."""
    return _call("POST", "/task", _token_from_env(), body or build_request())["task_id"]


def get_status(task_id: str) -> dict:
    """GET /status/{task_id}. (A 303 redirect when done is followed by urllib; the JSON of the task is returned.)"""
    return _call("GET", f"/status/{task_id}", _token_from_env())


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def download_bundle(task_id: str, out_dir: str, only_csv: bool = True) -> list:
    """GET /bundle/{id} then each /bundle/{id}/{file_id}: 302 -> presigned S3 URL, fetched WITHOUT the Authorization
    header (a presigned URL must not get an extra auth header)."""
    token = _token_from_env()
    os.makedirs(out_dir, exist_ok=True)
    saved = []
    for f in _call("GET", f"/bundle/{task_id}", token)["files"]:
        if only_csv and f.get("file_type") != "csv":
            continue
        req = urllib.request.Request(f"{API}/bundle/{task_id}/{f['file_id']}", headers={"Authorization": f"Bearer {token}"})
        try:
            urllib.request.build_opener(_NoRedirect).open(req, timeout=120)
            raise RuntimeError("expected a 302 redirect")
        except urllib.error.HTTPError as e:
            if e.code != 302:
                raise
            url = e.headers["Location"]
        dest = os.path.join(out_dir, os.path.basename(f["file_name"]))
        with urllib.request.urlopen(url, timeout=300) as r, open(dest, "wb") as out:
            out.write(r.read())
        saved.append(dest)
    return saved


if __name__ == "__main__":
    main()
