"""Diagnose Google One offer failure."""
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

def cmd(script, wait=30):
    r = client.instance.async_cmd(pad_codes=[PAD], script_content=script)
    tid = r.data[0]['taskId']
    for _ in range(wait // 2):
        time.sleep(2)
        tr = client.task.get_task_detail(task_ids=[tid])
        if isinstance(tr.data, list) and tr.data:
            t = tr.data[0]
            if t.get('taskStatus') in (2, 3) or t.get('taskResult') or t.get('errorMsg'):
                return t.get('taskResult') or t.get('errorMsg') or ''
    return 'TIMEOUT'

PKG = 'com.google.android.apps.subscriptions.red'

SCRIPT = r"""#!/system/bin/sh
echo "=== PROPS ==="
getprop ro.product.model
getprop ro.product.device
getprop ro.build.fingerprint
getprop ro.build.version.release
getprop ro.build.version.sdk
echo "=== GOOGLE ONE ==="
dumpsys package com.google.android.apps.subscriptions.red 2>/dev/null | grep -E 'versionName|firstInstall|lastUpdate' | head -5
echo "=== CACHE SIZE ==="
du -sh /data/data/com.google.android.apps.subscriptions.red/cache 2>/dev/null
echo "=== SHARED PREFS ==="
ls /data/data/com.google.android.apps.subscriptions.red/shared_prefs/ 2>/dev/null
echo "=== OFFER IN DB ==="
find /data/data/com.google.android.apps.subscriptions.red -name '*.db' 2>/dev/null | head -10
grep -roa 'partner-eft-onboard/[A-Z0-9]*' /data/data/com.google.android.apps.subscriptions.red/ 2>/dev/null | head -5
grep -roa 'not available\|unavailable\|eligible' /data/data/com.google.android.apps.subscriptions.red/ 2>/dev/null | head -5
echo "=== GMS DEVICE CHECKIN ==="
getprop ro.build.fingerprint
dumpsys deviceidle 2>/dev/null | grep -i 'device\|registered' | head -3
echo "=== DONE ==="
"""

print(f'PAD: {PAD}')
print('Diagnosing...')
out = cmd(SCRIPT, wait=35)
print(out[:3000])
client.close()
