import os
import zipfile
from datetime import datetime, timedelta

DATA_DIR = "data"
BACKUP_DIR = "backup"
os.makedirs(BACKUP_DIR, exist_ok=True)

# 保留這幾天內的資料（含今天）
days_to_keep = 7
today = datetime.today()
cutoff_date = today - timedelta(days=days_to_keep)

# 建立 ZIP 備份名稱
zip_name = os.path.join(BACKUP_DIR, f"{today.strftime('%Y-%m-%d')}.zip")
zipf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)

print(f"建立備份：{zip_name}")

for filename in os.listdir(DATA_DIR):
    full_path = os.path.join(DATA_DIR, filename)

    if filename == "sno_data.csv":
        continue

    if filename.endswith(".xlsx"):
        try:
            file_date = datetime.strptime(filename.replace(".xlsx", ""), "%Y-%m-%d")
            if file_date < cutoff_date:
                print(f"刪除過期檔案：{filename}")
                os.remove(full_path)
            else:
                print(f"保留：{filename}")
        except ValueError:
            continue

        # 全部非今天的資料都進 zip
        if file_date.date() != today.date():
            zipf.write(full_path, arcname=filename)

zipf.close()
print("備份完成")
