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

        write_count = 0

        for station in data:
            # 只保留指定欄位
            filtered_station = {
                "sno": station.get("sno"),
                "available_rent_bikes": station.get("available_rent_bikes"),
                "available_return_bikes": station.get("available_return_bikes"),
                "total": station.get("total"),
                "act": station.get("act"),
                "infoTime": station.get("infoTime")
            }

            sno = filtered_station["sno"]
            filename = os.path.join(folder_path, f"{sno}.json")

            record = {"time": time_str, "data": filtered_station}

            # 如果檔案已存在就檢查 infoTime 是否重複
            if os.path.exists(filename):
                with open(filename, "r+", encoding="utf-8") as f:
                    content = json.load(f)
                    last_info_time = content[-1]["data"]["infoTime"]
                    if last_info_time == filtered_station["infoTime"]:
                        continue  # infoTime 沒變，跳過這筆資料

                    content.append(record)
                    f.seek(0)
                    json.dump(content, f, ensure_ascii=False, indent=2)
                    f.truncate()
                    write_count += 1
            else:
                # 第一次寫入
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump([record], f, ensure_ascii=False, indent=2)
                    write_count += 1

        print(f"[{now}] 已寫入 {write_count} 筆站點資料")

    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    fetch_youbike_data_once()
