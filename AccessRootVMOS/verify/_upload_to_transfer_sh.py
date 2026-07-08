"""Upload binary files lên transfer.sh từ device, rồi Windows download về và push GitHub."""
import sys, time, os, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'VMOS SDK'))
from vmos_sdk import VmosClient

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
PAD    = AUTH['PADCODE']
TOKEN  = AUTH.get('GITHUB_TOKEN', '')
REPO   = 'tmq9999/VMOS-SDK-New'
REL_ID = 351160695
client = VmosClient(access_key=AUTH['Access Key ID'], secret_key=AUTH['Secret Access Key'])

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'magisk_env_bundle'))
os.makedirs(OUT_DIR, exist_ok=True)

def start_cmd(script):
    r = client.instance.async_cmd(pad_codes=[PAD], script_content=script)
    if isinstance(r.data, list) and r.data:
        return r.data[0]['taskId']
    return None

def poll(tid, max_wait=300):
    for _ in range(max_wait // 3):
        time.sleep(3)
        tr = client.task.get_task_detail(task_ids=[tid])
        if isinstance(tr.data, list) and tr.data:
            t = tr.data[0]
            if t.get('taskStatus') in (2, 3) or t.get('taskResult') or t.get('errorMsg'):
                return t.get('taskResult') or t.get('errorMsg') or ''
    return 'TIMEOUT'

def cmd(script, max_wait=300):
    tid = start_cmd(script)
    if not tid: return ''
    return poll(tid, max_wait)

print(f'PAD: {PAD}')

# Các host thử theo thứ tự
HOSTS = ['https://transfer.sh', 'https://bashupload.com', 'https://0x0.st']

def upload_to_host(device_path, fname):
    """Thử upload lên nhiều host, trả về URL đầu tiên thành công."""
    for host in HOSTS:
        print(f'  → {host}...')
        if host == 'https://transfer.sh':
            upload_cmd = f'curl -s --max-time 120 --upload-file "{device_path}" "{host}/{fname}"'
        elif host == 'https://bashupload.com':
            upload_cmd = f'curl -s --max-time 120 -T "{device_path}" "{host}/{fname}"'
        else:  # 0x0.st
            upload_cmd = f'curl -s --max-time 120 -F "file=@{device_path}" "{host}/"'

        out = cmd(upload_cmd, max_wait=150)
        out = out.strip()
        print(f'    response: {out[:150]}')
        if out and out.startswith('http') and 'error' not in out.lower():
            return out
        if 'http' in out:
            # parse URL từ response
            for word in out.split():
                if word.startswith('http'):
                    return word
    return None

def upload_to_github(local_path, asset_name):
    """Upload file từ Windows lên GitHub Releases."""
    # Delete old
    assets_out = urllib.request.urlopen(
        urllib.request.Request(
            f'https://api.github.com/repos/{REPO}/releases/{REL_ID}/assets',
            headers={'Authorization': f'token {TOKEN}', 'User-Agent': 'Python'}
        ), timeout=15
    ).read().decode()
    import json
    assets = json.loads(assets_out)
    for asset in assets:
        if asset['name'] == asset_name:
            urllib.request.urlopen(
                urllib.request.Request(
                    f'https://api.github.com/repos/{REPO}/releases/assets/{asset["id"]}',
                    method='DELETE',
                    headers={'Authorization': f'token {TOKEN}', 'User-Agent': 'Python'}
                ), timeout=15
            )
            print(f'    deleted old {asset_name}')
            break

    with open(local_path, 'rb') as f:
        data = f.read()
    req = urllib.request.Request(
        f'https://uploads.github.com/repos/{REPO}/releases/{REL_ID}/assets?name={asset_name}',
        data=data, method='POST',
        headers={
            'Authorization': f'token {TOKEN}',
            'Content-Type': 'application/octet-stream',
            'User-Agent': 'Python',
        }
    )
    resp = urllib.request.urlopen(req, timeout=120).read().decode()
    result = json.loads(resp)
    url = result.get('browser_download_url', '')
    print(f'    ✅ GitHub: {url}')
    return url

files = [
    ('/debug_ramdisk/magisk_env/magisk32',       'magisk32'),
    ('/debug_ramdisk/magisk_env/magisk64',        'magisk64'),
    ('/debug_ramdisk/magisk_env/magiskpolicy',    'magiskpolicy'),
    ('/debug_ramdisk/magisk_env/adb_magisk.zip',  'adb_magisk.zip'),
]

gh_urls = {}
for src, name in files:
    print(f'\n── {name} ──')
    tmp_url = upload_to_host(src, name)
    if not tmp_url:
        print(f'  ✗ Upload lên temp host thất bại')
        continue
    print(f'  temp URL: {tmp_url}')

    # Download về Windows
    local = os.path.join(OUT_DIR, name)
    print(f'  downloading to {local}...')
    try:
        urllib.request.urlretrieve(tmp_url, local)
        sz = os.path.getsize(local)
        print(f'  {sz:,} bytes')
    except Exception as e:
        print(f'  ✗ download: {e}')
        continue

    # Upload lên GitHub từ Windows
    print(f'  uploading to GitHub...')
    try:
        u = upload_to_github(local, name)
        if u: gh_urls[name] = u
    except Exception as e:
        print(f'  ✗ github upload: {e}')

print('\n── Summary ──')
for k, v in gh_urls.items():
    print(f'  {k}: {v}')

import json
url_file = os.path.join(OUT_DIR, 'DOWNLOAD_URLS.json')
try:
    existing = json.load(open(url_file)) if os.path.exists(url_file) else {}
except: existing = {}
existing.update(gh_urls)
json.dump(existing, open(url_file, 'w'), indent=2)
print(f'\nURLs saved: {url_file}')

client.close()
