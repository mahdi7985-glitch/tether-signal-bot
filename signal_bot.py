import requests
from datetime import datetime

BALE_TOKEN = "124178101:7dLO9-5SsUmHmNkTk7azkyyh62s8P-DVrd4"
BALE_CHAT_ID = "1049670320"

THRESHOLD_NORMAL = 0.1  # برای تست پایین آوردیم
THRESHOLD_STRONG = 0.5
TOTAL_FEE = 0.38

def get_prices():
    try:
        res = requests.get("https://api.nobitex.ir/market/stats?srcCurrency=usdt&dstCurrency=rls", timeout=10)
        tether = float(res.json()['stats']['usdt-rls']['bestSell']) / 10
        
        res2 = requests.get("https://api.nobitex.ir/market/stats?srcCurrency=usd&dstCurrency=rls", timeout=10)
        dollar = float(res2.json()['stats']['usd-rls']['bestSell']) / 10
        
        return tether, dollar
    except Exception as e:
        print(f"❌ خطا: {e}")
        return None, None

def check_opportunity(tether, dollar):
    if tether is None or dollar is None:
        return "ERROR", "❌ خطا در دریافت قیمت‌ها"
    
    diff = ((tether - dollar) / dollar) * 100
    profit = abs(diff) - TOTAL_FEE
    time = datetime.now().strftime("%Y/%m/%d - %H:%M")
    
    if diff > THRESHOLD_NORMAL:
        msg = f"""🔵 **سیگنال فروش تتر**
🔹 اختلاف: {diff:.2f}%
💰 سود خالص: {profit:.2f}%
✅ تتر را بفروشید
⏰ {time}"""
        return "SELL", msg
    
    elif diff < -THRESHOLD_NORMAL:
        msg = f"""🔵 **سیگنال خرید تتر**
🔹 اختلاف: {abs(diff):.2f}%
💰 سود خالص: {profit:.2f}%
✅ تتر بخرید
⏰ {time}"""
        return "BUY", msg
    
    else:
        msg = f"""⚪ **فعلاً خبری نیست**
🔹 اختلاف فعلی: {diff:.2f}%
🔸 آستانه: {THRESHOLD_NORMAL}%
💵 تتر: {tether:,.0f} | دلار: {dollar:,.0f}
⏰ {time}"""
        return "NONE", msg

def send_alert(msg):
    # امتحان با api و tapi
    urls = [
        f"https://api.bale.ai/bot{BALE_TOKEN}/sendMessage",
        f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage"
    ]
    
    for url in urls:
        try:
            r = requests.post(url, json={"chat_id": BALE_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
            if r.status_code == 200:
                print(f"✅ پیام با آدرس {url} ارسال شد")
                return True
            else:
                print(f"❌ خطا با آدرس {url}: {r.status_code} - {r.text}")
        except Exception as e:
            print(f"❌ خطا با آدرس {url}: {e}")
    
    return False

def main():
    print("🤖 ربات شروع به کار کرد...")
    tether, dollar = get_prices()
    if not tether or not dollar:
        print("❌ دریافت قیمت ناموفق")
        return
    
    signal_type, message = check_opportunity(tether, dollar)
    print(f"💵 تتر: {tether:,} | دلار: {dollar:,}")
    print(f"📊 اختلاف: {((tether - dollar) / dollar) * 100:.2f}%")
    
    success = send_alert(message)
    if success:
        print("✅ پیام ارسال شد")
    else:
        print("❌ ارسال پیام ناموفق")

if __name__ == "__main__":
    main()
