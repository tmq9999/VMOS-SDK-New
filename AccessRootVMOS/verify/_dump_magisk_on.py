"""Dump môi trường KHI Kitsune Magisk đang BẬT để hiểu sự khác biệt."""
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
print('=' * 55)

print('\n[1] Magisk binary + daemon:')
print(cmd(r"""#!/system/bin/sh
which magisk 2>/dev/null || echo no_magisk_bin
magisk --version 2>/dev/null || echo no_version
test -f /system/bin/resetprop && echo HAS_system_resetprop || echo NO_system_resetprop
test -f /data/local/tmp/resetprop && echo HAS_inject_resetprop || echo NO_inject_resetprop
ps -A 2>/dev/null | grep -E 'magisk' | head -5
"""))

print('\n[2] Magisk files + modules:')
print(cmd(r"""#!/system/bin/sh
ls /data/adb/magisk/ 2>/dev/null || echo no_magisk_dir
echo ---
ls /data/adb/modules/ 2>/dev/null || echo no_modules
"""))

print('\n[3] Props hiện tại:')
print(cmd(r"""#!/system/bin/sh
getprop ro.product.model
getprop ro.product.device
getprop ro.build.fingerprint
getprop ro.build.version.release
"""))

print('\n[4] ToolBox Magisk switch state:')
print(cmd(r"""#!/system/bin/sh
getprop persist.vmos.magisk 2>/dev/null || echo no_vmos_magisk_prop
getprop persist.magisk.enable 2>/dev/null || echo no_magisk_enable_prop
ls /data/adb/ 2>/dev/null
"""))

print('\n[5] Init boot image / overlay:')
print(cmd(r"""#!/system/bin/sh
ls /data/adb/magisk.img 2>/dev/null || echo no_magisk.img
ls /data/adb/magisk/ 2>/dev/null | head -10
mount | grep -i magisk | head -5
"""))

client.close()
