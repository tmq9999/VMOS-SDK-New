"""Đọc install.sh và uninstall.sh trong magisk_env để hiểu cơ chế bật/tắt."""
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

print('\n[install.sh]:')
print(cmd(r'cat /debug_ramdisk/magisk_env/install.sh 2>/dev/null || echo NOT_FOUND'))

print('\n[uninstall.sh]:')
print(cmd(r'cat /debug_ramdisk/magisk_env/uninstall.sh 2>/dev/null || echo NOT_FOUND'))

print('\n[installed_files.txt]:')
print(cmd(r'cat /debug_ramdisk/magisk_env/installed_files.txt 2>/dev/null | head -30'))

print('\n[adb_debug.prop]:')
print(cmd(r'cat /debug_ramdisk/adb_debug.prop 2>/dev/null || cat /debug_ramdisk/magisk_env/adb_debug.prop 2>/dev/null || echo NOT_FOUND'))

print('\n[vcloud_settings.prop]:')
print(cmd(r'cat /debug_ramdisk/vcloud_settings.prop 2>/dev/null || echo NOT_FOUND'))

print('\n[default_su_apps.txt]:')
print(cmd(r'cat /debug_ramdisk/magisk_env/default_su_apps.txt 2>/dev/null || echo NOT_FOUND'))

client.close()
