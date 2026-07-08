"""Lấy Magisk download URL từ VMOS API endpoint.

ToolBox dùng: /openapi/open/magisk/rom/oss/record/query
Base: https://api.vmoscloud.com (hoặc tương tự)
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

# Lấy base URL từ APK strings
print('\n[1] Tìm base URL trong APK:')
out = cmd(r"""#!/system/bin/sh
strings /system/priv-app/Tools_custom/Tools_custom.apk 2>/dev/null | grep -E "^https?://[a-z].*api\." | sort -u | head -10
strings /system/priv-app/Tools_custom/Tools_custom.apk 2>/dev/null | grep -E "vmoscloud|vmos" | grep -E "^https?://" | sort -u | head -10
strings /system/priv-app/Tools_custom/Tools_custom.apk 2>/dev/null | grep "openapi" | head -5
""")
print(out)

# Thử gọi API từ on-device với curl
print('\n[2] Gọi VMOS Magisk query API từ device:')
out2 = cmd(r"""#!/system/bin/sh
curl -s --max-time 15 \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"padCode":"PLACEHOLDER"}' \
  "https://api.vmoscloud.com/openapi/open/magisk/rom/oss/record/query" 2>/dev/null | head -c 1000
""")
print(f'  response: {out2.strip()[:500]}')

# Thử không có body
print('\n[3] Gọi không body:')
out3 = cmd(r"""#!/system/bin/sh
curl -s --max-time 15 \
  -X GET \
  "https://api.vmoscloud.com/openapi/open/magisk/rom/oss/record/query" 2>/dev/null | head -c 500
""")
print(f'  response: {out3.strip()[:500]}')

# Đọc app_database của ToolBox
print('\n[4] ToolBox app_database:')
out4 = cmd(r"""#!/system/bin/sh
sqlite3 /data/data/com.android.expansiontools/databases/app_database 2>/dev/null \
  ".tables"
""")
print(f'  tables: {out4.strip()}')

print('\n[5] Strings trong mmkv:')
out5 = cmd(r"""#!/system/bin/sh
strings /data/data/com.android.expansiontools/files/mmkv/mmkv.default 2>/dev/null | grep -v '^.$' | head -30
""")
print(out5)

client.close()
