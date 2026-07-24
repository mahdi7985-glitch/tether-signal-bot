import os
import requests
from datetime import datetime

# ==================== تنظیمات ====================

# ---------- تنظیمات بله (از GitHub Secrets خونده می‌شه) ----------
BALE_TOKEN = os.environ.get("BALE_TOKEN")
BALE_CHAT_ID = os.environ.get("BALE_CHAT_ID")

# ---------- تنظیمات تلگرام (از GitHub Secrets خونده می‌شه) ----------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# ---------- تنظیمات مشترک ----------
THRESHOLD_NORMAL = 1.0
THRESHOLD_STRONG = 2.0
TOTAL_FEE = 0.38

# ==================== توابع ====================

def get_prices():
    try:
        res = requests.post(
            "https://apiv2.nobitex.ir/market/stats",
            json={"srcCurrency": "usdt", "dstCurrency": "rls"},
            timeout=10
        )
        res.raise_for_status()
        tether = float(res.json()['stats']['usdt-rls']['bestSell']) / 10

        res2 = requests.post(
            "https://apiv2.nobitex.ir/market/stats",
            json={"srcCurrency": "usd", "dstCurrency": "rls"},
            timeout=10
        )
        res2.raise_for_status()
        dollar = float(res2.json()['stats']['usd-rls']['bestSell']) / 10

        return tether, dollar
    except Exception as e:
        print(f"❌ خطا در دریافت قیمت: {e}")
        return None, None

def get_emoji(diff):
    if abs(diff) >= THRESHOLD_STRONG:
        return "🟣"
    elif abs(diff) >= THRESHOLD_NORMAL:
        return "🔵"
    else:
        return "⚪"

def check_opportunity(tether, dollar):
    if tether is None or dollar is None:
        return "ERROR", "❌ خطا در دریافت قیمت‌ها"

    diff = ((tether - dollar) / dollar) * 100
    profit = abs(diff) - TOTAL_FEE
    emoji = get_emoji(diff)
    time = datetime.now().strftime("%Y/%m/%d - %H:%M")

    if diff > THRESHOLD_NORMAL:
        msg = f"""{emoji} **سیگنال فروش تتر**

🔹 اختلاف: {diff:.2f}%
💰 سود خالص: {profit:.2f}%
✅ تتر را بفروشید
⏰ {time}"""
        return "SELL", msg

    elif diff < -THRESHOLD_NORMAL:
        msg = f"""{emoji} **سیگنال خرید تتر**

🔹 اختلاف: {abs(diff):.2f}%
💰 سود خالص: {profit:.2f}%
✅ تتر بخرید
⏰ {time}"""
        return "BUY", msg

    else:
        msg = f"""⚪ **فعلاً خبری نیست**

🔹 اختلاف فعلی: {diff:.2f}%
🔸 آستانه مورد نیاز: {THRESHOLD_NORMAL}%
💵 تتر: {tether:,.0f} تومان
💵 دلار: {dollar:,.0f} تومان
⏰ {time}"""
        return "NONE", msg

# ==================== ارسال به بله ====================

def send_to_bale(msg):
    if not BALE_TOKEN or not BALE_CHAT_ID:
        print("⚠️ BALE_TOKEN یا BALE_CHAT_ID تنظیم نشده - از ارسال به بله صرف‌نظر شد")
        return False

    urls = [
        f"https://api.bale.ai/bot{BALE_TOKEN}/sendMessage",
        f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage"
    ]

    for url in urls:
        try:
            r = requests.post(url, json={
                "chat_id": BALE_CHAT_ID,
                "text": msg,
                "parse_mode": "Markdown"
            }, timeout=10)
            if r.status_code == 200:
                print("✅ پیام به بله ارسال شد")
                return True
            else:
                print(f"❌ خطا در بله ({url}): {r.status_code} - {r.text}")
        except Exception as e:
            print(f"❌ خطا در بله ({url}): {e}")

    return False

# ==================== ارسال به تلگرام ====================

def send_to_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ TELEGRAM_TOKEN یا TELEGRAM_CHAT_ID تنظیم نشده - از ارسال به تلگرام صرف‌نظر شد")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown"
        }, timeout=10)
        if r.status_code == 200:
            print("✅ پیام به تلگرام ارسال شد")
            return True
        else:
            print(f"❌ خطا در تلگرام: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"❌ خطا در تلگرام: {e}")
        return False

# ==================== تابع اصلی ====================

def main():
    print("🤖 ربات سیگنال‌دهنده شروع به کار کرد...")

    tether, dollar = get_prices()
    if not tether or not dollar:
        print("❌ دریافت قیمت ناموفق")
        return

    signal_type, message = check_opportunity(tether, dollar)

    print(f"💵 تتر: {tether:,} | دلار: {dollar:,}")
    print(f"📊 اختلاف: {((tether - dollar) / dollar) * 100:.2f}%")

    # ارسال به هر دو پیام‌رسان
    bale_ok = send_to_bale(message)
    telegram_ok = send_to_telegram(message)

    if bale_ok or telegram_ok:
        print("✅ پیام حداقل به یکی از پیام‌رسان‌ها ارسال شد")
    else:
        print("❌ ارسال پیام به هر دو پیام‌رسان ناموفق بود")

import http.client

conn = http.client.HTTPSConnection("apiv2.nobitex.ir")
payload = ''
headers = {
  'Accept': 'application/json'
}
conn.request("GET", "/market/stats", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))

# ==================== اجرا ====================

if __name__ == "__main__":
    main()
