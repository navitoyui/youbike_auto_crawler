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

        # 建立資料夾 & 檔案路徑
        os.makedirs("data", exist_ok=True)
        filename = os.path.join("data", f"{date_str}.json")

        # 建立新的紀錄 (單筆 snapshot)
        new_snapshot = {
            "time": time_str,
            "data": []
        }

        for station in data:
            filtered_station = {
                "sno": station.get("sno"),
                "available_rent_bikes": station.get("available_rent_bikes"),
                "available_return_bikes": station.get("available_return_bikes"),
                "total": station.get("total"),
                "act": station.get("act"),
                "infoTime": station.get("infoTime")
            }
            new_snapshot["data"].append(filtered_station)

        # 判斷是否需要寫入（根據 infoTime 是否有變）
        write_snapshot = True

        if os.path.exists(filename):
            with open(filename, "r+", encoding="utf-8") as f:
                content = json.load(f)
                if content:
                    last_data = content[-1]["data"]
                    # 比對第一個站點的 infoTime（假設全部站點 infoTime 同步）
                    if last_data and last_data[0]["infoTime"] == new_snapshot["data"][0]["infoTime"]:
                        write_snapshot = False
                if write_snapshot:
                    content.append(new_snapshot)
                    f.seek(0)
                    json.dump(content, f, ensure_ascii=False, indent=2)
                    f.truncate()
        else:
            # 第一次寫入
            with open(filename, "w", encoding="utf-8") as f:
                json.dump([new_snapshot], f, ensure_ascii=False, indent=2)

        if write_snapshot:
            print(f"[{now}] 已新增一筆快照，共 {len(new_snapshot['data'])} 個站點")
        else:
            print(f"[{now}] infoTime 無變化，未寫入")

    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    fetch_youbike_data_once()
