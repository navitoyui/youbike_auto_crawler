import requests
import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo

def fetch_youbike_data_once():
    url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"

    try:
        response = requests.get(url)
        data = response.json()

        now = datetime.now(ZoneInfo("Asia/Taipei"))
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M%S")
        time_hms = now.strftime("%H:%M:%S")

        os.makedirs("data", exist_ok=True)
        filename = os.path.join("data", f"{date_str}.json")

        # 準備這次抓到的資料 dict，以 sno 為 key
        current_data = {}
        for station in data:
            sno = station.get("sno")
            current_data[sno] = {
                "sno": sno,
                "available_rent_bikes": station.get("available_rent_bikes"),
                "available_return_bikes": station.get("available_return_bikes"),
                "total": station.get("total"),
                "act": station.get("act"),
                "infoTime": station.get("infoTime")
            }

        # 讀取舊資料（如果有）
        previous_snapshots = []
        last_station_info = {}  # key: sno -> last infoTime

        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                try:
                    previous_snapshots = json.load(f)
                    # 建立最後一次 snapshot 的站點狀態對照表
                    if previous_snapshots:
                        for station in previous_snapshots[-1]["data"]:
                            last_station_info[station["sno"]] = station["infoTime"]
                except json.JSONDecodeError:
                    previous_snapshots = []

        # 判斷哪些站點 infoTime 有變化
        changed_stations = []
        for sno, new_data in current_data.items():
            if sno not in last_station_info or new_data["infoTime"] != last_station_info[sno]:
                changed_stations.append(new_data)

        # 如果有變化就寫入新的 snapshot
        if changed_stations:
            new_snapshot = {
                "time": time_str,
                "time_str": time_hms,
                "data": changed_stations
            }
            previous_snapshots.append(new_snapshot)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(previous_snapshots, f, ensure_ascii=False, indent=2)
            print(f"[{now}] 有 {len(changed_stations)} 個站點變動，已寫入快照")
        else:
            print(f"[{now}] 所有站點 infoTime 無變化，未寫入")

    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    fetch_youbike_data_once()
