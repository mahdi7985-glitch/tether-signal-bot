import requests
from datetime import datetime

# ==================== تنظیمات ====================
BALE_TOKEN = "توکن_ربات_بله_خودتان"
BALE_CHAT_ID = "آیدی_چت_بله_خودتان"

TELEGRAM_TOKEN = "توکن_ربات_تلگرام_خودتان"
TELEGRAM_CHAT_ID = "آیدی_چت_تلگرام_خودتان"

# ==================== دریافت قیمت تتر ====================
def get_tether_price():
    try:
        print("🔍 دریافت قیمت تتر از نوبیتکس...")
        url_tether = "https://apiv2.nobitex.ir/market/stats?srcCurrency=usdt&dstCurrency=rls"
        response_tether = requests.get(url_tether, timeout=15)
        
        if response_tether.status_code != 200:
            print(f"❌ خطا در دریافت قیمت تتر: {response_tether.status_code}")
            return None
            
        tether_data = response_tether.json()
        # قیمت تتر به تومان (تقسیم بر ۱۰)
        tether_price = float(tether_data['stats']['usdt-rls']['bestSell']) / 10
        return tether_price
        
    except Exception as e:
        print(f"❌ خطا در دریافت قیمت تتر: {e}")
        return None

# ==================== ارسال پیام به بله ====================
def send_to_bale(msg):
    urls = [
        f"https://api.bale.ai/bot{BALE_TOKEN}/sendMessage",
        f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage"
    ]
    for url in urls:
        try:
            response = requests.post(url, json={
                "chat_id": BALE_CHAT_ID,
                "text": msg,
                "parse_mode": "Markdown"
            }, timeout=15)
            if response.status_code == 200:
                print("✅ پیام به بله ارسال شد")
                return True
            else:
                print(f"❌ خطا در بله ({url}): {response.status_code}")
        except Exception as e:
            print(f"❌ خطا در بله ({url}): {e}")
    return False

# ==================== ارسال پیام به تلگرام ====================
def send_to_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown"
        }, timeout=15)
        if response.status_code == 200:
            print("✅ پیام به تلگرام ارسال شد")
            return True
        else:
            print(f"❌ خطا در تلگرام: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ خطا در تلگرام: {e}")
        return False

# ==================== تابع اصلی ====================
def main():
    print("🤖 ربات تست قیمت تتر شروع به کار کرد...")
    print("📊 در حال دریافت قیمت لحظه‌ای تتر...")
    
    # دریافت قیمت تتر
    tether_price = get_tether_price()
    
    if tether_price is None:
        print("❌ دریافت قیمت تتر ناموفق. ربات متوقف شد.")
        return
    
    # ساخت پیام
    current_time = datetime.now().strftime("%Y/%m/%d - %H:%M")
    message = f"""💰 **قیمت لحظه‌ای تتر**

💵 قیمت تتر: **{tether_price:,.0f}** تومان
⏰ زمان: {current_time}
📌 این یک پیام تست است."""
    
    print("-" * 50)
    print(f"💵 قیمت تتر: {tether_price:,.0f} تومان")
    print("-" * 50)
    
    print("📤 در حال ارسال پیام به پیام‌رسان‌ها...")
    
    # ارسال به بله
    bale_result = send_to_bale(message)
    
    # ارسال به تلگرام
    telegram_result = send_to_telegram(message)
    
    # نتیجه نهایی
    if bale_result or telegram_result:
        print("✅ پیام حداقل به یکی از پیام‌رسان‌ها ارسال شد.")
    else:
        print("❌ ارسال پیام به هر دو پیام‌رسان ناموفق بود.")

# ==================== اجرا ====================
if __name__ == "__main__":
    main()
