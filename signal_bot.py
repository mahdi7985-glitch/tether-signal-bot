import requests
from datetime import datetime

# ==================== تنظیمات ====================
BALE_TOKEN = "توکن_ربات_بله_خودتان"
BALE_CHAT_ID = "آیدی_چت_بله_خودتان"

TELEGRAM_TOKEN = "توکن_ربات_تلگرام_خودتان"
TELEGRAM_CHAT_ID = "آیدی_چت_تلگرام_خودتان"

THRESHOLD_NORMAL = 1.0
THRESHOLD_STRONG = 2.0
TOTAL_FEE = 0.38

# ==================== دریافت قیمت ====================
def get_prices():
    try:
        print("🔍 دریافت قیمت تتر از نوبیتکس...")
        # ۱. دریافت قیمت تتر از نوبیتکس (موفق)
        url_tether = "https://apiv2.nobitex.ir/market/stats?srcCurrency=usdt&dstCurrency=rls"
        response_tether = requests.get(url_tether, timeout=15)
        
        if response_tether.status_code != 200:
            print(f"❌ خطا در دریافت قیمت تتر: {response_tether.status_code}")
            return None, None
            
        tether_data = response_tether.json()
        # قیمت تتر به تومان (تقسیم بر ۱۰)
        tether_price = float(tether_data['stats']['usdt-rls']['bestSell']) / 10
        
        print("🔍 دریافت قیمت دلار از tgju.org...")
        # ۲. دریافت قیمت دلار از tgju.org
        url_dollar = "https://www.tgju.org/profile/price_dollar_rl"
        response_dollar = requests.get(url_dollar, timeout=15)
        
        if response_dollar.status_code != 200:
            print(f"❌ خطا در دریافت قیمت دلار: {response_dollar.status_code}")
            return None, None
            
        dollar_data = response_dollar.json()
        # قیمت دلار به تومان
        dollar_price = float(dollar_data.get('price', dollar_data.get('last', 0)))
        
        # بررسی معتبر بودن قیمت‌ها
        if tether_price == 0 or dollar_price == 0:
            print("❌ قیمت دریافتی معتبر نیست (صفر)")
            return None, None
            
        print(f"✅ قیمت‌ها با موفقیت دریافت شدند")
        print(f"💵 دلار: {dollar_price:,.0f} | تتر: {tether_price:,.0f} تومان")
        return tether_price, dollar_price
        
    except Exception as e:
        print(f"❌ خطا در دریافت قیمت‌ها: {e}")
        return None, None

# ==================== بقیه توابع (بدون تغییر) ====================
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
    
    diff_percent = ((tether - dollar) / dollar) * 100
    net_profit = abs(diff_percent) - TOTAL_FEE
    emoji = get_emoji(diff_percent)
    current_time = datetime.now().strftime("%Y/%m/%d - %H:%M")
    
    if diff_percent > THRESHOLD_NORMAL:
        msg = f"""{emoji} **سیگنال فروش تتر**

🔹 اختلاف قیمت: **{diff_percent:.2f}%**
💰 سود خالص تقریبی: **{net_profit:.2f}%**
💡 تتر {diff_percent:.2f}% از دلار گران‌تر است.

✅ **اقدام پیشنهادی:** تتر خود را بفروشید و ریال (تومان) بگیرید.
⏰ زمان: {current_time}"""
        return "SELL", msg
    
    elif diff_percent < -THRESHOLD_NORMAL:
        msg = f"""{emoji} **سیگنال خرید تتر**

🔹 اختلاف قیمت: **{abs(diff_percent):.2f}%**
💰 سود خالص تقریبی: **{net_profit:.2f}%**
💡 دلار {abs(diff_percent):.2f}% از تتر گران‌تر است.

✅ **اقدام پیشنهادی:** با ریال (تومان)، تتر بخرید.
⏰ زمان: {current_time}"""
        return "BUY", msg
    
    else:
        msg = f"""⚪ **بازار در تعادل**

🔹 اختلاف فعلی: **{diff_percent:.2f}%**
🔸 آستانه مورد نیاز برای سیگنال: **{THRESHOLD_NORMAL}%**
💵 قیمت تتر: **{tether:,.0f}** تومان
💵 قیمت دلار: **{dollar:,.0f}** تومان
⏰ زمان: {current_time}"""
        return "NONE", msg

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

def main():
    print("🤖 ربات سیگنال‌دهنده شروع به کار کرد...")
    print("📊 در حال دریافت قیمت‌های لحظه‌ای...")
    
    tether_price, dollar_price = get_prices()
    if not tether_price or not dollar_price:
        print("❌ دریافت قیمت ناموفق. ربات متوقف شد.")
        return
    
    signal_type, message = check_opportunity(tether_price, dollar_price)
    
    print("-" * 50)
    print(f"💵 قیمت تتر: {tether_price:,.0f} تومان")
    print(f"💵 قیمت دلار: {dollar_price:,.0f} تومان")
    print(f"📊 اختلاف قیمت: {((tether_price - dollar_price) / dollar_price) * 100:.2f}%")
    print(f"📊 نوع سیگنال: {signal_type}")
    print("-" * 50)
    
    print("📤 در حال ارسال پیام...")
    bale_result = send_to_bale(message)
    telegram_result = send_to_telegram(message)
    
    if bale_result or telegram_result:
        print("✅ پیام حداقل به یکی از پیام‌رسان‌ها ارسال شد.")
    else:
        print("❌ ارسال پیام به هر دو پیام‌رسان ناموفق بود.")

if __name__ == "__main__":
    main()
