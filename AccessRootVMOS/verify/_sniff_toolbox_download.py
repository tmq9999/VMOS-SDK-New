"""Sniff URL download Magisk từ ToolBox.

Approach:
1. Đọc strings trong ToolBox APK để tìm URL pattern
2. Monitor logcat khi ToolBox đang chạy để bắt HTTP request
3. Kiểm tra databases của ToolBox
"""
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

AUTH = load_auth(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'Auth_Key.txt'))
PAD = AUTH['PADCODE']
client = VmosClient(access_key=AUTH['Access Key ID'], secret_key=AUTH['Secret Access Key'])

def cmd(script, max_wait=25):
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

print('\n[1] Tìm ToolBox APK path:')
apk_path = cmd(r'pm path com.android.expansiontools 2>/dev/null')
print(f'  {apk_path.strip()}')

# Extract APK path
apk = None
for line in apk_path.splitlines():
    if 'package:' in line:
        apk = line.split('package:')[1].strip()
        break
print(f'  APK: {apk}')

if apk:
    print('\n[2] Strings trong APK liên quan magisk/download/url:')
    print(cmd(f'strings "{apk}" 2>/dev/null | grep -iE "(magisk|install\\.sh|adb_magisk|https.*magisk|download.*magisk)" | head -20'))

    print('\n[3] Strings URL patterns trong APK:')
    print(cmd(f'strings "{apk}" 2>/dev/null | grep -E "^https?://" | grep -v "google\\|android\\|schema\\|xmlns\\|w3c\\|apache\\|github\\.com/google" | head -30'))

print('\n[4] ToolBox databases:')
print(cmd(r'ls /data/data/com.android.expansiontools/databases/ 2>/dev/null || echo no_db'))

print('\n[5] mmkv keys (ToolBox config store):')
print(cmd(r"""#!/system/bin/sh
ls /data/data/com.android.expansiontools/files/mmkv/ 2>/dev/null
strings /data/data/com.android.expansiontools/files/mmkv/mmkv.default 2>/dev/null | grep -iE 'magisk|install|download|url|http|version|zip' | head -20
"""))

print('\n[6] logcat filter ToolBox:')
print(cmd(r'logcat -d -t 100 --pid=$(pidof com.android.expansiontools 2>/dev/null) 2>/dev/null | grep -iE "magisk|download|install|http" | head -15'))

client.close()
