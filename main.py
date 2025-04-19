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

    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(SNO_DATA_FILE):
        static_fields = ["sno", "sna", "sarea", "total", "ar", "latitude", "longitude", "snaen", "sareaen", "aren"]
        static_data = [{k: item[k] for k in static_fields} for item in data]
        df_static = pd.DataFrame(static_data)
        df_static.to_csv(SNO_DATA_FILE, index=False, encoding="utf-8-sig")
        print(f"已建立場站靜態資料檔案：{SNO_DATA_FILE}")

    dynamic_fields = ["sno", "available_rent_bikes", "available_return_bikes", "act", "infoTime", "infoDate"]
    now = datetime.now()
    timestamp = now.strftime("%H:%M:%S")
    today_file = get_today_filename()

    print(f"開始寫入資料至 {today_file}...")

    from openpyxl import load_workbook
    from openpyxl.utils.exceptions import InvalidFileException

    try:
        writer = pd.ExcelWriter(today_file, engine='openpyxl', mode='a' if os.path.exists(today_file) else 'w', if_sheet_exists='overlay')
    except InvalidFileException as e:
        print(f"無法開啟 Excel 檔案：{e}")
        return

    for station in data:
        try:
            row = {k: station[k] for k in dynamic_fields}
            row["time"] = timestamp
            df = pd.DataFrame([row])[["time", "available_rent_bikes", "available_return_bikes", "act", "infoTime", "infoDate"]]
            sheet_name = row["sno"]

            try:
                existing = pd.read_excel(today_file, sheet_name=sheet_name, engine='openpyxl')
                df = pd.concat([existing, df], ignore_index=True)
            except Exception as e:
                print(f"新建工作表 {sheet_name}：{e}")

            df.to_excel(writer, sheet_name=sheet_name, index=False)
        except Exception as e:
            print(f"處理站點 {station.get('sno', '未知')} 發生錯誤：{e}")

    writer.close()

    print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} 資料已成功寫入 {today_file}")
    print("目前資料夾內容：", os.listdir(DATA_DIR))

if __name__ == "__main__":
    fetch_youbike_data_once()
