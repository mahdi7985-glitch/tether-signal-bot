import requests
from datetime import datetime

# ==================== تنظیمات ====================
BALE_TOKEN = "توکن_بله"
BALE_CHAT_ID = "آیدی_بله"

TELEGRAM_TOKEN = "توکن_تلگرام"
TELEGRAM_CHAT_ID = "آیدی_تلگرام"

THRESHOLD_NORMAL = 1.0
THRESHOLD_STRONG = 2.0
TOTAL_FEE = 0.38

# ==================== دریافت قیمت ====================

def get_prices():
    base_urls = [
        "https://api.nobitex.ir",
        "https://nobitex.ir",
        "https://api2.nobitex.ir"
    ]
    
    for base in base_urls:
        try:
            print(f"🔍 تلاش با آدرس: {base}")
            
            url_tether = f"{base}/market/stats?srcCurrency=usdt&dstCurrency=rls"
            res = requests.get(url_tether, timeout=10)
            
            if res.status_code != 200:
                print(f"❌ خطا در تتر: {res.status_code}")
                continue
                
            data = res.json()
            tether = float(data['stats']['usdt-rls']['bestSell']) / 10
            
            url_dollar = f"{base}/market/stats?srcCurrency=usd&dstCurrency=rls"
            res2 = requests.get(url_dollar, timeout=10)
            
            if res2.status_code != 200:
                print(f"❌ خطا در دلار: {res2.status_code}")
                continue
                
            data2 = res2.json()
            dollar = float(data2['stats']['usd-rls']['bestSell']) / 10
            
            print(f"✅ قیمت‌ها با موفقیت از {base} دریافت شدند")
            return tether, dollar
            
        except Exception as e:
            print(f"❌ خطا با {base}: {e}")
            continue
    
    print("❌ همه آدرس‌های API ناموفق بودند")
    return None, None

# ==================== توابع تحلیل ====================

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
                print(f"❌ خطا در بله ({url}): {r.status_code}")
        except Exception as e:
            print(f"❌ خطا در بله ({url}): {e}")
    return False

# ==================== ارسال به تلگرام ====================

def send_to_telegram(msg):
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
            print(f"❌ خطا در تلگرام: {r.status_code}")
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
    
    bale_ok = send_to_bale(message)
    telegram_ok = send_to_telegram(message)
    
    if bale_ok or telegram_ok:
        print("✅ پیام حداقل به یکی از پیام‌رسان‌ها ارسال شد")
    else:
        print("❌ ارسال پیام به هر دو پیام‌رسان ناموفق بود")

# ==================== اجرا ====================

if __name__ == "__main__":
    main()
