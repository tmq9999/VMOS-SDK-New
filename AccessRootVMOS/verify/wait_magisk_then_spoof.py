"""Chờ bạn bật Kitsune Magisk thủ công → tự động spoof Pixel 10 Pro.

Flow:
  1. Kiểm tra Magisk đã bật chưa
  2. Nếu chưa → in hướng dẫn, poll đến khi Magisk active (tối đa 10 phút)
  3. Sau khi Magisk active → spoof Pixel 10 Pro tự động
"""
import os, sys, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "VMOS SDK"))
from vmos_sdk import VmosClient

def load_auth(path):
    c = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if ":" in line:
                k, _, v = line.partition(":")
                c[k.strip()] = v.strip()
    return c

AUTH = load_auth(os.path.join(os.path.dirname(__file__), "..", "..", "docs", "Auth_Key.txt"))
PAD  = AUTH["PADCODE"]
client = VmosClient(access_key=AUTH["Access Key ID"], secret_key=AUTH["Secret Access Key"])

# ── Pixel 10 Pro props ────────────────────────────────────────────────────────
BRAND = "google"; DEVICE = "blazer"; MODEL = "Pixel 10 Pro"; MANUFACTURER = "Google"
BUILD_ID = "CP2A.260605.012"; INCREMENTAL = "15430684"; RELEASE = "17"; SDK = "37"
SECURITY_PATCH = "2026-06-05"; DATE_UTC = "1778884555"
BUILD_DATE = "Fri May 15 15:35:55 PDT 2026"; BUILD_HOST = "8168aecbd96d"
FLAVOR = "blazer-user"; FIRST_API_LEVEL = "36"; DEVICE_FAMILY = "FL5BZ5MT5RG5"
SOC_MODEL = "Tensor G5"; SOC_MANUFACTURER = "Google"; OEM_ID = "00e0"
FP = f"{BRAND}/{DEVICE}/{DEVICE}:{RELEASE}/{BUILD_ID}/{INCREMENTAL}:user/release-keys"
DESCRIPTION = f"{DEVICE}-user {RELEASE} {BUILD_ID} {INCREMENTAL} release-keys"
RP = "/system/bin/resetprop"

# ── Helpers ───────────────────────────────────────────────────────────────────
def poll(tid, max_wait=30):
    for _ in range(max_wait // 2):
        time.sleep(2)
        tr = client.task.get_task_detail(task_ids=[tid])
        if isinstance(tr.data, list) and tr.data:
            t = tr.data[0]
            if t.get("taskStatus") in (2, 3) or t.get("taskResult") or t.get("errorMsg"):
                return t.get("taskResult") or t.get("errorMsg") or ""
    return "TIMEOUT"

def cmd(script, max_wait=20):
    r = client.instance.async_cmd(pad_codes=[PAD], script_content=script)
    if not (isinstance(r.data, list) and r.data):
        return ""
    return poll(r.data[0]["taskId"], max_wait)

def pad_status():
    r = client.instance.get_list_info(pad_codes=[PAD])
    pd = r.data.get("pageData", []) if isinstance(r.data, dict) else []
    return pd[0].get("padStatus") if pd else None

def is_magisk_active():
    try:
        out = cmd("test -f /system/bin/resetprop && echo YES || echo NO", max_wait=15)
        return "YES" in out
    except Exception:
        return False

# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("  Wait Magisk → Auto Spoof Pixel 10 Pro")
print(f"  PAD: {PAD}")
print("=" * 60)

# Step 0: instance running?
s = pad_status()
print(f"\n[0] padStatus={s}")
if s != 10:
    print("❌ Instance chưa chạy."); client.close(); sys.exit(1)

# Step 1: switchRoot
print("\n[1] switchRoot...")
sr = client.instance.switch_root(pad_codes=[PAD], global_root=True, root_status=1)
print(f"  code={sr.code}"); time.sleep(3)

# Step 2: Kiểm tra Magisk
print("\n[2] Kiểm tra Magisk...")
if is_magisk_active():
    print("  ✓ Magisk đã active — tiến hành spoof luôn")
else:
    # ── Chờ user bật Kitsune Magisk ──────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  ⚠️  KITSUNE MAGISK CHƯA BẬT")
    print()
    print("  👉 Vào VMOS ToolBox → bật Kitsune Magisk")
    print("     (Đợi download xong → Confirm → Restart now)")
    print()
    print("  Script sẽ tự động tiếp tục sau khi reboot xong.")
    print("=" * 60 + "\n")

    # Poll đến khi padStatus trở lại 10 VÀ Magisk active
    TIMEOUT = 600  # 10 phút
    deadline = time.time() + TIMEOUT
    stage = "waiting_magisk"  # waiting_magisk → waiting_reboot → waiting_online

    while time.time() < deadline:
        elapsed = int(time.time() - (deadline - TIMEOUT))
        s = pad_status()

        if stage == "waiting_magisk":
            # Kiểm tra xem Magisk có bật chưa (trước reboot)
            if is_magisk_active():
                print(f"  [{elapsed}s] ✓ Magisk active!")
                break
            # Hoặc device bắt đầu reboot (padStatus != 10)
            if s != 10:
                print(f"  [{elapsed}s] Device đang reboot (padStatus={s})...")
                stage = "waiting_online"
            else:
                print(f"  [{elapsed}s] Chờ bạn bật Magisk... (padStatus={s})", end="\r")
                time.sleep(8)

        elif stage == "waiting_online":
            if s == 10:
                print(f"\n  [{elapsed}s] ✓ Device online!")
                time.sleep(8)
                # Re-enable switchRoot
                print("  Re-enable switchRoot...")
                try:
                    client.instance.switch_root(pad_codes=[PAD], global_root=True, root_status=1)
                except Exception as e:
                    print(f"  switchRoot warn: {e}")
                time.sleep(5)
                if is_magisk_active():
                    print("  ✓ Magisk active sau reboot!")
                    break
                else:
                    print("  ⚠️  Magisk chưa active — tiếp tục đợi...")
                    stage = "waiting_magisk"
            else:
                print(f"  [{elapsed}s] Đợi online... (padStatus={s})", end="\r")
                time.sleep(8)
    else:
        print(f"\n❌ Timeout {TIMEOUT}s — Magisk không active.")
        client.close(); sys.exit(1)

# ── Step 3: Spoof Batch 1 ─────────────────────────────────────────────────────
print(f"\n[3] Spoof Pixel 10 Pro — Batch 1...")
BATCH1 = f"""#!/system/bin/sh
RP={RP}
$RP ro.product.brand {BRAND}
$RP ro.product.manufacturer {MANUFACTURER}
$RP ro.product.model "{MODEL}"
$RP ro.product.device {DEVICE}
$RP ro.product.name {DEVICE}
$RP ro.product.board {DEVICE}
$RP ro.build.product {DEVICE}
$RP ro.hardware {DEVICE}
$RP ro.build.fingerprint "{FP}"
$RP ro.build.id {BUILD_ID}
$RP ro.build.display.id {BUILD_ID}
$RP ro.build.description "{DESCRIPTION}"
$RP ro.build.version.incremental {INCREMENTAL}
$RP ro.build.version.release {RELEASE}
$RP ro.build.version.release_or_codename {RELEASE}
$RP ro.build.version.sdk {SDK}
$RP ro.build.version.security_patch {SECURITY_PATCH}
$RP ro.build.version.codename REL
$RP ro.build.tags release-keys
$RP ro.build.type user
$RP ro.build.flavor {FLAVOR}
$RP ro.build.date.utc {DATE_UTC}
$RP ro.build.date "{BUILD_DATE}"
$RP ro.build.user android-build
$RP ro.build.host {BUILD_HOST}
$RP ro.build.device_family {DEVICE_FAMILY}
$RP ro.product.first_api_level {FIRST_API_LEVEL}
$RP ro.product.product.brand {BRAND}
$RP ro.product.product.device {DEVICE}
$RP ro.product.product.manufacturer {MANUFACTURER}
$RP ro.product.product.model "{MODEL}"
$RP ro.product.product.name {DEVICE}
$RP ro.product.build.fingerprint "{FP}"
$RP ro.product.build.id {BUILD_ID}
$RP ro.product.vendor.brand {BRAND}
$RP ro.product.vendor.device {DEVICE}
$RP ro.product.vendor.manufacturer {MANUFACTURER}
$RP ro.product.vendor.model "{MODEL}"
$RP ro.product.vendor.name {DEVICE}
$RP ro.vendor.build.fingerprint "{FP}"
$RP ro.vendor.build.id {BUILD_ID}
$RP ro.vendor.build.security_patch {SECURITY_PATCH}
$RP ro.vendor.build.version.incremental {INCREMENTAL}
$RP ro.product.odm.brand {BRAND}
$RP ro.product.odm.device {DEVICE}
$RP ro.product.odm.manufacturer {MANUFACTURER}
$RP ro.product.odm.model "{MODEL}"
$RP ro.product.odm.name {DEVICE}
$RP ro.odm.build.fingerprint "{FP}"
$RP ro.odm.build.id {BUILD_ID}
echo BATCH1_OK
"""
out1 = poll(client.instance.async_cmd(pad_codes=[PAD], script_content=BATCH1).data[0]["taskId"], 40)
print(f"  {out1.strip()}")

# ── Step 4: Spoof Batch 2 + Verify ───────────────────────────────────────────
print("\n[4] Spoof Batch 2 + Verify...")
BATCH2 = f"""#!/system/bin/sh
RP={RP}
$RP ro.product.system.brand {BRAND}
$RP ro.product.system.device {DEVICE}
$RP ro.product.system.manufacturer {MANUFACTURER}
$RP ro.product.system.model "{MODEL}"
$RP ro.product.system.name {DEVICE}
$RP ro.system.build.fingerprint "{FP}"
$RP ro.system.build.id {BUILD_ID}
$RP ro.product.system_ext.brand {BRAND}
$RP ro.product.system_ext.device {DEVICE}
$RP ro.product.system_ext.manufacturer {MANUFACTURER}
$RP ro.product.system_ext.model "{MODEL}"
$RP ro.product.system_ext.name {DEVICE}
$RP ro.system_ext.build.fingerprint "{FP}"
$RP ro.product.bootimage.brand {BRAND}
$RP ro.product.bootimage.device {DEVICE}
$RP ro.product.bootimage.manufacturer {MANUFACTURER}
$RP ro.product.bootimage.model "{MODEL}"
$RP ro.product.bootimage.name {DEVICE}
$RP ro.bootimage.build.fingerprint "{FP}"
$RP ro.product.brand_for_attestation {BRAND}
$RP ro.product.device_for_attestation {DEVICE}
$RP ro.product.manufacturer_for_attestation {MANUFACTURER}
$RP ro.product.model_for_attestation "{MODEL}"
$RP ro.product.name_for_attestation {DEVICE}
$RP ro.boot.hwname {DEVICE}
$RP ro.boot.hwdevice {DEVICE}
$RP ro.product.hardware.sku {DEVICE}
$RP ro.boot.product.hardware.sku {DEVICE}
$RP ro.soc.manufacturer {SOC_MANUFACTURER}
$RP ro.soc.model "{SOC_MODEL}"
$RP ro.com.google.clientidbase android-google
$RP ro.opa.eligible_device true
$RP ro.quick_start.device_id {DEVICE}
$RP ro.quick_start.oem_id {OEM_ID}
$RP ro.support_one_handed_mode true
$RP ro.hotword.detection_service_required false
$RP ro.incremental.enable true
setprop vendor.usb.product_string "{MODEL}"
setprop sys.oem_unlock_allowed 0
settings delete global hidden_api_policy 2>/dev/null
echo ""
echo "=== VERIFY ==="
echo model=$(getprop ro.product.model)
echo device=$(getprop ro.product.device)
echo fingerprint=$(getprop ro.build.fingerprint)
echo release=$(getprop ro.build.version.release)
echo sdk=$(getprop ro.build.version.sdk)
echo security=$(getprop ro.build.version.security_patch)
echo magisk=$(getprop ro.sys.cloud.magisk)
echo "=== DONE ==="
"""
out2 = poll(client.instance.async_cmd(pad_codes=[PAD], script_content=BATCH2).data[0]["taskId"], 40)
print(out2)

print("\n" + "=" * 60)
if MODEL in out2:
    print(f"✅ SPOOF THÀNH CÔNG!")
    print(f"   model={MODEL} | Android {RELEASE} | SDK {SDK}")
    print(f"\n⚠️  Props mất sau reboot → chạy lại script này sau mỗi restart.")
else:
    print("⚠️  Kết quả không như mong đợi.")
print("=" * 60)

client.close()
