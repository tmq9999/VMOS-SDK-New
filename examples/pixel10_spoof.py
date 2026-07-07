"""VMOS SDK - Spoof Google Pixel 9 Pro → Pixel 10 Pro.

Ví dụ triển khai module spoof device properties cho dự án Tool VMOS Supporter.
Sử dụng updatePadAndroidProp và updatePadProperties APIs.

Tham khảo: InstanceAndroidPropList.txt cho danh sách ro.* properties.
"""

from vmos_sdk import VmosClient

# Khởi tạo client
client = VmosClient(
    access_key="R3ZAcmkLn0zu2RWyJCQYn5RHHW9j03G4",
    secret_key="vYeoL2mCuwLJIQoLXkXAUREO",
)

# === Pixel 10 Pro Properties ===
# Thay thế device fingerprint từ Pixel 9 Pro sang Pixel 10 Pro
PIXEL_10_PRO_PROPS = {
    # Device model info
    "ro.product.brand": "google",
    "ro.product.model": "Pixel 10 Pro",
    "ro.product.manufacturer": "Google",
    "ro.product.device": "comet",
    "ro.product.name": "comet",
    "ro.product.board": "comet",
    "ro.build.product": "comet",
    "ro.hardware": "comet",

    # Build fingerprint (Android 16)
    "ro.build.fingerprint": "google/comet/comet:16/BP1A.250605.007/12345678:user/release-keys",
    "ro.build.description": "comet-user 16 BP1A.250605.007 12345678 release-keys",
    "ro.build.display.id": "BP1A.250605.007",
    "ro.build.id": "BP1A.250605.007",
    "ro.build.version.incremental": "12345678",
    "ro.build.tags": "release-keys",
    "ro.build.flavor": "comet-user",

    # Fingerprints across partitions
    "ro.odm.build.fingerprint": "google/comet/comet:16/BP1A.250605.007/12345678:user/release-keys",
    "ro.product.build.fingerprint": "google/comet/comet:16/BP1A.250605.007/12345678:user/release-keys",
    "ro.system.build.fingerprint": "google/comet/comet:16/BP1A.250605.007/12345678:user/release-keys",
    "ro.system_ext.build.fingerprint": "google/comet/comet:16/BP1A.250605.007/12345678:user/release-keys",
    "ro.vendor.build.fingerprint": "google/comet/comet:16/BP1A.250605.007/12345678:user/release-keys",

    # Product properties across partitions
    "ro.product.odm.device": "comet",
    "ro.product.odm.model": "Pixel 10 Pro",
    "ro.product.odm.name": "comet",
    "ro.product.product.device": "comet",
    "ro.product.product.model": "Pixel 10 Pro",
    "ro.product.product.name": "comet",
    "ro.product.system.device": "comet",
    "ro.product.system.model": "Pixel 10 Pro",
    "ro.product.system.name": "comet",
    "ro.product.system_ext.device": "comet",
    "ro.product.system_ext.model": "Pixel 10 Pro",
    "ro.product.system_ext.name": "comet",
    "ro.product.vendor.device": "comet",
    "ro.product.vendor.model": "Pixel 10 Pro",
    "ro.product.vendor.name": "comet",
}

# GPU info
PIXEL_10_PRO_GPU = {
    "persist.sys.cloud.gpu.gl_vendor": "Arm",
    "persist.sys.cloud.gpu.gl_renderer": "Mali-G720 Immortalis MC12",
    "persist.sys.cloud.gpu.gl_version": '"OpenGL ES 3.2"',
}


def spoof_to_pixel_10_pro(pad_codes: list[str], restart: bool = True):
    """Apply Pixel 10 Pro spoofing properties to instances.

    Args:
        pad_codes: List of instance padCodes to spoof.
        restart: Whether to restart after applying (required for ro.* props).
    """
    print(f"🔧 Spoofing {len(pad_codes)} instance(s) to Pixel 10 Pro...")

    for pad_code in pad_codes:
        # 1. Apply Android modification props (requires restart)
        result = client.instance.update_android_props(
            pad_code=pad_code,
            props=PIXEL_10_PRO_PROPS,
            restart=restart,
        )
        print(f"  ✅ {pad_code}: Android props updated (code={result.code})")

        # 2. Apply GPU & other persistent props (dynamic, immediate effect)
        result = client.instance.update_properties(
            pad_codes=[pad_code],
            system_persist=PIXEL_10_PRO_GPU,
        )
        print(f"  ✅ {pad_code}: GPU props updated (code={result.code})")

    print(f"✨ Spoof complete! {'Restart initiated.' if restart else 'Manual restart required.'}")


if __name__ == "__main__":
    # Thay bằng padCode thực tế
    TARGET_INSTANCES = ["AC22030022693"]

    spoof_to_pixel_10_pro(TARGET_INSTANCES, restart=True)

    client.close()
