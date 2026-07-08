"""Fix Google One offer: clear eligibility cache + force re-check.

Vấn đề: Google One đã cache "not available" trong PartnerOfferEligibilityCache.db
Fix: 
  1. Verify props đang đúng (Pixel 10 Pro)
  2. Force-stop Google One
  3. Xóa cache + eligibility DB
  4. Launch lại Google One
  5. Đợi load → click Get Started tại (720, 2770) trên màn hình 1440x3120
  6. Verify offer xuất hiện
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

def poll(tid, max_wait=30):
    for _ in range(max_wait // 2):
        time.sleep(2)
        tr = client.task.get_task_detail(task_ids=[tid])
        if isinstance(tr.data, list) and tr.data:
            t = tr.data[0]
            if t.get('taskStatus') in (2, 3) or t.get('taskResult') or t.get('errorMsg'):
                return t.get('taskResult') or t.get('errorMsg') or ''
    return 'TIMEOUT'

def cmd(script, max_wait=25):
    r = client.instance.async_cmd(pad_codes=[PAD], script_content=script)
    if not (isinstance(r.data, list) and r.data):
        return ''
    return poll(r.data[0]['taskId'], max_wait)

PKG = 'com.google.android.apps.subscriptions.red'

print(f'PAD: {PAD}')
print('=' * 55)

# Step 1: Verify props
print('\n[1] Verify spoof props...')
props = cmd(r"""#!/system/bin/sh
getprop ro.product.model
getprop ro.product.device
getprop ro.build.version.release
""", max_wait=15)
print(f'  {props.strip()}')
if 'Pixel 10 Pro' not in props:
    print('  ⚠️  Props chưa spoof! Cần chạy auto_spoof_no_toolbox.py trước.')
else:
    print('  ✓ Props OK')

# Step 2: Read PartnerOfferEligibilityCache nội dung
print('\n[2] Đọc PartnerOfferEligibilityCache.db...')
db_content = cmd(r"""#!/system/bin/sh
DB=/data/data/com.google.android.apps.subscriptions.red/files/accounts/1/SqliteKeyValueCache:PartnerOfferEligibilityCache.db
strings "$DB" 2>/dev/null | grep -v '^.$' | head -30
""", max_wait=20)
print(f'  Cache content:\n  {db_content.strip()[:500]}')

# Step 3: Force-stop Google One
print('\n[3] Force-stop Google One...')
out3 = cmd(f'am force-stop {PKG}; echo STOPPED', max_wait=15)
print(f'  {out3.strip()}')
time.sleep(2)

# Step 4: Xóa toàn bộ cache + eligibility DB
print('\n[4] Xóa cache + eligibility DBs...')
out4 = cmd(r"""#!/system/bin/sh
PKG=com.google.android.apps.subscriptions.red
rm -rf /data/data/$PKG/cache/*
rm -f /data/data/$PKG/files/accounts/1/SqliteKeyValueCache:PartnerOfferEligibilityCache.db
rm -f /data/data/$PKG/files/accounts/1/SqliteKeyValueCache:G1EligibilityCache.db
rm -f /data/data/$PKG/files/accounts/1/SqliteKeyValueCache:HomeLayoutDataCache.db
rm -f /data/data/$PKG/cache/accounts/1/SqliteKeyValueCache:DarkPatternsEligibilityCache.db
rm -f /data/data/$PKG/cache/accounts/1/SqliteKeyValueCache:ListCalloutsCache.db
echo CLEARED
ls /data/data/$PKG/files/accounts/1/ 2>/dev/null
""", max_wait=20)
print(f'  {out4.strip()[:300]}')

# Step 5: Launch Google One
print('\n[5] Launch Google One...')
out5 = cmd(f'am start -n {PKG}/com.google.subscriptions.red.activity.MainActivity 2>&1', max_wait=15)
print(f'  {out5.strip()[:200]}')
print('  Đợi 8s cho app load...')
time.sleep(8)

# Step 6: Dump màn hình - kiểm tra loading
print('\n[6] Kiểm tra màn hình Google One...')
out6 = cmd(r"""#!/system/bin/sh
uiautomator dump /sdcard/window_g1.xml >/dev/null 2>&1
grep -o 'text="[^"]*"' /sdcard/window_g1.xml | grep -iE 'offer|started|trial|available|storage|upgrade|not' | head -10
""", max_wait=25)
print(f'  UI texts: {out6.strip()[:400]}')

# Step 7: Click Get Started (tọa độ từ Flow_Gemini.md: 720, 2770 trên 1440x3120)
print('\n[7] Click Get Started (720, 2770)...')
out7 = cmd('input tap 720 2770', max_wait=15)
print(f'  {out7.strip()}')
time.sleep(6)

# Step 8: Dump màn hình sau click
print('\n[8] Kiểm tra màn hình sau click...')
out8 = cmd(r"""#!/system/bin/sh
uiautomator dump /sdcard/window_g1b.xml >/dev/null 2>&1
grep -o 'text="[^"]*"' /sdcard/window_g1b.xml | grep -iE 'trial|offer|started|available|get|upgrade|not|error' | head -15
""", max_wait=25)
print(f'  UI texts: {out8.strip()[:400]}')

if 'trial' in out8.lower() or 'start' in out8.lower():
    print('\n✅ Offer có thể available! Chạy extract_offer.py để lấy link.')
elif 'not available' in out8.lower():
    print('\n❌ Vẫn "not available" — account đã dùng offer hoặc eligibility server-side bị block.')
    print('   Thử: dùng account Google khác chưa từng dùng offer này.')
else:
    print(f'\n⚠️  Màn hình không rõ: {out8.strip()[:200]}')
    print('   Xem screenshot để confirm.')

print('\n' + '=' * 55)
client.close()
