"""Launch Google One đúng cách + wait for offer screen."""
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

# Tìm launcher activity đúng
print('[1] Tìm main activity...')
act = cmd(f'cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.LAUNCHER {PKG} 2>/dev/null', max_wait=15)
print(f'  {act.strip()[:200]}')

# Launch bằng monkey (luôn hoạt động)
print('\n[2] Launch Google One bằng monkey...')
out = cmd(f'monkey -p {PKG} -c android.intent.category.LAUNCHER 1 2>&1', max_wait=15)
print(f'  {out.strip()[:200]}')
time.sleep(10)

# Dump UI
print('\n[3] Dump UI sau 10s...')
ui = cmd(r"""#!/system/bin/sh
uiautomator dump /sdcard/w.xml >/dev/null 2>&1
grep -o 'text="[^"]*"' /sdcard/w.xml | grep -v 'text=""' | head -20
""", max_wait=20)
print(f'  {ui.strip()[:500]}')

# Nếu thấy offer/get started
if any(x in ui.lower() for x in ['get started', 'offer', 'trial', 'start trial']):
    print('\n✅ Offer screen hiện! Click Get Started...')
    cmd('input tap 720 2770', max_wait=10)
    time.sleep(5)
    ui2 = cmd(r"""#!/system/bin/sh
uiautomator dump /sdcard/w2.xml >/dev/null 2>&1
grep -o 'text="[^"]*"' /sdcard/w2.xml | grep -v 'text=""' | head -20
""", max_wait=20)
    print(f'  After click: {ui2.strip()[:300]}')
elif 'not available' in ui.lower():
    print('\n❌ "This offer is not available" — vấn đề server-side (account/device eligibility).')
    print('\nNguyên nhân có thể:')
    print('  1. Account đã từng nhận offer này rồi')
    print('  2. Google server chưa nhận device registration mới (cần chờ hoặc reset GMS)')
    print('  3. Cần thêm bước reset GMS Android ID')
else:
    print(f'\n⚠️  UI hiện tại:\n{ui.strip()[:400]}')
    print('\nWait thêm 15s và thử lại...')
    time.sleep(15)
    ui3 = cmd(r"""#!/system/bin/sh
uiautomator dump /sdcard/w3.xml >/dev/null 2>&1
grep -o 'text="[^"]*"' /sdcard/w3.xml | grep -v 'text=""' | head -25
""", max_wait=20)
    print(f'  UI sau 15s: {ui3.strip()[:500]}')

client.close()
