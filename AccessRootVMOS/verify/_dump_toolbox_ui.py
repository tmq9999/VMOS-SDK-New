"""Dump ToolBox UI để biết texts và structure."""
import sys, time, os, re
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

# Launch ToolBox
print('\n[1] Launch ToolBox...')
out = cmd('am start -n com.android.expansiontools/.home.MainActivity 2>&1', max_wait=10)
print(f'  {out.strip()[:100]}')
time.sleep(6)

# Dump UI — lấy tất cả node text + bounds
print('\n[2] Dump UI nodes (text + bounds):')
out2 = cmd(r"""#!/system/bin/sh
uiautomator dump /sdcard/w.xml >/dev/null 2>&1
grep -o 'text="[^"]*" resource-id="[^"]*"[^>]*bounds="[^"]*"' /sdcard/w.xml | head -40
""", max_wait=20)
print(out2)

print('\n[3] Tất cả text không rỗng:')
out3 = cmd(r"""#!/system/bin/sh
grep -o 'text="[^"]*"' /sdcard/w.xml | grep -v 'text=""' | sort -u
""", max_wait=15)
print(out3)

print('\n[4] Nodes có checked/selected (toggle state):')
out4 = cmd(r"""#!/system/bin/sh
grep -o '<node[^>]*checked="true"[^>]*>' /sdcard/w.xml | head -10
grep -o '<node[^>]*selected="true"[^>]*>' /sdcard/w.xml | head -10
""", max_wait=15)
print(out4)

client.close()
