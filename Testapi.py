import requests

# دریافت قیمت تتر
url_tether = "https://apiv2.nobitex.ir/market/stats?srcCurrency=usdt&dstCurrency=rls"
response_tether = requests.get(url_tether, timeout=15)

print(f"وضعیت تتر: {response_tether.status_code}")
print(f"پاسخ تتر: {response_tether.text[:300]}...")  # چاپ بخشی از پاسخ

# دریافت قیمت دلار
url_dollar = "https://apiv2.nobitex.ir/market/stats?srcCurrency=usd&dstCurrency=rls"
response_dollar = requests.get(url_dollar, timeout=15)

print(f"\nوضعیت دلار: {response_dollar.status_code}")
print(f"پاسخ دلار: {response_dollar.text[:300]}...")
