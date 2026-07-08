"""Launch ToolBox và poll UI đến khi load."""
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

# Launch
print('\n[1] am start ToolBox...')
out = cmd('am start -n com.android.expansiontools/com.android.tools.home.MainActivity 2>&1', max_wait=10)
print(f'  {out.strip()[:150]}')

# Poll UI mỗi 4s, tối đa 40s
print('\n[2] Polling UI...')
for i in range(10):
    time.sleep(4)
    ui = cmd(r"""#!/system/bin/sh
uiautomator dump /sdcard/w.xml 2>/dev/null
grep -o 'text="[^"]*"' /sdcard/w.xml | grep -v 'text=""'
""", max_wait=15)
    texts = [t.replace('text="', '').rstrip('"') for t in ui.splitlines() if 'text="' in t]
    print(f'  [{(i+1)*4}s] texts={texts[:10]}')
    if texts:
        break

print('\n[3] "Toolbox" item trên Home screen → click:')
node = cmd(r"""#!/system/bin/sh
uiautomator dump /sdcard/w.xml >/dev/null 2>&1
grep -o '<node[^>]*text="Toolbox"[^>]*>' /sdcard/w.xml
""", max_wait=15)
print(f'  node: {node.strip()[:200]}')

m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
if m:
    cx = (int(m.group(1)) + int(m.group(3))) // 2
    cy = (int(m.group(2)) + int(m.group(4))) // 2
    print(f'  → Click ({cx},{cy})')
    cmd(f'input tap {cx} {cy}', max_wait=10)
    time.sleep(5)

    # Dump bên trong Toolbox
    print('\n[4] UI trong Toolbox:')
    for i in range(6):
        time.sleep(3)
        ui2 = cmd(r"""#!/system/bin/sh
uiautomator dump /sdcard/w.xml >/dev/null 2>&1
grep -o 'text="[^"]*"' /sdcard/w.xml | grep -v 'text=""'
""", max_wait=15)
        texts2 = [t.replace('text="', '').rstrip('"') for t in ui2.splitlines() if 'text="' in t]
        print(f'  [{(i+1)*3}s] {texts2}')
        if len(texts2) > 2:
            break
else:
    print('  → Không tìm thấy Toolbox node trên Home')
    print('  Thử click vào icon góc phải (VMOS Toolbox side menu)...')
    # VMOS Toolbox là sidebar bên phải — click icon đầu tiên
    cmd('input tap 487 78', max_wait=10)  # tọa độ từ Flow_Gemini section 1.2
    time.sleep(4)
    ui3 = cmd(r"""#!/system/bin/sh
uiautomator dump /sdcard/w.xml >/dev/null 2>&1
grep -o 'text="[^"]*"' /sdcard/w.xml | grep -v 'text=""'
""", max_wait=15)
    texts3 = [t.replace('text="', '').rstrip('"') for t in ui3.splitlines() if 'text="' in t]
    print(f'  After tap: {texts3}')

client.close()
