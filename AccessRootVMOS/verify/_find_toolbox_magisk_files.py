"""Tìm xem ToolBox (expansiontools) lưu Magisk files ở đâu trước khi copy vào /debug_ramdisk/."""
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

print('\n[1] ToolBox data dir:')
print(cmd(r'ls /data/data/com.android.expansiontools/ 2>/dev/null'))

print('\n[2] ToolBox files dir:')
print(cmd(r'ls /data/data/com.android.expansiontools/files/ 2>/dev/null'))

print('\n[3] Tìm adb_magisk.zip hoặc magisk64 trong toàn bộ /data/:')
print(cmd(r'find /data/data/com.android.expansiontools/ -name "*.zip" -o -name "magisk*" -o -name "install.sh" 2>/dev/null | head -20'))

print('\n[4] Tìm rộng hơn:')
print(cmd(r'find /sdcard/ /data/local/ /data/app/ -name "magisk*" -o -name "adb_magisk*" 2>/dev/null | head -10'))

print('\n[5] ToolBox shared_prefs (settings/config):')
print(cmd(r'ls /data/data/com.android.expansiontools/shared_prefs/ 2>/dev/null'))

print('\n[6] Nội dung shared_prefs quan trọng:')
print(cmd(r"""#!/system/bin/sh
for f in /data/data/com.android.expansiontools/shared_prefs/*.xml; do
    echo "--- $f ---"
    grep -iE 'magisk|install|download|url|version' "$f" 2>/dev/null | head -5
done
"""))

print('\n[7] ToolBox có APK nào bundled không:')
print(cmd(r'find /data/app -path "*expansiontools*" -name "*.apk" 2>/dev/null | head -3'))

client.close()
