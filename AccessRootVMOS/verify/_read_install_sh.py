"""Đọc install.sh đầy đủ — không bị truncate bằng cách split."""
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

# Đọc từng phần 50 dòng
print('\n[install.sh lines 1-60]:')
print(cmd(r'sed -n "1,60p" /debug_ramdisk/magisk_env/install.sh 2>/dev/null'))

print('\n[install.sh lines 61-120]:')
print(cmd(r'sed -n "61,120p" /debug_ramdisk/magisk_env/install.sh 2>/dev/null'))

print('\n[install.sh lines 121-180]:')
print(cmd(r'sed -n "121,180p" /debug_ramdisk/magisk_env/install.sh 2>/dev/null'))

print('\n[install.sh lines 181-end]:')
print(cmd(r'sed -n "181,300p" /debug_ramdisk/magisk_env/install.sh 2>/dev/null'))

client.close()
