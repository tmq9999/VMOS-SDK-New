"""Probe môi trường thực tế trên VMOS real device sau switchRoot.

Mục tiêu:
  1. Bật globalRoot qua switchRoot API.
  2. Kiểm tra uid, SELinux, resetprop, magisk binary.
  3. Kiểm tra /data/local/tmp có execute-permission không.
  4. In kết quả rõ để quyết định hướng inject tiếp theo.
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


def poll(tid: int, wait: int = 20) -> str:
    time.sleep(wait)
    tr = client.task.get_task_detail(task_ids=[tid])
    if isinstance(tr.data, list) and tr.data:
        t = tr.data[0]
        return t.get("taskResult") or t.get("errorMsg") or "NO OUTPUT"
    return "NO DATA"


def cmd(script: str, label: str = "", wait: int = 15) -> str:
    if label:
        print(f"\n[CMD] {label}")
    r = client.instance.async_cmd(pad_codes=[PAD], script_content=script)
    if not (isinstance(r.data, list) and r.data):
        print(f"  asyncCmd failed: {r}")
        return ""
    tid = r.data[0]["taskId"]
    out = poll(tid, wait)
    print(out.strip())
    return out


# ── 1. Enable globalRoot ──────────────────────────────────────────────────────
print(f"PAD: {PAD}")
print("\n[1] Enabling switchRoot globalRoot=True ...")
sr = client.instance.switch_root(pad_codes=[PAD], global_root=True, root_status=1)
print(f"    switchRoot: code={sr.code} msg={sr.msg}")
time.sleep(5)

# ── 2. Root identity ──────────────────────────────────────────────────────────
cmd("id; whoami; echo context=$(cat /proc/self/attr/current 2>/dev/null)",
    "Root identity")

# ── 3. SELinux ────────────────────────────────────────────────────────────────
cmd("getenforce 2>/dev/null; cat /sys/fs/selinux/enforce 2>/dev/null || echo 'selinux_enforce_unreadable'",
    "SELinux status")

# ── 4. resetprop / magisk binaries ────────────────────────────────────────────
cmd("""
ls -la /system/bin/resetprop 2>/dev/null || echo 'NO /system/bin/resetprop'
which resetprop 2>/dev/null || echo 'resetprop not in PATH'
which magisk 2>/dev/null || echo 'magisk not in PATH'
ls /data/adb/ 2>/dev/null || echo 'NO /data/adb'
ls /data/adb/magisk/ 2>/dev/null || echo 'NO /data/adb/magisk'
""", "resetprop / magisk check")

# ── 5. /data/local/tmp execute test ──────────────────────────────────────────
cmd("""
ls -la /data/local/tmp/ 2>/dev/null || echo 'NO /data/local/tmp'
mount | grep -E '/data ' | head -3
# Check noexec flag
mount | grep 'noexec' | grep '/data' | head -3 || echo 'no noexec on /data mounts shown'
""", "/data/local/tmp and mount flags")

# ── 6. Test write + execute trên /data/local/tmp ──────────────────────────────
cmd("""
echo '#!/system/bin/sh
echo EXEC_TEST_OK' > /data/local/tmp/test_exec.sh
chmod 755 /data/local/tmp/test_exec.sh
/data/local/tmp/test_exec.sh 2>&1 || echo 'EXEC_FAILED (noexec?)'
rm -f /data/local/tmp/test_exec.sh
""", "Execute test on /data/local/tmp")

# ── 7. setprop test (ro.* writable?) ─────────────────────────────────────────
cmd("""
setprop ro.test.probe hello123 2>&1
echo test_result=$(getprop ro.test.probe)
""", "setprop ro.* test (without resetprop)")

# ── 8. /system writable? ─────────────────────────────────────────────────────
cmd("""
touch /system/test_write_probe 2>&1 && echo 'system_writable=YES' && rm /system/test_write_probe || echo 'system_writable=NO'
""", "/system writable check")

# ── 9. Architecture ───────────────────────────────────────────────────────────
cmd("""
uname -m
getprop ro.product.cpu.abi
getprop ro.product.cpu.abilist
""", "Architecture")

# ── Cleanup ───────────────────────────────────────────────────────────────────
print("\n[Cleanup] Disabling globalRoot ...")
client.instance.switch_root(pad_codes=[PAD], global_root=True, root_status=0)
client.close()
print("\nProbe complete.")
