import requests
import json

print("🚀 شروع تست API نوبیتکس (apiv2)...")

# تست ۱: دریافت قیمت تتر
url_tether = "https://apiv2.nobitex.ir/market/stats?srcCurrency=usdt&dstCurrency=rls"
try:
    print("\n🔹 درخواست به:", url_tether)
    response_tether = requests.get(url_tether, timeout=15)
    print(f"🔹 وضعیت: {response_tether.status_code}")
    
    if response_tether.status_code == 200:
        data = response_tether.json()
        print("🔹 کلیدهای اصلی:", list(data.keys()))
        print("🔹 ساختار stats:", list(data.get('stats', {}).keys()))
        
        # نمایش قیمت تتر
        usdt_stats = data.get('stats', {}).get('usdt-rls', {})
        print("🔹 داده‌های usdt-rls:", list(usdt_stats.keys()))
        print("🔹 bestSell:", usdt_stats.get('bestSell', 'ناموجود'))
        print("🔹 latest:", usdt_stats.get('latest', 'ناموجود'))
        
    else:
        print("🔹 پاسخ:", response_tether.text[:300])
        
except Exception as e:
    print(f"❌ خطا: {e}")

# تست ۲: دریافت قیمت دلار
url_dollar = "https://apiv2.nobitex.ir/market/stats?srcCurrency=usd&dstCurrency=rls"
try:
    print("\n🔹 درخواست به:", url_dollar)
    response_dollar = requests.get(url_dollar, timeout=15)
    print(f"🔹 وضعیت: {response_dollar.status_code}")
    
    if response_dollar.status_code == 200:
        data = response_dollar.json()
        usd_stats = data.get('stats', {}).get('usd-rls', {})
        print("🔹 داده‌های usd-rls:", list(usd_stats.keys()))
        print("🔹 bestSell:", usd_stats.get('bestSell', 'ناموجود'))
        print("🔹 latest:", usd_stats.get('latest', 'ناموجود'))
        
    else:
        print("🔹 پاسخ:", response_dollar.text[:300])
        
except Exception as e:
    print(f"❌ خطا: {e}")

print("\n✅ تست کامل شد!")
