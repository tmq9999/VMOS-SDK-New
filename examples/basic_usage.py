"""VMOS SDK - Ví dụ sử dụng cơ bản.

Demo: kết nối, query instance, restart, ADB command.
"""

from vmos_sdk import VmosClient

# Khởi tạo client với AK/SK
client = VmosClient(
    access_key="R3ZAcmkLn0zu2RWyJCQYn5RHHW9j03G4",
    secret_key="vYeoL2mCuwLJIQoLXkXAUREO",
)

# === 1. Danh sách cloud phone ===
result = client.cloud_phone.list_phones()
print("Cloud phone list:", result.data)

# === 2. Chi tiết instance ===
result = client.instance.get_detail(rows=5)
if result.data:
    for item in result.data.get("pageData", []):
        print(f"  PadCode: {item['padCode']}, Status: {item['padStatus']}")

# === 3. Query properties của instance ===
# Thay PAD_CODE bằng padCode thực tế
PAD_CODE = "AC22030022693"
result = client.instance.get_properties(PAD_CODE)
print(f"Properties of {PAD_CODE}:", result.data)

# === 4. Async ADB Command ===
result = client.instance.async_cmd(
    pad_codes=[PAD_CODE],
    script_content="getprop ro.product.model",
)
print("ADB task created:", result.data)

# === 5. Restart instance ===
result = client.instance.restart(pad_codes=[PAD_CODE])
print("Restart result:", result.data)

# === 6. Query task result ===
# Lấy taskId từ kết quả restart
if result.data:
    task_list = result.data if isinstance(result.data, list) else [result.data]
    for task in task_list:
        task_id = task.get("taskId")
        if task_id:
            detail = client.task.get_task_detail(task_id=task_id)
            print(f"Task {task_id} detail:", detail.data)

client.close()
