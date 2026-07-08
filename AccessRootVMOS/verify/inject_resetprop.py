"""Inject resetprop binary lên VMOS real device mà không cần ToolBox.

Flow:
  1. switchRoot globalRoot=True (cấp root shell cho asyncCmd)
  2. Phương án A: uploadFileV3 (upload magisk_arm64 từ VMOS cloud storage)
     - Upload binary lên cloud storage → lấy URL → download vào device
  3. Phương án B: wget APK từ GitHub trực tiếp → unzip lấy libmagisk.so → rename resetprop
  4. chmod 755, symlink /data/local/tmp/resetprop
  5. Verify: /data/local/tmp/resetprop ro.product.model → getprop

Sau khi script này thành công, spoof_resetprop.py sẽ dùng RP=/data/local/tmp/resetprop.
"""

import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "VMOS SDK"))

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


_auth_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "Auth_Key.txt")
AUTH = load_auth(_auth_path)
PAD = AUTH["PADCODE"]

client = VmosClient(
    access_key=AUTH["Access Key ID"],
    secret_key=AUTH["Secret Access Key"],
)

# ── URL public của Kitsune Magisk APK (dùng cho phương án B) ──────────────────
# HuskyDG Kitsune Magisk v29999 (tương thích với VMOS real device)
KITSUNE_APK_URL = "https://github.com/HuskyDG/magisk-files/releases/download/29999/app-release.apk"

# Nếu bạn đã host magisk_arm64 tại URL riêng, điền vào đây (phương án A nhanh hơn):
BINARY_URL = ""  # e.g. "https://yourhost.com/magisk_arm64"

RESETPROP_PATH = "/data/local/tmp/resetprop"
APK_CACHE_PATH = "/data/local/tmp/kitsune.apk"


def poll(tid: int, wait: int = 20) -> str:
    for _ in range(wait // 2):
        time.sleep(2)
        tr = client.task.get_task_detail(task_ids=[tid])
        if isinstance(tr.data, list) and tr.data:
            t = tr.data[0]
            if t.get("taskStatus") in (2, 3) or t.get("taskResult") or t.get("errorMsg"):
                return t.get("taskResult") or t.get("errorMsg") or "NO OUTPUT"
    return "TIMEOUT"


def cmd(script: str, label: str = "", wait: int = 20) -> str:
    if label:
        print(f"\n[CMD] {label}")
    r = client.instance.async_cmd(pad_codes=[PAD], script_content=script)
    if not (isinstance(r.data, list) and r.data):
        print(f"  asyncCmd error: {r}")
        return ""
    tid = r.data[0]["taskId"]
    out = poll(tid, wait)
    print(out.strip() if out else "(no output)")
    return out or ""


def check_pad_running() -> bool:
    r = client.instance.get_list_info(pad_codes=[PAD])
    pd = r.data.get("pageData", []) if isinstance(r.data, dict) else []
    s = pd[0].get("padStatus") if pd else None
    print(f"padStatus={s} (need 10)")
    return s == 10


def upload_binary_to_vmos_cloud(binary_path: str) -> str:
    """Upload file lên VMOS cloud storage, trả về download URL."""
    print(f"Uploading {binary_path} to VMOS cloud storage...")
    r = client.app.upload_to_cloud_storage(binary_path)
    if r.code != 200:
        raise RuntimeError(f"Upload failed: {r}")
    # Response thường chứa URL trong data
    if isinstance(r.data, dict):
        url = r.data.get("url") or r.data.get("downloadUrl") or r.data.get("fileUrl")
        if url:
            print(f"  Cloud URL: {url}")
            return url
    print(f"  Raw response data: {r.data}")
    raise RuntimeError("Could not extract URL from upload response")


# ═══════════════════════════════════════════════════════════════════════════════
print(f"🔧 inject_resetprop.py — PAD: {PAD}")
print("=" * 60)

# Step 0: Kiểm tra instance running
print("\n[0] Kiểm tra instance status...")
if not check_pad_running():
    print("❌ Instance chưa chạy. Cần padStatus=10.")
    client.close()
    sys.exit(1)
print("  ✓ Instance running")

# Step 1: Enable switchRoot
print("\n[1] Enable switchRoot globalRoot=True...")
sr = client.instance.switch_root(pad_codes=[PAD], global_root=True, root_status=1)
print(f"  switchRoot: code={sr.code} msg={sr.msg}")
time.sleep(5)

# Step 2: Kiểm tra resetprop đã có chưa
print("\n[2] Kiểm tra resetprop hiện tại...")
out = cmd(
    f"ls -la /system/bin/resetprop 2>/dev/null && echo HAS_SYSTEM_RESETPROP || echo NO_SYSTEM_RESETPROP;"
    f"ls -la {RESETPROP_PATH} 2>/dev/null && echo HAS_TMP_RESETPROP || echo NO_TMP_RESETPROP",
    wait=15,
)

if "HAS_SYSTEM_RESETPROP" in out:
    print("\n✅ /system/bin/resetprop đã có sẵn — không cần inject!")
    print("   Chạy spoof_resetprop.py trực tiếp là được.")
    client.instance.switch_root(pad_codes=[PAD], global_root=True, root_status=0)
    client.close()
    sys.exit(0)

if "HAS_TMP_RESETPROP" in out:
    print(f"\n✓ {RESETPROP_PATH} đã tồn tại — kiểm tra hoạt động...")
    test_out = cmd(
        f"{RESETPROP_PATH} ro.product.model 2>&1 && echo RP_WORKS || echo RP_BROKEN",
        wait=15,
    )
    if "RP_WORKS" in test_out or "Pixel" in test_out or "google" in test_out.lower():
        print(f"✅ {RESETPROP_PATH} đã hoạt động — không cần inject lại!")
        client.instance.switch_root(pad_codes=[PAD], global_root=True, root_status=0)
        client.close()
        sys.exit(0)

# Step 3: Inject resetprop binary
print("\n[3] Inject resetprop...")

# --- Phương án A: BINARY_URL đã được chỉ định ---
if BINARY_URL:
    print(f"  [3A] Download binary từ URL: {BINARY_URL}")
    out3 = cmd(
        f"wget -q '{BINARY_URL}' -O {RESETPROP_PATH} 2>&1"
        f" || curl -sL '{BINARY_URL}' -o {RESETPROP_PATH} 2>&1;"
        f"ls -la {RESETPROP_PATH} 2>/dev/null",
        wait=60,
    )
    if RESETPROP_PATH in out3 and "No such" not in out3:
        print("  ✓ Download thành công")
    else:
        print("  ✗ Download thất bại, thử phương án B...")
        BINARY_URL = ""

# --- Phương án B: Upload local binary lên VMOS cloud, rồi download vào device ---
if not BINARY_URL:
    local_binary = os.path.join(os.path.dirname(__file__), "magisk_arm64")
    if os.path.exists(local_binary):
        print(f"  [3B] Upload local binary ({os.path.getsize(local_binary)} bytes) lên VMOS cloud...")
        try:
            cloud_url = upload_binary_to_vmos_cloud(local_binary)
            print(f"  Downloading from cloud: {cloud_url}")
            out3b = cmd(
                f"wget -q '{cloud_url}' -O {RESETPROP_PATH} 2>&1"
                f" || curl -sL '{cloud_url}' -o {RESETPROP_PATH} 2>&1;"
                f"ls -la {RESETPROP_PATH} 2>/dev/null",
                wait=60,
            )
            print("  3B result:", out3b.strip()[:200])
        except Exception as e:
            print(f"  [3B] Upload thất bại: {e} — thử phương án C...")
            local_binary = ""
    else:
        print(f"  magisk_arm64 không tìm thấy tại {local_binary}")
        local_binary = ""

# --- Phương án C: Wget Kitsune APK từ GitHub, unzip lấy libmagisk.so ---
print(f"  [3C] Download Kitsune APK từ GitHub rồi extract binary trên device...")
print(f"  URL: {KITSUNE_APK_URL}")
out3c = cmd(
    f"cd /data/local/tmp && "
    f"wget -q '{KITSUNE_APK_URL}' -O kitsune.apk 2>&1"
    f" || curl -sL '{KITSUNE_APK_URL}' -o kitsune.apk 2>&1; "
    f"ls -la kitsune.apk 2>/dev/null; "
    f"echo DOWNLOAD_DONE",
    wait=120,  # APK ~11MB, cần thời gian
    label="Download Kitsune APK (có thể mất 1-2 phút)",
)

if "kitsune.apk" in out3c and "No such" not in out3c:
    print("  ✓ APK download thành công, extracting libmagisk.so...")
    out_extract = cmd(
        f"cd /data/local/tmp && "
        f"unzip -o kitsune.apk lib/arm64-v8a/libmagisk.so 2>&1; "
        f"ls lib/arm64-v8a/libmagisk.so 2>/dev/null; "
        f"mv lib/arm64-v8a/libmagisk.so {RESETPROP_PATH} 2>&1; "
        f"chmod 755 {RESETPROP_PATH}; "
        f"ls -la {RESETPROP_PATH}; "
        f"rm -rf kitsune.apk lib/",
        wait=30,
        label="Extract libmagisk.so → resetprop",
    )
    print("  Extract result:", out_extract.strip()[:300])
else:
    print("  ✗ APK download thất bại. Kiểm tra network access trên device.")
    print("  → Cần dùng uploadFileV3 với URL public riêng.")

# Step 4: chmod + verify
print("\n[4] Chmod 755 và verify resetprop...")
out4 = cmd(
    f"chmod 755 {RESETPROP_PATH} 2>&1; "
    f"ls -la {RESETPROP_PATH}; "
    f"file {RESETPROP_PATH} 2>/dev/null || echo '(file cmd not available)'; "
    f"{RESETPROP_PATH} --version 2>&1 || echo '(--version not supported)'",
    wait=15,
    label="chmod + file info",
)

# Step 5: Test thực sự — ghi ro.product.model
print("\n[5] Test ghi ro.product.model với inject resetprop...")
out5 = cmd(
    f"{RESETPROP_PATH} ro.product.model 'INJECT_TEST_OK' 2>&1; "
    f"getprop ro.product.model",
    wait=15,
    label="Test resetprop write",
)

if "INJECT_TEST_OK" in out5:
    print("\n" + "=" * 60)
    print("✅ THÀNH CÔNG! resetprop inject hoạt động!")
    print(f"   Path: {RESETPROP_PATH}")
    print(f"   → Chạy spoof_resetprop.py với RP={RESETPROP_PATH}")
    print("=" * 60)
else:
    print("\n⚠️  resetprop chạy nhưng kết quả không như mong đợi:")
    print(f"   Output: {out5.strip()[:300]}")
    print("   Có thể cần SELinux permissive hoặc Magisk daemon.")

# Cleanup: tắt globalRoot
print("\n[Cleanup] Tắt globalRoot...")
client.instance.switch_root(pad_codes=[PAD], global_root=True, root_status=0)
client.close()
print("Done.")
