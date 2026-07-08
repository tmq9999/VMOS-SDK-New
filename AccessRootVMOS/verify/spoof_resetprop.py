"""Pixel 10 Pro Spoof dùng resetprop (Magisk Kitsune đã enable).

Props theo module: Blazer_CP2A.260605.012 (Android 17, SDK 37).
resetprop ghi đè ro.* ngay lập tức, không cần reboot, không cần module.
Chạy script này mỗi lần sau khi instance boot xong.
"""

import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

from vmos_sdk import VmosClient


def load_auth(path: str) -> dict:
    creds = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if ":" in line:
                key, _, val = line.partition(":")
                creds[key.strip()] = val.strip()
    return creds


_auth_path = os.path.join(os.path.dirname(__file__), "..", "docs", "Auth_Key.txt")
AUTH = load_auth(_auth_path)
PAD = AUTH["PADCODE"]

client = VmosClient(
    access_key=AUTH["Access Key ID"],
    secret_key=AUTH["Secret Access Key"],
)

# ==============================================================
# Module props — Pixel 10 Pro "blazer" (Blazer_CP2A.260605.012)
# Cập nhật module mới: sửa các hằng dưới đây là đủ.
# ==============================================================
BRAND = "google"
DEVICE = "blazer"
MODEL = "Pixel 10 Pro"
MANUFACTURER = "Google"

BUILD_ID = "CP2A.260605.012"
INCREMENTAL = "15430684"
RELEASE = "17"                       # ro.build.version.release
SDK = "37"                           # ro.build.version.sdk
SECURITY_PATCH = "2026-06-05"
DATE_UTC = "1778884555"
BUILD_DATE = "Fri May 15 15:35:55 PDT 2026"
BUILD_HOST = "8168aecbd96d"
FLAVOR = "blazer-user"
FIRST_API_LEVEL = "36"               # ro.product.first_api_level
DEVICE_FAMILY = "FL5BZ5MT5RG5"       # ro.build.device_family
SOC_MODEL = "Tensor G5"
SOC_MANUFACTURER = "Google"
OEM_ID = "00e0"

# Fingerprint "blazer" (giữ cho ro.build.fingerprint vì resetprop không có pihooks;
# module gốc đặt ro.build.fingerprint = generic GSI và dựa vào pihooks để spoof Build.*).
FP = f"{BRAND}/{DEVICE}/{DEVICE}:{RELEASE}/{BUILD_ID}/{INCREMENTAL}:user/release-keys"
DESCRIPTION = f"{DEVICE}-user {RELEASE} {BUILD_ID} {INCREMENTAL} release-keys"

# ==============================================================
# Batch 1: Core identity + build + partitions (product/vendor/odm)
# ==============================================================
BATCH1 = f"""#!/system/bin/sh
RP=/system/bin/resetprop
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

# ==============================================================
# Batch 2: system/system_ext/bootimage/attestation + misc + verify
# ==============================================================
BATCH2 = f"""#!/system/bin/sh
RP=/system/bin/resetprop
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
echo gpu=$(getprop persist.sys.cloud.gpu.gl_renderer)
echo "=== DONE ==="
"""


def get_pad_status():
    r = client.instance.get_list_info(pad_codes=[PAD])
    pd = r.data.get("pageData", []) if isinstance(r.data, dict) else []
    return pd[0].get("padStatus") if pd else None


def poll_result(tid: int, interval: int = 2, max_polls: int = 20) -> str:
    """Poll taskId mỗi interval giây cho đến khi có kết quả."""
    for _ in range(max_polls):
        time.sleep(interval)
        tr = client.task.get_task_detail(task_ids=[tid])
        if isinstance(tr.data, list) and tr.data:
            result = tr.data[0].get("taskResult")
            error  = tr.data[0].get("errorMsg")
            status = tr.data[0].get("taskStatus")  # 1=pending, 2=done, 3=error
            if status in (2, 3) or result or error:
                return result or error or "NO OUTPUT"
    return "TIMEOUT"


print(f"🚀 Pixel 10 Pro Spoof — resetprop (Magisk Kitsune)")
print(f"� Build: {BUILD_ID} (Android {RELEASE}, SDK {SDK})")
print(f"�📱 Pad: {PAD}\n")

# Kiểm tra instance running
s = get_pad_status()
print(f"padStatus={s} (10=running)")
if s != 10:
    print("❌ Instance chưa chạy — hãy chờ instance boot xong trước.")
    client.close()
    sys.exit(1)

# Batch 1
print("[1/2] Sending batch1 (core identity + build + partitions)...")
r1 = client.instance.async_cmd(pad_codes=[PAD], script_content=BATCH1)
tid1 = r1.data[0]["taskId"]
print(f"  taskId={tid1} — polling...")
out1 = poll_result(tid1)
print(f"  {out1.strip()}")

# Batch 2
print("[2/2] Sending batch2 (system/attestation/misc + verify)...")
r2 = client.instance.async_cmd(pad_codes=[PAD], script_content=BATCH2)
tid2 = r2.data[0]["taskId"]
print(f"  taskId={tid2} — polling...")
out2 = poll_result(tid2)
print(out2)

client.close()
