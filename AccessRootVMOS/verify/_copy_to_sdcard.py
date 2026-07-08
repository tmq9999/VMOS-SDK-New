"""Copy magisk_env files ra /sdcard/Download/magisk_env/ để user lấy."""
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

AUTH   = load_auth(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'Auth_Key.txt'))
PAD    = AUTH['PADCODE']
client = VmosClient(access_key=AUTH['Access Key ID'], secret_key=AUTH['Secret Access Key'])

def cmd(script, max_wait=30):
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

print('\n[1] Copy files ra /sdcard/Download/magisk_env/...')
out = cmd(r"""#!/system/bin/sh
DST=/sdcard/Download/magisk_env
mkdir -p "$DST"
for f in adb_magisk.zip magisk32 magisk64 magiskpolicy install.sh uninstall.sh \
          install_modules.sh uninstall_modules.sh installed_files.txt \
          default_su_apps.txt sepolicy.rule; do
    cp /debug_ramdisk/magisk_env/$f "$DST/" 2>/dev/null && echo "OK: $f" || echo "FAIL: $f"
done
echo "---"
ls -lah "$DST/"
""", max_wait=30)
print(out)

client.close()
