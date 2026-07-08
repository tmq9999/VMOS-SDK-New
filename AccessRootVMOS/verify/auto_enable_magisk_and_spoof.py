"""Auto Enable Kitsune Magisk + Spoof Pixel 10 Pro — Fully Automated.

Flow hoàn toàn tự động, không cần ToolBox UI:
  Step 0: Verify instance running (padStatus=10)
  Step 1: switchRoot → cấp root shell
  Step 2: Kiểm tra Magisk đã bật chưa
  Step 2B: Nếu chưa → kiểm tra /debug_ramdisk/magisk_env/install.sh
  Step 2C: Nếu không có magisk_env/ → download từ GitHub Releases → setup thủ công
  Step 2D: sh install.sh → reboot → đợi online
  Step 3: Spoof Pixel 10 Pro (2 batch)
  Step 4: Verify

GitHub Releases: https://github.com/tmq9999/VMOS-SDK-New/releases/tag/v1.0.0-magisk
"""

import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "VMOS SDK"))

from vmos_sdk import VmosClient


# ── Auth ──────────────────────────────────────────────────────────────────────
def load_auth(path: str) -> dict:
    creds = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if ":" in line:
                key, _, val = line.partition(":")
                creds[key.strip()] = val.strip()
    return creds


_auth_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "Auth_Key.txt")
AUTH = load_auth(_auth_path)
PAD = AUTH["PADCODE"]

client = VmosClient(
    access_key=AUTH["Access Key ID"],
    secret_key=AUTH["Secret Access Key"],
)

# ── Pixel 10 Pro props ────────────────────────────────────────────────────────
BRAND        = "google"
DEVICE       = "blazer"
MODEL        = "Pixel 10 Pro"
MANUFACTURER = "Google"
BUILD_ID     = "CP2A.260605.012"
INCREMENTAL  = "15430684"
RELEASE      = "17"
SDK          = "37"
SECURITY_PATCH   = "2026-06-05"
DATE_UTC     = "1778884555"
BUILD_DATE   = "Fri May 15 15:35:55 PDT 2026"
BUILD_HOST   = "8168aecbd96d"
FLAVOR       = "blazer-user"
FIRST_API_LEVEL  = "36"
DEVICE_FAMILY    = "FL5BZ5MT5RG5"
SOC_MODEL        = "Tensor G5"
SOC_MANUFACTURER = "Google"
OEM_ID       = "00e0"
FP = f"{BRAND}/{DEVICE}/{DEVICE}:{RELEASE}/{BUILD_ID}/{INCREMENTAL}:user/release-keys"
DESCRIPTION  = f"{DEVICE}-user {RELEASE} {BUILD_ID} {INCREMENTAL} release-keys"

RESETPROP_SYSTEM = "/system/bin/resetprop"
INSTALL_SH       = "/debug_ramdisk/magisk_env/install.sh"
MAGISK_PROP      = "ro.sys.cloud.magisk"

REBOOT_TIMEOUT   = 180   # giây tối đa đợi reboot xong


# ── Helpers ───────────────────────────────────────────────────────────────────
def poll(tid: int, max_wait: int = 30) -> str:
    for _ in range(max_wait // 2):
        time.sleep(2)
        tr = client.task.get_task_detail(task_ids=[tid])
        if isinstance(tr.data, list) and tr.data:
            t = tr.data[0]
            if t.get("taskStatus") in (2, 3) or t.get("taskResult") or t.get("errorMsg"):
                return t.get("taskResult") or t.get("errorMsg") or ""
    return "TIMEOUT"


def cmd(script: str, max_wait: int = 20) -> str:
    r = client.instance.async_cmd(pad_codes=[PAD], script_content=script)
    if not (isinstance(r.data, list) and r.data):
        return ""
    return poll(r.data[0]["taskId"], max_wait)


def pad_status() -> int | None:
    r = client.instance.get_list_info(pad_codes=[PAD])
    pd = r.data.get("pageData", []) if isinstance(r.data, dict) else []
    return pd[0].get("padStatus") if pd else None


def wait_for_online(timeout: int = REBOOT_TIMEOUT) -> bool:
    """Đợi instance trở lại padStatus=10 sau reboot."""
    print(f"  Polling padStatus mỗi 10s (tối đa {timeout}s)...")
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(10)
        s = pad_status()
        elapsed = int(timeout - (deadline - time.time()))
        print(f"  [{elapsed}s] padStatus={s}")
        if s == 10:
            return True
    return False


# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("  Auto Enable Kitsune Magisk + Spoof Pixel 10 Pro")
print(f"  PAD: {PAD}")
print("=" * 60)

# ── Step 0: Verify instance running ──────────────────────────────────────────
s = pad_status()
print(f"\n[0] padStatus={s}")
if s != 10:
    print("❌ Instance chưa chạy (cần padStatus=10). Thoát.")
    client.close()
    sys.exit(1)
print("  ✓ Instance running")

# ── Step 1: Enable global root ────────────────────────────────────────────────
print("\n[1] switchRoot globalRoot=True...")
sr = client.instance.switch_root(pad_codes=[PAD], global_root=True, root_status=1)
print(f"  code={sr.code} msg={sr.msg}")
if sr.code != 200:
    print("❌ switchRoot thất bại.")
    client.close()
    sys.exit(1)
time.sleep(3)

# ── Step 2: Kiểm tra Magisk đã bật chưa ──────────────────────────────────────
print("\n[2] Kiểm tra Kitsune Magisk status...")
check = cmd(r"""#!/system/bin/sh
echo MAGISK_PROP=$(getprop ro.sys.cloud.magisk)
test -f /system/bin/resetprop && echo HAS_RESETPROP || echo NO_RESETPROP
ps -A 2>/dev/null | grep -c magiskd | awk '{print "MAGISKD_COUNT="$1}'
test -f /debug_ramdisk/magisk_env/install.sh && echo HAS_INSTALL_SH || echo NO_INSTALL_SH
""", max_wait=20)
print(f"  {check.strip()}")

magisk_on  = "HAS_RESETPROP" in check and "MAGISK_PROP=1" in check
has_install = "HAS_INSTALL_SH" in check

if magisk_on:
    print("  ✓ Kitsune Magisk đã bật — bỏ qua bước install")
else:
    # ── Step 2B: Chạy install.sh để bật Magisk ───────────────────────────────
    print("\n[2B] Kitsune Magisk CHƯA bật — chạy install.sh...")

    if not has_install:
        # ── Step 2C: Download magisk_env từ GitHub Releases ──────────────────
        print("\n[2C] Không có magisk_env/ → download từ GitHub Releases...")
        BASE_URL = "https://github.com/tmq9999/VMOS-SDK-New/releases/download/v1.0.0-magisk"
        FILES = [
            "adb_magisk.zip", "magisk32", "magisk64", "magiskpolicy",
            "install.sh", "uninstall.sh", "install_modules.sh",
            "uninstall_modules.sh", "installed_files.txt",
            "default_su_apps.txt", "sepolicy.rule",
        ]
        dl_out = cmd(f"""#!/system/bin/sh
mkdir -p /debug_ramdisk/magisk_env
cd /debug_ramdisk/magisk_env
for f in {' '.join(FILES)}; do
    curl -sL --max-time 60 -o "$f" "{BASE_URL}/$f" 2>/dev/null && echo "OK: $f" || echo "FAIL: $f"
done
chmod +x install.sh uninstall.sh install_modules.sh uninstall_modules.sh magisk32 magisk64 magiskpolicy
ls -lah /debug_ramdisk/magisk_env/ | head -15
""", max_wait=300)
        print(f"  {dl_out.strip()[:800]}")

        if "FAIL:" in dl_out and "OK:" not in dl_out:
            print("❌ Download thất bại — device không ra được internet?")
            client.close()
            sys.exit(1)

        # Verify install.sh có rồi
        chk2 = cmd("test -f /debug_ramdisk/magisk_env/install.sh && echo HAS_INSTALL_SH || echo NO")
        if "HAS_INSTALL_SH" not in chk2:
            print("❌ install.sh vẫn không có sau download!")
            client.close()
            sys.exit(1)
        print("  ✓ magisk_env/ setup xong từ GitHub")

    print("  Chạy install.sh (unzip + setprop ro.sys.cloud.magisk=1)...")
    install_out = cmd("sh /debug_ramdisk/magisk_env/install.sh 2>&1", max_wait=60)
    print(f"  install.sh output:\n{install_out.strip()[:600]}")

    if "error" in install_out.lower() and "✅" not in install_out:
        print("❌ install.sh có lỗi!")
        client.close()
        sys.exit(1)

    # Verify prop được set
    prop_check = cmd(f"getprop {MAGISK_PROP}", max_wait=10)
    print(f"  ro.sys.cloud.magisk={prop_check.strip()}")
    if prop_check.strip() != "1":
        print("❌ setprop ro.sys.cloud.magisk=1 thất bại!")
        client.close()
        sys.exit(1)

    print("  ✓ install.sh thành công — cần reboot để Magisk active")

    # ── Step 2C: Reboot ───────────────────────────────────────────────────────
    print("\n[2C] Reboot device...")
    cmd("reboot 2>&1 &", max_wait=10)
    print("  Đợi 15s để device bắt đầu reboot...")
    time.sleep(15)

    print("\n[2D] Đợi instance online trở lại...")
    if not wait_for_online(timeout=REBOOT_TIMEOUT):
        print(f"❌ Timeout {REBOOT_TIMEOUT}s — device không trở lại online!")
        client.close()
        sys.exit(1)
    print("  ✓ Instance online (padStatus=10)")

    # Re-enable switchRoot sau reboot
    print("\n[2E] Re-enable switchRoot sau reboot...")
    time.sleep(5)
    sr2 = client.instance.switch_root(pad_codes=[PAD], global_root=True, root_status=1)
    print(f"  code={sr2.code} msg={sr2.msg}")
    time.sleep(5)

    # Verify Magisk đã active sau reboot
    print("\n[2F] Verify Magisk active sau reboot...")
    verify = cmd(r"""#!/system/bin/sh
echo MAGISK_PROP=$(getprop ro.sys.cloud.magisk)
test -f /system/bin/resetprop && echo HAS_RESETPROP || echo NO_RESETPROP
ps -A 2>/dev/null | grep magiskd | head -2
""", max_wait=20)
    print(f"  {verify.strip()}")

    if "HAS_RESETPROP" not in verify:
        print("❌ Magisk chưa active sau reboot — /system/bin/resetprop không có!")
        print("   Có thể cần đợi thêm hoặc install.sh cần chạy lại.")
        client.close()
        sys.exit(1)
    print("  ✓ Kitsune Magisk active! /system/bin/resetprop có sẵn")

# ── Step 3: Spoof Pixel 10 Pro — Batch 1 ─────────────────────────────────────
RP = RESETPROP_SYSTEM
print(f"\n[3] Spoof Pixel 10 Pro — Batch 1 (dùng {RP})...")

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

r1 = client.instance.async_cmd(pad_codes=[PAD], script_content=BATCH1)
tid1 = r1.data[0]["taskId"]
print(f"  taskId={tid1} — polling...")
out1 = poll(tid1, max_wait=40)
print(f"  {out1.strip()}")

# ── Step 4: Spoof Batch 2 + Verify ───────────────────────────────────────────
print("\n[4] Spoof Pixel 10 Pro — Batch 2 + Verify...")

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
setprop net.tethering.noprovisioning true
settings delete global hidden_api_policy 2>/dev/null
settings delete global hidden_api_policy_pre_p_apps 2>/dev/null
settings delete global hidden_api_policy_p_apps 2>/dev/null
echo ""
echo "=== VERIFY ==="
echo model=$(getprop ro.product.model)
echo device=$(getprop ro.product.device)
echo fingerprint=$(getprop ro.build.fingerprint)
echo release=$(getprop ro.build.version.release)
echo sdk=$(getprop ro.build.version.sdk)
echo security=$(getprop ro.build.version.security_patch)
echo magisk=$(getprop ro.sys.cloud.magisk)
echo resetprop_path={RP}
echo "=== DONE ==="
"""

r2 = client.instance.async_cmd(pad_codes=[PAD], script_content=BATCH2)
tid2 = r2.data[0]["taskId"]
print(f"  taskId={tid2} — polling...")
out2 = poll(tid2, max_wait=40)
print(out2)

# ── Final summary ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
if MODEL in out2:
    print("✅ HOÀN TẤT!")
    print(f"   model={MODEL}")
    print(f"   Build: {BUILD_ID} (Android {RELEASE}, SDK {SDK})")
    print(f"   resetprop: {RP}")
    print(f"\n⚠️  Props mất sau reboot → chạy lại script này sau mỗi restart.")
    print(f"   (Magisk vẫn còn vì ro.sys.cloud.magisk=1 persistent)")
else:
    print("⚠️  Kết quả không như mong đợi — xem verify output bên trên.")
print("=" * 60)

client.close()
