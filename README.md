# VMOS Cloud Python SDK

> SDK Python hoàn chỉnh cho VMOS Cloud OpenAPI — quản lý cloud phone instances, ứng dụng, proxy, và nhiều tính năng khác.

**Phiên bản:** 1.0.0 | **Python:** ≥ 3.10 | **Xác thực:** V2 Simplified Signature (SHA-256)

---

## 📋 Mục lục

- [Giới thiệu](#giới-thiệu)
- [Cài đặt](#cài-đặt)
- [Cấu hình](#cấu-hình)
- [Khởi tạo Client](#khởi-tạo-client)
- [Các Module API](#các-module-api)
  - [Instance Management](#1-instance-management)
  - [Application Management](#2-application-management)
  - [Cloud Phone Management](#3-cloud-phone-management)
  - [Cloud Space Management](#4-cloud-space-management)
  - [Task Management](#5-task-management)
  - [Proxy Management](#6-proxy-management)
  - [Email Service](#7-email-verification-service)
  - [Automation (RPA)](#8-automation-rpa)
  - [Account Matrix](#9-account-matrix)
  - [SDK Token](#10-sdk-token)
- [Callback Webhook](#callback-webhook)
- [Xác thực (Authentication)](#xác-thực-authentication)
- [Xử lý lỗi](#xử-lý-lỗi)
- [Ví dụ thực tế](#ví-dụ-thực-tế)
- [Danh sách Endpoints](#danh-sách-endpoints-đầy-đủ)
- [Dự án Tool VMOS Supporter](#dự-án-tool-vmos-supporter)

---

## Giới thiệu

**VMOS Cloud Python SDK** cung cấp interface Python cho toàn bộ VMOS Cloud OpenAPI, bao gồm:

- **~120+ endpoints** thuộc 10 module chính
- **V2 Simplified Signature** — xác thực SHA-256 đơn giản, an toàn
- **V4 HMAC-SHA256** — hỗ trợ legacy signing scheme
- **Callback/Webhook handler** — nhận kết quả async operations tự động
- **Auto-retry** với exponential backoff
- **Error handling** — custom exceptions theo mã lỗi VMOS

SDK được xây dựng từ tài liệu chính thức VMOS Cloud API, phục vụ dự án **Tool VMOS Supporter** — triển khai module spoof Google Pixel 9 Pro → Pixel 10 Pro trên VMOS Cloud instances.

---

## Cài đặt

```bash
# Cài từ source
pip install -e .

# Với callback webhook support (Flask)
pip install -e ".[callbacks]"

# Với development tools (pytest)
pip install -e ".[dev]"
```

### Yêu cầu

- Python ≥ 3.10
- `requests` ≥ 2.28.0

---

## Cấu hình

### 1. Lấy AK/SK

1. Đăng nhập [VMOS Cloud Console](https://console.vmoscloud.com)
2. Vào **Developer → API**
3. Copy **Access Key ID** (AK) và **Secret Access Key** (SK)

### 2. Cấu hình credentials

**Cách 1: Environment variables (khuyến nghị)**

```bash
export VMOS_ACCESS_KEY="your_access_key_id"
export VMOS_SECRET_KEY="your_secret_access_key"
```

**Cách 2: File `.env`**

```bash
cp .env.example .env
# Sửa file .env với AK/SK thực tế
```

**Cách 3: Truyền trực tiếp**

```python
client = VmosClient(
    access_key="your_access_key_id",
    secret_key="your_secret_access_key",
)
```

> ⚠️ **Bảo mật:** Không hardcode AK/SK vào source code. Sử dụng env vars hoặc `.env` file (đã có trong `.gitignore`).

---

## Khởi tạo Client

```python
from vmos_sdk import VmosClient

# Cách 1: Đọc từ env vars
client = VmosClient()

# Cách 2: Truyền trực tiếp
client = VmosClient(
    access_key="your_ak",
    secret_key="your_sk",
)

# Cách 3: Tùy chỉnh config
client = VmosClient(
    access_key="your_ak",
    secret_key="your_sk",
    base_url="https://api.vmoscloud.com",  # Mặc định
    timeout=30,                             # Timeout (giây)
    max_retries=3,                          # Số lần retry
    signing_version="v2",                   # "v2" (recommended) hoặc "v4"
)

# Cách 4: Context manager (tự động close)
with VmosClient(access_key="ak", secret_key="sk") as client:
    result = client.cloud_phone.list_phones()
```

---

## Các Module API

SDK chia thành 8 module, truy cập qua property của `VmosClient`:

| Module | Property | Mô tả |
|--------|----------|-------|
| Instance Management | `client.instance` | Quản lý instances: restart, reset, ADB, properties, proxy |
| Application Management | `client.app` | Cài đặt, gỡ, khởi động ứng dụng |
| Cloud Phone Management | `client.cloud_phone` | Mua, tạo, danh sách cloud phone |
| Cloud Space Management | `client.cloud_space` | Quản lý cloud storage |
| Task Management | `client.task` | Query kết quả async tasks |
| Proxy Management | `client.proxy` | Proxy tĩnh + proxy động |
| Email Service | `client.email` | Dịch vụ email xác thực |
| Automation (RPA) | `client.automation` | Flow scripts, batch tasks, scheduled tasks |
| Account Matrix | `client.account_matrix` | Account CRUD, binding, batch operations |
| SDK Token | `client.sdk_token` | Quản lý SDK token |

---

### 1. Instance Management

Module lớn nhất — quản lý toàn bộ cloud phone instances.

#### Restart / Reset

```python
# Restart instance(s)
result = client.instance.restart(pad_codes=["AC22030022693"])

# Reset instance (⚠️ XÓA TOÀN BỘ DỮ LIỆU)
result = client.instance.reset(pad_codes=["AC22030022693"])
```

#### One-Key New Device ⭐

```python
# Reset toàn bộ device với country code
result = client.instance.one_key_new_device(
    pad_codes=["AC22030022693"],
    country_code="VN",
    wipe_data=True,
)

# Auto SIM/GPS/Timezone version
result = client.instance.one_key_new_device_auto(
    pad_codes=["AC22030022693"],
    country_code="US",
)
```

#### Async ADB Command ⭐

```python
# Chạy ADB command
result = client.instance.async_cmd(
    pad_codes=["AC22030022693"],
    script_content="getprop ro.product.model",
)

# Cài APK via ADB
result = client.instance.async_cmd(
    pad_codes=["AC22030022693"],
    script_content="pm install /sdcard/app.apk",
)

# Lấy kết quả task
task_id = result.data[0]["taskId"]
detail = client.task.get_task_detail(task_id=task_id)
```

#### Instance Properties

```python
# Query properties
result = client.instance.get_properties(pad_code="AC22030022693")

# Batch query (max 200)
result = client.instance.batch_get_properties(
    pad_codes=["AC22030022693", "AC22030022694"]
)

# Cập nhật dynamic properties (có hiệu lực ngay)
result = client.instance.update_properties(
    pad_codes=["AC22030022693"],
    modem_persist={"IMEI": "123456789", "ICCID": "00998877"},
    system_persist={
        "ro.product.manufacturer": "Google",
        "ro.product.brand": "google",
    },
    setting={"language": "vi-VN", "timezone": "Asia/Ho_Chi_Minh"},
)

# Cập nhật Android modification props (cần restart)
result = client.instance.update_android_props(
    pad_code="AC22030022693",
    props={
        "ro.product.model": "Pixel 10 Pro",
        "ro.product.device": "comet",
        "ro.build.fingerprint": "google/comet/comet:16/BP1A.250605.007/12345678:user/release-keys",
    },
    restart=True,  # Tự động restart sau khi apply
)
```

#### Network & Proxy

```python
# Set proxy
result = client.instance.set_proxy(
    pad_codes=["AC22030022693"],
    ip="134.81.40.147",
    port=54212,
    account="user",
    password="pass",
    proxy_type="socks5",
    enable=True,
)

# Smart IP (tự động đổi IP + SIM + GPS + timezone)
result = client.instance.set_smart_ip(
    pad_codes=["AC22030022693"],
    host="proxy.example.com",
    port=1080,
    account="user",
    password="pass",
    proxy_type="socks5",
    mode="vpn",
)

# Cancel smart IP
result = client.instance.cancel_smart_ip(pad_codes=["AC22030022693"])

# Set WiFi
result = client.instance.set_wifi(
    pad_codes=["AC22030022693"],
    wifi_json_list=[{
        "SSID": "MyWiFi",
        "BSSID": "AA:BB:CC:DD:EE:FF",
        "MAC": "11:22:33:44:55:66",
        "IP": "192.168.1.100",
        "gateway": "192.168.1.1",
        "DNS1": "8.8.8.8",
        "DNS2": "8.8.4.4",
    }],
)
```

#### GPS, Timezone, Language

```python
# Set GPS
result = client.instance.set_gps(
    pad_codes=["AC22030022693"],
    latitude=21.0285,
    longitude=105.8542,
    altitude=15.0,
)

# Set timezone
result = client.instance.update_timezone(
    pad_codes=["AC22030022693"],
    timezone="Asia/Ho_Chi_Minh",
)

# Set language
result = client.instance.update_language(
    pad_codes=["AC22030022693"],
    language="vi",
    country="VN",
)
```

#### Screenshot & Preview

```python
# Chụp screenshot
result = client.instance.screenshot(pad_codes=["AC22030022693"])

# Lấy preview image URL
result = client.instance.get_preview_image(
    pad_codes=["AC22030022693"],
    format="jpg",
    quality=80,
)
```

#### Touch Simulation

```python
# Simulate touch
result = client.instance.simulate_touch(
    pad_codes=["AC22030022693"],
    width=1080,
    height=2400,
    point_count=1,
    positions=[{"x": 540, "y": 1200, "action": "click"}],
)

# Text input
result = client.instance.input_text(
    pad_codes=["AC22030022693"],
    text="Hello from VMOS SDK!",
)

# Simulate SMS
result = client.instance.simulate_send_sms(
    pad_codes=["AC22030022693"],
    sender_number="+84901234567",
    sms_content="Mã xác thực: 123456",
)
```

#### Các chức năng khác

```python
# Switch root
result = client.instance.switch_root(
    pad_codes=["AC22030022693"],
    global_root=True,
    root_status=True,
)

# Enable ADB
result = client.instance.enable_adb(
    pad_codes=["AC22030022693"],
    open_status=True,
)

# Get ADB connection info
result = client.instance.get_adb_info(pad_code="AC22030022693")

# Reset GAID
result = client.instance.reset_gaid(pad_codes=["AC22030022693"])

# Upload file via URL
result = client.instance.upload_file(
    pad_codes=["AC22030022693"],
    url="https://example.com/app.apk",
    auto_install=1,
)

# Inject audio
result = client.instance.inject_audio(
    pad_codes=["AC22030022693"],
    url="https://example.com/audio.mp3",
    enable=True,
)

# Query danh sách quốc gia hỗ trợ One-key new device
result = client.instance.query_countries()

# Danh sách WebView versions
result = client.instance.query_webview_versions()

# Instance group list
result = client.instance.get_list_info(page=1, rows=20)
```

---

### 2. Application Management

```python
# Cài ứng dụng via URL
result = client.app.upload_file(
    pad_codes=["AC22030022693"],
    url="https://example.com/app.apk",
    auto_install=1,
    package_name="com.example.app",
)

# Gỡ ứng dụng
result = client.app.uninstall(
    pad_code_list=["AC22030022693"],
    apk_package_list=["com.example.app"],
)

# Start / Stop / Restart app
result = client.app.start(pad_codes=["AC22030022693"], package_name="com.example.app")
result = client.app.stop(pad_codes=["AC22030022693"], package_name="com.example.app")
result = client.app.restart_app(pad_codes=["AC22030022693"], package_name="com.example.app")

# Danh sách ứng dụng đã cài
result = client.app.list_installed(pad_codes=["AC22030022693"])

# Upload file lên cloud storage
result = client.app.upload_to_cloud_storage("path/to/file.apk")

# Query user files
result = client.app.query_user_files()
```

---

### 3. Cloud Phone Management

```python
# Danh sách cloud phone
result = client.cloud_phone.list_phones()

# Thông tin chi tiết
result = client.cloud_phone.get_info(pad_code="AC22030022693")

# Danh sách SKU
result = client.cloud_phone.get_sku_list(android_version="14")

# Tạo cloud phone mới
result = client.cloud_phone.create(good_id="good123", good_num=1)

# Image versions
result = client.cloud_phone.get_image_versions(pad_code="AC22030022693")

# Presale purchase
result = client.cloud_phone.presale_purchase(good_id="good123", good_num=1)

# Timing device operations
result = client.cloud_phone.create_timing_order(good_id="good123", good_num=1)
result = client.cloud_phone.timing_power_on(pad_codes=["AC22030022693"])
result = client.cloud_phone.timing_power_off(pad_codes=["AC22030022693"])
result = client.cloud_phone.timing_destroy(pad_codes=["AC22030022693"])
```

---

### 4. Cloud Space Management

```python
# Dung lượng còn lại
result = client.cloud_space.get_remaining_storage()

# Danh sách sản phẩm storage
result = client.cloud_space.get_product_list()

# Mua mở rộng storage
result = client.cloud_space.purchase_expansion(storage_id="storage123")

# Auto-renewal
result = client.cloud_space.toggle_auto_renew(renew_storage_status=True)

# Xóa backup data
result = client.cloud_space.delete_backup_data(backup_ids=["backup123"])
```

---

### 5. Task Management

```python
# Chi tiết task theo taskId
result = client.task.get_task_detail(task_id=12345)

# Chi tiết nhiều tasks
result = client.task.get_task_detail(task_ids=[12345, 12346, 12347])

# File task detail
result = client.task.get_file_task_detail(task_id=12345)
```

---

### 6. Proxy Management

#### Static Residential Proxy

```python
# Danh sách sản phẩm
result = client.proxy.get_static_products()

# Quốc gia/thành phố hỗ trợ
result = client.proxy.get_static_regions()

# Mua proxy
result = client.proxy.purchase_static(
    proxy_good_id="pgood123", num=1, country="US"
)

# Danh sách proxy
result = client.proxy.query_static_list(current=1, size=20)

# Gia hạn
result = client.proxy.renew_static(
    proxy_good_id="pgood123", proxy_ips=["1.2.3.4"]
)
```

#### Dynamic Proxy

```python
# Danh sách sản phẩm
result = client.proxy.get_dynamic_products()

# Regions
result = client.proxy.get_dynamic_regions()

# Balance
result = client.proxy.get_dynamic_balance()

# Tạo proxy
result = client.proxy.create_dynamic(
    country_code="US", proxy_type="socks5", time=30
)

# Gán proxy cho instance
result = client.proxy.configure_for_instance(
    pad_codes=["AC22030022693"],
    set_proxy_flag=True,
    proxy_ids=["proxy123"],
)

# Xóa proxy
result = client.proxy.delete_dynamic(ids=["proxy123"])
```

---

### 7. Email Verification Service

```python
# Danh sách dịch vụ
result = client.email.get_service_list()

# Loại email & stock
result = client.email.get_types_and_stock(service_id="svc123")

# Mua email
result = client.email.create_order(
    service_id="svc123", email_type_id="type123", good_num=10
)

# Danh sách email đã mua
result = client.email.get_purchased_list(page=1, size=20)

# Lấy verification code
result = client.email.get_verification_code(order_id="order123")
```

---

### 8. Automation (RPA)

Module quản lý flow automation — scripts, tasks, và scheduled tasks.
Scripts được tạo bằng VMOS Cloud console flow editor.

```python
# Danh sách flow scripts
result = client.automation.list_scripts(page=1, size=20)

# Chi tiết script
result = client.automation.get_script(script_id=1024)

# Batch dispatch flow task (tối đa 200 instances)
# Mode A — shared params (JSON string hoặc dict, dict sẽ tự serialize)
result = client.automation.batch_dispatch(
    script_id=1024,
    pad_codes=["AC22030022693", "AC22030022694"],
    params={"keyword": "summer sale"},
)

# Mode B — per-device params
result = client.automation.batch_dispatch(
    script_id=1024,
    items=[
        {"padCode": "AC22030022693", "params": {"account": "a@x.com"}},
        {"padCode": "AC22030022694", "params": {"account": "b@x.com"}},
    ],
)

# Danh sách tasks
result = client.automation.list_tasks(page=1, size=20)

# Chi tiết task
result = client.automation.get_task(task_id=30215)

# Logs (step-level)
result = client.automation.get_task_logs(task_id=30215)

# Cancel task
result = client.automation.cancel_task(task_id=30215)

# Tạo scheduled task (recurring hoặc one-shot; cron 6 trường, có giây)
result = client.automation.create_scheduled_task(
    task_name="Daily Task",
    script_id=1024,
    pad_codes=["AC22030022693"],
    cron_expr="0 0 8 * * *",  # 8:00 AM hàng ngày
)

# Toggle on/off
result = client.automation.toggle_scheduled_task(task_id=501, enabled=False)

# Xóa scheduled task
result = client.automation.delete_scheduled_task(task_id=501)
```

---

### 9. Account Matrix

Account-centric operations: CRUD, binding, batch triggering.
Credentials write-only (AES-GCM encrypted at rest), plaintext never readable via API.

```python
# Danh sách accounts
result = client.account_matrix.list_accounts(
    page=1, size=20, platform="tiktok", status="active", device_bound=True
)

# Chi tiết account
result = client.account_matrix.get_account(account_id=22)

# Tạo account (credentials mã hóa AES-GCM at rest)
result = client.account_matrix.create_account(
    platform="tiktok",
    username="user",
    password="pass",
    handle="myaccount",
)

# Bind instance (force=True để rebind khi conflict)
result = client.account_matrix.bind_instance(
    account_id=22, pad_code="AC22030022693"
)

# Unbind instance
result = client.account_matrix.unbind_instance(account_id=22)

# Batch trigger operation (credentials inject qua fromCredential)
result = client.account_matrix.batch_trigger(
    script_id=1024,
    account_ids=[22, 17],
    shared_options=[
        {"key": "account", "fromCredential": "username"},
        {"key": "password", "fromCredential": "password"},
    ],
)

# Account data snapshots
result = client.account_matrix.get_snapshots(account_id=22)

# Account works
result = client.account_matrix.get_works(account_id=22)

# Groups
result = client.account_matrix.list_groups()
result = client.account_matrix.move_group(account_id=22, group_id=12)

# Delete account (soft-delete)
result = client.account_matrix.delete_account(account_id=22)
```

---

### 10. SDK Token

```python
# Token theo padCode
result = client.sdk_token.get_token_by_padcode(pad_code="AC22030022693")

# Session token
result = client.sdk_token.get_session_token()

# Clear token
result = client.sdk_token.clear_token(token="token_string")
```

---

## Callback Webhook

SDK hỗ trợ nhận callback từ VMOS Cloud khi async tasks hoàn thành.

### Supported Events

| Type | Event | Mô tả |
|------|-------|-------|
| 999 | Instance Status | Thay đổi trạng thái instance |
| 1000 | Restart | Restart hoàn thành |
| 1001 | Reset | Reset hoàn thành |
| 1002 | ADB Command | Kết quả ADB command |
| 1003 | App Install | Cài app hoàn thành |
| 1004 | App Uninstall | Gỡ app hoàn thành |
| 1005 | App Stop | Dừng app hoàn thành |
| 1006 | App Restart | Restart app hoàn thành |
| 1007 | App Start | Start app hoàn thành |
| 1009 | File Upload | Upload file hoàn thành |
| 1012 | Image Upgrade | Nâng cấp image hoàn thành |
| 1124 | One-Key New Device | Reset device hoàn thành |
| 4001 | Image Upload | Upload image hoàn thành |

### Sử dụng

```python
from vmos_sdk.callbacks import CallbackHandler

handler = CallbackHandler()

# Đăng ký handler cho ADB result
@handler.on_adb_result
def handle_adb(event):
    print(f"ADB result for {event.pad_code}: {event.cmd_result}")

# Đăng ký handler cho restart
@handler.on_restart
def handle_restart(event):
    print(f"Restart completed: {event.pad_code}, result: {event.task_result}")

# Đăng ký handler cho one-key new device
@handler.on_new_device
def handle_new_device(event):
    print(f"New device ready: {event.pad_code}")

# Catch-all handler
@handler.on_all
def handle_all(event):
    print(f"Event type={event.task_business_type} pad={event.pad_code}")

# Flask integration
from flask import Flask
app = Flask(__name__)
app.route("/webhook", methods=["POST"])(handler.flask_view)
```

---

## Xác thực (Authentication)

SDK hỗ trợ hai scheme xác thực:

### V2 Simplified Signature (Mặc định, Khuyến nghị)

```
signString = SK + Timestamp + Path + BodyOrQuery
X-Sign = SHA-256(signString)
```

Headers: `X-Access-Key`, `X-Timestamp`, `X-Sign`

- Đơn giản: chỉ cần SHA-256
- Không cần derived key, JSON re-ordering, hay UTC formatting
- Timestamp: 10 chữ số (unix seconds), window ±5 phút

### V4 HMAC-SHA256 (Legacy)

```python
client = VmosClient(
    access_key="ak", secret_key="sk",
    signing_version="v4",  # Sử dụng V4 legacy
)
```

### bodyOrQuery Rules

| Loại request | bodyOrQuery |
|-------------|-------------|
| GET | Raw query string (vd: `startDate=2026-05-01&endDate=2026-05-31`) |
| POST/PUT (JSON) | Raw body JSON (không re-order, không strip whitespace) |
| File upload (`/uploadFile`, `/asyncCmd`, `/syncCmd`) | Empty string (file body không được sign) |

---

## Xử lý lỗi

SDK tự động parse error codes và raise exception tương ứng:

```python
from vmos_sdk import VmosClient, VmosAuthError, VmosInstanceError, VmosRateLimitError

client = VmosClient(access_key="ak", secret_key="sk")

try:
    result = client.instance.restart(pad_codes=["INVALID"])
except VmosAuthError as e:
    print(f"Lỗi xác thực: {e.code} - {e.message}")
except VmosInstanceError as e:
    print(f"Lỗi instance: {e.code} - {e.message}")
except VmosRateLimitError as e:
    print(f"Rate limit: {e.code} - {e.message}")
```

### Bảng mã lỗi

| Code | Loại | Mô tả |
|------|------|-------|
| 200 | Success | Thành công |
| 2019 | VmosAuthError | Xác thực signature thất bại |
| 2031 | VmosAuthError | Key không hợp lệ |
| 2032 | VmosAuthError | Thiếu header xác thực |
| 2033 | VmosAuthError | Timestamp expired hoặc malformed |
| 100000 | VmosRequestError | Tham số request không hợp lệ |
| 110013 | VmosInstanceError | Instance không tồn tại |
| 110031 | VmosInstanceError | Instance chưa sẵn sàng |
| 110014 | VmosRateLimitError | Request quá thường xuyên |

---

## Ví dụ thực tế

### Spoof Pixel 9 Pro → Pixel 10 Pro

```python
from vmos_sdk import VmosClient

client = VmosClient(access_key="ak", secret_key="sk")

PIXEL_10_PROPS = {
    "ro.product.model": "Pixel 10 Pro",
    "ro.product.device": "comet",
    "ro.product.brand": "google",
    "ro.build.fingerprint": "google/comet/comet:16/BP1A.250605.007/12345678:user/release-keys",
    # ... (xem examples/pixel10_spoof.py cho đầy đủ)
}

result = client.instance.update_android_props(
    pad_code="AC22030022693",
    props=PIXEL_10_PROPS,
    restart=True,
)
```

### Batch ADB Commands

```python
# Chạy ADB trên nhiều instance
pad_codes = ["AC22030022693", "AC22030022694", "AC22030022695"]

result = client.instance.async_cmd(
    pad_codes=pad_codes,
    script_content="getprop ro.product.model && getprop ro.build.fingerprint",
)

# Polling task results
import time
for task_item in result.data:
    task_id = task_item["taskId"]
    while True:
        detail = client.task.get_task_detail(task_id=task_id)
        if detail.data and detail.data.get("taskStatus") == 3:  # COMPLETED
            print(f"Result: {detail.data.get('taskResult')}")
            break
        time.sleep(2)
```

Xem thêm trong thư mục `examples/`:
- `examples/basic_usage.py` — Sử dụng cơ bản
- `examples/pixel10_spoof.py` — Spoof Pixel 10 Pro

---

## Danh sách Endpoints đầy đủ

### Instance Management (~55 endpoints)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `instance.restart()` | POST /restart | Restart instance |
| `instance.reset()` | POST /reset | Reset instance |
| `instance.one_key_new_device()` | POST /replacePad | One-key new device |
| `instance.one_key_new_device_auto()` | POST /padReplaceNew | One-key new device (auto SIM/GPS) |
| `instance.async_cmd()` | POST /asyncCmd | Async ADB command |
| `instance.switch_root()` | POST /switchRoot | Switch root |
| `instance.get_properties()` | POST /padProperties | Query properties |
| `instance.batch_get_properties()` | POST /batchPadProperties | Batch query properties |
| `instance.update_properties()` | POST /updatePadProperties | Update dynamic properties |
| `instance.update_android_props()` | POST /updatePadAndroidProp | Update Android props |
| `instance.update_sim()` | POST /updateSIM | Update SIM |
| `instance.set_wifi()` | POST /setWifiList | Set WiFi |
| `instance.check_ip()` | POST /checkIP | Smart IP check |
| `instance.set_smart_ip()` | POST /smartIp | Set smart IP |
| `instance.cancel_smart_ip()` | POST /notSmartIp | Cancel smart IP |
| `instance.set_proxy()` | POST /setProxy | Set proxy |
| `instance.get_task_status()` | POST /getTaskStatus | Smart IP task status |
| `instance.get_detail()` | POST /padDetail | Instance detail list |
| `instance.get_installed_apps()` | POST /getListInstalledApp | Get installed apps |
| `instance.list_installed_apps()` | POST /listInstalledApp | Realtime installed apps |
| `instance.get_list_info()` | POST /infos | Instance group list |
| `instance.screenshot()` | POST /screenshot | Screenshot |
| `instance.get_preview_image()` | POST /getLongGenerateUrl | Preview image |
| `instance.simulate_touch()` | POST /simulateTouch | Touch simulation |
| `instance.simulate_click()` | POST /simulateClick | Click simulation |
| `instance.simulate_swipe()` | POST /simulateSwipe | Swipe simulation |
| `instance.simulate_long_press()` | POST /simulateLongPress | Long press |
| `instance.input_text()` | POST /inputText | Text input |
| `instance.simulate_send_sms()` | POST /simulateSendSms | Simulate SMS |
| `instance.import_call_logs()` | POST /addPhoneRecord | Import call logs |
| `instance.upload_file()` | POST /uploadFileV3 | Upload file via URL |
| `instance.batch_upload_files()` | POST /batchUploadFile | Batch upload |
| `instance.inject_audio()` | POST /injectAudioToMic | Inject audio |
| `instance.unmanned_live()` | POST /unmannedLive | Video injection |
| `instance.inject_picture()` | POST /injectPicture | Image injection |
| `instance.upload_user_image()` | POST /addUserRom | Upload user image |
| `instance.update_timezone()` | POST /updateTimeZone | Set timezone |
| `instance.update_language()` | POST /updateLanguage | Set language |
| `instance.set_gps()` | POST /gpsInjectInfo | Set GPS |
| `instance.update_contacts()` | POST /updateContacts | Update contacts |
| `instance.query_countries()` | GET /country | Supported countries |
| `instance.query_webview_versions()` | POST /webview/version/list | WebView versions |
| `instance.set_keep_alive_app()` | POST /setKeepAliveApp | App keep-alive |
| `instance.modify_real_adi_template()` | POST /replaceRealAdiTemplate | Modify ADI template |
| `instance.upgrade_image()` | POST /upgradeImage | Upgrade image |
| `instance.upgrade_real_device_image()` | POST /virtualRealSwitch | Upgrade real image |
| `instance.get_real_device_templates()` | POST /templateList | Real device templates |
| `instance.enable_adb()` | POST /openOnlineAdb | Enable/disable ADB |
| `instance.get_adb_info()` | POST /adb | ADB connection info |
| `instance.reset_gaid()` | POST /resetGAID | Reset GAID |
| `instance.stop_streaming()` | POST /dissolveRoom | Stop streaming |
| `instance.device_replacement()` | POST /replacement | Device replacement |
| `instance.transfer()` | POST /confirmTransfer | Transfer cloud phone |
| `instance.hide_accessibility()` | POST /setHideAccessibilityAppList | Hide accessibility |
| `instance.toggle_process_hide()` | POST /toggleProcessHide | Show/hide process |

### Application Management (6 endpoints)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `app.uninstall()` | POST /uninstallApp | Gỡ ứng dụng |
| `app.start()` | POST /startApp | Khởi động app |
| `app.stop()` | POST /stopApp | Dừng app |
| `app.restart_app()` | POST /restartApp | Restart app |
| `app.list_installed()` | POST /listInstalledApp | Danh sách app |
| `app.upload_file()` | POST /uploadFileV3 | Upload file |

### Cloud Phone Management (~12 endpoints)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `cloud_phone.create()` | POST /createMoneyOrder | Tạo cloud phone |
| `cloud_phone.list_phones()` | POST /userPadList | Danh sách |
| `cloud_phone.get_info()` | POST /padInfo | Thông tin |
| `cloud_phone.get_sku_list()` | GET /getCloudGoodList | SKU list |
| `cloud_phone.get_image_versions()` | POST /imageVersionList | Image versions |
| `cloud_phone.presale_purchase()` | POST /createMoneyProOrder | Presale |
| `cloud_phone.query_presale_orders()` | POST /queryProOrderList | Query presale |
| `cloud_phone.create_timing_order()` | POST /createByTimingOrder | Timing order |
| `cloud_phone.timing_power_on()` | POST /timingPadOn | Power on |
| `cloud_phone.timing_power_off()` | POST /timingPadOff | Power off |
| `cloud_phone.timing_destroy()` | POST /timingPadDel | Destroy |
| `cloud_phone.get_storage_packages()` | GET /vcTimingBackupList | Storage packages |

### Automation (RPA) (12 endpoints)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `automation.list_scripts()` | POST /automation/scripts/list | Danh sách scripts |
| `automation.get_script()` | POST /automation/scripts/get | Chi tiết script |
| `automation.batch_dispatch()` | POST /automation/tasks/batch-dispatch | Batch dispatch task |
| `automation.list_tasks()` | POST /automation/tasks/list | Danh sách tasks |
| `automation.get_task()` | POST /automation/tasks/get | Chi tiết task |
| `automation.get_task_logs()` | POST /automation/tasks/logs | Task logs |
| `automation.cancel_task()` | POST /automation/tasks/cancel | Cancel task |
| `automation.list_scheduled_tasks()` | POST /automation/scheduled-tasks/list | Scheduled tasks |
| `automation.create_scheduled_task()` | POST /automation/scheduled-tasks/create | Tạo scheduled |
| `automation.update_scheduled_task()` | POST /automation/scheduled-tasks/update | Cập nhật scheduled |
| `automation.toggle_scheduled_task()` | POST /automation/scheduled-tasks/toggle | Bật/tắt scheduled |
| `automation.delete_scheduled_task()` | POST /automation/scheduled-tasks/delete | Xóa scheduled |

### Account Matrix (13 endpoints)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `account_matrix.list_accounts()` | POST /automation/accounts/list | Danh sách accounts |
| `account_matrix.get_account()` | POST /automation/accounts/get | Chi tiết account |
| `account_matrix.get_snapshots()` | POST /automation/accounts/snapshots | Data snapshots |
| `account_matrix.get_works()` | POST /automation/accounts/works | Works list |
| `account_matrix.get_work_snapshots()` | POST /automation/accounts/work-snapshots | Work snapshots |
| `account_matrix.list_groups()` | POST /automation/accounts/groups/list | Group list |
| `account_matrix.batch_trigger()` | POST /automation/accounts/operations/batch | Batch trigger |
| `account_matrix.batch_scheduled_tasks()` | POST /automation/accounts/scheduled-tasks/batch | Batch scheduled |
| `account_matrix.create_account()` | POST /automation/accounts/create | Tạo account |
| `account_matrix.bind_instance()` | POST /automation/accounts/bind | Bind instance |
| `account_matrix.unbind_instance()` | POST /automation/accounts/unbind | Unbind instance |
| `account_matrix.delete_account()` | POST /automation/accounts/delete | Xóa account |
| `account_matrix.move_group()` | POST /automation/accounts/group | Move group |

### Proxy Management (~18 endpoints)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `proxy.get_static_products()` | GET /proxyGoodList | Sản phẩm tĩnh |
| `proxy.get_static_regions()` | GET /getProxyRegion | Regions tĩnh |
| `proxy.purchase_static()` | POST /createProxyOrder | Mua proxy tĩnh |
| `proxy.get_static_orders()` | POST /selectProxyOrderList | Orders tĩnh |
| `proxy.renew_static()` | POST /createRenewProxyOrder | Gia hạn tĩnh |
| `proxy.query_static_list()` | POST /queryProxyList | Danh sách tĩnh |
| `proxy.get_dynamic_products()` | GET /getDynamicGoodService | Sản phẩm động |
| `proxy.get_dynamic_regions()` | GET /getDynamicProxyRegion | Regions động |
| `proxy.get_dynamic_balance()` | GET /queryCurrentTrafficBalance | Balance |
| `proxy.get_supported_servers()` | GET /getDynamicProxyHost | Server regions |
| `proxy.purchase_dynamic()` | POST /buyDynamicProxy | Mua proxy động |
| `proxy.create_dynamic()` | POST /createProxy | Tạo proxy động |
| `proxy.get_dynamic_list()` | GET /getProxys | Danh sách động |
| `proxy.get_dynamic_orders()` | POST /getDynamicProxyOrders | Orders động |
| `proxy.configure_for_instance()` | POST /batchPadConfigProxy | Gán cho instance |
| `proxy.query_batch_proxy_task()` | POST /selectBatchPadProxyTask | Query batch task |
| `proxy.get_auto_renew_info()` | GET /getDynamicProxyAutomaticRenewal | Auto-renew info |
| `proxy.set_auto_renew()` | POST /setAutoRenewSwitch | Auto-renew switch |
| `proxy.delete_dynamic()` | POST /delProxyByIds | Xóa proxy |

---

## Dự án Tool VMOS Supporter

SDK này là nền tảng cho dự án **Tool VMOS Supporter** — triển khai các module cần thiết để:

1. **Spoof device identity**: Pixel 9 Pro → Pixel 10 Pro (Android 16)
2. **Quản lý instances hàng loạt**: restart, reset, one-key new device
3. **ADB automation**: Chạy ADB commands trên nhiều instances
4. **Property management**: Cập nhật system/modem/setting properties
5. **Proxy management**: Cấu hình proxy cho từng instance

Xem `examples/pixel10_spoof.py` để bắt đầu.

---

## Cấu trúc dự án

```
.
├── vmos_sdk/
│   ├── __init__.py          # Package entry point
│   ├── auth.py              # V2 + V4 authentication
│   ├── client.py            # VmosClient (main entry)
│   ├── config.py            # Configuration
│   ├── constants.py         # Enums (PadStatus, TaskStatus, ...)
│   ├── exceptions.py        # Custom exceptions
│   ├── models.py            # Response models
│   ├── utils.py             # Utility functions
│   ├── api/
│   │   ├── instance.py      # Instance Management (~55 methods)
│   │   ├── application.py   # Application Management
│   │   ├── automation.py    # Flow Automation (RPA)
│   │   ├── account_matrix.py # Account Matrix
│   │   ├── cloud_phone.py   # Cloud Phone Management
│   │   ├── cloud_space.py   # Cloud Space Management
│   │   ├── task.py          # Task Management
│   │   ├── proxy.py         # Proxy Management
│   │   ├── email.py         # Email Service
│   │   └── sdk_token.py     # SDK Token
│   └── callbacks/
│       ├── handler.py       # Webhook callback handler
│       └── models.py        # Callback event models
├── docs/                    # API documentation
├── examples/                # Ví dụ sử dụng
├── tests/                   # Unit tests
├── pyproject.toml           # Project configuration
├── .env.example             # Environment template
└── README.md                # Tài liệu (file này)
```

---

## License

MIT
