"""Tìm base URL thật sự trong ToolBox APK."""
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

APK = '/system/priv-app/Tools_custom/Tools_custom.apk'

print('\n[1] Tất cả strings chứa "http":')
print(cmd(f'strings "{APK}" 2>/dev/null | grep -i "http" | grep -v "schema\\|xmlns\\|http/1\\|okhttp\\|//w3" | sort -u | head -30'))

print('\n[2] Strings chứa domain pattern:')
print(cmd(f'strings "{APK}" 2>/dev/null | grep -E "[a-z0-9-]+\\.(com|cn|net|io)/[a-z]" | grep -v "android\\|google\\|schema\\|apache\\|java\\|kotlin" | sort -u | head -30'))

print('\n[3] Strings chứa "magisk" context rộng hơn:')
print(cmd(f'strings "{APK}" 2>/dev/null | grep -B2 -A2 "magisk" 2>/dev/null | head -40'))

print('\n[4] Thử logcat TRONG KHI ToolBox đang chạy (network calls):')
print(cmd(r"""#!/system/bin/sh
logcat -d -s okhttp.OkHttpClient:* OkHttp:* -t 200 2>/dev/null | grep -iE "url|http|magisk|GET|POST" | head -20
"""))

print('\n[5] /proc/net/tcp6 connections của ToolBox:')
print(cmd(r"""#!/system/bin/sh
TB_PID=$(pidof com.android.expansiontools 2>/dev/null)
echo "PID=$TB_PID"
cat /proc/net/tcp6 2>/dev/null | head -10
"""))

client.close()
