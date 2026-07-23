import time
import requests
from datetime import datetime

# ==================== تنظیمات ====================
BALE_TOKEN = "124178101:7dLO9-5SsUmHmNkTk7azkyyh62s8P-DVrd4"  # توکن فرضی
BALE_CHAT_ID = "1049670320"  # آیدی چت فرضی

THRESHOLD_NORMAL = 1.0  # آستانه ۱٪ (ایموجی آبی)
THRESHOLD_STRONG = 2.0  # آستانه ۲٪ (ایموجی بنفش)
TOTAL_FEE = 0.38  # مجموع کارمزدها (درصد)

# ==================== توابع ====================

def get_prices():
    """دریافت قیمت تتر و دلار از نوبیتکس"""
    try:
        # دریافت قیمت تتر
        response_tether = requests.get(
            "https://api.nobitex.ir/market/stats?srcCurrency=usdt&dstCurrency=rls",
            timeout=10
        )
        data_tether = response_tether.json()
        tether_price = float(data_tether['stats']['usdt-rls']['bestSell']) / 10
        
        # دریافت قیمت دلار
        response_dollar = requests.get(
            "https://api.nobitex.ir/market/stats?srcCurrency=usd&dstCurrency=rls",
            timeout=10
        )
        data_dollar = response_dollar.json()
        dollar_price = float(data_dollar['stats']['usd-rls']['bestSell']) / 10
        
        return tether_price, dollar_price
    except Exception as e:
        print(f"❌ خطا در دریافت قیمت: {e}")
        return None, None

def get_emoji(diff_percent):
    """بر اساس درصد اختلاف، ایموجی مناسب را برمی‌گرداند"""
    if abs(diff_percent) >= THRESHOLD_STRONG:
        return "🟣"  # بنفش برای اختلاف بالای ۲٪
    elif abs(diff_percent) >= THRESHOLD_NORMAL:
        return "🔵"  # آبی برای اختلاف بالای ۱٪
    else:
        return "⚪"  # سفید برای اختلاف کمتر از ۱٪

def check_opportunity(tether_price, dollar_price):
    """بررسی فرصت معاملاتی"""
    if tether_price is None or dollar_price is None:
        return "ERROR", "❌ خطا در دریافت قیمت‌ها"
    
    diff_percent = ((tether_price - dollar_price) / dollar_price) * 100
    net_profit = abs(diff_percent) - TOTAL_FEE
    emoji = get_emoji(diff_percent)
    current_time = datetime.now().strftime("%Y/%m/%d - %H:%M")
    
    if diff_percent > THRESHOLD_NORMAL:
        signal_type = "SELL_TETHER"
        message = f"""{emoji} **سیگنال فروش تتر**

🔹 اختلاف قیمت: **{diff_percent:.2f}%**
🔸 کارمزد کل: **{TOTAL_FEE:.2f}%**
💰 **سود خالص**: **{net_profit:.2f}%**
💡 تتر {diff_percent:.2f}% از دلار گران‌تر است.

✅ اقدام پیشنهادی: تتر خود را بفروشید و ریال بگیرید.
⏰ زمان: {current_time}"""
    
    elif diff_percent < -THRESHOLD_NORMAL:
        signal_type = "BUY_TETHER"
        message = f"""{emoji} **سیگنال خرید تتر**

🔹 اختلاف قیمت: **{abs(diff_percent):.2f}%**
🔸 کارمزد کل: **{TOTAL_FEE:.2f}%**
💰 **سود خالص**: **{net_profit:.2f}%**
💡 دلار {abs(diff_percent):.2f}% از تتر گران‌تر است.

✅ اقدام پیشنهادی: با ریال، تتر بخرید.
⏰ زمان: {current_time}"""
    
    else:
        signal_type = "NO_SIGNAL"
        message = f"""⚪ **بازار در تعادل**

🔹 اختلاف فعلی: **{diff_percent:.2f}%**
🔸 آستانه تنظیم شده: **{THRESHOLD_NORMAL}%**
⏳ در حال رصد بازار...
⏰ زمان: {current_time}"""
    
    return signal_type, message

def send_to_bale(message):
    """ارسال پیام به ربات بله با استفاده از API"""
    url = f"https://api.bale.ai/bot{BALE_TOKEN}/sendMessage"
    payload = {
        "chat_id": BALE_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ پیام با موفقیت ارسال شد")
        else:
            print(f"❌ خطا در ارسال پیام: {response.text}")
    except Exception as e:
        print(f"❌ خطا در ارسال پیام: {e}")

# ==================== تابع اصلی ====================

def main():
    print("🤖 ربات سیگنال‌دهنده راه‌اندازی شد!")
    print(f"📊 آستانه معمولی: {THRESHOLD_NORMAL}% | آستانه قوی: {THRESHOLD_STRONG}%")
    print("-" * 50)
    
    # دریافت قیمت‌ها
    tether_price, dollar_price = get_prices()
    
    if tether_price and dollar_price:
        # بررسی فرصت
        signal_type, message = check_opportunity(tether_price, dollar_price)
        
        # چاپ در کنسول
        print(f"🔄 تتر: {tether_price:,} | دلار: {dollar_price:,}")
        print(f"📊 اختلاف: {((tether_price - dollar_price) / dollar_price) * 100:.2f}%")
        print("-" * 50)
        
        # ارسال پیام فقط اگر سیگنال وجود داشته باشد
        if signal_type != "NO_SIGNAL":
            send_to_bale(message)
        else:
            print("⏳ بازار در تعادل - سیگنالی ارسال نشد")
    else:
        print("❌ خطا در دریافت قیمت‌ها")

# ==================== اجرا ====================

if __name__ == "__main__":
    main()            text=message,
            parse_mode="markdown"
        )
        print(f"✅ پیام ارسال شد: {message[:50]}...")
    except Exception as e:
        print(f"❌ خطا در ارسال پیام: {e}")

# ==================== تابع اصلی ربات ====================

async def main():
    """حلقه اصلی ربات"""
    client = Client(token=BALE_TOKEN)
    await client.start()
    
    print("🤖 ربات سیگنال‌دهنده راه‌اندازی شد!")
    print(f"⏱️ هر {CHECK_INTERVAL//60} دقیقه یکبار قیمت‌ها بررسی می‌شوند.")
    print(f"📊 آستانه معمولی: {THRESHOLD_NORMAL}% | آستانه قوی: {THRESHOLD_STRONG}%")
    print("-" * 50)
    
    last_signal = {}  # برای جلوگیری از ارسال مکرر سیگنال
    
    while True:
        try:
            # دریافت قیمت‌ها
            tether_price, dollar_price = get_prices()
            
            if tether_price and dollar_price:
                # بررسی فرصت
                signal_type, message = check_opportunity(tether_price, dollar_price)
                
                # چاپ در کنسول برای دیباگ
                print(f"🔄 {datetime.now().strftime('%H:%M:%S')} - تتر: {tether_price:,} | دلار: {dollar_price:,}")
                
                # ارسال سیگنال (فقط اگر سیگنال جدید باشد)
                if signal_type != "NO_SIGNAL":
                    # جلوگیری از ارسال مکرر همان سیگنال
                    signal_key = f"{signal_type}_{int(tether_price)}_{int(dollar_price)}"
                    if signal_key != last_signal.get("key"):
                        await send_message(client, message)
                        last_signal = {"key": signal_key, "time": time.time()}
                else:
                    # اگر بازار متعادل بود، هر ۱ ساعت یکبار اطلاع بده
                    if time.time() - last_signal.get("time", 0) > 3600:
                        await send_message(client, message)
                        last_signal["time"] = time.time()
            
            # منتظر بمان تا دوباره چک کند
            await asyncio.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            print(f"❌ خطا در حلقه اصلی: {e}")
            await asyncio.sleep(60)  # در صورت خطا، ۱ دقیقه صبر کن

# ==================== اجرای ربات ====================

if __name__ == "__main__":
    asyncio.run(main())
