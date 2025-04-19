import requests
import os
import json
from datetime import datetime

def fetch_youbike_data_once():
    url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
    
    try:
        # 抓取資料
        response = requests.get(url)
        data = response.json()

        # 當前時間
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M%S")

        # 建立日期資料夾
        folder_path = os.path.join("data", date_str)
        os.makedirs(folder_path, exist_ok=True)

        for station in data:
            sno = station["sno"]
            filename = os.path.join(folder_path, f"{sno}.json")

            record = {"time": time_str, "data": station}

            # 如果檔案已存在就 append
            if os.path.exists(filename):
                with open(filename, "r+", encoding="utf-8") as f:
                    content = json.load(f)
                    content.append(record)
                    f.seek(0)
                    json.dump(content, f, ensure_ascii=False, indent=2)
                    f.truncate()
            else:
                # 第一次寫入
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump([record], f, ensure_ascii=False, indent=2)

        print(f"[{now}] 已寫入 {len(data)} 筆站點資料")

    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    fetch_youbike_data_once()
