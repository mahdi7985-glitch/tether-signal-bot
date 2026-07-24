import requests
from datetime import datetime

# ==================== تنظیمات ====================
BALE_TOKEN = "توکن_ربات_بله_خودتان"
BALE_CHAT_ID = "آیدی_چت_بله_خودتان"

TELEGRAM_TOKEN = "توکن_ربات_تلگرام_خودتان"
TELEGRAM_CHAT_ID = "آیدی_چت_تلگرام_خودتان"

THRESHOLD_NORMAL = 1.0   # آستانه سیگنال معمولی (ایموجی آبی)
THRESHOLD_STRONG = 2.0   # آستانه سیگنال قوی (ایموجی بنفش)
TOTAL_FEE = 0.38         # مجموع کارمزدها (درصد)

# ==================== دریافت قیمت از نوبیتکس ====================
def get_prices():
    # لیست آدرس‌های نسخه‌های مختلف API نوبیتکس
    base_urls = [
        "https://apiv2.nobitex.ir",  # نسخه جدیدتر
        "https://api.nobitex.ir",    # نسخه اصلی
        "https://nobitex.ir"         # نسخه جایگزین
    ]
    
    for base in base_urls:
        try:
            print(f"🔍 تلاش با آدرس: {base}")
            
            # دریافت قیمت تتر (USDT) به ریال
            url_tether = f"{base}/market/stats?srcCurrency=usdt&dstCurrency=rls"
            res = requests.get(url_tether, timeout=10)
            
            if res.status_code != 200:
                print(f"❌ خطا در دریافت تتر: {res.status_code}")
                continue
                
            data = res.json()
            # قیمت فروش (bestSell) را بر ۱۰ تقسیم می‌کنیم چون نوبیتکس قیمت را به ریال (بدون تومان) برمی‌گرداند
            tether = float(data['stats']['usdt-rls']['bestSell']) / 10
            
            # دریافت قیمت دلار (USD) به ریال
            url_dollar = f"{base}/market/stats?srcCurrency=usd&dstCurrency=rls"
            res2 = requests.get(url_dollar, timeout=10)
            
            if res2.status_code != 200:
                print(f"❌ خطا در دریافت دلار: {res2.status_code}")
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

# ==================== توابع تحلیل و ساخت پیام ====================
def get_emoji(diff):
    """انتخاب ایموجی بر اساس میزان اختلاف قیمت"""
    if abs(diff) >= THRESHOLD_STRONG:
        return "🟣"  # بنفش برای اختلاف بالای ۲٪
    elif abs(diff) >= THRESHOLD_NORMAL:
        return "🔵"  # آبی برای اختلاف بالای ۱٪
    else:
        return "⚪"  # سفید برای اختلاف کمتر از ۱٪

def check_opportunity(tether, dollar):
    """بررسی وضعیت بازار و ساخت پیام مناسب"""
    if tether is None or dollar is None:
        return "ERROR", "❌ خطا در دریافت قیمت‌ها"
    
    # محاسبه درصد اختلاف قیمت
    diff_percent = ((tether - dollar) / dollar) * 100
    # محاسبه سود خالص پس از کسر کارمزد
    net_profit = abs(diff_percent) - TOTAL_FEE
    # دریافت ایموجی مناسب
    emoji = get_emoji(diff_percent)
    # زمان فعلی
    current_time = datetime.now().strftime("%Y/%m/%d - %H:%M")
    
    # ========== سیگنال فروش تتر (تتر گران‌تر از دلار) ==========
    if diff_percent > THRESHOLD_NORMAL:
        msg = f"""{emoji} **سیگنال فروش تتر**

🔹 اختلاف قیمت: **{diff_percent:.2f}%**
💰 سود خالص تقریبی: **{net_profit:.2f}%**
💡 تتر {diff_percent:.2f}% از دلار گران‌تر است.

✅ **اقدام پیشنهادی:** تتر خود را بفروشید و ریال (تومان) بگیرید.
⏰ زمان: {current_time}"""
        return "SELL", msg
    
    # ========== سیگنال خرید تتر (دلار گران‌تر از تتر) ==========
    elif diff_percent < -THRESHOLD_NORMAL:
        msg = f"""{emoji} **سیگنال خرید تتر**

🔹 اختلاف قیمت: **{abs(diff_percent):.2f}%**
💰 سود خالص تقریبی: **{net_profit:.2f}%**
💡 دلار {abs(diff_percent):.2f}% از تتر گران‌تر است.

✅ **اقدام پیشنهادی:** با ریال (تومان)، تتر بخرید.
⏰ زمان: {current_time}"""
        return "BUY", msg
    
    # ========== بازار در تعادل (بدون سیگنال) ==========
    else:
        msg = f"""⚪ **بازار در تعادل**

🔹 اختلاف فعلی: **{diff_percent:.2f}%**
🔸 آستانه مورد نیاز برای سیگنال: **{THRESHOLD_NORMAL}%**
💵 قیمت تتر: **{tether:,.0f}** تومان
💵 قیمت دلار: **{dollar:,.0f}** تومان
⏰ زمان: {current_time}"""
        return "NONE", msg

# ==================== ارسال پیام به پیام‌رسان‌ها ====================

def send_to_bale(msg):
    """ارسال پیام به ربات در پیام‌رسان بله"""
    # آدرس‌های مختلف API بله (برخی کاربران با یکی از آنها مشکل دارند)
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
                # اگر خطا ۴۰۳ بود، ممکن است توکن یا آیدی اشتباه باشد
                if response.status_code == 403:
                    print("   ⚠️ لطفاً توکن و آیدی چت بله را بررسی کنید.")
        except Exception as e:
            print(f"❌ خطا در بله ({url}): {e}")
    
    return False

def send_to_telegram(msg):
    """ارسال پیام به ربات در پیام‌رسان تلگرام"""
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
            if response.status_code == 403:
                print("   ⚠️ لطفاً توکن و آیدی چت تلگرام را بررسی کنید.")
            return False
    except Exception as e:
        print(f"❌ خطا در تلگرام: {e}")
        return False

# ==================== تابع اصلی ====================
def main():
    print("🤖 ربات سیگنال‌دهنده شروع به کار کرد...")
    print("📊 در حال دریافت قیمت‌های لحظه‌ای از نوبیتکس...")
    
    # دریافت قیمت‌ها
    tether_price, dollar_price = get_prices()
    if not tether_price or not dollar_price:
        print("❌ دریافت قیمت ناموفق. ربات متوقف شد.")
        return
    
    # تحلیل بازار و ساخت پیام
    signal_type, message = check_opportunity(tether_price, dollar_price)
    
    # نمایش اطلاعات در لاگ
    print("-" * 50)
    print(f"💵 قیمت تتر: {tether_price:,.0f} تومان")
    print(f"💵 قیمت دلار: {dollar_price:,.0f} تومان")
    print(f"📊 اختلاف قیمت: {((tether_price - dollar_price) / dollar_price) * 100:.2f}%")
    print(f"📊 نوع سیگنال: {signal_type}")
    print("-" * 50)
    
    # ارسال پیام به هر دو پیام‌رسان
    print("📤 در حال ارسال پیام...")
    bale_result = send_to_bale(message)
    telegram_result = send_to_telegram(message)
    
    # نتیجه نهایی
    if bale_result or telegram_result:
        print("✅ پیام حداقل به یکی از پیام‌رسان‌ها ارسال شد.")
    else:
        print("❌ ارسال پیام به هر دو پیام‌رسان ناموفق بود.")
        print("   ⚠️ لطفاً تنظیمات شبکه، توکن‌ها و آیدی‌های چت را بررسی کنید.")

# ==================== نقطه شروع اجرا ====================
if __name__ == "__main__":
    main()
