import requests
import os
import time

BASE_URL = "https://mjjbox.com"

# 从环境变量读取
COOKIE = os.getenv("MJJBOX_COOKIE")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
CSRF_TOKEN = os.getenv("CSRF_TOKEN")  # x-csrf-token

MAX_RETRIES = 2
RETRY_DELAY = 5

def checkin_once():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": COOKIE,
        "x-csrf-token": CSRF_TOKEN,
        "x-requested-with": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    }

    # GET 请求签到
    resp = requests.get(f"{BASE_URL}/checkin.json", headers=headers, timeout=15)
    resp.raise_for_status()
    return f"签到状态: {resp.json()}"

def send_tg(text):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print("未设置 TG 推送，跳过发送")
        return
    tg_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    try:
        requests.post(tg_url, data={"chat_id": TG_CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print("TG 推送失败:", e)

def checkin_with_retry():
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            result = checkin_once()
            print(f"[成功] 第{attempt}次尝试")
            send_tg(result)
            return
        except Exception as e:
            print(f"[失败] 第{attempt}次尝试: {e}")
            if attempt <= MAX_RETRIES:
                print(f"等待 {RETRY_DELAY} 秒重试...")
                time.sleep(RETRY_DELAY)
            else:
                send_tg(f"签到失败，尝试 {MAX_RETRIES+1} 次，错误: {e}")

if __name__ == "__main__":
    checkin_with_retry()
