import requests
import os
import pandas as pd
from datetime import datetime
import zipfile

# === 基本設定 ===
DATA_DIR = "data"
SNO_DATA_FILE = os.path.join(DATA_DIR, "sno_data.csv")

def get_today_filename():
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(DATA_DIR, f"{date_str}.xlsx")

def is_valid_excel(file_path):
    if not os.path.exists(file_path):
        return False
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            return True
    except zipfile.BadZipFile:
        return False

def fetch_youbike_data_once():
    url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
    response = requests.get(url)
    data = response.json()

    os.makedirs(DATA_DIR, exist_ok=True)

    # 建立靜態資料 CSV（只建立一次）
    if not os.path.exists(SNO_DATA_FILE):
        static_fields = ["sno", "sna", "sarea", "total", "ar", "latitude", "longitude", "snaen", "sareaen", "aren"]
        static_data = [{k: item[k] for k in static_fields} for item in data]
        df_static = pd.DataFrame(static_data)
        df_static.to_csv(SNO_DATA_FILE, index=False, encoding="utf-8-sig")
        print(f"✅ 已建立場站靜態資料檔案：{SNO_DATA_FILE}")

    # 動態欄位設定
    dynamic_fields = ["sno", "available_rent_bikes", "available_return_bikes", "act", "infoTime", "infoDate"]
    now = datetime.now()
    timestamp = now.strftime("%H:%M:%S")
    today_file = get_today_filename()

    print(f"📥 開始寫入資料至 {today_file}...")

    # 確保 ExcelWriter 開啟時檔案是合法的
    if is_valid_excel(today_file):
        writer = pd.ExcelWriter(today_file, engine='openpyxl', mode='a', if_sheet_exists='overlay')
    else:
        writer = pd.ExcelWriter(today_file, engine='openpyxl', mode='w')

    # 每個站一張工作表，附加時間資料
    for station in data:
        row = {k: station[k] for k in dynamic_fields}
        row["time"] = timestamp
        df = pd.DataFrame([row])[["time", "available_rent_bikes", "available_return_bikes", "act", "infoTime", "infoDate"]]
        sheet_name = row["sno"]

        try:
            # 嘗試讀取工作表內容
            if is_valid_excel(today_file):
                existing = pd.read_excel(today_file, sheet_name=sheet_name, engine='openpyxl')
                df = pd.concat([existing, df], ignore_index=True)
        except Exception as e:
            print(f"⚠️ 工作表 {sheet_name} 初次建立：{e}")

        # 寫入（不管是新表或加資料）
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    writer.close()
    print(f"✅ {now.strftime('%Y-%m-%d %H:%M:%S')} 資料已成功寫入 {today_file}")

if __name__ == "__main__":
    fetch_youbike_data_once()
