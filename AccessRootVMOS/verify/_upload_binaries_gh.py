"""Upload binary files lên GitHub Releases từ device — từng file một, poll task."""
import sys, time, os
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

AUTH     = load_auth(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'Auth_Key.txt'))
PAD      = AUTH['PADCODE']
TOKEN    = AUTH.get('GITHUB_TOKEN', '')
REPO     = 'tmq9999/VMOS-SDK-New'
REL_ID   = 351160695
client   = VmosClient(access_key=AUTH['Access Key ID'], secret_key=AUTH['Secret Access Key'])

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

def upload_binary(device_path, asset_name):
    print(f'\n── {asset_name} ──')
    # Xóa asset cũ nếu có
    old = poll(start_cmd(f"""curl -s --max-time 15 \
-H "Authorization: token {TOKEN}" \
"https://api.github.com/repos/{REPO}/releases/{REL_ID}/assets" | \
grep -B1 '"name": "{asset_name}"' | grep '"id"' | head -1"""), 30)
    for line in (old or '').splitlines():
        if '"id"' in line:
            try:
                aid = int(line.split(':')[1].strip().rstrip(','))
                poll(start_cmd(f'curl -s -X DELETE -H "Authorization: token {TOKEN}" '
                               f'"https://api.github.com/repos/{REPO}/releases/assets/{aid}"'), 20)
                print(f'  deleted old asset id={aid}')
            except: pass

    print(f'  uploading...')
    tid = start_cmd(f"""curl -s --max-time 300 \
-X POST \
-H "Authorization: token {TOKEN}" \
-H "Content-Type: application/octet-stream" \
--data-binary @{device_path} \
"https://uploads.github.com/repos/{REPO}/releases/{REL_ID}/assets?name={asset_name}" \
2>/dev/null | grep -E '"browser_download_url"|"state"|"size"'""")

    if not tid:
        print('  ✗ task not started'); return None

    # Poll tối đa 5 phút
    out = poll(tid, max_wait=320)
    print(f'  {out.strip()[:300]}')
    for line in (out or '').splitlines():
        if 'browser_download_url' in line:
            url = line.split('"')[-2]
            print(f'  ✅ {url}')
            return url
    return None

print(f'PAD: {PAD}  REL_ID: {REL_ID}')

files = [
    ('/debug_ramdisk/magisk_env/magisk32',      'magisk32'),
    ('/debug_ramdisk/magisk_env/magisk64',      'magisk64'),
    ('/debug_ramdisk/magisk_env/magiskpolicy',  'magiskpolicy'),
    ('/debug_ramdisk/magisk_env/adb_magisk.zip','adb_magisk.zip'),
]

urls = {}
for src, name in files:
    u = upload_binary(src, name)
    if u:
        urls[name] = u

print('\n── Summary ──')
for k, v in urls.items():
    print(f'  {k}: {v}')

missing = [name for _, name in files if name not in urls]
if missing:
    print(f'\n⚠️  Chưa upload được: {missing}')
else:
    print('\n✅ Tất cả files đã upload!')

client.close()
