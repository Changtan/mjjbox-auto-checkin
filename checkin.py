import requests
import os
import time

BASE_URL = "https://mjjbox.com"

COOKIE = os.getenv("MJJBOX_COOKIE")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
CSRF_TOKEN = os.getenv("CSRF_TOKEN")

MAX_RETRIES = 2
RETRY_DELAY = 5

def format_checkin_status(data):
    """把签到 JSON 格式化成可读文本"""
    user_checkin_count = data.get('user_checkin_count', 0)
    consecutive_days = data.get('consecutive_days', 0)
    today_checked_in = data.get('today_checked_in', False)
    current_points = data.get('current_points', 0)

    # 本次签到的积分
    checkin_history = data.get('checkin_history', [])
    today_points = 0
    if checkin_history:
        today_points = checkin_history[0].get('points_earned', 0)

    status = "✅ 已签到" if today_checked_in else "❌ 未签到"

    text = (
        f"{status}\n"
        f"连续签到天数: {consecutive_days}\n"
        f"本次获得积分: {today_points}\n"
        f"总积分: {current_points}\n"
        f"累计签到次数: {user_checkin_count}"
    )
    return text

def checkin_once():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": COOKIE,
        "x-csrf-token": CSRF_TOKEN,
        "x-requested-with": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    }

    resp = requests.get(f"{BASE_URL}/checkin.json", headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return format_checkin_status(data)

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
