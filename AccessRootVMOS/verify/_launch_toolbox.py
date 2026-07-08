"""Tìm và launch ToolBox đúng cách."""
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

print('\n[1] ToolBox launcher activity:')
print(cmd('cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.LAUNCHER com.android.expansiontools 2>/dev/null'))

print('\n[2] Launch bằng monkey:')
out = cmd('monkey -p com.android.expansiontools -c android.intent.category.LAUNCHER 1 2>&1', max_wait=15)
print(f'  {out.strip()[:200]}')
time.sleep(6)

print('\n[3] Dump UI sau launch:')
out3 = cmd(r"""#!/system/bin/sh
uiautomator dump /sdcard/w.xml >/dev/null 2>&1
grep -o 'text="[^"]*"' /sdcard/w.xml | grep -v 'text=""' | sort -u
""", max_wait=20)
print(out3)

print('\n[4] Tìm "Toolbox" node và click:')
out4 = cmd(r"""#!/system/bin/sh
uiautomator dump /sdcard/w.xml >/dev/null 2>&1
grep -o '<node[^>]*text="Toolbox"[^>]*>' /sdcard/w.xml
""", max_wait=15)
print(out4)

# Parse bounds và click
m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', out4)
if m:
    cx = (int(m.group(1)) + int(m.group(3))) // 2
    cy = (int(m.group(2)) + int(m.group(4))) // 2
    print(f'  → Click Toolbox tại ({cx},{cy})')
    cmd(f'input tap {cx} {cy}', max_wait=10)
    time.sleep(4)

    print('\n[5] Dump UI trong Toolbox:')
    out5 = cmd(r"""#!/system/bin/sh
uiautomator dump /sdcard/w.xml >/dev/null 2>&1
grep -o 'text="[^"]*"' /sdcard/w.xml | grep -v 'text=""' | sort -u
""", max_wait=20)
    print(out5)

client.close()
