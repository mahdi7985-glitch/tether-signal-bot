import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re
import sys

# ==================== تنظیمات ====================
BALE_TOKEN = "124178101:nDLCPlvd_KlqblUI-6jrbBUCIbx99RRsedU"
BALE_CHAT_ID = "1049670320"

TELEGRAM_TOKEN = "8925877849:AAECDTzPuETHqhUbFbLoTt7O5UespZWOZ7M"
TELEGRAM_CHAT_ID = "292739287"

THRESHOLD_NORMAL = 1.0
THRESHOLD_STRONG = 2.0
TOTAL_FEE = 0.38

# ==================== دریافت قیمت دلار از TGJU (اصلاح‌شده) ====================
def get_dollar_price_from_tgju():
    try:
        print("🔍 تلاش برای دریافت قیمت دلار از TGJU...")
        url = "https://www.tgju.org/profile/price_dollar_rl"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # روش اصلی: جستجوی عنصر با data-col='last'
        price_element = soup.find('span', {'data-col': 'last'})
        if price_element:
            price_text = price_element.get_text().strip()
            clean_price = re.sub(r'[^\d.]', '', price_text)
            if clean_price:
                price = float(clean_price)
                if price > 1000:
                    price = price / 10
                print(f"✅ قیمت دلار از TGJU دریافت شد: {price:,.0f} تومان")
                return price
        
        # روش جایگزین: جستجوی اعداد بزرگ در صفحه
        text = soup.get_text()
        numbers = re.findall(r'(\d{1,3}(?:,\d{3})*\.?\d*)', text)
        for num in numbers:
            clean_num = num.replace(',', '')
            if clean_num.replace('.', '').isdigit():
                price = float(clean_num)
                # محدوده منطقی برای قیمت دلار به ریال: ۱۰۰,۰۰۰ تا ۱۰,۰۰۰,۰۰۰
                if 100000 < price < 10000000:
                    price = price / 10
                    print(f"✅ قیمت دلار از TGJU دریافت شد: {price:,.0f} تومان")
                    return price
        
        print("⚠️ قیمت دلار در TGJU پیدا نشد.")
        return None
        
    except Exception as e:
        print(f"❌ خطا در دریافت قیمت از TGJU: {e}")
        return None

# ==================== دریافت قیمت تتر از نوبیتکس ====================
def get_tether_price():
    try:
        print("🔍 دریافت قیمت تتر از نوبیتکس...")
        url_tether = "https://apiv2.nobitex.ir/market/stats?srcCurrency=usdt&dstCurrency=rls"
        response_tether = requests.get(url_tether, timeout=15)
        
        if response_tether.status_code != 200:
            print(f"❌ خطا در دریافت قیمت تتر: {response_tether.status_code}")
            return None
            
        tether_data = response_tether.json()
        tether_price = float(tether_data['stats']['usdt-rls']['bestSell']) / 10
        print(f"✅ قیمت تتر از نوبیتکس دریافت شد: {tether_price:,.0f} تومان")
        return tether_price
        
    except Exception as e:
        print(f"❌ خطا در دریافت قیمت تتر: {e}")
        return None

# ==================== دریافت قیمت‌ها ====================
def get_prices():
    tether_price = get_tether_price()
    if tether_price is None:
        return None, None
    
    dollar_price = get_dollar_price_from_tgju()
    
    # اگر TGJU کار نکرد، از قیمت تتر به عنوان تخمین استفاده می‌شود
    if dollar_price is None or dollar_price == 0:
        print("⚠️ عدم دسترسی به قیمت دلار. از قیمت تتر به عنوان تخمین استفاده می‌شود.")
        dollar_price = tether_price
    
    print(f"💵 قیمت نهایی: دلار {dollar_price:,.0f} | تتر {tether_price:,.0f} تومان")
    return tether_price, dollar_price

# ==================== تحلیل و ساخت سیگنال ====================
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
    
    tether_price, dollar_price = get_prices()
    
    if tether_price is None or dollar_price is None:
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

# ==================== اجرا ====================
if __name__ == "__main__":
    main()
