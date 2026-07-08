"""Probe cấu trúc device mới — tìm Magisk env path."""
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

print('\n[1] /debug_ramdisk/:')
print(cmd('ls /debug_ramdisk/ 2>/dev/null || echo EMPTY_OR_MISSING'))

print('\n[2] mount | grep debug:')
print(cmd('mount | grep -i debug | head -10'))

print('\n[3] /data/adb/:')
print(cmd('ls /data/adb/ 2>/dev/null || echo EMPTY'))

print('\n[4] Kitsune app installed?')
print(cmd('pm list packages io.github.huskydg.magisk 2>/dev/null || echo NOT_INSTALLED'))

print('\n[5] ro.sys.cloud.*:')
print(cmd('getprop | grep -E "cloud|magisk|expansion" | head -15'))

print('\n[6] expansiontools có chạy không?')
print(cmd('ps -A 2>/dev/null | grep expansion | head -5'))

print('\n[7] Device info:')
print(cmd(r"""#!/system/bin/sh
getprop ro.product.model
getprop ro.product.device
getprop ro.build.version.release
"""))

client.close()
