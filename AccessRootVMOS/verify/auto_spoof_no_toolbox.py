"""Auto Spoof Pixel 10 Pro — KHÔNG cần bật Kitsune Magisk thủ công qua ToolBox.

Flow tự động hoàn toàn:
  Step 1: switchRoot globalRoot=True  (cấp root shell)
  Step 2: Kiểm tra resetprop có sẵn không
          - Nếu có /system/bin/resetprop → dùng luôn (Magisk đã bật sẵn)
          - Nếu không → inject resetprop binary từ Kitsune APK (GitHub URL)
  Step 3: Spoof Pixel 10 Pro (toàn bộ props từ spoof_resetprop.py)
  Step 4: Verify output

Yêu cầu: instance đang chạy (padStatus=10), có network.
resetprop inject tồn tại đến khi reboot → chạy lại script này sau mỗi restart.
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

# ── Config ────────────────────────────────────────────────────────────────────
# URL Kitsune Magisk APK (chứa libmagisk.so = multi-call binary có resetprop)
KITSUNE_APK_URL = "https://github.com/HuskyDG/magisk-files/releases/download/29999/app-release.apk"
RESETPROP_INJECT = "/data/local/tmp/resetprop"   # path sau khi inject
RESETPROP_SYSTEM = "/system/bin/resetprop"        # path nếu Magisk đã bật


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


# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("  Auto Spoof Pixel 10 Pro — No ToolBox Required")
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
print("\n[1] Enable switchRoot globalRoot=True...")
sr = client.instance.switch_root(pad_codes=[PAD], global_root=True, root_status=1)
print(f"  code={sr.code} msg={sr.msg}")
if sr.code != 200:
    print("❌ switchRoot thất bại.")
    client.close()
    sys.exit(1)
time.sleep(5)

# ── Step 2: Xác định resetprop path ──────────────────────────────────────────
print("\n[2] Xác định resetprop path...")
check = cmd(
    f"test -f {RESETPROP_SYSTEM} && echo HAS_SYSTEM || echo NO_SYSTEM; "
    f"test -f {RESETPROP_INJECT} && echo HAS_INJECT || echo NO_INJECT; "
    f"id",
    max_wait=20,
)
print(f"  {check.strip()}")

RP = None

if "HAS_SYSTEM" in check:
    RP = RESETPROP_SYSTEM
    print(f"  ✓ Dùng {RP} (Magisk đã bật sẵn)")
elif "HAS_INJECT" in check:
    # Verify hoạt động
    v = cmd(f"{RESETPROP_INJECT} ro.product.model 2>&1", max_wait=15)
    if "error" not in v.lower() and "permission denied" not in v.lower():
        RP = RESETPROP_INJECT
        print(f"  ✓ Dùng {RP} (đã inject trước đó)")
    else:
        print(f"  ✗ {RESETPROP_INJECT} có nhưng không hoạt động: {v.strip()}")

if RP is None:
    # ── Step 2B: Inject resetprop từ Kitsune APK ─────────────────────────────
    print(f"\n[2B] Inject resetprop từ Kitsune Magisk APK...")
    print(f"  Downloading APK (~11MB) từ GitHub...")
    print(f"  URL: {KITSUNE_APK_URL}")

    dl_out = cmd(
        f"cd /data/local/tmp && "
        f"curl -sL --max-time 120 '{KITSUNE_APK_URL}' -o kitsune.apk 2>&1; "
        f"echo DLSIZE=$(wc -c < kitsune.apk 2>/dev/null)",
        max_wait=150,
    )
    print(f"  Download: {dl_out.strip()[:200]}")

    # Kiểm tra file đã download
    size_check = cmd(
        "wc -c /data/local/tmp/kitsune.apk 2>/dev/null | awk '{print $1}'",
        max_wait=15,
    )
    apk_size = int(size_check.strip()) if size_check.strip().isdigit() else 0
    print(f"  APK size trên device: {apk_size} bytes")

    if apk_size < 1_000_000:
        print("❌ APK download thất bại hoặc file quá nhỏ.")
        print(f"   APK size: {apk_size} bytes (cần > 1MB)")
        print(f"   curl output: {dl_out.strip()[:300]}")
        print(f"\n💡 GitHub có thể redirect — thử dùng uploadFileV3 với magisk_arm64 local.")
        client.instance.switch_root(pad_codes=[PAD], global_root=True, root_status=0)
        client.close()
        sys.exit(1)

    # Extract libmagisk.so → rename resetprop
    ext_out = cmd(
        f"cd /data/local/tmp && "
        f"unzip -o kitsune.apk 'lib/arm64-v8a/libmagisk.so' 2>&1; "
        f"ls lib/arm64-v8a/libmagisk.so 2>/dev/null || echo EXTRACT_FAIL; "
        f"mv lib/arm64-v8a/libmagisk.so {RESETPROP_INJECT} 2>&1; "
        f"chmod 755 {RESETPROP_INJECT}; "
        f"rm -rf /data/local/tmp/kitsune.apk /data/local/tmp/lib; "
        f"ls -la {RESETPROP_INJECT}",
        max_wait=30,
    )
    print(f"  Extract: {ext_out.strip()[:300]}")

    if "EXTRACT_FAIL" in ext_out or "No such" in ext_out:
        print("❌ Extract libmagisk.so thất bại.")
        client.instance.switch_root(pad_codes=[PAD], global_root=True, root_status=0)
        client.close()
        sys.exit(1)

    RP = RESETPROP_INJECT
    print(f"  ✓ resetprop inject tại {RP}")

    # Test nhanh
    t = cmd(f"{RP} ro.product.model 2>&1", max_wait=15)
    print(f"  Quick test: {t.strip()[:100]}")

# ── Step 3: Spoof Batch 1 ─────────────────────────────────────────────────────
print("\n[3] Spoof Pixel 10 Pro — Batch 1 (core identity + build + partitions)...")
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

# ── Step 4: Spoof Batch 2 ─────────────────────────────────────────────────────
print("\n[4] Spoof Pixel 10 Pro — Batch 2 (system/attestation/misc + verify)...")
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
echo release_or_codename=$(getprop ro.build.version.release_or_codename)
echo sdk=$(getprop ro.build.version.sdk)
echo security=$(getprop ro.build.version.security_patch)
echo first_api_level=$(getprop ro.product.first_api_level)
echo device_family=$(getprop ro.build.device_family)
echo soc=$(getprop ro.soc.model)
echo build_type=$(getprop ro.build.type)
echo build_id=$(getprop ro.build.id)
echo "=== DONE ==="
"""

r2 = client.instance.async_cmd(pad_codes=[PAD], script_content=BATCH2)
tid2 = r2.data[0]["taskId"]
print(f"  taskId={tid2} — polling...")
out2 = poll(tid2, max_wait=40)
print(out2)

# ── Final check ───────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
if f'model={MODEL}' in out2 or MODEL in out2:
    print(f"✅ SPOOF THÀNH CÔNG!")
    print(f"   model={MODEL}")
    print(f"   Build: {BUILD_ID} (Android {RELEASE}, SDK {SDK})")
    print(f"   resetprop path: {RP}")
    if RP == RESETPROP_INJECT:
        print(f"\n⚠️  Lưu ý: {RP} bị xóa sau khi reboot!")
        print(f"   → Chạy lại script này sau mỗi lần restart instance.")
else:
    print("⚠️  Kết quả không như mong đợi — xem verify output bên trên.")
print("=" * 60)

client.close()
