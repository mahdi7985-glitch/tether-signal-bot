import requests
from datetime import datetime

# ==================== تنظیمات ====================
# توکن و آیدی ربات بله (از فایل env یا مستقیم)
BALE_TOKEN = "124178101:7dLO9-5SsUmHmNkTk7azkyyh62s8P-DVrd4"
BALE_CHAT_ID = "1049670320"

THRESHOLD_NORMAL = 1.0
THRESHOLD_STRONG = 2.0
TOTAL_FEE = 0.38

# ==================== توابع ====================

def get_prices():
    try:
        # قیمت تتر
        res = requests.get("https://api.nobitex.ir/market/stats?srcCurrency=usdt&dstCurrency=rls", timeout=10)
        tether = float(res.json()['stats']['usdt-rls']['bestSell']) / 10
        
        # قیمت دلار
        res2 = requests.get("https://api.nobitex.ir/market/stats?srcCurrency=usd&dstCurrency=rls", timeout=10)
        dollar = float(res2.json()['stats']['usd-rls']['bestSell']) / 10
        
        return tether, dollar
    except Exception as e:
        print(f"❌ خطا: {e}")
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
        return "ERROR", "خطا در دریافت قیمت"
    
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
        msg = f"""⚪ **بازار متعادل**

🔹 اختلاف: {diff:.2f}%
⏰ {time}"""
        return "NONE", msg

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
    
    if signal_type != "NONE":
        send_alert(message)
    else:
        print("⏳ بدون سیگنال")

# ==================== اجرا ====================

if __name__ == "__main__":
    main()
