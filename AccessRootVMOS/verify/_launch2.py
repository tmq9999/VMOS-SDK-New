"""Launch Google One + dump UI nhiều lần."""
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

PKG = 'com.google.android.apps.subscriptions.red'

# Force stop + launch với LauncherActivity
print('[1] Force-stop...')
cmd(f'am force-stop {PKG}', max_wait=10)
time.sleep(2)

print('[2] Launch...')
out = cmd(f'am start -n {PKG}/.LauncherActivity 2>&1', max_wait=15)
print(f'  {out.strip()[:200]}')

# Poll UI mỗi 5s trong 60s
print('[3] Polling UI...')
for i in range(12):
    time.sleep(5)
    ui = cmd(r"""#!/system/bin/sh
uiautomator dump /sdcard/w.xml 2>&1
wc -c /sdcard/w.xml
grep -c 'node' /sdcard/w.xml 2>/dev/null
grep -o 'text="[^"]*"' /sdcard/w.xml | grep -v 'text=""' | head -15
""", max_wait=20)
    elapsed = (i + 1) * 5
    lines = [x for x in ui.strip().split('\n') if x.strip() and 'Killed' not in x]
    print(f'  [{elapsed}s] {" | ".join(lines[:5])}')

    if any(x in ui.lower() for x in ['get started', 'trial', 'offer', 'not available', 'google one']):
        print(f'\n  -> Screen detected at {elapsed}s!')
        break

print('\nDone. Check screenshot to see current state.')
client.close()
