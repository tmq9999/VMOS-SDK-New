"""So sánh môi trường: CÓ Kitsune Magisk vs KHÔNG có."""
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
print('=' * 55)

print('\n[1] Magisk / resetprop status:')
out1 = cmd(r"""#!/system/bin/sh
test -f /system/bin/resetprop && echo HAS_system_resetprop || echo NO_system_resetprop
test -f /data/local/tmp/resetprop && echo HAS_inject_resetprop || echo NO_inject_resetprop
ls /data/adb/magisk/ 2>/dev/null | head -5 || echo NO_magisk_dir
which magisk 2>/dev/null || echo no_magisk_bin
pm list packages io.github.huskydg.magisk 2>/dev/null || echo no_kitsune_pkg
ps -A 2>/dev/null | grep magiskd | head -3
""")
print(out1)

print('\n[2] Props + attestation:')
out2 = cmd(r"""#!/system/bin/sh
getprop ro.product.model
getprop ro.build.fingerprint
getprop ro.product.brand_for_attestation
getprop ro.product.model_for_attestation
getprop ro.build.version.security_patch
settings get secure android_id
""")
print(out2)

print('\n[3] Modules + zygisk:')
out3 = cmd(r"""#!/system/bin/sh
ls /data/adb/modules/ 2>/dev/null || echo no_modules
getprop persist.sys.zygisk.enable 2>/dev/null || echo no_zygisk_prop
""")
print(out3)

client.close()
