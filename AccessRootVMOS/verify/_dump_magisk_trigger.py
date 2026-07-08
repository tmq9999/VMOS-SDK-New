"""Tìm cơ chế ToolBox dùng để bật Kitsune Magisk — để tự động hóa."""
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

def cmd(script, max_wait=20):
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

print('\n[1] ToolBox package + service:')
print(cmd(r"""#!/system/bin/sh
pm list packages com.android.expansiontools 2>/dev/null
dumpsys package com.android.expansiontools 2>/dev/null | grep -E 'versionName|enabled' | head -5
"""))

print('\n[2] expansiontools services / activities:')
print(cmd(r"""#!/system/bin/sh
dumpsys package com.android.expansiontools 2>/dev/null | grep -E 'Service|Activity|Provider' | head -20
"""))

print('\n[3] persist props liên quan Magisk:')
print(cmd(r"""#!/system/bin/sh
getprop | grep -iE 'magisk|kitsune|vmos|expansion|root' | head -20
"""))

print('\n[4] post-fs-data.d + service.d scripts:')
print(cmd(r"""#!/system/bin/sh
ls /data/adb/post-fs-data.d/ 2>/dev/null
ls /data/adb/service.d/ 2>/dev/null
cat /data/adb/post-fs-data.d/*.sh 2>/dev/null | head -20
"""))

print('\n[5] magisk_env mount point:')
print(cmd(r"""#!/system/bin/sh
ls /debug_ramdisk/magisk_env/ 2>/dev/null
ls /debug_ramdisk/ 2>/dev/null
cat /debug_ramdisk/magisk_env/.magisk/config 2>/dev/null || echo no_config
"""))

print('\n[6] ToolBox APK có method nào bật Magisk:')
print(cmd(r"""#!/system/bin/sh
find /data/app -name '*.apk' 2>/dev/null | xargs -I{} sh -c 'unzip -p "{}" classes.dex 2>/dev/null | strings | grep -i magisk | head -5' 2>/dev/null | head -20
"""))

client.close()
