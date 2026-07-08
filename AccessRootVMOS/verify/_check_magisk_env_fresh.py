"""Kiểm tra magisk_env khi Magisk đang BẬT vs trạng thái fresh (chưa bật lần đầu).

Mục tiêu: xác định files nào đã có sẵn trong /debug_ramdisk/magisk_env/
và files nào ToolBox phải download về trước khi chạy install.sh.
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

print('\n[1] Toàn bộ files trong /debug_ramdisk/magisk_env/ với size:')
print(cmd(r'ls -lah /debug_ramdisk/magisk_env/ 2>/dev/null'))

print('\n[2] Size adb_magisk.zip (file quan trọng nhất):')
print(cmd(r'ls -lah /debug_ramdisk/magisk_env/adb_magisk.zip 2>/dev/null && echo EXISTS || echo MISSING'))

print('\n[3] installed_files.txt có không (chỉ xuất hiện sau install):')
print(cmd(r'ls -lah /debug_ramdisk/magisk_env/installed_files.txt 2>/dev/null && echo EXISTS || echo MISSING'))

print('\n[4] magisk.apk size:')
print(cmd(r'ls -lah /debug_ramdisk/magisk_env/magisk.apk 2>/dev/null || echo MISSING'))

print('\n[5] Kiểm tra mount source của /debug_ramdisk/magisk_env/:')
print(cmd(r'mount | grep -E "magisk_env|debug_ramdisk" | head -10'))

print('\n[6] /debug_ramdisk/ là partition hay tmpfs?')
print(cmd(r'mount | grep debug_ramdisk | head -5'))

print('\n[7] Tổng size /debug_ramdisk/:')
print(cmd(r'df -h /debug_ramdisk/ 2>/dev/null'))

print('\n[8] ro.sys.cloud.magisk và related props:')
print(cmd(r"""#!/system/bin/sh
getprop ro.sys.cloud.magisk
getprop ro.sys.cloud.magisk.code
getprop ro.sys.cloud.magisk.version
getprop ro.sys.cloud.magisk.url 2>/dev/null || echo no_url_prop
getprop ro.sys.cloud.magisk.download 2>/dev/null || echo no_download_prop
"""))

client.close()
