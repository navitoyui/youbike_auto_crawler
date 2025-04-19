import requests
import os
import pandas as pd
from datetime import datetime

# 資料夾名稱
DATA_DIR = "data"
SNO_DATA_FILE = os.path.join(DATA_DIR, "sno_data.csv")

# 每天一個 Excel 檔
def get_today_filename():
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(DATA_DIR, f"{date_str}.xlsx")

def fetch_youbike_data_once():
    url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
    response = requests.get(url)
    data = response.json()

    # 確保資料夾存在
    os.makedirs(DATA_DIR, exist_ok=True)

    # 如果是第一次，就建立 sno_data.csv
    if not os.path.exists(SNO_DATA_FILE):
        static_fields = ["sno", "sna", "sarea", "total", "ar", "latitude", "longitude", "snaen", "sareaen", "aren"]
        static_data = [{k: item[k] for k in static_fields} for item in data]
        df_static = pd.DataFrame(static_data)
        df_static.to_csv(SNO_DATA_FILE, index=False, encoding="utf-8-sig")
        print(f"已建立場站靜態資料檔案：{SNO_DATA_FILE}")

    # 需要的欄位（動態欄位）
    dynamic_fields = ["sno", "available_rent_bikes", "available_return_bikes", "act", "infoTime", "infoDate"]

    now = datetime.now()
    timestamp = now.strftime("%H:%M:%S")

    # 建立 today.xlsx 檔案
    today_file = get_today_filename()

    # 嘗試讀入今天的 Excel 檔案
    if os.path.exists(today_file):
        writer = pd.ExcelWriter(today_file, engine='openpyxl', mode='a', if_sheet_exists='overlay')
    else:
        writer = pd.ExcelWriter(today_file, engine='openpyxl')

    # 為每個站點新增一筆資料（寫入對應工作表）
    for station in data:
        row = {k: station[k] for k in dynamic_fields}
        row["time"] = timestamp  # 新增欄位：紀錄時間
        df = pd.DataFrame([row])[["time", "available_rent_bikes", "available_return_bikes", "act", "infoTime", "infoDate"]]

        sheet_name = row["sno"]

        # 讀取現有工作表內容（如果有）
        try:
            existing = pd.read_excel(today_file, sheet_name=sheet_name, engine='openpyxl')
            df = pd.concat([existing, df], ignore_index=True)
        except:
            pass  # 如果沒有工作表就直接寫入

        # 寫入該工作表
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    writer.close()
    print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} 資料已寫入 {today_file}")

if __name__ == "__main__":
    fetch_youbike_data_once()
