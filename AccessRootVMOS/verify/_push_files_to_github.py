"""Upload từng file magisk_env lên GitHub Releases.

Dùng GitHub Releases API — upload từng file nhỏ riêng lẻ thay vì 1 tar lớn.
"""
import sys, time, os, json
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

AUTH = load_auth(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'Auth_Key.txt'))
PAD = AUTH['PADCODE']
GITHUB_TOKEN = AUTH.get('GITHUB_TOKEN', '')
GITHUB_REPO = 'tmq9999/VMOS-SDK-New'
RELEASE_TAG = 'v1.0.0-magisk'

client = VmosClient(access_key=AUTH['Access Key ID'], secret_key=AUTH['Secret Access Key'])

def cmd(script, max_wait=180):
    r = client.instance.async_cmd(pad_codes=[PAD], script_content=script)
    if not (isinstance(r.data, list) and r.data):
        return ''
    tid = r.data[0]['taskId']
    for _ in range(max_wait // 2):
        time.sleep(2)
        tr = client.task.get_task_detail(task_ids=[tid])
        if isinstance(tr.data, list) and tr.data:
            t = tr.data[0]
            if t.get('taskStatus') in (2, 3) or t.get('taskResult') or t.get('errorMsg'):
                return t.get('taskResult') or t.get('errorMsg') or ''
    return 'TIMEOUT'

print(f'PAD: {PAD}')

# Lấy release_id
print('\n[1] Get release id...')
rel = cmd(f"""curl -s --max-time 15 \
  -H "Authorization: token {GITHUB_TOKEN}" \
  "https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{RELEASE_TAG}" | \
  grep '"id"' | head -1""", max_wait=20)
print(f'  {rel.strip()}')
release_id = None
for line in rel.splitlines():
    if '"id"' in line:
        try:
            release_id = int(line.split(':')[1].strip().rstrip(','))
            break
        except: pass
print(f'  release_id={release_id}')
if not release_id:
    print('❌ Không lấy được release_id'); client.close(); sys.exit(1)

# Xóa asset cũ nếu có (tránh duplicate)
def delete_old_asset(name):
    assets = cmd(f"""curl -s --max-time 15 \
  -H "Authorization: token {GITHUB_TOKEN}" \
  "https://api.github.com/repos/{GITHUB_REPO}/releases/{release_id}/assets" | \
  grep -E '"id"|"name"' | head -30""", max_wait=20)
    # Tìm id của asset cần xóa
    lines = assets.splitlines()
    for i, line in enumerate(lines):
        if f'"{name}"' in line and i > 0:
            prev = lines[i-1]
            if '"id"' in prev:
                try:
                    aid = int(prev.split(':')[1].strip().rstrip(','))
                    cmd(f"""curl -s --max-time 15 -X DELETE \
  -H "Authorization: token {GITHUB_TOKEN}" \
  "https://api.github.com/repos/{GITHUB_REPO}/releases/assets/{aid}" """, max_wait=15)
                    print(f'  deleted old asset {name} (id={aid})')
                except: pass

def upload_file(device_path, asset_name, size_kb):
    print(f'\n[upload] {asset_name} (~{size_kb}KB)...')
    delete_old_asset(asset_name)
    out = cmd(f"""curl -s --max-time 180 \
  -X POST \
  -H "Authorization: token {GITHUB_TOKEN}" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @{device_path} \
  "https://uploads.github.com/repos/{GITHUB_REPO}/releases/{release_id}/assets?name={asset_name}" | \
  grep -E '"browser_download_url"|"size"|"state"|"name"'""", max_wait=200)
    print(f'  {out.strip()[:300]}')
    for line in out.splitlines():
        if 'browser_download_url' in line:
            url = line.split('"')[-2]
            print(f'  ✅ {url}')
            return url
    return None

urls = {}

# Upload text scripts (từ backup đã copy trước)
TEXT_FILES = [
    ('install.sh', 4), ('uninstall.sh', 3), ('install_modules.sh', 2),
    ('uninstall_modules.sh', 2), ('installed_files.txt', 2),
    ('default_su_apps.txt', 1), ('sepolicy.rule', 1),
]
for fname, kb in TEXT_FILES:
    u = upload_file(f'/debug_ramdisk/magisk_env/{fname}', fname, kb)
    if u: urls[fname] = u

# Upload binaries
BIN_FILES = [
    ('magisk32', 276), ('magisk64', 430), ('magiskpolicy', 324),
]
for fname, kb in BIN_FILES:
    u = upload_file(f'/debug_ramdisk/magisk_env/{fname}', fname, kb)
    if u: urls[fname] = u

# adb_magisk.zip — file lớn nhất (2.7MB) upload cuối
u = upload_file('/debug_ramdisk/magisk_env/adb_magisk.zip', 'adb_magisk.zip', 2860)
if u: urls['adb_magisk.zip'] = u

# Lưu URLs
url_file = os.path.join(os.path.dirname(__file__), '..', '..', 'magisk_env_bundle', 'DOWNLOAD_URLS.json')
os.makedirs(os.path.dirname(url_file), exist_ok=True)
with open(url_file, 'w') as f:
    json.dump(urls, f, indent=2)
print(f'\n✅ URLs saved: {url_file}')
print(json.dumps(urls, indent=2))

client.close()
