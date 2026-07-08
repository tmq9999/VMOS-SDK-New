"""Probe để hiểu /debug_ramdisk/magisk_env/ tồn tại ở đâu trên disk
và có thể backup/restore không sau khi ToolBox download lần đầu."""
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

print('\n[1] dm-3 là block device nào?')
print(cmd(r'ls -la /dev/mapper/dm-3 2>/dev/null; dmsetup info dm-3 2>/dev/null | head -10'))

print('\n[2] /debug_ramdisk mount source thật sự:')
print(cmd(r'cat /proc/mounts | grep debug_ramdisk | head -5'))

print('\n[3] magisk_env/ có thể copy ra /data/ không?')
print(cmd(r"""#!/system/bin/sh
ls -lah /debug_ramdisk/magisk_env/ 2>/dev/null | head -5
echo "---"
df -h /debug_ramdisk/ 2>/dev/null
df -h /data/ 2>/dev/null
"""))

print('\n[4] Thử copy magisk_env toàn bộ ra /data/local/tmp/magisk_env_backup/:')
print(cmd(r"""#!/system/bin/sh
cp -r /debug_ramdisk/magisk_env/ /data/local/tmp/magisk_env_backup/ 2>&1
echo EXIT=$?
ls /data/local/tmp/magisk_env_backup/ 2>/dev/null | head -5
du -sh /data/local/tmp/magisk_env_backup/ 2>/dev/null
""", max_wait=30))

print('\n[5] /data/local/tmp là partition nào? writable?')
print(cmd(r'mount | grep " /data " | head -3; df -h /data/local/tmp/'))

client.close()
