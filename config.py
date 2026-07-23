import os
from dotenv import load_dotenv

load_dotenv()

BALE_TOKEN = os.getenv("BALE_TOKEN")
BALE_CHAT_ID = os.getenv("BALE_CHAT_ID")

THRESHOLD_NORMAL = 1.0
THRESHOLD_STRONG = 2.0
TOTAL_FEE = 0.38
NOBITEX_API_URL = "https://api.nobitex.ir/market/stats"
MAX_HOLD_HOURS = 24
STOP_LOSS = 0.5
