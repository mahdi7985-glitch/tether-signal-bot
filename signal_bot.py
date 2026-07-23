import requests
from datetime import datetime

# ==================== تنظیمات ====================
# توکن و آیدی ربات بله (از فایل env یا مستقیم)
BALE_TOKEN = "124178101:7dLO9-5SsUmHmNkTk7azkyyh62s8P-DVrd4"
BALE_CHAT_ID = "1049670320"

THRESHOLD_NORMAL = 1.0
THRESHOLD_STRONG = 2.0
TOTAL_FEE = 0.38

# ==================== تابع ارسال پیام ====================

def send_alert(msg):
    url = f"https://api.bale.ai/bot{BALE_TOKEN}/sendMessage"
    data = {
        "chat_id": BALE_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=data, timeout=10)
        if r.status_code == 200:
            print("✅ پیام ارسال شد")
        else:
            print(f"❌ خطا: {r.text}")
    except Exception as e:
        print(f"❌ خطا: {e}")
