import requests
import sqlite3
from datetime import datetime
import os

DB_PATH = "youbike_data.db"

def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS youbike_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sno TEXT,
            available_rent_bikes INTEGER,
            available_return_bikes INTEGER,
            total INTEGER,
            act TEXT,
            info_time TEXT,
            fetched_time TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_youbike_data_once():
    url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
    
    try:
        response = requests.get(url)
        data = response.json()

        now = datetime.now()
        fetched_time = now.strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        for station in data:
            c.execute('''
                INSERT INTO youbike_records (
                    sno, available_rent_bikes, available_return_bikes, total, act, info_time, fetched_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                station.get("sno"),
                station.get("available_rent_bikes"),
                station.get("available_return_bikes"),
                station.get("total"),
                station.get("act"),
                station.get("infoTime"),
                fetched_time
            ))

        conn.commit()
        conn.close()
        print(f"[{fetched_time}] 已寫入 {len(data)} 筆資料")

    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    initialize_db()
    fetch_youbike_data_once()
