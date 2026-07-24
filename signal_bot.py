import requests
from datetime import datetime

# ==================== تنظیمات ====================
BALE_TOKEN = "124178101:nDLCPlvd_KlqblUI-6jrbBUCIbx99RRsedU"
BALE_CHAT_ID = "1049670320"

TELEGRAM_TOKEN = "8925877849:AAECDTzPuETHqhUbBfLoTt7O5UespZWOZ7M"
TELEGRAM_CHAT_ID = "292739287"

# آستانه‌های سیگنال (به درصد)
THRESHOLD_NORMAL = 1.0   # آستانه معمولی (ایموجی آبی)
THRESHOLD_STRONG = 2.0   # آستانه قوی (ایموجی بنفش)
TOTAL_FEE = 0.38         # مجموع کارمزدها (درصد)

# ==================== دریافت قیمت‌ها ====================
def get_prices():
    try:
        print("🔍 دریافت قیمت تتر از نوبیتکس...")
        url_tether = "https://apiv2.nobitex.ir/market/stats?srcCurrency=usdt&dstCurrency=rls"
        response_tether = requests.get(url_tether, timeout=15)
        
        if response_tether.status_code != 200:
            print(f"❌ خطا در دریافت قیمت تتر: {response_tether.status_code}")
            return None, None
            
        tether_data = response_tether.json()
        tether_price = float(tether_data['stats']['usdt-rls']['bestSell']) / 10
        
        print("🔍 دریافت قیمت دلار از کانال بله...")
        # دریافت آخرین قیمت دلار از کانال
        dollar_price = get_dollar_from_channel()
        
        # اگر قیمت دلار دریافت نشد، از قیمت تتر به عنوان تخمین استفاده می‌شود
        if dollar_price is None or dollar_price == 0:
            print("⚠️ عدم دسترسی به قیمت دلار. از قیمت تتر به عنوان تخمین استفاده می‌شود.")
            dollar_price = tether_price
        
        print(f"✅ قیمت‌ها با موفقیت دریافت شدند")
        print(f"💵 دلار: {dollar_price:,.0f} | تتر: {tether_price:,.0f} تومان")
        return tether_price, dollar_price
        
    except Exception as e:
        print(f"❌ خطا در دریافت قیمت‌ها: {e}")
        return None, None

def get_dollar_from_channel():
    """دریافت قیمت دلار از کانال بله (با شناسه @channel_username)"""
    try:
        # شناسه کانال خود را اینجا وارد کنید
        CHANNEL_ID = "@your_channel_username"  # ← این را تغییر دهید
        
        url = f"https://api.bale.ai/bot{BALE_TOKEN}/getUpdates"
        params = {
            "chat_id": CHANNEL_ID,
            "limit": 5  # دریافت ۵ پیام آخر
        }
        
        response = requests.get(url, params=params, timeout=15)
        if response.status_code != 200:
            print(f"⚠️ خطا در دریافت از کانال: {response.status_code}")
            return None
            
        data = response.json()
        if not data.get('result'):
            print("⚠️ پیامی در کانال یافت نشد.")
            return None
            
        # بررسی آخرین پیام‌ها برای پیدا کردن قیمت
        import re
        for msg in reversed(data['result']):
            if 'text' in msg:
                text = msg['text']
                # جستجوی اعداد با کاما یا بدون کاما
                numbers = re.findall(r'[\d,]+', text)
                if numbers:
                    clean_text = numbers[0].replace(',', '')
                    price = float(clean_text)
                    # اگر عدد بزرگتر از ۱۰۰۰۰ بود، احتمالاً قیمت است
                    if price > 10000:
                        print(f"✅ قیمت دلار از کانال دریافت شد: {price}")
                        return price
        
        print("⚠️ قیمتی در پیام‌های کانال پیدا نشد.")
        return None
        
    except Exception as e:
        print(f"⚠️ خطا در دریافت از کانال: {e}")
        return None

# ==================== تحلیل و ساخت سیگنال ====================
def get_emoji(diff):
    if abs(diff) >= THRESHOLD_STRONG:
        return "🟣"  # بنفش برای اختلاف بالای ۲٪
    elif abs(diff) >= THRESHOLD_NORMAL:
        return "🔵"  # آبی برای اختلاف بالای ۱٪
    else:
        return "⚪"  # سفید برای اختلاف کمتر از ۱٪

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

# ==================== ارسال پیام ====================
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

# ==================== تابع اصلی ====================
def main():
    print("🤖 ربات سیگنال‌دهنده شروع به کار کرد...")
    print("📊 در حال دریافت قیمت‌های لحظه‌ای...")
    
    # دریافت قیمت‌ها
    tether_price, dollar_price = get_prices()
    
    if tether_price is None or dollar_price is None:
        print("❌ دریافت قیمت ناموفق. ربات متوقف شد.")
        return
    
    # تحلیل بازار و ساخت پیام
    signal_type, message = check_opportunity(tether_price, dollar_price)
    
    print("-" * 50)
    print(f"💵 قیمت تتر: {tether_price:,.0f} تومان")
    print(f"💵 قیمت دلار: {dollar_price:,.0f} تومان")
    print(f"📊 اختلاف قیمت: {((tether_price - dollar_price) / dollar_price) * 100:.2f}%")
    print(f"📊 نوع سیگنال: {signal_type}")
    print("-" * 50)
    
    print("📤 در حال ارسال پیام...")
    
    # ارسال به بله و تلگرام
    bale_result = send_to_bale(message)
    telegram_result = send_to_telegram(message)
    
    if bale_result or telegram_result:
        print("✅ پیام حداقل به یکی از پیام‌رسان‌ها ارسال شد.")
    else:
        print("❌ ارسال پیام به هر دو پیام‌رسان ناموفق بود.")

# ==================== اجرا ====================
if __name__ == "__main__":
    main()
