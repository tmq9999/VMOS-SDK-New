"""Upload files từ local Magisk_env/ lên GitHub Releases."""
import sys, os, json, urllib.request, urllib.error

sys.stdout.reconfigure(encoding='utf-8')

def load_auth(p):
    c = {}
    with open(p, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if ':' in line:
                k, _, v = line.partition(':')
                c[k.strip()] = v.strip()
    return c

AUTH   = load_auth(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'Auth_Key.txt'))
TOKEN  = AUTH.get('GITHUB_TOKEN', '')
REPO   = 'tmq9999/VMOS-SDK-New'
REL_ID = 351160695

LOCAL_DIR = os.path.join(os.path.dirname(__file__), '..', 'Magisk_env')

def gh_request(url, method='GET', data=None, content_type='application/json'):
    req = urllib.request.Request(url, data=data, method=method, headers={
        'Authorization': f'token {TOKEN}',
        'User-Agent': 'Python',
        'Content-Type': content_type,
    })
    try:
        resp = urllib.request.urlopen(req, timeout=120)
        return resp.read().decode(), resp.status
    except urllib.error.HTTPError as e:
        return e.read().decode(), e.code

def delete_existing(asset_name):
    body, _ = gh_request(f'https://api.github.com/repos/{REPO}/releases/{REL_ID}/assets')
    assets = json.loads(body)
    for a in assets:
        if a['name'] == asset_name:
            gh_request(f'https://api.github.com/repos/{REPO}/releases/assets/{a["id"]}', method='DELETE')
            print(f'  deleted old: {asset_name}')
            return

def upload_file(local_path, asset_name):
    print(f'  uploading {asset_name} ({os.path.getsize(local_path):,} bytes)...')
    delete_existing(asset_name)
    with open(local_path, 'rb') as f:
        data = f.read()
    url = f'https://uploads.github.com/repos/{REPO}/releases/{REL_ID}/assets?name={asset_name}'
    body, status = gh_request(url, method='POST', data=data, content_type='application/octet-stream')
    if status in (200, 201):
        result = json.loads(body)
        dl_url = result.get('browser_download_url', '')
        print(f'  ✅ {dl_url}')
        return dl_url
    else:
        print(f'  ✗ status={status}: {body[:200]}')
        return None

print(f'Repo: {REPO}  Release: {REL_ID}')
print(f'Source: {os.path.abspath(LOCAL_DIR)}\n')

files = sorted(os.listdir(LOCAL_DIR))
urls = {}
for fname in files:
    local = os.path.join(LOCAL_DIR, fname)
    if os.path.isfile(local):
        u = upload_file(local, fname)
        if u:
            urls[fname] = u

print(f'\n── Summary ({len(urls)}/{len(files)}) ──')
for k, v in urls.items():
    print(f'  {k}')

url_file = os.path.join(LOCAL_DIR, '..', '..', 'magisk_env_bundle', 'DOWNLOAD_URLS.json')
os.makedirs(os.path.dirname(url_file), exist_ok=True)
json.dump(urls, open(url_file, 'w'), indent=2)
print(f'\nURLs saved: {os.path.abspath(url_file)}')
