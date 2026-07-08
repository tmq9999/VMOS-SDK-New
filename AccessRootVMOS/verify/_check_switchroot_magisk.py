"""Kiểm tra: switchRoot API có bật Kitsune Magisk daemon không?

So sánh trước/sau switchRoot:
- magiskd process
- /system/bin/resetprop
- /data/adb/magisk/
- Zygisk
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

def snapshot():
    return cmd(r"""#!/system/bin/sh
test -f /system/bin/resetprop && echo HAS_system_resetprop || echo NO_system_resetprop
ls /data/adb/magisk/ 2>/dev/null | wc -l | awk '{print "magisk_files="$1}'
ps -A 2>/dev/null | grep magiskd | head -2
which magisk 2>/dev/null || echo no_magisk_bin
ls /data/adb/modules/ 2>/dev/null | head -3 || echo no_modules
""")

print(f'PAD: {PAD}')

# Snapshot TRƯỚC switchRoot
print('\n[BEFORE switchRoot]:')
before = snapshot()
print(before)

# Gọi switchRoot với rootStatus=1 (bật Magisk)
print('\n[switchRoot rootStatus=1, globalRoot=True]...')
sr = client.instance.switch_root(pad_codes=[PAD], global_root=True, root_status=1)
print(f'  code={sr.code} msg={sr.msg}')
print('  Đợi 10s...')
time.sleep(10)

# Snapshot SAU switchRoot
print('\n[AFTER switchRoot (10s)]:')
after = snapshot()
print(after)

# So sánh
print('\n=== KẾT LUẬN ===')
if 'HAS_system_resetprop' in after:
    print('✅ switchRoot bật ĐƯỢC /system/bin/resetprop → Kitsune Magisk đã kích hoạt!')
elif 'magiskd' in after.lower():
    print('✅ magiskd đang chạy → Magisk daemon active')
else:
    print('❌ switchRoot KHÔNG bật Kitsune Magisk daemon')
    print('   → Chỉ cấp root shell (uid=0), không có Magisk environment')
    print('   → Cần bật Kitsune Magisk thủ công qua ToolBox để nhận Gemini offer')

# Cleanup
client.instance.switch_root(pad_codes=[PAD], global_root=True, root_status=0)
client.close()
