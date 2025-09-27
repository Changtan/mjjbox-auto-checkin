import requests
import os
import time

BASE_URL = "https://mjjbox.com"

# 从环境变量读取
COOKIE = os.getenv("MJJBOX_COOKIE")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

MAX_RETRIES = 2      # 失败重试次数
RETRY_DELAY = 5      # 秒

def checkin_once():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Cookie": COOKIE
    })

    url = f"{BASE_URL}/plugin.php?id=dsu_paulsign:sign"
    data = {
        "qdxq": "kx",                # 心情: kx=开心 ng=难过 ym=郁闷 wl=无聊
        "qdmode": "1",               # 1=每日签到
        "todaysay": "GitHub Actions 签到"
    }

    resp = session.post(url, data=data, timeout=15)
    resp.raise_for_status()
    return f"Status: {resp.status_code}\nResponse: {resp.text[:200]}"

def send_tg(text):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print("未设置 TG 推送参数，跳过发送。")
        return

    tg_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(tg_url, data={
            "chat_id": TG_CHAT_ID,
            "text": text
        }, timeout=10)
        print("TG 推送结果:", r.text)
    except Exception as e:
        print("TG 推送失败:", e)

def checkin_with_retry():
    for attempt in range(1, MAX_RETRIES + 2):  # 1次+重试次数
        try:
            result_text = checkin_once()
            print(f"[成功] 第{attempt}次尝试")
            send_tg(result_text)
            return
        except Exception as e:
            print(f"[失败] 第{attempt}次尝试: {e}")
            if attempt <= MAX_RETRIES:
                print(f"等待 {RETRY_DELAY} 秒后重试...")
                time.sleep(RETRY_DELAY)
            else:
                send_tg(f"签到失败，已尝试 {MAX_RETRIES+1} 次。\n错误: {e}")

if __name__ == "__main__":
    checkin_with_retry()
